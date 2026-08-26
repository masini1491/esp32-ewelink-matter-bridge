#include <array>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>

#include "bridge_core/binding.hpp"
#include "bridge_core/device_model.hpp"
#include "bridge_core/envelope.hpp"
#include "bridge_core/transport.hpp"
#if defined(_WIN32)
#include "windows_cng_crypto_provider.hpp"
using HostCryptoProvider = WindowsCngCryptoProvider;
#else
#include "openssl_crypto_provider.hpp"
using HostCryptoProvider = OpenSslCryptoProvider;
#endif

namespace {

int failures = 0;

#define EXPECT_TRUE(expression)                                                                    \
    do {                                                                                           \
        if (!(expression)) {                                                                       \
            std::cerr << "FAILED " << __FUNCTION__ << ": " << #expression << '\n';             \
            ++failures;                                                                            \
        }                                                                                          \
    } while (false)

bridge_core::DeviceIdentity Identity() { return {"ewelink", "device-1000000001"}; }

bridge_core::ProtocolEnvelope PlainEnvelope() {
    std::string path;
    EXPECT_TRUE(bridge_core::BuildZeroconfPath("switch", &path) == bridge_core::Status::kOk);
    return {"seq-1", Identity(), "switch", path, "synthetic-self-apikey", bridge_core::EnvelopeForm::kPlain,
            bridge_core::PlainPayload{"{\"opaque\":true}"}};
}

std::string Hex(const std::array<std::uint8_t, 16>& bytes) {
    constexpr char hex[] = "0123456789abcdef";
    std::string result;
    for (auto byte : bytes) {
        result.push_back(hex[(byte >> 4) & 0xf]);
        result.push_back(hex[byte & 0xf]);
    }
    return result;
}

class FakeTransport final : public bridge_core::CommandTransport {
public:
    bridge_core::Status next = bridge_core::Status::kOk;
    std::vector<bridge_core::CommandIntent> requests;

    bridge_core::Status Send(const bridge_core::CommandIntent& intent) override {
        requests.push_back(intent);
        return next;
    }
};

void TestEnvelopeRoundTrip() {
    const auto source = PlainEnvelope();
    std::vector<std::uint8_t> wire;
    EXPECT_TRUE(bridge_core::SerializeEnvelope(source, &wire) == bridge_core::Status::kOk);
    bridge_core::ProtocolEnvelope parsed{};
    EXPECT_TRUE(bridge_core::ParseEnvelope(wire, &parsed) == bridge_core::Status::kOk);
    EXPECT_TRUE(parsed.identity == source.identity);
    EXPECT_TRUE(parsed.sequence == "seq-1");
    EXPECT_TRUE(parsed.path == "/zeroconf/switch");
    EXPECT_TRUE(std::get<bridge_core::PlainPayload>(parsed.payload).data_json == "{\"opaque\":true}");
}

void TestEnvelopeBoundaries() {
    auto source = PlainEnvelope();
    source.sequence.clear();
    std::vector<std::uint8_t> wire;
    EXPECT_TRUE(bridge_core::SerializeEnvelope(source, &wire) == bridge_core::Status::kMissingField);
    source = PlainEnvelope();
    source.command = "switch/bad";
    EXPECT_TRUE(bridge_core::SerializeEnvelope(source, &wire) == bridge_core::Status::kMissingField);
    source = PlainEnvelope();
    source.path = "/zeroconf/getState";
    EXPECT_TRUE(bridge_core::SerializeEnvelope(source, &wire) == bridge_core::Status::kMalformed);
    source = PlainEnvelope();
    std::get<bridge_core::PlainPayload>(source.payload).data_json.assign(bridge_core::kMaxEnvelopeFieldBytes + 1, 'x');
    EXPECT_TRUE(bridge_core::SerializeEnvelope(source, &wire) == bridge_core::Status::kTooLarge);
    EXPECT_TRUE(bridge_core::ParseEnvelope({0, 1, 2}, &source) == bridge_core::Status::kMalformed);
    wire = {'E', 'W', 'B', '1', 99};
    EXPECT_TRUE(bridge_core::ParseEnvelope(wire, &source) == bridge_core::Status::kUnsupported);
    wire = {'E', 'W', 'B', '1', 1, 0, 4, 'x'};
    EXPECT_TRUE(bridge_core::ParseEnvelope(wire, &source) == bridge_core::Status::kMalformed);
    EXPECT_TRUE(bridge_core::BuildZeroconfPath("", &source.path) == bridge_core::Status::kMalformed);
}

void TestEncryptedEnvelopeRoundTrip() {
    auto source = PlainEnvelope();
    source.form = bridge_core::EnvelopeForm::kEncrypted;
    source.payload = bridge_core::EncryptedPayload{"Y2lwaGVydGV4dA==", "AAECAwQFBgcICQoLDA0ODw=="};
    std::vector<std::uint8_t> wire;
    EXPECT_TRUE(bridge_core::SerializeEnvelope(source, &wire) == bridge_core::Status::kOk);
    bridge_core::ProtocolEnvelope parsed{};
    EXPECT_TRUE(bridge_core::ParseEnvelope(wire, &parsed) == bridge_core::Status::kOk);
    const auto encrypted = std::get<bridge_core::EncryptedPayload>(parsed.payload);
    EXPECT_TRUE(encrypted.ciphertext_base64 == "Y2lwaGVydGV4dA==");
    EXPECT_TRUE(encrypted.iv_base64 == "AAECAwQFBgcICQoLDA0ODw==");
}

void TestCryptoVector() {
    HostCryptoProvider provider;
    std::array<std::uint8_t, 16> key{};
    EXPECT_TRUE(provider.DeriveMd5Key("synthetic-device-key", &key) == bridge_core::Status::kOk);
    const std::array<std::uint8_t, 16> iv{{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}};
    const std::vector<std::uint8_t> plaintext{'{', '"', 'v', '"', ':', '1', '}'};
    bridge_core::EncryptedPayload encrypted;
    EXPECT_TRUE(bridge_core::EncryptPayload(provider, "synthetic-device-key", iv, plaintext, &encrypted) == bridge_core::Status::kOk);
    EXPECT_TRUE(Hex(key) == "bb567d45afbd4b01cf5c124ca9cda2b4");
    EXPECT_TRUE(encrypted.ciphertext_base64 == "BnvlsA0eu50NK8W6KQonuw==");
    EXPECT_TRUE(encrypted.iv_base64 == "AAECAwQFBgcICQoLDA0ODw==");
    const std::vector<std::uint8_t> block_plaintext(16, 'A');
    EXPECT_TRUE(bridge_core::EncryptPayload(provider, "synthetic-device-key", iv, block_plaintext, &encrypted) == bridge_core::Status::kOk);
    EXPECT_TRUE(encrypted.ciphertext_base64.size() == 44);  // PKCS#7 adds a complete block at the boundary.
}

void TestModelPendingAndConvergence() {
    bridge_core::UnifiedDeviceModel model(Identity());
    model.MarkReconnected();
    EXPECT_TRUE(model.availability() == bridge_core::Availability::kAvailable);
    EXPECT_TRUE(model.FindChannel(bridge_core::kChannelCount) == nullptr);
    EXPECT_TRUE(!model.FindChannel(0)->fresh);
    const bridge_core::CommandIntent intent{0, bridge_core::BinaryState::kOn, "seq-9"};
    EXPECT_TRUE(model.IssueCommand(intent) == bridge_core::Status::kOk);
    EXPECT_TRUE(model.FindChannel(0)->observed_state == bridge_core::BinaryState::kUnknown);
    EXPECT_TRUE(model.MarkTransportAccepted(0) == bridge_core::Status::kOk);
    EXPECT_TRUE(model.FindChannel(0)->pending.has_value());
    EXPECT_TRUE(model.ApplyObservation(0, bridge_core::BinaryState::kOn) == bridge_core::Status::kOk);
    EXPECT_TRUE(model.FindChannel(0)->convergence == bridge_core::Convergence::kMatched);
    EXPECT_TRUE(!model.FindChannel(0)->pending.has_value());
    EXPECT_TRUE(model.FindChannel(0)->fresh);
}

void TestModelConflictAndAvailability() {
    bridge_core::UnifiedDeviceModel model(Identity());
    model.MarkReconnected();
    EXPECT_TRUE(model.ApplyObservation(1, bridge_core::BinaryState::kOff) == bridge_core::Status::kOk);
    EXPECT_TRUE(model.IssueCommand({1, bridge_core::BinaryState::kOn, "seq-2"}) == bridge_core::Status::kOk);
    EXPECT_TRUE(model.MarkTransportAccepted(1) == bridge_core::Status::kOk);
    EXPECT_TRUE(model.ApplyObservation(1, bridge_core::BinaryState::kOff) == bridge_core::Status::kOk);
    EXPECT_TRUE(model.FindChannel(1)->convergence == bridge_core::Convergence::kConflicted);
    model.MarkDisconnected();
    EXPECT_TRUE(model.availability() == bridge_core::Availability::kUnavailable);
    EXPECT_TRUE(model.FindChannel(1)->observed_state == bridge_core::BinaryState::kOff);
    EXPECT_TRUE(!model.FindChannel(1)->fresh);
    model.MarkReconnected();
    EXPECT_TRUE(model.availability() == bridge_core::Availability::kAvailable);
    EXPECT_TRUE(!model.FindChannel(1)->fresh);
    EXPECT_TRUE(model.ApplyObservation(1, bridge_core::BinaryState::kUnknown) == bridge_core::Status::kInvalidState);
}

void TestFourChannelIsolationAndBindings() {
    bridge_core::UnifiedDeviceModel model(Identity());
    model.MarkReconnected();
    EXPECT_TRUE(model.ApplyObservation(0, bridge_core::BinaryState::kOn) == bridge_core::Status::kOk);
    EXPECT_TRUE(model.ApplyObservation(3, bridge_core::BinaryState::kOff) == bridge_core::Status::kOk);
    EXPECT_TRUE(model.FindChannel(1)->observed_state == bridge_core::BinaryState::kUnknown);
    const auto bindings = bridge_core::BuildOnOffBindings(Identity());
    EXPECT_TRUE(bindings[0].stable_binding_key != bindings[1].stable_binding_key);
    EXPECT_TRUE(bindings[2].stable_binding_key != bindings[3].stable_binding_key);
    EXPECT_TRUE(bindings[0].stable_binding_key == bridge_core::StableBindingKey(Identity(), 0));
    EXPECT_TRUE(bridge_core::StableBindingKey({"ewelink", "device-1000000001"}, 0) == bindings[0].stable_binding_key);
    EXPECT_TRUE(bridge_core::StableBindingKey({"ewelink", "device-1000000001"}, 4).empty());
}

void TestFakeTransport() {
    bridge_core::UnifiedDeviceModel model(Identity());
    model.MarkReconnected();
    FakeTransport transport;
    bridge_core::CommandOrchestrator orchestrator(transport);
    EXPECT_TRUE(orchestrator.Submit(model, {2, bridge_core::BinaryState::kOn, "seq-3"}) == bridge_core::Status::kOk);
    EXPECT_TRUE(transport.requests.size() == 1);
    EXPECT_TRUE(model.FindChannel(2)->disposition == bridge_core::TransportDisposition::kAccepted);
    EXPECT_TRUE(model.FindChannel(2)->observed_state == bridge_core::BinaryState::kUnknown);
    transport.next = bridge_core::Status::kUnsupported;
    EXPECT_TRUE(orchestrator.Submit(model, {3, bridge_core::BinaryState::kOff, "seq-4"}) == bridge_core::Status::kUnsupported);
    EXPECT_TRUE(model.FindChannel(3)->disposition == bridge_core::TransportDisposition::kRejected);
    EXPECT_TRUE(model.FindChannel(3)->convergence == bridge_core::Convergence::kRejected);
}

}  // namespace

int main() {
    TestEnvelopeRoundTrip();
    TestEnvelopeBoundaries();
    TestEncryptedEnvelopeRoundTrip();
    TestCryptoVector();
    TestModelPendingAndConvergence();
    TestModelConflictAndAvailability();
    TestFourChannelIsolationAndBindings();
    TestFakeTransport();
    if (failures != 0) {
        std::cerr << failures << " host test assertion(s) failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "All host tests passed\n";
    return EXIT_SUCCESS;
}
