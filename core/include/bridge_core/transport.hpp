#pragma once

#include "bridge_core/device_model.hpp"
#include "bridge_core/status.hpp"

namespace bridge_core {

class CommandTransport {
public:
    virtual ~CommandTransport() = default;
    virtual Status Send(const CommandIntent& intent) = 0;
};

class CommandOrchestrator {
public:
    explicit CommandOrchestrator(CommandTransport& transport) : transport_(transport) {}

    Status Submit(UnifiedDeviceModel& model, const CommandIntent& intent);

private:
    CommandTransport& transport_;
};

}  // namespace bridge_core
