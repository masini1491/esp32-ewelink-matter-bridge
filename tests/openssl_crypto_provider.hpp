#pragma once

#include "bridge_core/envelope.hpp"

class OpenSslCryptoProvider final : public bridge_core::CryptoProvider {
public:
    bridge_core::Status DeriveMd5Key(const std::string& device_key,
                                     std::array<std::uint8_t, 16>* output) override;
    bridge_core::Status EncryptAesCbcPkcs7(const std::array<std::uint8_t, 16>& key,
                                           const std::array<std::uint8_t, 16>& iv,
                                           const std::vector<std::uint8_t>& plaintext,
                                           std::vector<std::uint8_t>* output) override;
    bridge_core::Status Base64Encode(const std::vector<std::uint8_t>& input, std::string* output) override;
};
