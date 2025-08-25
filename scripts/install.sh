#!/usr/bin/env bash
set -euo pipefail

REPO_DEFAULT="https://github.com/TheOneironaut/aws-cli.git"
REPO="${1:-$REPO_DEFAULT}"
INSTALL_DIR_DEFAULT="$HOME/.awsctl/aws-cli"
INSTALL_DIR="${2:-$INSTALL_DIR_DEFAULT}"
BIN_DIR_DEFAULT="/usr/local/bin"
BIN_DIR="${3:-$BIN_DIR_DEFAULT}"

ensure_dir() {
  mkdir -p "$1"
}

# If we run from inside the repo, use current dir; else clone/update
if [ -f "Dockerfile" ] && [ -f "main.py" ]; then
  REPO_DIR="$(pwd)"
else
  ensure_dir "$(dirname "$INSTALL_DIR")"
  if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Updating existing repo at $INSTALL_DIR"
    git -C "$INSTALL_DIR" pull --rebase
  else
    echo "Cloning $REPO to $INSTALL_DIR"
    git clone "$REPO" "$INSTALL_DIR"
  fi
  REPO_DIR="$INSTALL_DIR"
fi

echo "Building Docker image awsctl:latest"
docker build -t awsctl:latest "$REPO_DIR"

ensure_dir "$BIN_DIR"
cp "$REPO_DIR/scripts/awsctl" "$BIN_DIR/awsctl"
chmod +x "$BIN_DIR/awsctl"

echo "Installation complete. Try: awsctl --help"
