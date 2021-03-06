#!/bin/bash

set -e

essarch settings generate --debug -q --no-overwrite
essarch install -q

echo "Installing profiles"
python ESSArch_Core/install/install_profiles_se.py
python ESSArch_Core/install/install_profiles_no.py
python ESSArch_Core/install/install_profiles_eark.py

echo "Starting server"
python manage.py runserver 0:8000
