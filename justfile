set windows-shell := ["powershell.exe", "-c"]

export SEP := if os() == "windows" { ";" } else { ":" }
export PY := if os() == "windows" { "python" } else { "python3" }

# list recipes
default:
    just --list

# run game
run:
    {{ PY }} main.py

# build game
build:
    {{ PY }} -m PyInstaller --onefile --add-data "assets{{ SEP }}assets" --add-data "const{{ SEP }}const" --add-data "src{{ SEP }}src" main.py --name "Central Defense"
