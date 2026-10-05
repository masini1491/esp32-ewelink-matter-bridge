#include <cstdlib>
#include <iostream>
#include <string>

#include "bridge_simulator/synthetic_device.hpp"

namespace {

int failures = 0;

#define EXPECT_TRUE(expression)                                                                    \
    do {                                                                                           \
        if (!(expression)) {                                                                       \
            std::cerr << "FAILED " << __FUNCTION__ << ": " << #expression << '\n';                \
            ++failures;                                                                            \
        }                                                                                          \
    } while (false)

using bridge_core::Availability;
using bridge_core::BinaryState;
using bridge_core::CommandIntent;
using bridge_core::Convergence;
using bridge_core::Status;
using bridge_core::TransportDisposition;
using bridge_simulator::NextTransportResult;
using bridge_simulator::SyntheticDevice;

SyntheticDevice MakeDevice() { return SyntheticDevice({"synthetic-test", "synthetic-device"}); }

void TestAcceptedCommandWaitsForObservation() {
    auto device = MakeDevice();
    device.Connect();

    const CommandIntent intent{0, BinaryState::kOn, "synthetic-seq-1"};
    EXPECT_TRUE(device.Submit(intent) == Status::kOk);
    EXPECT_TRUE(device.submitted_intents().size() == 1);
    EXPECT_TRUE(device.submitted_intents().front().channel == intent.channel);
    EXPECT_TRUE(device.submitted_intents().front().correlation == intent.correlation);

    const auto* channel = device.FindChannel(0);
    EXPECT_TRUE(channel != nullptr);
    EXPECT_TRUE(channel->observed_state == BinaryState::kUnknown);
    EXPECT_TRUE(!channel->fresh);
    EXPECT_TRUE(channel->pending.has_value());
    EXPECT_TRUE(channel->disposition == TransportDisposition::kAccepted);
    EXPECT_TRUE(channel->convergence == Convergence::kNone);
}

void TestMatchingObservationConverges() {
    auto device = MakeDevice();
    device.Connect();
    EXPECT_TRUE(device.InjectObservation(1, BinaryState::kOff) == Status::kOk);
    EXPECT_TRUE(device.Submit({1, BinaryState::kOn, "synthetic-match"}) == Status::kOk);
    EXPECT_TRUE(device.InjectObservation(1, BinaryState::kOn) == Status::kOk);

    const auto* channel = device.FindChannel(1);
    EXPECT_TRUE(channel->observed_state == BinaryState::kOn);
    EXPECT_TRUE(channel->fresh);
    EXPECT_TRUE(!channel->pending.has_value());
    EXPECT_TRUE(channel->convergence == Convergence::kMatched);
}

void TestOppositeObservationConflicts() {
    auto device = MakeDevice();
    device.Connect();
    EXPECT_TRUE(device.InjectObservation(2, BinaryState::kOff) == Status::kOk);
    EXPECT_TRUE(device.Submit({2, BinaryState::kOn, "synthetic-conflict"}) == Status::kOk);
    EXPECT_TRUE(device.InjectObservation(2, BinaryState::kOff) == Status::kOk);

    const auto* channel = device.FindChannel(2);
    EXPECT_TRUE(channel->observed_state == BinaryState::kOff);
    EXPECT_TRUE(channel->convergence == Convergence::kConflicted);
    EXPECT_TRUE(!channel->pending.has_value());
}

void TestRejectedTransportConvergesRejected() {
    auto device = MakeDevice();
    device.Connect();
    device.SetNextTransportResult(NextTransportResult::kRejected);

    EXPECT_TRUE(device.Submit({3, BinaryState::kOn, "synthetic-rejected"}) == Status::kUnsupported);
    EXPECT_TRUE(device.submitted_intents().size() == 1);
    const auto* channel = device.FindChannel(3);
    EXPECT_TRUE(channel->observed_state == BinaryState::kUnknown);
    EXPECT_TRUE(channel->disposition == TransportDisposition::kRejected);
    EXPECT_TRUE(channel->convergence == Convergence::kRejected);
    EXPECT_TRUE(!channel->pending.has_value());
}

void TestDisconnectStaleAndReconnectFreshness() {
    auto device = MakeDevice();
    device.Connect();
    EXPECT_TRUE(device.InjectObservation(0, BinaryState::kOn) == Status::kOk);
    EXPECT_TRUE(device.InjectObservation(1, BinaryState::kOff) == Status::kOk);

    device.Disconnect();
    EXPECT_TRUE(device.availability() == Availability::kUnavailable);
    EXPECT_TRUE(device.FindChannel(0)->observed_state == BinaryState::kOn);
    EXPECT_TRUE(device.FindChannel(1)->observed_state == BinaryState::kOff);
    EXPECT_TRUE(!device.FindChannel(0)->fresh);
    EXPECT_TRUE(!device.FindChannel(1)->fresh);

    device.Reconnect();
    EXPECT_TRUE(device.availability() == Availability::kAvailable);
    EXPECT_TRUE(!device.FindChannel(0)->fresh);
    EXPECT_TRUE(!device.FindChannel(1)->fresh);

    EXPECT_TRUE(device.InjectObservation(0, BinaryState::kOn) == Status::kOk);
    device.MarkStale();
    EXPECT_TRUE(device.availability() == Availability::kUnavailable);
    EXPECT_TRUE(device.FindChannel(0)->observed_state == BinaryState::kOn);
    EXPECT_TRUE(!device.FindChannel(0)->fresh);
}

void TestFourChannelIsolation() {
    auto device = MakeDevice();
    device.Connect();

    for (std::uint8_t channel = 0; channel < 4; ++channel) {
        const auto initial = channel % 2 == 0 ? BinaryState::kOff : BinaryState::kOn;
        EXPECT_TRUE(device.InjectObservation(channel, initial) == Status::kOk);
    }
    for (std::uint8_t channel = 0; channel < 4; ++channel) {
        const auto requested = channel % 2 == 0 ? BinaryState::kOn : BinaryState::kOff;
        EXPECT_TRUE(device.Submit({channel, requested, "synthetic-channel-" + std::to_string(channel)}) ==
                    Status::kOk);
    }

    EXPECT_TRUE(device.submitted_intents().size() == 4);
    for (std::uint8_t channel = 0; channel < 4; ++channel) {
        EXPECT_TRUE(device.submitted_intents()[channel].channel == channel);
        EXPECT_TRUE(device.FindChannel(channel)->pending.has_value());
    }

    for (std::uint8_t channel = 0; channel < 4; ++channel) {
        const auto requested = channel % 2 == 0 ? BinaryState::kOn : BinaryState::kOff;
        EXPECT_TRUE(device.InjectObservation(channel, requested) == Status::kOk);
        EXPECT_TRUE(device.FindChannel(channel)->convergence == Convergence::kMatched);
        for (std::uint8_t other = static_cast<std::uint8_t>(channel + 1); other < 4; ++other) {
            EXPECT_TRUE(device.FindChannel(other)->pending.has_value());
            const auto unchanged = other % 2 == 0 ? BinaryState::kOff : BinaryState::kOn;
            EXPECT_TRUE(device.FindChannel(other)->observed_state == unchanged);
        }
    }
}

}  // namespace

int main() {
    TestAcceptedCommandWaitsForObservation();
    TestMatchingObservationConverges();
    TestOppositeObservationConflicts();
    TestRejectedTransportConvergesRejected();
    TestDisconnectStaleAndReconnectFreshness();
    TestFourChannelIsolation();

    if (failures != 0) {
        std::cerr << failures << " simulator assertion(s) failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "bridge_simulator_tests: 6 scenarios passed\n";
    return EXIT_SUCCESS;
}
