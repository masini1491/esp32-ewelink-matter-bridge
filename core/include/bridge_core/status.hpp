#pragma once

namespace bridge_core {

enum class Status {
    kOk,
    kMissingField,
    kMalformed,
    kTooLarge,
    kUnsupported,
    kInvalidState,
    kCryptoFailure,
};

}  // namespace bridge_core
