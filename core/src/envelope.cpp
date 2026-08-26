#include "bridge_core/envelope.hpp"

#include <algorithm>

#include <cctype>

namespace bridge_core {
namespace {

constexpr std::array<std::uint8_t, 4> kMagic{{'E', 'W', 'B', '1'}};

bool IsFieldValid(const std::string& value) {
    return !value.empty() && value.size() <= kMaxEnvelopeFieldBytes;
}

bool IsCommandValid(const std::string& command) {
    if (!IsFieldValid(command) || command.size() > 64) return false;
    for (const char ch : command) {
        if (!std::isalnum(static_cast<unsigned char>(ch)) && ch != '_' && ch != '-') return false;
    }
    return true;
}

void PutU16(std::vector<std::uint8_t>* output, std::uint16_t value) {
    output->push_back(static_cast<std::uint8_t>(value >> 8));
    output->push_back(static_cast<std::uint8_t>(value & 0xff));
}

Status PutString(const std::string& value, std::vector<std::uint8_t>* output) {
    if (!IsFieldValid(value) || value.size() > 0xffff) return Status::kTooLarge;
    PutU16(output, static_cast<std::uint16_t>(value.size()));
    output->insert(output->end(), value.begin(), value.end());
    return Status::kOk;
}

Status GetString(const std::vector<std::uint8_t>& input, std::size_t* offset, std::string* output) {
    if (*offset + 2 > input.size()) return Status::kMalformed;
    const auto size = static_cast<std::size_t>((input[*offset] << 8) | input[*offset + 1]);
    *offset += 2;
    if (size == 0) return Status::kMissingField;
    if (size > kMaxEnvelopeFieldBytes) return Status::kTooLarge;
    if (*offset + size > input.size()) return Status::kMalformed;
    output->assign(reinterpret_cast<const char*>(input.data() + *offset), size);
    *offset += size;
    return Status::kOk;
}

Status ValidateEnvelope(const ProtocolEnvelope& envelope) {
    if (!IsFieldValid(envelope.sequence) || !IsValidIdentity(envelope.identity) ||
        !IsCommandValid(envelope.command) || !IsFieldValid(envelope.self_apikey)) {
        return Status::kMissingField;
    }
    std::string expected_path;
    if (BuildZeroconfPath(envelope.command, &expected_path) != Status::kOk || envelope.path != expected_path) {
        return Status::kMalformed;
    }
    if (envelope.form == EnvelopeForm::kPlain && !std::holds_alternative<PlainPayload>(envelope.payload)) return Status::kMalformed;
    if (envelope.form == EnvelopeForm::kEncrypted && !std::holds_alternative<EncryptedPayload>(envelope.payload)) return Status::kMalformed;
    return Status::kOk;
}

}  // namespace

bool IsValidIdentityPart(const std::string& value) {
    if (value.empty() || value.size() > 128) return false;
    for (const char ch : value) {
        if (!std::isalnum(static_cast<unsigned char>(ch)) && ch != '-' && ch != '_' && ch != '.') return false;
    }
    return true;
}

bool IsValidIdentity(const DeviceIdentity& value) {
    return IsValidIdentityPart(value.source_namespace) && IsValidIdentityPart(value.device_id);
}

Status BuildZeroconfPath(const std::string& command, std::string* output) {
    if (!output || !IsCommandValid(command)) return Status::kMalformed;
    *output = "/zeroconf/" + command;
    return Status::kOk;
}

Status SerializeEnvelope(const ProtocolEnvelope& envelope, std::vector<std::uint8_t>* output) {
    if (!output) return Status::kInvalidState;
    const Status validation = ValidateEnvelope(envelope);
    if (validation != Status::kOk) return validation;
    output->clear();
    output->insert(output->end(), kMagic.begin(), kMagic.end());
    output->push_back(static_cast<std::uint8_t>(envelope.form));
    for (const std::string* field : {&envelope.sequence, &envelope.identity.source_namespace, &envelope.identity.device_id,
                                     &envelope.command, &envelope.path, &envelope.self_apikey}) {
        const Status result = PutString(*field, output);
        if (result != Status::kOk) return result;
    }
    if (const auto* plain = std::get_if<PlainPayload>(&envelope.payload)) return PutString(plain->data_json, output);
    const auto* encrypted = std::get_if<EncryptedPayload>(&envelope.payload);
    if (!encrypted) return Status::kMalformed;
    const Status ciphertext = PutString(encrypted->ciphertext_base64, output);
    return ciphertext == Status::kOk ? PutString(encrypted->iv_base64, output) : ciphertext;
}

Status ParseEnvelope(const std::vector<std::uint8_t>& input, ProtocolEnvelope* output) {
    if (!output || input.size() < 5 || !std::equal(kMagic.begin(), kMagic.end(), input.begin())) return Status::kMalformed;
    const auto form = static_cast<EnvelopeForm>(input[4]);
    if (form != EnvelopeForm::kPlain && form != EnvelopeForm::kEncrypted) return Status::kUnsupported;
    std::size_t offset = 5;
    ProtocolEnvelope parsed{};
    parsed.form = form;
    for (std::string* field : {&parsed.sequence, &parsed.identity.source_namespace, &parsed.identity.device_id,
                               &parsed.command, &parsed.path, &parsed.self_apikey}) {
        const Status result = GetString(input, &offset, field);
        if (result != Status::kOk) return result;
    }
    if (form == EnvelopeForm::kPlain) {
        PlainPayload plain;
        const Status result = GetString(input, &offset, &plain.data_json);
        if (result != Status::kOk) return result;
        parsed.payload = std::move(plain);
    } else {
        EncryptedPayload encrypted;
        const Status ciphertext = GetString(input, &offset, &encrypted.ciphertext_base64);
        const Status iv = ciphertext == Status::kOk ? GetString(input, &offset, &encrypted.iv_base64) : ciphertext;
        if (iv != Status::kOk) return iv;
        parsed.payload = std::move(encrypted);
    }
    if (offset != input.size()) return Status::kMalformed;
    const Status validation = ValidateEnvelope(parsed);
    if (validation != Status::kOk) return validation;
    *output = std::move(parsed);
    return Status::kOk;
}

Status EncryptPayload(CryptoProvider& provider, const std::string& device_key,
                      const std::array<std::uint8_t, 16>& test_or_runtime_iv,
                      const std::vector<std::uint8_t>& plaintext, EncryptedPayload* output) {
    if (!output || device_key.empty() || plaintext.empty()) return Status::kMissingField;
    std::array<std::uint8_t, 16> key{};
    Status result = provider.DeriveMd5Key(device_key, &key);
    if (result != Status::kOk) return result;
    std::vector<std::uint8_t> ciphertext;
    result = provider.EncryptAesCbcPkcs7(key, test_or_runtime_iv, plaintext, &ciphertext);
    if (result != Status::kOk) return result;
    result = provider.Base64Encode(ciphertext, &output->ciphertext_base64);
    if (result != Status::kOk) return result;
    return provider.Base64Encode(std::vector<std::uint8_t>(test_or_runtime_iv.begin(), test_or_runtime_iv.end()), &output->iv_base64);
}

}  // namespace bridge_core
