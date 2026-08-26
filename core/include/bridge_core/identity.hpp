#pragma once

#include <string>

namespace bridge_core {

struct DeviceIdentity {
    std::string source_namespace;
    std::string device_id;

    bool operator==(const DeviceIdentity& other) const {
        return source_namespace == other.source_namespace && device_id == other.device_id;
    }
};

bool IsValidIdentityPart(const std::string& value);
bool IsValidIdentity(const DeviceIdentity& value);

}  // namespace bridge_core
