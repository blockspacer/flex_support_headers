# see https://github.com/chromium/chromium/blob/9db0b5162b8648833c3a6b1af044cebd9d7d3855/base/BUILD.gn

cmake_minimum_required(VERSION 3.4)

# project() must be before checks, see https://stackoverflow.com/a/26437667/10904212
set(PROJECT_NAME "flex_support_headers")
set(PROJECT_VERSION 1.0.0.1)
project(${PROJECT_NAME}
  VERSION ${PROJECT_VERSION}
  LANGUAGES CXX C)

set(LIB_NAME ${PROJECT_NAME})

set(ENABLE_CLING TRUE CACHE BOOL "ENABLE_CLING")
message(STATUS "ENABLE_CLING=${ENABLE_CLING}")

set(ENABLE_CLANG_FROM_CONAN FALSE CACHE BOOL "ENABLE_CLANG_FROM_CONAN")
message(STATUS "ENABLE_CLANG_FROM_CONAN=${ENABLE_CLANG_FROM_CONAN}")

if(ENABLE_CLANG_FROM_CONAN AND ENABLE_CLING)
  message(FATAL_ERROR
    "don't use both ENABLE_CLING and ENABLE_CLANG_FROM_CONAN at the same time. cling already provides clang libtooling")
endif()


# --------------------------- conan configuration ------------------------------

# Note: FetchContent is available since CMake 3.11
# see https://cmake.org/cmake/help/git-master/module/FetchContent.html
# By default, everything is downloaded into your build directory
# Once CMake successfully downloads our external content, it sets two variables that can be used in CMakeLists.txt to locate the new data:
# 1 <resource_name>_SOURCE_DIR
#   specifies the location of the downloaded sources,
# 2 <resource_name>_BINARY_DIR
#   specifies where is the default build directory for the downloaded sources.
include(FetchContent)

set(FetchContent_conan_auto_install "conan_auto_install")
FetchContent_Declare(
  ${FetchContent_conan_auto_install}
  PREFIX external_dependencies/${FetchContent_conan_auto_install}
  GIT_REPOSITORY https://github.com/blockspacer/conan_auto_install.git
  GIT_TAG origin/master
  # Disable warning about detached HEAD https://stackoverflow.com/a/36794768
  GIT_CONFIG        advice.detachedHead=false
  SOURCE_DIR        "${CMAKE_BINARY_DIR}/${FetchContent_conan_auto_install}"
  BINARY_DIR        "${CMAKE_BINARY_DIR}/${FetchContent_conan_auto_install}-build"
  CMAKE_ARGS        "-Wno-dev"
  CONFIGURE_COMMAND ""
  BUILD_COMMAND     ""
  INSTALL_COMMAND   ""
  TEST_COMMAND      ""
)
FetchContent_GetProperties(${FetchContent_conan_auto_install})
if (NOT ${FetchContent_conan_auto_install}_POPULATED)
  # Populate command can be used only once for every resource
  # during cmake configuration, which explains the conditional above.
  FetchContent_Populate(${FetchContent_conan_auto_install})
endif()
message(STATUS "${FetchContent_conan_auto_install}_SOURCE_DIR = ${${FetchContent_conan_auto_install}_SOURCE_DIR}")
message(STATUS "${FetchContent_conan_auto_install}_BINARY_DIR = ${${FetchContent_conan_auto_install}_BINARY_DIR}")
include(${${FetchContent_conan_auto_install}_SOURCE_DIR}/conan-auto-install.cmake)
option(CONAN_AUTO_INSTALL "Let CMake call conan install automatically"
  OFF
)
if (CONAN_AUTO_INSTALL)
  set(CONAN_PROFILE
      "clang"
      CACHE STRING "Conan profile to use during installation")
  if (NOT CMAKE_BUILD_TYPE MATCHES "Debug" )
    set(conan_build_type "Release")
  else()
    set(conan_build_type "Debug")
  endif()
  # No --build=missing cause llvm requires long build
  conan_auto_install(
    CONAN_OPTIONS "--profile=${CONAN_PROFILE} -s build_type=${conan_build_type} -s cling_conan:build_type=Release -o openssl:shared=True"
    #FORCE
  )
endif()

if(EXISTS "${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake")
  list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_BINARY_DIR}/)
  include(${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake)
  include(${CMAKE_CURRENT_BINARY_DIR}/conan_paths.cmake OPTIONAL)
  conan_basic_setup(
    # prevent conan_basic_setup from resetting cmake variables
    TARGETS
    KEEP_RPATHS
    # see https://github.com/conan-io/conan/issues/6012
    NO_OUTPUT_DIRS
    )
else()
  message (FATAL_ERROR "must use conan")
endif()

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/)

find_package(cmake_platform_detection REQUIRED)
run_cmake_platform_detection()

find_package(cmake_build_options REQUIRED)
setup_default_build_type(RELEASE)
setup_cmake_build_options(RELEASE DEBUG)

# uses Config.cmake or a -config.cmake file
# see https://gitlab.kitware.com/cmake/community/wikis/doc/tutorials/How-to-create-a-ProjectConfig.cmake-file
find_package(chromium_build_util REQUIRED)
#
if(TARGET chromium_build_util::chromium_build_util-static)
  set(build_util_LIB chromium_build_util::chromium_build_util-static)
else()
  message(FATAL_ERROR "not supported: using system provided chromium_build_util library")
endif()

include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/PlatformChecks.cmake)

include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/CommonOptions.cmake)

include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/ProjectFiles.cmake)

# Keep symbols for JIT resolution
set(LLVM_NO_DEAD_STRIP 1)

if(NOT TARGET CONAN_PKG::chromium_base)
  message(FATAL_ERROR "Use chromium_base from conan")
endif()

find_package(chromium_base REQUIRED)

find_package(chromium_base REQUIRED)
if(NOT TARGET ${base_LIB})
  message(FATAL_ERROR "not supported ${base_LIB}: using system provided chromium_base library")
endif()

# see https://doc.magnum.graphics/corrade/corrade-cmake.html#corrade-cmake-subproject
#find_package(Corrade REQUIRED PluginManager)

#find_package( X11 REQUIRED )
#message(STATUS "X11_LIBRARIES = ${X11_LIBRARIES}")
#
#find_package( EXPAT REQUIRED )
#message(STATUS "EXPAT_LIBRARIES = ${EXPAT_LIBRARIES}")
#
#find_package( ZLIB REQUIRED )
#message(STATUS "ZLIB_LIBRARIES = ${ZLIB_LIBRARIES}")

# $<INSTALL_INTERFACE:...> is exported using install(EXPORT)
# $<BUILD_INTERFACE:...> is exported using export(), or when the target is used by another target in the same buildsystem
macro(add_relative_include_dir TARGET VISIBILITY_BUILD VISIBILITY_INSTALL NEW_ELEM)
  target_include_directories(${TARGET}
    ${VISIBILITY_BUILD} "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/${NEW_ELEM}>"
    ${VISIBILITY_INSTALL} "$<INSTALL_INTERFACE:$<INSTALL_PREFIX>/${CMAKE_INSTALL_INCLUDEDIR}/${NEW_ELEM}>"
  )
endmacro(add_relative_include_dir)

add_library(${LIB_NAME} INTERFACE
  # nothing
)

add_relative_include_dir(${LIB_NAME} INTERFACE INTERFACE "flex")

if(NOT DEFINED build_util_LIB)
  message(FATAL_ERROR "NOT DEFINED: build_util_LIB")
endif(NOT DEFINED build_util_LIB)

list(APPEND USED_3DPARTY_LIBS
  ${base_LIB}
  ${build_util_LIB}
)

find_package(basis REQUIRED)
if(${basis_HEADER_DIR} STREQUAL "")
  message(FATAL_ERROR "unable to find basis_HEADER_DIR")
endif()

list(APPEND USED_3DPARTY_LIBS
  ${basis_LIB}
  CONAN_PKG::boost
  ${USED_BOOST_LIBS}
  #boost_outcome
  #microsoft_gsl
)

if(ENABLE_CLING)
  find_package(Cling REQUIRED)

  list(APPEND CLING_DEFINITIONS CLING_IS_ON=1)
  target_link_libraries(${LIB_NAME} INTERFACE#PRIVATE
    CONAN_PKG::cling_conan
  )

  get_target_property (cling_conan_IMPORTED_LOCATION CONAN_PKG::cling_conan INTERFACE_INCLUDE_DIRECTORIES)
  message( STATUS "cling_conan=${cling_conan_IMPORTED_LOCATION}" )
  target_include_directories( ${LIB_NAME} INTERFACE ${cling_conan_IMPORTED_LOCATION} )

  #if(MSVC)
  #  set_target_properties(${LIB_NAME} PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS 1)
  #  set_property(
  #    TARGET ${LIB_NAME}
  #    APPEND_STRING
  #    PROPERTY LINK_FLAGS
  #             "/EXPORT:?setValueNoAlloc@internal@runtime@cling@@YAXPEAX00D_K@Z
  #              /EXPORT:?setValueNoAlloc@internal@runtime@cling@@YAXPEAX00DM@Z
  #              /EXPORT:cling_runtime_internal_throwIfInvalidPointer")
  #endif()

  target_compile_definitions(${LIB_NAME} INTERFACE CLING_IS_ON=1)
endif(ENABLE_CLING)

if(ENABLE_CLANG_FROM_CONAN)
  target_link_libraries( ${LIB_NAME} INTERFACE
    CONAN_PKG::libclang
    CONAN_PKG::clang_tooling
    CONAN_PKG::clang_tooling_core
    CONAN_PKG::llvm_support
  )
endif(ENABLE_CLANG_FROM_CONAN)

# install and export steps
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/Exports.cmake)
