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

echo "Configuring shell completion..."
SHELL_TYPE=""
# Detect shell from the SHELL environment variable
if [ -n "$SHELL" ]; then
  SHELL_TYPE=$(basename "$SHELL")
fi

PROFILE_FILE=""
case "$SHELL_TYPE" in
  bash)
    PROFILE_FILE="$HOME/.bashrc"
    ;;
  zsh)
    PROFILE_FILE="$HOME/.zshrc"
    ;;
  fish)
    PROFILE_FILE="$HOME/.config/fish/config.fish"
    ;;
  *)
    echo "Could not detect shell. Skipping completion setup."
    ;;
esac


# Use python directly to generate the completion command, to avoid click Aborted error in docker context
if [ -n "$PROFILE_FILE" ]; then

  # Generate completion command using Docker so dependencies are available
  COMPLETION_SCRIPT_CMD=$(docker run --rm -v "$REPO_DIR:/app" -w /app awsctl:latest python main.py completion "$SHELL_TYPE")

  if ! grep -q "$COMPLETION_SCRIPT_CMD" "$PROFILE_FILE" 2>/dev/null; then
    echo "Adding completion to $PROFILE_FILE"
    echo "" >> "$PROFILE_FILE"
    echo "# awsctl completion" >> "$PROFILE_FILE"
    echo "$COMPLETION_SCRIPT_CMD" >> "$PROFILE_FILE"
    echo "Restart your shell or source your profile file to enable completion."
  else
    echo "Completion already configured in $PROFILE_FILE"
  fi
fi

echo "Installation complete. Try: awsctl --help"
