#!/bin/bash

# ====== Установка игры "Demoniac" ======

# ------- АВТОР -------
# Putilin Daniil -> "Demoniac" v1.1.0
# https://github.com/Devilord-coder

# ----- ИНСТРУКЦИЯ -----
# Запустите этот файл с помощью sudo


# Ссылка на проект
APP_LINK="https://github.com/Devilord-coder/Demoniac"
DEST_DIR="~/Downloads"


echo "======= Starting installation ======="
echo ""

cd ~/Downloads
mkdir app_repo_clone
cd app_repo_clone
git clone "$APP_LINK"
cd Demoniac

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

pyinstaller Demoniac.spec
mv dist/Demoniac.app ~/Downloads

echo ""
echo "====================================="
echo "Succesfully installed Demoniac v1.1.0"