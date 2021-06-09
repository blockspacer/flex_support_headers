# About

Header-only library that can simplify usage of `Cling C++ interpreter` with flextool.

`flextool` can be found at [https://github.com/blockspacer/flextool](https://github.com/blockspacer/flextool)

## Usage

Pass command-line argument to flextool `--cling_scripts=${flex_support_headers}`

Where `${flex_support_headers}` is path to `flex_support_headers/flex/cling_preloader.inc`

`--cling_scripts` argument allows to preload include files or whole C++ source files.

That may be useful because `Cling` may fail to include header file at runtime using `process` function (we want to process included file once).

See for details https://github.com/root-project/cling/blob/master/include/cling/Interpreter/Interpreter.h

## Before installation

- [installation guide](https://blockspacer.github.io/flex_docs/download/)

## Installation

```bash
export CXX=clang++-10
export CC=clang-10

export VERBOSE=1
export CONAN_REVISIONS_ENABLED=1
export CONAN_VERBOSE_TRACEBACK=1
export CONAN_PRINT_RUN_COMMANDS=1
export CONAN_LOGGING_LEVEL=10
export GIT_SSL_NO_VERIFY=true

# NOTE: change `build_type=Debug` to `build_type=Release` in production
# NOTE: use --build=missing if you got error `ERROR: Missing prebuilt package`
cmake -E time \
  conan create . conan/stable \
  -s build_type=Debug -s cling_conan:build_type=Release \
  --profile clang \
      -o flex_support_headers:enable_clang_from_conan=False

# clean build cache
conan remove "*" --build --force
```
