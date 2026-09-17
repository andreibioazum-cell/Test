cmake_minimum_required(VERSION 3.22.1)

project(openrblx_mobile LANGUAGES C CXX)

if(NOT ANDROID)
    message(FATAL_ERROR "The OpenRBLX native target is Android-only")
endif()

if(NOT DEFINED OPENRBLX_ROOT)
    get_filename_component(OPENRBLX_ROOT "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
endif()

if(NOT EXISTS "${OPENRBLX_ROOT}/lib/luau/VM/src/lapi.cpp")
    message(FATAL_ERROR "Luau submodule is missing. Configure checkout with submodules: recursive.")
endif()

# raylib is built for Android as part of the APK.  The repository contains
# desktop convenience binaries, but those cannot be linked into a phone APK.
include(FetchContent)
set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(CUSTOMIZE_BUILD OFF CACHE BOOL "" FORCE)
set(PLATFORM "Android" CACHE STRING "" FORCE)
FetchContent_Declare(
    raylib
    GIT_REPOSITORY https://github.com/raysan5/raylib.git
    GIT_TAG 5.5
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(raylib)

file(GLOB OPENRBLX_C_SOURCES CONFIGURE_DEPENDS
    "${OPENRBLX_ROOT}/src/*.c"
    "${OPENRBLX_ROOT}/src/filetypes/*.c"
    "${OPENRBLX_ROOT}/src/luau/*.c"
)

list(APPEND OPENRBLX_C_SOURCES
    "${OPENRBLX_ROOT}/lib/cJSON/src/cJSON.c"
    "${OPENRBLX_ROOT}/lib/lz4/src/lz4.c"
    "${OPENRBLX_ROOT}/lib/xml/src/xml.c"
    "${OPENRBLX_ROOT}/lib/zstd/src/zstd_decompress.c"
    "${OPENRBLX_ROOT}/player/player.c"
)

file(GLOB OPENRBLX_LUAU_CXX_SOURCES CONFIGURE_DEPENDS
    "${OPENRBLX_ROOT}/lib/luau/VM/src/*.cpp"
    "${OPENRBLX_ROOT}/lib/luau/Compiler/src/*.cpp"
    "${OPENRBLX_ROOT}/lib/luau/Ast/src/*.cpp"
)

add_library(openrblx SHARED
    ${OPENRBLX_C_SOURCES}
    ${OPENRBLX_LUAU_CXX_SOURCES}
)

set_target_properties(openrblx PROPERTIES
    OUTPUT_NAME "openrblx"
    C_STANDARD 99
    C_STANDARD_REQUIRED YES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    POSITION_INDEPENDENT_CODE ON
)

target_compile_definitions(openrblx PRIVATE
    OPENRBLX_MOBILE
    OPENRBLX_NO_CURL
    PLATFORM_ANDROID
    # Luau's public C API is implemented by C++ files but consumed by the C
    # engine.  Keep those exported functions unmangled.
    "$<$<COMPILE_LANGUAGE:CXX>:LUA_API=extern \"C\">"
    "$<$<COMPILE_LANGUAGE:CXX>:LUACODE_API=extern \"C\">"
)

target_include_directories(openrblx PRIVATE
    "${raylib_SOURCE_DIR}/src"
    "${OPENRBLX_ROOT}/include"
    "${OPENRBLX_ROOT}/src"
    "${OPENRBLX_ROOT}/lib/cJSON/include"
    "${OPENRBLX_ROOT}/lib/lz4/include"
    "${OPENRBLX_ROOT}/lib/xml/include"
    "${OPENRBLX_ROOT}/lib/lz4/src"
    "${OPENRBLX_ROOT}/lib/zstd/include"
    "${OPENRBLX_ROOT}/lib/luau/VM/include"
    "${OPENRBLX_ROOT}/lib/luau/Compiler/include"
    "${OPENRBLX_ROOT}/lib/luau/Common/include"
    "${OPENRBLX_ROOT}/lib/luau/Ast/include"
    "${OPENRBLX_ROOT}/lib/luau/VM/src"
)

target_link_libraries(openrblx PRIVATE
    raylib
    log
    android
    EGL
    GLESv2
    OpenSLES
    atomic
    m
    dl
)

# Only player/player.c is added above; the desktop Studio executable is not an
# input to this Android target.
