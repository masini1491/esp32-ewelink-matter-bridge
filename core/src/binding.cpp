#include "bridge_core/binding.hpp"

namespace bridge_core {

std::string StableBindingKey(const DeviceIdentity& identity, const std::uint8_t channel) {
    if (!IsValidIdentity(identity) || channel >= kChannelCount) return {};
    return "ewelink/" + identity.source_namespace + "/" + identity.device_id + "/on_off/" + std::to_string(channel);
}

std::array<MatterBindingDescriptor, kChannelCount> BuildOnOffBindings(const DeviceIdentity& identity) {
    std::array<MatterBindingDescriptor, kChannelCount> bindings{};
    for (std::uint8_t channel = 0; channel < kChannelCount; ++channel) {
        bindings[channel] = MatterBindingDescriptor{channel, StableBindingKey(identity, channel)};
    }
    return bindings;
}

}  // namespace bridge_core
