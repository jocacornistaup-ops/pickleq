"""
styles.py
---------
Central place for PICKLEQ's minimal blue-and-white look, so every screen
stays visually consistent.
"""

import tkinter as tk
from tkinter import ttk

# Palette
NAVY = "#0D3B66"
BLUE = "#1565C0"
BLUE_LIGHT = "#4A90D9"
SKY = "#8EC5FC"
WHITE = "#FFFFFF"
OFF_WHITE = "#F4F8FC"
GREY_TEXT = "#5B6B79"
DANGER = "#D64550"
SUCCESS = "#2E9E5B"

FONT_FAMILY = "Segoe UI"


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb


def draw_vertical_gradient(canvas, width, height, color_top, color_bottom):
    """Paints a top-to-bottom gradient onto a Canvas widget."""
    canvas.delete("gradient")
    r1, g1, b1 = hex_to_rgb(color_top)
    r2, g2, b2 = hex_to_rgb(color_bottom)
    steps = max(height, 1)
    for i in range(steps):
        ratio = i / steps
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        color = rgb_to_hex((r, g, b))
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")
    canvas.tag_lower("gradient")


def apply_theme(root):
    """Configures ttk widgets to match the blue/white theme."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("TFrame", background=WHITE)
    style.configure("Card.TFrame", background=WHITE)

    style.configure(
        "TNotebook", background=OFF_WHITE, borderwidth=0, tabmargins=[10, 10, 10, 0]
    )
    style.configure(
        "TNotebook.Tab",
        background=OFF_WHITE,
        foreground=NAVY,
        padding=[16, 10],
        font=(FONT_FAMILY, 10, "bold"),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", BLUE)],
        foreground=[("selected", WHITE)],
    )

    style.configure(
        "Treeview",
        background=WHITE,
        fieldbackground=WHITE,
        foreground="#20313F",
        rowheight=28,
        font=(FONT_FAMILY, 10),
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=NAVY,
        foreground=WHITE,
        font=(FONT_FAMILY, 10, "bold"),
        relief="flat",
    )
    style.map("Treeview", background=[("selected", SKY)])

    style.configure(
        "Blue.TButton",
        background=BLUE,
        foreground=WHITE,
        font=(FONT_FAMILY, 10, "bold"),
        padding=[14, 8],
        borderwidth=0,
    )
    style.map("Blue.TButton", background=[("active", NAVY)])

    style.configure(
        "Outline.TButton",
        background=WHITE,
        foreground=BLUE,
        font=(FONT_FAMILY, 10, "bold"),
        padding=[14, 8],
        borderwidth=1,
    )
    style.map("Outline.TButton", background=[("active", OFF_WHITE)])

    style.configure(
        "Danger.TButton",
        background=DANGER,
        foreground=WHITE,
        font=(FONT_FAMILY, 10, "bold"),
        padding=[10, 6],
        borderwidth=0,
    )
    style.map("Danger.TButton", background=[("active", "#A83140")])

    return style


def rounded_entry(parent, textvariable, show=None, width=28):
    """A simple, clean-looking entry field used throughout the app."""
    entry = tk.Entry(
        parent,
        textvariable=textvariable,
        show=show,
        width=width,
        font=(FONT_FAMILY, 11),
        relief="flat",
        bg=OFF_WHITE,
        fg="#20313F",
        insertbackground=BLUE,
        highlightthickness=1,
        highlightbackground="#D7E3EE",
        highlightcolor=BLUE,
    )
    return entry
