#!/bin/sh

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y --no-install-recommends tesseract-ocr-deu

$MAYAN_PIP_BIN install -r ${MAYAN_INSTALL_DIR}/requirements-testing.txt

$MAYAN_BIN test --mayan-apps --settings=mayan.settings.testing
