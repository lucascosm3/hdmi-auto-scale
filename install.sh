#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== hdmi-auto-scale installer ==="

if ! command -v inotifywait &>/dev/null; then
    echo "inotifywait not found. Installing inotify-tools..."
    sudo apt install -y inotify-tools
fi

INSTALL_DIR="$HOME/.local/scripts"
mkdir -p "$INSTALL_DIR"

cp "$SCRIPT_DIR/hdmi-scale-monitor.sh" "$INSTALL_DIR/hdmi-scale-monitor.sh"
chmod +x "$INSTALL_DIR/hdmi-scale-monitor.sh"

SYSTEMD_DIR="$HOME/.config/systemd/user"
mkdir -p "$SYSTEMD_DIR"
cp "$SCRIPT_DIR/hdmi-scale-monitor.service" "$SYSTEMD_DIR/hdmi-scale-monitor.service"

sed -i "s|%h|$(echo "$HOME" | sed 's/\//\\\//g')|g" "$SYSTEMD_DIR/hdmi-scale-monitor.service"

systemctl --user daemon-reload
systemctl --user enable --now hdmi-scale-monitor.service

echo ""
echo "Service installed and started!"
echo "  Log: ${XDG_LOG_HOME:-$HOME/.local/state}/hdmi-auto-scale.log"
echo "  Status: systemctl --user status hdmi-scale-monitor.service"