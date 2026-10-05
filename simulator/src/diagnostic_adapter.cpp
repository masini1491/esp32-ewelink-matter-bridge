#include <cstddef>
#include <cstdint>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

#include "bridge_simulator/synthetic_device.hpp"

namespace {

constexpr std::size_t kMaxEvents = 32;
constexpr std::size_t kMaxSubmittedIntents = 64;

const char* StateName(const bridge_core::BinaryState state) {
    switch (state) {
        case bridge_core::BinaryState::kOn:
            return "on";
        case bridge_core::BinaryState::kOff:
            return "off";
        case bridge_core::BinaryState::kUnknown:
            return "unknown";
    }
    return "unknown";
}

const char* AvailabilityName(const bridge_core::Availability availability) {
    return availability == bridge_core::Availability::kAvailable ? "available" : "unavailable";
}

const char* DispositionName(const bridge_core::TransportDisposition disposition) {
    switch (disposition) {
        case bridge_core::TransportDisposition::kPending:
            return "pending";
        case bridge_core::TransportDisposition::kAccepted:
            return "accepted";
        case bridge_core::TransportDisposition::kRejected:
            return "rejected";
    }
    return "pending";
}

const char* ConvergenceName(const bridge_core::Convergence convergence) {
    switch (convergence) {
        case bridge_core::Convergence::kNone:
            return "none";
        case bridge_core::Convergence::kMatched:
            return "matched";
        case bridge_core::Convergence::kConflicted:
            return "conflicted";
        case bridge_core::Convergence::kRejected:
            return "rejected";
    }
    return "none";
}

const char* StatusName(const bridge_core::Status status) {
    switch (status) {
        case bridge_core::Status::kOk:
            return "ok";
        case bridge_core::Status::kInvalidState:
            return "invalid_state";
        default:
            return "invalid_action";
    }
}

std::string EscapeJson(const std::string& value) {
    std::string escaped;
    escaped.reserve(value.size());
    for (const unsigned char character : value) {
        switch (character) {
            case '"':
                escaped += "\\\"";
                break;
            case '\\':
                escaped += "\\\\";
                break;
            case '\n':
                escaped += "\\n";
                break;
            case '\r':
                escaped += "\\r";
                break;
            case '\t':
                escaped += "\\t";
                break;
            default:
                if (character < 0x20) {
                    escaped += '?';
                } else {
                    escaped += static_cast<char>(character);
                }
        }
    }
    return escaped;
}

std::optional<bridge_core::BinaryState> ParseActionState(const std::string& value) {
    if (value == "on") return bridge_core::BinaryState::kOn;
    if (value == "off") return bridge_core::BinaryState::kOff;
    return std::nullopt;
}

std::string ErrorJson(const char* error) { return std::string("{\"error\":\"") + error + "\"}"; }

class DiagnosticAdapter {
public:
    std::string Handle(const std::string& line, bool* should_quit) {
        std::istringstream input(line);
        std::string operation;
        std::string first;
        std::string second;
        std::string extra;
        int channel = -1;
        if (!(input >> operation)) return ErrorJson("invalid_command");

        if (operation == "state") {
            if (input >> extra) return ErrorJson("invalid_command");
            return SnapshotJson();
        }
        if (operation == "quit") {
            if (input >> extra) return ErrorJson("invalid_command");
            *should_quit = true;
            return SnapshotJson();
        }
        if (operation == "connect" || operation == "disconnect" || operation == "stale" ||
            operation == "reconnect") {
            if (input >> extra) return ErrorJson("invalid_command");
            if (operation == "connect") {
                device_.Connect();
            } else if (operation == "disconnect") {
                device_.Disconnect();
            } else if (operation == "stale") {
                device_.MarkStale();
            } else {
                device_.Reconnect();
            }
            AddEvent(operation == "stale" ? "Simulator state marked stale" :
                     operation == "connect" ? "Simulator connected" :
                     operation == "disconnect" ? "Simulator disconnected" : "Simulator reconnected");
            return SnapshotJson();
        }
        if (operation == "transport") {
            if (!(input >> first) || (input >> extra) || (first != "accepted" && first != "rejected")) {
                return ErrorJson("invalid_command");
            }
            const bool accepted = first == "accepted";
            device_.SetNextTransportResult(accepted ? bridge_simulator::NextTransportResult::kAccepted
                                                    : bridge_simulator::NextTransportResult::kRejected);
            AddEvent(std::string("Next synthetic transport result: ") + (accepted ? "accepted" : "rejected"));
            return SnapshotJson();
        }
        if (operation == "command" || operation == "observe") {
            if (!(input >> channel >> first) || (input >> extra) || channel < 0 || channel >= 4) {
                return ErrorJson("invalid_command");
            }
            const auto state = ParseActionState(first);
            if (!state) return ErrorJson("invalid_command");

            if (operation == "observe") {
                const auto status = device_.InjectObservation(static_cast<std::uint8_t>(channel), *state);
                if (status != bridge_core::Status::kOk) return ErrorJson(StatusName(status));
                AddEvent("Synthetic observation CH" + std::to_string(channel + 1) + " " + StateName(*state));
                return SnapshotJson();
            }

            if (device_.submitted_intents().size() >= kMaxSubmittedIntents) {
                return ErrorJson("intent_limit_reached");
            }
            const auto status = device_.Submit({static_cast<std::uint8_t>(channel), *state,
                                                "synthetic-" + std::to_string(next_sequence_++)});
            if (status != bridge_core::Status::kOk && status != bridge_core::Status::kUnsupported) {
                return ErrorJson(StatusName(status));
            }
            const auto* snapshot = device_.FindChannel(static_cast<std::uint8_t>(channel));
            AddEvent("Synthetic command CH" + std::to_string(channel + 1) + " " + StateName(*state) +
                     (snapshot->disposition == bridge_core::TransportDisposition::kAccepted ? " accepted" :
                                                                                              " rejected"));
            return SnapshotJson();
        }
        return ErrorJson("invalid_command");
    }

private:
    void AddEvent(std::string event) {
        if (events_.size() == kMaxEvents) events_.erase(events_.begin());
        events_.push_back(std::move(event));
    }

    std::string SnapshotJson() const {
        std::ostringstream output;
        output << "{\"availability\":\"" << AvailabilityName(device_.availability()) << "\",\"channels\":[";
        for (std::uint8_t index = 0; index < 4; ++index) {
            if (index != 0) output << ',';
            const auto* channel = device_.FindChannel(index);
            output << "{\"index\":" << static_cast<unsigned int>(index)
                   << ",\"observed_state\":\"" << StateName(channel->observed_state)
                   << "\",\"fresh\":" << (channel->fresh ? "true" : "false")
                   << ",\"pending_state\":";
            if (channel->pending) {
                output << '"' << StateName(channel->pending->requested_state) << '"';
            } else {
                output << "null";
            }
            output << ",\"transport_disposition\":\"" << DispositionName(channel->disposition)
                   << "\",\"convergence\":\"" << ConvergenceName(channel->convergence) << "\"}";
        }
        output << "],\"submitted_intents\":[";
        const auto& intents = device_.submitted_intents();
        for (std::size_t index = 0; index < intents.size(); ++index) {
            if (index != 0) output << ',';
            const auto& intent = intents[index];
            output << "{\"channel\":" << static_cast<unsigned int>(intent.channel)
                   << ",\"requested_state\":\"" << StateName(intent.requested_state)
                   << "\",\"correlation\":\"" << EscapeJson(intent.correlation) << "\"}";
        }
        output << "],\"events\":[";
        for (std::size_t index = 0; index < events_.size(); ++index) {
            if (index != 0) output << ',';
            output << '"' << EscapeJson(events_[index]) << '"';
        }
        output << "]}";
        return output.str();
    }

    bridge_simulator::SyntheticDevice device_{bridge_core::DeviceIdentity{"synthetic", "simulator"}};
    std::vector<std::string> events_;
    std::uint32_t next_sequence_ = 1;
};

}  // namespace

int main() {
    DiagnosticAdapter adapter;
    std::string line;
    bool should_quit = false;
    while (std::getline(std::cin, line)) {
        const std::string response = adapter.Handle(line, &should_quit);
        std::cout << response << '\n' << std::flush;
        if (should_quit) break;
    }
    return 0;
}
