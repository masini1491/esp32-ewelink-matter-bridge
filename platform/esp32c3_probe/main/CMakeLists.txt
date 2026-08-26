set(BRIDGE_CORE_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../../core")

idf_component_register(
    SRCS
        "bridge_compile_probe.cpp"
        "${BRIDGE_CORE_ROOT}/src/binding.cpp"
        "${BRIDGE_CORE_ROOT}/src/device_model.cpp"
        "${BRIDGE_CORE_ROOT}/src/envelope.cpp"
    INCLUDE_DIRS "." "${BRIDGE_CORE_ROOT}/include"
    REQUIRES esp_matter
)

target_compile_features(${COMPONENT_LIB} PUBLIC cxx_std_17)
target_compile_options(${COMPONENT_LIB} PRIVATE "-DCHIP_HAVE_CONFIG_H")
target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,-u,bridge_compile_probe_anchor")
