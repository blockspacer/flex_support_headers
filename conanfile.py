from conans import ConanFile, CMake, tools
import traceback
import os
import shutil

# conan runs the methods in this order:
# config_options(),
# configure(),
# requirements(),
# package_id(),
# build_requirements(),
# build_id(),
# system_requirements(),
# source(),
# imports(),
# build(),
# package(),
# package_info()

class flex_support_headers_conan_project(ConanFile):
    name = "flex_support_headers"

    # Indicates License type of the packaged library
    # TODO (!!!)
    # license = "MIT"

    version = "master"

    # TODO (!!!)
    #url = "https://github.com/blockspacer/CXXCTP"

    description = "C++ library"
    topics = ('c++')

    options = {
        "shared": [True, False],
        "debug": [True, False],
        "enable_sanitizers": [True, False],
        "enable_clang_from_conan": [True, False],
        "enable_web_pthreads": [True, False]
    }

    default_options = (
        "shared=False",
        "enable_clang_from_conan=False",
        "debug=False",
        "enable_sanitizers=False",
        "enable_web_pthreads=True"
        # build
        #"*:shared=False"
    )

    # Custom attributes for Bincrafters recipe conventions
    _source_subfolder = "."
    _build_subfolder = "."

    # NOTE: no cmake_find_package due to custom FindXXX.cmake
    generators = "cmake", "cmake_paths", "virtualenv"

    # Packages the license for the conanfile.py
    #exports = ["LICENSE.md"]

    # If the source code is going to be in the same repo as the Conan recipe,
    # there is no need to define a `source` method. The source folder can be
    # defined like this
    exports_sources = ("LICENSE", "*.md", "include/*", "src/*",
                       "cmake/*", "CMakeLists.txt", "tests/*", "benchmarks/*",
                       "scripts/*", "tools/*", "codegen/*", "assets/*",
                       "docs/*", "licenses/*", "patches/*", "resources/*",
                       "submodules/*", "thirdparty/*", "third-party/*",
                       "third_party/*", "cobalt/*", "flex/*")

    settings = "os", "compiler", "build_type", "arch"

    #def source(self):
    #  url = "https://github.com/....."
    #  self.run("git clone %s ......." % url)

    def build_requirements(self):
        self.build_requires("cmake_platform_detection/master@conan/stable")
        self.build_requires("cmake_build_options/master@conan/stable")

    def requirements(self):
        self.requires("chromium_build_util/master@conan/stable")

        #if self._is_tests_enabled():
        #    self.requires("catch2/[>=2.1.0]@bincrafters/stable")
        #    self.requires("gtest/[>=1.8.0]@bincrafters/stable")
        #    self.requires("FakeIt/[>=2.0.4]@gasuketsu/stable")

        #if not self.options.use_system_boost:
        #    self.requires("boost/1.71.0@dev/stable")

        self.requires("chromium_build_util/master@conan/stable")

        if self.options.enable_clang_from_conan:
          self.requires("llvm_support/6.0.1@Manu343726/testing")
          self.requires("libclang/6.0.1@Manu343726/testing")
          self.requires("clang_tooling/6.0.1@Manu343726/testing")
          self.requires("clang_tooling_core/6.0.1@Manu343726/testing")
          self.requires("clang_analysis/6.0.1@Manu343726/testing")
          self.requires("clang_ast/6.0.1@Manu343726/testing")
          self.requires("llvm/6.0.1@Manu343726/testing")
        else:
          self.requires("cling_conan/master@conan/stable")

        self.requires("chromium_base/master@conan/stable")

        self.requires("basis/master@conan/stable")

        # if self.settings.os == "Linux":
        #     self.requires("chromium_dynamic_annotations/master@conan/stable")

        #self.requires("corrade/2019.10@magnum/stable")

        #self.requires("type_safe/0.2@conan/stable")

        #self.requires("double-conversion/3.1.1@bincrafters/stable")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.parallel = True
        cmake.verbose = True

        if self.options.shared:
            cmake.definitions["flex_support_headers_BUILD_SHARED_LIBS"] = "ON"

        def add_cmake_option(var_name, value):
            value_str = "{}".format(value)
            var_value = "ON" if value_str == 'True' else "OFF" if value_str == 'False' else value_str
            cmake.definitions[var_name] = var_value

        add_cmake_option("ENABLE_SANITIZERS", self.options.enable_sanitizers)

        add_cmake_option("ENABLE_WEB_PTHREADS", self.options.enable_web_pthreads)

        cmake.configure(build_folder=self._build_subfolder)

        return cmake

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def build(self):
        cmake = self._configure_cmake()
        if self.settings.compiler == 'gcc':
            cmake.definitions["CMAKE_C_COMPILER"] = "gcc-{}".format(
                self.settings.compiler.version)
            cmake.definitions["CMAKE_CXX_COMPILER"] = "g++-{}".format(
                self.settings.compiler.version)

        #cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = 'conan_paths.cmake'

        # The CMakeLists.txt file must be in `source_folder`
        cmake.configure(source_folder=".")

        cpu_count = tools.cpu_count()
        self.output.info('Detected %s CPUs' % (cpu_count))

        # -j flag for parallel builds
        cmake.build(args=["--", "-j%s" % cpu_count])

    # Importing files copies files from the local store to your project.
    def imports(self):
        dest = os.getenv("CONAN_IMPORT_PATH", "bin")
        self.output.info("CONAN_IMPORT_PATH is ${CONAN_IMPORT_PATH}")
        self.copy("license*", dst=dest, ignore_case=True)
        self.copy("*.dll", dst=dest, src="bin")
        self.copy("*.so*", dst=dest, src="bin")
        self.copy("*.pdb", dst=dest, src="lib")
        self.copy("*.dylib*", dst=dest, src="lib")
        self.copy("*.lib*", dst=dest, src="lib")
        self.copy("*.a*", dst=dest, src="lib")

    # package_info() method specifies the list of
    # the necessary libraries, defines and flags
    # for different build configurations for the consumers of the package.
    # This is necessary as there is no possible way to extract this information
    # from the CMake install automatically.
    # For instance, you need to specify the lib directories, etc.
    def package_info(self):
        #self.cpp_info.libs = ["flex_support_headers"]

        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.bindirs = ["bin"]
        self.env_info.LD_LIBRARY_PATH.append(
            os.path.join(self.package_folder, "lib"))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        for libpath in self.deps_cpp_info.lib_paths:
            self.env_info.LD_LIBRARY_PATH.append(libpath)

        #self.cpp_info.includedirs.append(os.getcwd())
        #self.cpp_info.includedirs.append(
        #  os.path.join("base", "third_party", "tcmalloc"))
        #self.cpp_info.includedirs.append(
        #  os.path.join("base", "third_party", "tcmalloc", "compat"))

        #if self.settings.os == "Linux":
        #  self.cpp_info.defines.append('HAVE_CONFIG_H=1')

        # in linux we need to link also with these libs
        #if self.settings.os == "Linux":
        #    self.cpp_info.libs.extend(["pthread", "dl", "rt"])

        #self.cpp_info.libs = tools.collect_libs(self)
        #self.cpp_info.defines.append('PDFLIB_DLL')

    def package_id(self):
        # see https://docs.conan.io/en/latest/howtos/header_only.html
        self.info.header_only()
