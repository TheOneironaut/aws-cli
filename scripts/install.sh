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

# Generate completion command using local Python installation
if [ -n "$PROFILE_FILE" ]; then
  # Check if python3 is available
  if command -v python3 >/dev/null 2>&1; then
    # Install required packages temporarily for completion generation
    echo "Installing required packages temporarily for completion setup..."
    pip3 install --user boto3==1.40.13 click==8.1.7 >/dev/null 2>&1
    
    # Generate completion script using local Python
    cd "$REPO_DIR"
    COMPLETION_SCRIPT_CMD=$(_AWSCTL_COMPLETE=1 python3 main.py completion "$SHELL_TYPE" 2>/dev/null)
    
    # Clean up temporary packages
    pip3 uninstall -y boto3 click >/dev/null 2>&1
    
    if [ -n "$COMPLETION_SCRIPT_CMD" ] && ! grep -q "$COMPLETION_SCRIPT_CMD" "$PROFILE_FILE" 2>/dev/null; then
      echo "Adding completion to $PROFILE_FILE"
      echo "" >> "$PROFILE_FILE"
      echo "# awsctl completion" >> "$PROFILE_FILE"
      echo "$COMPLETION_SCRIPT_CMD" >> "$PROFILE_FILE"
      echo "Restart your shell or source your profile file to enable completion."
    elif [ -n "$COMPLETION_SCRIPT_CMD" ]; then
      echo "Completion already configured in $PROFILE_FILE"
    else
      echo "Could not generate completion script. Shell completion will not be available."
    fi
  else
    echo "Python3 not found. Skipping completion setup."
  fi
fi

echo "Installation complete. Try: awsctl --help"
