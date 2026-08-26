#include "windows_cng_crypto_provider.hpp"

#include <windows.h>
#include <bcrypt.h>
#include <wincrypt.h>

namespace {

bool IsSuccess(const NTSTATUS status) { return status >= 0; }

}  // namespace

bridge_core::Status WindowsCngCryptoProvider::DeriveMd5Key(const std::string& device_key,
                                                           std::array<std::uint8_t, 16>* output) {
    if (!output) return bridge_core::Status::kInvalidState;
    BCRYPT_ALG_HANDLE algorithm = nullptr;
    BCRYPT_HASH_HANDLE hash = nullptr;
    DWORD object_size = 0;
    DWORD bytes = 0;
    std::vector<std::uint8_t> object;
    if (!IsSuccess(BCryptOpenAlgorithmProvider(&algorithm, BCRYPT_MD5_ALGORITHM, nullptr, 0)) ||
        !IsSuccess(BCryptGetProperty(algorithm, BCRYPT_OBJECT_LENGTH, reinterpret_cast<PUCHAR>(&object_size), sizeof(object_size), &bytes, 0))) {
        if (algorithm) BCryptCloseAlgorithmProvider(algorithm, 0);
        return bridge_core::Status::kCryptoFailure;
    }
    object.resize(object_size);
    const NTSTATUS created = BCryptCreateHash(algorithm, &hash, object.data(), object_size, nullptr, 0, 0);
    const NTSTATUS hashed = IsSuccess(created) ? BCryptHashData(hash, reinterpret_cast<PUCHAR>(const_cast<char*>(device_key.data())), static_cast<ULONG>(device_key.size()), 0) : created;
    const NTSTATUS finished = IsSuccess(hashed) ? BCryptFinishHash(hash, output->data(), static_cast<ULONG>(output->size()), 0) : hashed;
    if (hash) BCryptDestroyHash(hash);
    BCryptCloseAlgorithmProvider(algorithm, 0);
    return IsSuccess(finished) ? bridge_core::Status::kOk : bridge_core::Status::kCryptoFailure;
}

bridge_core::Status WindowsCngCryptoProvider::EncryptAesCbcPkcs7(const std::array<std::uint8_t, 16>& key,
                                                                 const std::array<std::uint8_t, 16>& iv,
                                                                 const std::vector<std::uint8_t>& plaintext,
                                                                 std::vector<std::uint8_t>* output) {
    if (!output || plaintext.empty()) return bridge_core::Status::kInvalidState;
    BCRYPT_ALG_HANDLE algorithm = nullptr;
    BCRYPT_KEY_HANDLE symmetric_key = nullptr;
    DWORD object_size = 0;
    DWORD bytes = 0;
    std::vector<std::uint8_t> key_object;
    if (!IsSuccess(BCryptOpenAlgorithmProvider(&algorithm, BCRYPT_AES_ALGORITHM, nullptr, 0)) ||
        !IsSuccess(BCryptSetProperty(algorithm, BCRYPT_CHAINING_MODE, reinterpret_cast<PUCHAR>(const_cast<wchar_t*>(BCRYPT_CHAIN_MODE_CBC)),
                                     sizeof(BCRYPT_CHAIN_MODE_CBC), 0)) ||
        !IsSuccess(BCryptGetProperty(algorithm, BCRYPT_OBJECT_LENGTH, reinterpret_cast<PUCHAR>(&object_size), sizeof(object_size), &bytes, 0))) {
        if (algorithm) BCryptCloseAlgorithmProvider(algorithm, 0);
        return bridge_core::Status::kCryptoFailure;
    }
    key_object.resize(object_size);
    if (!IsSuccess(BCryptGenerateSymmetricKey(algorithm, &symmetric_key, key_object.data(), object_size,
                                               const_cast<PUCHAR>(key.data()), static_cast<ULONG>(key.size()), 0))) {
        BCryptCloseAlgorithmProvider(algorithm, 0);
        return bridge_core::Status::kCryptoFailure;
    }
    std::vector<std::uint8_t> padded = plaintext;
    const auto padding = static_cast<std::uint8_t>(16 - (padded.size() % 16));
    padded.insert(padded.end(), padding, padding);
    ULONG encrypted_size = 0;
    auto mutable_iv = iv;
    NTSTATUS status = BCryptEncrypt(symmetric_key, padded.data(), static_cast<ULONG>(padded.size()), nullptr,
                                    mutable_iv.data(), static_cast<ULONG>(mutable_iv.size()), nullptr, 0, &encrypted_size, 0);
    if (IsSuccess(status)) {
        output->resize(encrypted_size);
        mutable_iv = iv;
        status = BCryptEncrypt(symmetric_key, padded.data(), static_cast<ULONG>(padded.size()), nullptr,
                               mutable_iv.data(), static_cast<ULONG>(mutable_iv.size()), output->data(), encrypted_size, &encrypted_size, 0);
        output->resize(encrypted_size);
    }
    BCryptDestroyKey(symmetric_key);
    BCryptCloseAlgorithmProvider(algorithm, 0);
    return IsSuccess(status) ? bridge_core::Status::kOk : bridge_core::Status::kCryptoFailure;
}

bridge_core::Status WindowsCngCryptoProvider::Base64Encode(const std::vector<std::uint8_t>& input, std::string* output) {
    if (!output || input.empty()) return bridge_core::Status::kInvalidState;
    DWORD chars = 0;
    if (!CryptBinaryToStringA(input.data(), static_cast<DWORD>(input.size()), CRYPT_STRING_BASE64 | CRYPT_STRING_NOCRLF, nullptr, &chars)) {
        return bridge_core::Status::kCryptoFailure;
    }
    std::string encoded(chars, '\0');
    if (!CryptBinaryToStringA(input.data(), static_cast<DWORD>(input.size()), CRYPT_STRING_BASE64 | CRYPT_STRING_NOCRLF, encoded.data(), &chars)) {
        return bridge_core::Status::kCryptoFailure;
    }
    encoded.resize(chars);
    *output = std::move(encoded);
    return bridge_core::Status::kOk;
}
