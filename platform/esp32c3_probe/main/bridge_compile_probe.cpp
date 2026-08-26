#include <array>
#include <cstdint>

#include <esp_matter_bridge.h>

#include "bridge_core/binding.hpp"

namespace {

constexpr std::uint32_t kSyntheticOnOffDeviceType = 0x0100;

}  // namespace

extern "C" void bridge_compile_probe_anchor() {
    const bridge_core::DeviceIdentity identity{"synthetic", "compile-probe-four-channel"};
    const auto bindings = bridge_core::BuildOnOffBindings(identity);
    std::array<std::uint16_t, bridge_core::kChannelCount> endpoint_ids{};

    // Compile/link-only reference: this function is not called by app_main and no
    // node, endpoint, Wi-Fi, BLE, fabric or persistence runtime is initialized.
    (void)bindings;
    (void)kSyntheticOnOffDeviceType;
    (void)esp_matter_bridge::get_bridged_endpoint_ids(endpoint_ids.data());
}

extern "C" void app_main(void) {
    // Intentionally empty. S2C never boots or runs this image.
}
