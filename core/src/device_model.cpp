#include "bridge_core/device_model.hpp"

#include <utility>

#include <stdexcept>

#include "bridge_core/transport.hpp"

namespace bridge_core {

UnifiedDeviceModel::UnifiedDeviceModel(DeviceIdentity identity) : identity_(std::move(identity)) {}

bool UnifiedDeviceModel::IsChannel(const std::uint8_t index) const { return index < kChannelCount; }

const ChannelSnapshot& UnifiedDeviceModel::channel(const std::uint8_t index) const {
    if (!IsChannel(index)) throw std::out_of_range("channel index");
    return channels_[index];
}

Status UnifiedDeviceModel::IssueCommand(const CommandIntent& intent) {
    if (!IsChannel(intent.channel) || (intent.requested_state != BinaryState::kOn && intent.requested_state != BinaryState::kOff)) {
        return Status::kInvalidState;
    }
    if (availability_ != Availability::kAvailable) return Status::kInvalidState;
    auto& snapshot = channels_[intent.channel];
    snapshot.pending = intent;
    snapshot.disposition = TransportDisposition::kPending;
    snapshot.convergence = Convergence::kNone;
    return Status::kOk;
}

Status UnifiedDeviceModel::MarkTransportAccepted(const std::uint8_t index) {
    if (!IsChannel(index) || !channels_[index].pending) return Status::kInvalidState;
    channels_[index].disposition = TransportDisposition::kAccepted;
    return Status::kOk;
}

Status UnifiedDeviceModel::MarkTransportRejected(const std::uint8_t index) {
    if (!IsChannel(index) || !channels_[index].pending) return Status::kInvalidState;
    auto& snapshot = channels_[index];
    snapshot.disposition = TransportDisposition::kRejected;
    snapshot.convergence = Convergence::kRejected;
    snapshot.pending.reset();
    return Status::kOk;
}

Status UnifiedDeviceModel::ApplyObservation(const std::uint8_t index, const BinaryState state) {
    if (!IsChannel(index) || state == BinaryState::kUnknown) return Status::kInvalidState;
    auto& snapshot = channels_[index];
    snapshot.observed_state = state;
    snapshot.fresh = true;
    availability_ = Availability::kAvailable;
    if (snapshot.pending) {
        snapshot.convergence = snapshot.pending->requested_state == state ? Convergence::kMatched : Convergence::kConflicted;
        snapshot.pending.reset();
    }
    return Status::kOk;
}

void UnifiedDeviceModel::MarkDisconnected() {
    availability_ = Availability::kUnavailable;
    for (auto& snapshot : channels_) snapshot.fresh = false;
}

void UnifiedDeviceModel::MarkReconnected() {
    availability_ = Availability::kAvailable;
    for (auto& snapshot : channels_) snapshot.fresh = false;
}

void UnifiedDeviceModel::MarkStale() { MarkDisconnected(); }

Status CommandOrchestrator::Submit(UnifiedDeviceModel& model, const CommandIntent& intent) {
    Status result = model.IssueCommand(intent);
    if (result != Status::kOk) return result;
    result = transport_.Send(intent);
    if (result != Status::kOk) {
        model.MarkTransportRejected(intent.channel);
        return result;
    }
    return model.MarkTransportAccepted(intent.channel);
}

}  // namespace bridge_core
