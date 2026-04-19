#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1200, 675

FONT_DIR = "/usr/share/fonts/truetype/ubuntu/"
FONT_REGULAR = os.path.join(FONT_DIR, "Ubuntu-C.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "Ubuntu-B.ttf")
FONT_MONO = "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf"

BG = "#2c2c2c"
TOPBAR = "#1a1a1a"
PANEL_BG = "#333333"
TEXT_WHITE = "#ffffff"
TEXT_GRAY = "#aaaaaa"
ACCENT = "#4a90d9"
DESKTOP_GREEN = "#3a6b3a"

ICON_COLORS = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]


def make_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def draw_icon(draw, x, y, size, color, label, font):
    draw.rounded_rectangle([x, y, x + size, y + size], radius=8, fill=color)
    draw.text((x + size // 2, y + size + 4), label, fill=TEXT_WHITE, font=font, anchor="mt")


def draw_topbar(draw, label, font_label, font_clock, scale_label):
    draw.rectangle([0, 0, W, 28], fill=TOPBAR)
    draw.text((15, 14), "Activities", fill=TEXT_WHITE, font=font_label, anchor="lm")
    draw.text((W // 2, 14), label, fill=TEXT_WHITE, font=font_label, anchor="lm")
    draw.text((W - 15, 14), "14:32", fill=TEXT_WHITE, font=font_clock, anchor="rm")
    badge_w = 120
    draw.rounded_rectangle([W - 170, 4, W - 170 + badge_w, 24], radius=4, fill="#e74c3c" if "125%" in scale_label else "#2ecc71")
    draw.text((W - 170 + badge_w // 2, 14), scale_label, fill="#ffffff", font=font_label, anchor="mm")


def draw_taskbar(draw, font):
    tb_h = 48
    draw.rectangle([0, H - tb_h, W, H], fill=PANEL_BG)
    icons_x = [W // 2 - 80, W // 2, W // 2 + 80]
    labels = ["Files", "Firefox", "Terminal"]
    colors = ["#e74c3c", "#3498db", "#2ecc71"]
    for ix, (cx, lbl, col) in enumerate(zip(icons_x, labels, colors)):
        draw.ellipse([cx - 12, H - tb_h + 8, cx + 12, H - tb_h + 32], fill=col)
        draw.text((cx, H - tb_h + 36), lbl, fill=TEXT_WHITE, font=font, anchor="mt")


def draw_window(draw, x, y, w, h, title, font_title, content_lines, font_content, scale_factor=1.0):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=6, fill="#353535", outline="#555555")
    draw.rectangle([x + 1, y + 1, x + w - 1, y + 26], fill="#454545")
    for i, c in enumerate(["#e74c3c", "#f39c12", "#2ecc71"]):
        draw.ellipse([x + 12 + i * 18, y + 8, x + 12 + i * 18 + 10, y + 8 + 10], fill=c)
    draw.text((x + w // 2, y + 14), title, fill=TEXT_WHITE, font=font_title, anchor="mm")
    ty = y + 36
    for line in content_lines:
        draw.text((x + 14, ty), line, fill="#cccccc", font=font_content)
        ty += int(18 * scale_factor)


def draw_connector(draw, font, connected):
    x_conn = W - 180
    y_conn = 45
    draw.rounded_rectangle([x_conn, y_conn, W - 30, y_conn + 55], radius=8, fill="#1a1a2e", outline="#555555")
    if connected:
        draw.rounded_rectangle([x_conn + 6, y_conn + 6, W - 36, y_conn + 49], radius=4, fill="#1a3a1a", outline="#4a90d9")
        draw.text((x_conn + 70, y_conn + 16), "HDMI", fill="#4a90d9", font=font, anchor="mm")
        draw.ellipse([x_conn + 15, y_conn + 12, x_conn + 27, y_conn + 24], fill="#2ecc71")
        draw.text((x_conn + 70, y_conn + 38), "Connected", fill="#2ecc71", font=font, anchor="mm")
    else:
        draw.rounded_rectangle([x_conn + 6, y_conn + 6, W - 36, y_conn + 49], radius=4, fill="#2a1a1a", outline="#555555")
        draw.text((x_conn + 70, y_conn + 16), "HDMI", fill="#888888", font=font, anchor="mm")
        draw.text((x_conn + 70, y_conn + 38), "Disconnected", fill="#e74c3c", font=font, anchor="mm")


def draw_notification(draw, font, text, y_offset=50):
    nx = W // 2 - 140
    ny = y_offset
    nw, nh = 280, 36
    draw.rounded_rectangle([nx, ny, nx + nw, ny + nh], radius=8, fill="#353535", outline="#4a90d9")
    draw.text((nx + nw // 2, ny + nh // 2), text, fill=TEXT_WHITE, font=font, anchor="mm")


def create_frame(scale_mode, connected, show_notification=None):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    if scale_mode == "125":
        scale = 1.25
        scale_str = "Scale 125%"
        icon_size = 68
        icon_font_size = 14
        lbl = "Notebook (eDP-1)"
    else:
        scale = 1.0
        scale_str = "Scale 100%"
        icon_size = 48
        icon_font_size = 11
        lbl = "Notebook + Monitor"

    font_topbar = make_font(FONT_REGULAR, 12)
    font_topbar_clk = make_font(FONT_REGULAR, 12)
    font_icon = make_font(FONT_BOLD, icon_font_size)
    font_window_title = make_font(FONT_BOLD, 12)
    font_window_content = make_font(FONT_MONO, 11)
    font_conn = make_font(FONT_REGULAR, 13)
    font_notif = make_font(FONT_BOLD, 13)
    font_taskbar = make_font(FONT_REGULAR, 10)

    draw_topbar(draw, lbl, font_topbar, font_topbar_clk, scale_str)

    cols = 6
    start_x = 60
    start_y = 70
    spacing_x = int(160 * scale)
    spacing_y = int(140 * scale)

    icon_labels = ["Files", "Firefox", "Terminal", "Settings", "Discord", "VS Code"]
    for idx, (color, label) in enumerate(zip(ICON_COLORS, icon_labels)):
        col = idx % cols
        row = idx // cols
        ix = start_x + col * spacing_x
        iy = start_y + row * spacing_y
        draw_icon(draw, ix, iy, icon_size, color, label, font_icon)

    if scale == 1.0:
        win_x, win_y = 40, 340
        win_w, win_h = 560, 230
        draw_window(
            draw, win_x, win_y, win_w, win_h, "Terminal",
            font_window_title,
            ["$ xrandr --query | grep -E 'eDP|HDMI'",
             "eDP-1 connected primary 1920x1080",
             "HDMI-1 connected 2560x1080",
             "$# hdmi-auto-scale: scale 1x1 applied"],
            font_window_content, scale_factor=1.0
        )
    else:
        win_x, win_y = 40, 380
        win_w, win_h = int(580 * 1.1), int(200 * 1.1)
        draw_window(
            draw, win_x, win_y, win_w, win_h, "Terminal",
            font_window_title,
            ["$ xrandr --query | grep -E 'eDP'",
             "eDP-1 connected primary 1920x1080",
             "HDMI-1 disconnected",
             "$# hdmi-auto-scale: scale 1.6x1.6 applied"],
            font_window_content, scale_factor=scale
        )

    draw_connector(draw, font_conn, connected)
    draw_taskbar(draw, font_taskbar)

    if show_notification:
        draw_notification(draw, font_notif, show_notification)

    return img


def main():
    frames = []

    n_pause = 30
    n_transition = 10

    for _ in range(n_pause):
        frames.append(create_frame("125", False, show_notification="Sem HDMI - Escala 125%"))

    for i in range(n_transition):
        frames.append(create_frame("125", False, show_notification="HDMI conectado detectado!"))

    for _ in range(n_pause):
        frames.append(create_frame("100", True, show_notification="Com HDMI - Escala 100%"))

    for i in range(n_transition):
        frames.append(create_frame("100", True, show_notification="HDMI desconectado!"))

    for _ in range(n_pause):
        frames.append(create_frame("125", False, show_notification="Sem HDMI - Escala 125%"))

    out = "/home/lucas/hdmi-auto-scale/demo.gif"
    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=80,
        loop=0,
        optimize=True,
    )
    print(f"GIF salvo em {out} ({os.path.getsize(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()