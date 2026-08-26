#pragma once

#include <array>
#include <cstdint>
#include <string>
#include <variant>
#include <vector>

#include "bridge_core/identity.hpp"
#include "bridge_core/status.hpp"

namespace bridge_core {

constexpr std::size_t kMaxEnvelopeFieldBytes = 4096;

enum class EnvelopeForm : std::uint8_t {
    kPlain = 1,
    kEncrypted = 2,
};

struct PlainPayload {
    // A bounded opaque JSON value/document. Its device schema is intentionally not parsed in S2B.
    std::string data_json;
};

struct EncryptedPayload {
    std::string ciphertext_base64;
    std::string iv_base64;
};

struct ProtocolEnvelope {
    std::string sequence;
    DeviceIdentity identity;
    std::string command;
    std::string path;
    std::string self_apikey;
    EnvelopeForm form;
    std::variant<PlainPayload, EncryptedPayload> payload;
};

Status BuildZeroconfPath(const std::string& command, std::string* output);
Status SerializeEnvelope(const ProtocolEnvelope& envelope, std::vector<std::uint8_t>* output);
Status ParseEnvelope(const std::vector<std::uint8_t>& input, ProtocolEnvelope* output);

class CryptoProvider {
public:
    virtual ~CryptoProvider() = default;
    virtual Status DeriveMd5Key(const std::string& device_key, std::array<std::uint8_t, 16>* output) = 0;
    virtual Status EncryptAesCbcPkcs7(const std::array<std::uint8_t, 16>& key,
                                      const std::array<std::uint8_t, 16>& iv,
                                      const std::vector<std::uint8_t>& plaintext,
                                      std::vector<std::uint8_t>* output) = 0;
    virtual Status Base64Encode(const std::vector<std::uint8_t>& input, std::string* output) = 0;
};

Status EncryptPayload(CryptoProvider& provider, const std::string& device_key,
                      const std::array<std::uint8_t, 16>& test_or_runtime_iv,
                      const std::vector<std::uint8_t>& plaintext, EncryptedPayload* output);

}  // namespace bridge_core
