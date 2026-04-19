#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGFILE="${XDG_LOG_HOME:-$HOME/.local/state}/hdmi-auto-scale.log"
INTERNAL_DISPLAY="${INTERNAL_DISPLAY:-eDP-1}"

SCALE_WITHOUT_HDMI="${SCALE_WITHOUT_HDMI:-1.6x1.6}"
SCALE_WITH_HDMI="${SCALE_WITH_HDMI:-1x1}"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOGFILE"
}

get_display() {
    local d
    d=$(who 2>/dev/null | grep -m1 '(' | grep -oP ':\d+' | head -1)
    if [ -z "$d" ]; then
        d=$(ls /tmp/.X11-unix/ 2>/dev/null | head -1 | sed 's/X/:/')
    fi
    echo "${d:-:1}"
}

apply_scale() {
    local HDMI_CONNECTED=0
    for status_file in /sys/class/drm/card*-HDMI-*/status; do
        if [ -f "$status_file" ]; then
            local status
            status=$(cat "$status_file" 2>/dev/null || echo "")
            if [ "$status" = "connected" ]; then
                HDMI_CONNECTED=1
                break
            fi
        fi
    done

    local disp
    disp=$(get_display)
    log "DISPLAY=$disp HDMI=$HDMI_CONNECTED"

    if [ "$HDMI_CONNECTED" -eq 1 ]; then
        DISPLAY="$disp" XAUTHORITY="$HOME/.Xauthority" xrandr --output "$INTERNAL_DISPLAY" --scale "$SCALE_WITH_HDMI" 2>>"$LOGFILE" || true
        log "Applied scale $SCALE_WITH_HDMI (HDMI connected)"
    else
        DISPLAY="$disp" XAUTHORITY="$HOME/.Xauthority" xrandr --output "$INTERNAL_DISPLAY" --scale "$SCALE_WITHOUT_HDMI" 2>>"$LOGFILE" || true
        log "Applied scale $SCALE_WITHOUT_HDMI (no HDMI)"
    fi
}

apply_scale

HDMI_PATHS=()
for p in /sys/class/drm/card*-HDMI-*/status; do
    [ -f "$p" ] && HDMI_PATHS+=("$p")
done

if [ ${#HDMI_PATHS[@]} -eq 0 ]; then
    log "No HDMI sysfs paths found, exiting"
    exit 1
fi

inotifywait -m -e modify -e create -e delete "${HDMI_PATHS[@]}" 2>>"$LOGFILE" | while read -r path event; do
    sleep 2
    apply_scale
done