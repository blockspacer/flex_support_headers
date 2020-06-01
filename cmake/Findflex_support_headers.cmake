get_filename_component(CURRENT_CMAKE_DIR "${CMAKE_CURRENT_LIST_FILE}" PATH)
list(APPEND CMAKE_MODULE_PATH ${CURRENT_CMAKE_DIR})

#include(CMakeFindDependencyMacro) # use find_package instead

# NOTE: some packages may be optional (platform-specific, etc.)
find_package(chromium_build_util REQUIRED)

list(REMOVE_AT CMAKE_MODULE_PATH -1)

if(NOT TARGET CONAN_PKG::flex_support_headers)
  message(FATAL_ERROR "Use flex_support_headers from conan")
endif()
# conan package has '/include' dir
set(flex_support_header_HEADER_FILE
  ${CONAN_FLEX_SUPPORT_HEADERS_ROOT}/include/flex/cling_preloader.inc
)
if(flex_support_headers_LOCAL_BUILD)
  # no '/include' dir on local build
  set(flex_support_header_HEADER_FILE
    ${CONAN_FLEX_SUPPORT_HEADERS_ROOT}/flex/cling_preloader.inc
  )
else()
  # uses Config.cmake or a -config.cmake file
  # see https://gitlab.kitware.com/cmake/community/wikis/doc/tutorials/How-to-create-a-ProjectConfig.cmake-file
  # BELOW MUST BE EQUAL TO find_package(... CONFIG REQUIRED)
  # NOTE: find_package(CONFIG) not supported with EMSCRIPTEN, so use include()
  include(${CMAKE_CURRENT_LIST_DIR}/cmake/flex_support_headers-config.cmake)
endif()
