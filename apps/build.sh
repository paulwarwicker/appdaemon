#! env bash

# PYTHON_VERSION=${1:-3.10.14}
PYTHON_VERSION=${1:-3.8.19}
BUILD_ARCH=$(uname -m)
BUILD_VERSION="0.0.1"
BUILD_DATE="$(date)"
BUILD_REF=$BUILD_VERSION

docker buildx build --build-arg PYTHON_VERSION="$PYTHON_VERSION" --build-arg BUILD_ARCH="$BUILD_ARCH" --build-arg BUILD_VERSION="$BUILD_VERSION" --build-arg BUILD_DATE="$BUILD_DATE" --build-arg BUILD_REF="$BUILD_REF" -t appdaemon-testing:"${BUILD_VERSION}-${PYTHON_VERSION}" .
