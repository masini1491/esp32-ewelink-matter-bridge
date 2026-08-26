#pragma once

#include <array>
#include <cstdint>
#include <optional>
#include <string>

#include "bridge_core/identity.hpp"
#include "bridge_core/status.hpp"

namespace bridge_core {

constexpr std::size_t kChannelCount = 4;

enum class BinaryState { kOn, kOff, kUnknown };
enum class Availability { kAvailable, kUnavailable };
enum class TransportDisposition { kPending, kAccepted, kRejected };
enum class Convergence { kNone, kMatched, kConflicted, kRejected };

struct CommandIntent {
    std::uint8_t channel;
    BinaryState requested_state;
    std::string correlation;
};

struct ChannelSnapshot {
    BinaryState observed_state = BinaryState::kUnknown;
    bool fresh = false;
    std::optional<CommandIntent> pending;
    TransportDisposition disposition = TransportDisposition::kPending;
    Convergence convergence = Convergence::kNone;
};

class UnifiedDeviceModel {
public:
    explicit UnifiedDeviceModel(DeviceIdentity identity);

    const DeviceIdentity& identity() const { return identity_; }
    Availability availability() const { return availability_; }
    const ChannelSnapshot& channel(std::uint8_t index) const;

    Status IssueCommand(const CommandIntent& intent);
    Status MarkTransportAccepted(std::uint8_t channel);
    Status MarkTransportRejected(std::uint8_t channel);
    Status ApplyObservation(std::uint8_t channel, BinaryState state);
    void MarkDisconnected();
    void MarkReconnected();
    void MarkStale();

private:
    bool IsChannel(std::uint8_t index) const;
    DeviceIdentity identity_;
    Availability availability_ = Availability::kUnavailable;
    std::array<ChannelSnapshot, kChannelCount> channels_{};
};

}  // namespace bridge_core
