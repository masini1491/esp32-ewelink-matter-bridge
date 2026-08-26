#include "openssl_crypto_provider.hpp"

#include <openssl/evp.h>

#include <limits>

namespace {

bridge_core::Status CryptoFailure() { return bridge_core::Status::kUnsupported; }

}  // namespace

bridge_core::Status OpenSslCryptoProvider::DeriveMd5Key(
    const std::string& device_key, std::array<std::uint8_t, 16>* output) {
    if (output == nullptr) {
        return bridge_core::Status::kMalformed;
    }
    unsigned int size = 0;
    if (EVP_Digest(device_key.data(), device_key.size(), output->data(), &size, EVP_md5(), nullptr) != 1 ||
        size != output->size()) {
        return CryptoFailure();
    }
    return bridge_core::Status::kOk;
}

bridge_core::Status OpenSslCryptoProvider::EncryptAesCbcPkcs7(
    const std::array<std::uint8_t, 16>& key, const std::array<std::uint8_t, 16>& iv,
    const std::vector<std::uint8_t>& plaintext, std::vector<std::uint8_t>* output) {
    if (output == nullptr || plaintext.size() > static_cast<std::size_t>(std::numeric_limits<int>::max())) {
        return bridge_core::Status::kMalformed;
    }
    EVP_CIPHER_CTX* context = EVP_CIPHER_CTX_new();
    if (context == nullptr) {
        return CryptoFailure();
    }
    output->assign(plaintext.size() + EVP_MAX_BLOCK_LENGTH, 0);
    int first_size = 0;
    int final_size = 0;
    const int initialized = EVP_EncryptInit_ex(context, EVP_aes_128_cbc(), nullptr, key.data(), iv.data());
    const int updated = initialized == 1
                            ? EVP_EncryptUpdate(context, output->data(), &first_size, plaintext.data(),
                                                static_cast<int>(plaintext.size()))
                            : 0;
    const int finalized = updated == 1 ? EVP_EncryptFinal_ex(context, output->data() + first_size, &final_size) : 0;
    EVP_CIPHER_CTX_free(context);
    if (finalized != 1) {
        output->clear();
        return CryptoFailure();
    }
    output->resize(static_cast<std::size_t>(first_size + final_size));
    return bridge_core::Status::kOk;
}

bridge_core::Status OpenSslCryptoProvider::Base64Encode(const std::vector<std::uint8_t>& input, std::string* output) {
    if (output == nullptr || input.size() > static_cast<std::size_t>(std::numeric_limits<int>::max())) {
        return bridge_core::Status::kMalformed;
    }
    const auto encoded_size = 4 * ((input.size() + 2) / 3);
    output->assign(encoded_size, '\0');
    const int written = EVP_EncodeBlock(reinterpret_cast<unsigned char*>(output->data()), input.data(),
                                        static_cast<int>(input.size()));
    if (written < 0) {
        output->clear();
        return CryptoFailure();
    }
    output->resize(static_cast<std::size_t>(written));
    return bridge_core::Status::kOk;
}
