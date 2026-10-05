cmake_minimum_required(VERSION 3.20)

project(esp32_ewelink_matter_bridge LANGUAGES CXX)

option(BRIDGE_BUILD_HOST_TESTS "Build portable-core and synthetic-simulator host tests" ON)

add_library(bridge_core
    core/src/binding.cpp
    core/src/device_model.cpp
    core/src/envelope.cpp
)

target_compile_features(bridge_core PUBLIC cxx_std_17)
target_include_directories(bridge_core PUBLIC core/include)

if(BRIDGE_BUILD_HOST_TESTS)
    enable_testing()

    add_library(bridge_simulator
        simulator/src/synthetic_device.cpp
    )
    target_compile_features(bridge_simulator PUBLIC cxx_std_17)
    target_include_directories(bridge_simulator PUBLIC simulator/include)
    target_link_libraries(bridge_simulator PUBLIC bridge_core)

    add_executable(bridge_simulator_tests tests/simulator_tests.cpp)
    target_link_libraries(bridge_simulator_tests PRIVATE bridge_simulator)
    add_test(NAME bridge_simulator_tests COMMAND bridge_simulator_tests)

    if(WIN32)
        add_executable(bridge_host_tests
            tests/host_tests.cpp
            tests/windows_cng_crypto_provider.cpp
        )
        target_link_libraries(bridge_host_tests PRIVATE bridge_core bcrypt crypt32)
        target_include_directories(bridge_host_tests PRIVATE tests)
        add_test(NAME bridge_host_tests COMMAND bridge_host_tests)
    else()
        find_package(OpenSSL REQUIRED COMPONENTS Crypto)
        add_executable(bridge_host_tests
            tests/host_tests.cpp
            tests/openssl_crypto_provider.cpp
        )
        target_link_libraries(bridge_host_tests PRIVATE bridge_core OpenSSL::Crypto)
        target_include_directories(bridge_host_tests PRIVATE tests)
        add_test(NAME bridge_host_tests COMMAND bridge_host_tests)
    endif()
endif()
