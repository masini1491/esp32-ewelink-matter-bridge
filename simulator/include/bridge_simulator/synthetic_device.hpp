#pragma once

#include <cstdint>
#include <vector>

#include "bridge_core/transport.hpp"

namespace bridge_simulator {

enum class NextTransportResult { kAccepted, kRejected };

// Deterministic host-only test device. Its identity and observations are synthetic.
class SyntheticDevice final : private bridge_core::CommandTransport {
public:
    explicit SyntheticDevice(bridge_core::DeviceIdentity identity);
    SyntheticDevice(const SyntheticDevice&) = delete;
    SyntheticDevice& operator=(const SyntheticDevice&) = delete;
    SyntheticDevice(SyntheticDevice&&) = delete;
    SyntheticDevice& operator=(SyntheticDevice&&) = delete;

    void Connect();
    void Disconnect();
    void MarkStale();
    void Reconnect();

    void SetNextTransportResult(NextTransportResult result);
    bridge_core::Status Submit(const bridge_core::CommandIntent& intent);
    bridge_core::Status InjectObservation(std::uint8_t channel, bridge_core::BinaryState state);

    bridge_core::Availability availability() const;
    const bridge_core::ChannelSnapshot* FindChannel(std::uint8_t channel) const;
    const std::vector<bridge_core::CommandIntent>& submitted_intents() const;

private:
    bridge_core::Status Send(const bridge_core::CommandIntent& intent) override;

    bridge_core::UnifiedDeviceModel model_;
    NextTransportResult next_transport_result_ = NextTransportResult::kAccepted;
    std::vector<bridge_core::CommandIntent> submitted_intents_;
    bridge_core::CommandOrchestrator orchestrator_;
};

}  // namespace bridge_simulator
