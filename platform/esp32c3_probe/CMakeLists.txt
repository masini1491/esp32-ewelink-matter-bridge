cmake_minimum_required(VERSION 3.16)

# Keep compile-probe metadata aligned with the pinned esp-matter example pattern.
set(PROJECT_VER "0.0.1")
set(PROJECT_VER_NUMBER 1)

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(esp32c3_compile_probe)
