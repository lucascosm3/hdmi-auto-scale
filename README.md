# hdmi-auto-scale

Automatically adjust your laptop display scaling when an external HDMI monitor is plugged or unplugged — for **GNOME on X11** with fractional scaling.

Tested on a **Lenovo IdeaPad Flex 5 14ALC7** (Ryzen 5 5500U, 14" FHD IPS) running **Pop!_OS 22.04** with GNOME on X11.

## Why?

GNOME on X11 with fractional scaling (`x11-randr-fractional-scaling`) requires manual scale adjustment every time you plug or unplug an external monitor. If you use 125% on the laptop screen for readability, but need 100% when mirrored or side-by-side with a larger external display, you have to open Settings > Displays every single time.

This project automates that by watching HDMI hotplug events via `inotifywait` and applying the correct `xrandr` scale factor instantly.

## How it works

```
┌─────────────────────────────────────────────────────────┐
│  inotifywait watches /sys/class/drm/card*-HDMI-*/status │
│                         │                                │
│              ┌──────────┴──────────┐                     │
│              │  HDMI connected?     │                     │
│              └──────────┬──────────┘                     │
│                    ┌────┴────┐                            │
│                 YES          NO                           │
│                  │            │                            │
│          scale 1x1      scale 1.6x1.6                     │
│          (100%)         (GNOME "125%")                    │
└─────────────────────────────────────────────────────────┘
```

GNOME 125% fractional scaling on X11 uses `xrandr --scale 1.6x1.6` (transform factor 2/1.25), which produces a virtual resolution of 3072×1728 on a 1920×1080 panel. This is **not** 1.25×1.25 — the Mutter compositor applies a different transform internally.

## Requirements

- GNOME on **X11** (Wayland handles fractional scaling differently)
- `xrandr` (usually pre-installed)
- `inotify-tools` (install script handles this on Debian/Ubuntu)
- Bash ≥ 4

## Quick Install

```bash
git clone https://github.com/lucasleisival/hdmi-auto-scale.git
cd hdmi-auto-scale
./install.sh
```

The install script will:

1. Install `inotify-tools` via apt if missing
2. Copy `hdmi-scale-monitor.sh` to `~/.local/scripts/`
3. Copy and configure the systemd user service
4. Enable and start the service immediately

## Manual Install

```bash
# Install dependencies
sudo apt install inotify-tools

# Copy the script
mkdir -p ~/.local/scripts
cp hdmi-scale-monitor.sh ~/.local/scripts/
chmod +x ~/.local/scripts/hdmi-scale-monitor.sh

# Copy the systemd service
mkdir -p ~/.config/systemd/user/
cp hdmi-scale-monitor.service ~/.config/systemd/user/

# Replace %h with your home directory path in the service file
sed -i "s|%h|$HOME|g" ~/.config/systemd/user/hdmi-scale-monitor.service

# Enable and start
systemctl --user daemon-reload
systemctl --user enable --now hdmi-scale-monitor.service
```

## Configuration

All configuration is done via environment variables, which you can set in the systemd service override:

| Variable | Default | Description |
|---|---|---|
| `INTERNAL_DISPLAY` | `eDP-1` | Your laptop's internal display connector name |
| `SCALE_WITHOUT_HDMI` | `1.6x1.6` | Scale when no external monitor (GNOME 125%) |
| `SCALE_WITH_HDMI` | `1x1` | Scale when HDMI is connected (100%) |

### Finding your display name

```bash
xrandr --query | grep -E "^eDP|^DP|^LVDS"
```

### Overriding defaults

```bash
# Create a systemd override
systemctl --user edit hdmi-scale-monitor.service
```

Add your overrides:

```ini
[Service]
Environment="INTERNAL_DISPLAY=eDP-1"
Environment="SCALE_WITHOUT_HDMI=1.6x1.6"
Environment="SCALE_WITH_HDMI=1x1"
```

### monitors.xml (optional)

For a clean GNOME experience, you should also configure `~/.config/monitors.xml` to match your desired layouts. See [`monitors.xml.example`](monitors.xml.example) for a template — replace the vendor/product/serial values with your own (run `xrandr --query` to find them).

## Monitoring & Logs

```bash
# Check service status
systemctl --user status hdmi-scale-monitor.service

# View live logs
tail -f ~/.local/state/hdmi-auto-scale.log

# View journal
journalctl --user -u hdmi-scale-monitor.service -f
```

## Uninstall

```bash
./uninstall.sh
```

Or manually:

```bash
systemctl --user disable --now hdmi-scale-monitor.service
rm ~/.local/scripts/hdmi-scale-monitor.sh
rm ~/.config/systemd/user/hdmi-scale-monitor.service
systemctl --user daemon-reload
```

## Troubleshooting

### Scale doesn't apply on hotplug

- Verify the service is running: `systemctl --user status hdmi-scale-monitor.service`
- Check the log: `cat ~/.local/state/hdmi-auto-scale.log`
- Ensure you're on X11, not Wayland: `echo $XDG_SESSION_TYPE` should return `x11`
- If your HDMI appears on a different card, check: `ls /sys/class/drm/card*-HDMI-*/status`

### GNOME overrides my scale settings

- The script reacts after GNOME applies its own settings. There may be a brief flash as GNOME sets its scale, then this script corrects it.
- For a persistent solution, configure `~/.config/monitors.xml` to match your desired scales (see the example file).

### Wrong display detected

- Set `INTERNAL_DISPLAY` to match your connector name (check `xrandr --query`).

### The 1.6x1.6 scale looks wrong

- GNOME "125%" fractional scaling on X11 uses scale 1.6 (which is 2/1.25), not 1.25. If you use a different fractional scale, adjust `SCALE_WITHOUT_HDMI` accordingly:

  | GNOME Setting | xrandr Scale |
  |---|---|
  | 100% | 1x1 |
  | 125% | 1.6x1.6 |
  | 150% | 1.33x1.33 |
  | 175% | 1.14x1.14 |
  | 200% | 1x1 (doubles on its own) |

## How it works internally

1. **On startup**, the script immediately checks all HDMI status files and applies the correct scale.
2. **inotifywait** monitors all `/sys/class/drm/card*-HDMI-*/status` files for changes (hotplug events via kernel DRM subsystem).
3. **On change**, a 2-second debounce delay allows the kernel/hardware to settle, then the scale is applied via `xrandr`.
4. **The script runs as a systemd user service**, so it has access to the user's X11 display and Xauthority.

## Compatible Hardware

Developed and tested on:

- **Lenovo IdeaPad Flex 5 14ALC7** (Ryzen 5 5500U, 14" FHD 1920×1080 IPS)
- **LG HDR WFHD** (2560×1080 ultrawide via HDMI)

Should work on any GNOME + X11 setup with a laptop display (eDP) and HDMI output. If you use it on different hardware, feel free to open an issue or PR to add to this list.

## Contributing

Issues and pull requests welcome. If this works (or doesn't) on your hardware, let me know.

## License

[MIT](LICENSE)