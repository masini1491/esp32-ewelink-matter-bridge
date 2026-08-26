#pragma once

#include <array>
#include <cstdint>
#include <string>

#include "bridge_core/device_model.hpp"

namespace bridge_core {

struct MatterBindingDescriptor {
    std::uint8_t channel;
    std::string stable_binding_key;
    const char* capability = "on_off";
};

std::string StableBindingKey(const DeviceIdentity& identity, std::uint8_t channel);
std::array<MatterBindingDescriptor, kChannelCount> BuildOnOffBindings(const DeviceIdentity& identity);

}  // namespace bridge_core
