#include "bridge_simulator/synthetic_device.hpp"

#include <utility>

namespace bridge_simulator {

SyntheticDevice::SyntheticDevice(bridge_core::DeviceIdentity identity)
    : model_(std::move(identity)), orchestrator_(*this) {}

void SyntheticDevice::Connect() { model_.MarkReconnected(); }

void SyntheticDevice::Disconnect() { model_.MarkDisconnected(); }

void SyntheticDevice::MarkStale() { model_.MarkStale(); }

void SyntheticDevice::Reconnect() { model_.MarkReconnected(); }

void SyntheticDevice::SetNextTransportResult(const NextTransportResult result) {
    next_transport_result_ = result;
}

bridge_core::Status SyntheticDevice::Submit(const bridge_core::CommandIntent& intent) {
    return orchestrator_.Submit(model_, intent);
}

bridge_core::Status SyntheticDevice::InjectObservation(const std::uint8_t channel,
                                                       const bridge_core::BinaryState state) {
    return model_.ApplyObservation(channel, state);
}

bridge_core::Availability SyntheticDevice::availability() const { return model_.availability(); }

const bridge_core::ChannelSnapshot* SyntheticDevice::FindChannel(const std::uint8_t channel) const {
    return model_.FindChannel(channel);
}

const std::vector<bridge_core::CommandIntent>& SyntheticDevice::submitted_intents() const {
    return submitted_intents_;
}

bridge_core::Status SyntheticDevice::Send(const bridge_core::CommandIntent& intent) {
    submitted_intents_.push_back(intent);
    const bool accepted = next_transport_result_ == NextTransportResult::kAccepted;
    next_transport_result_ = NextTransportResult::kAccepted;
    return accepted ? bridge_core::Status::kOk : bridge_core::Status::kUnsupported;
}

}  // namespace bridge_simulator
