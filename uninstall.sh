#!/usr/bin/env bash
set -euo pipefail

echo "=== hdmi-auto-scale uninstaller ==="

systemctl --user disable --now hdmi-scale-monitor.service 2>/dev/null || true

rm -f "$HOME/.local/scripts/hdmi-scale-monitor.sh"
rm -f "$HOME/.config/systemd/user/hdmi-scale-monitor.service"

systemctl --user daemon-reload

echo "Service removed."