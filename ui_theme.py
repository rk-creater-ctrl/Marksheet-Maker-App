import tkinter as tk
from tkinter import ttk

from data_store import ASSETS_DIR


COLORS = {
    "bg": "#f7f9fc",
    "brand": "#102a43",
    "surface": "#ffffff",
    "surface_alt": "#f1f5f9",
    "border": "#d9e2ec",
    "text": "#172033",
    "muted": "#64748b",
    "primary": "#0f766e",
    "primary_dark": "#115e59",
    "primary_soft": "#ccfbf1",
    "secondary": "#4f46e5",
    "secondary_dark": "#3730a3",
    "secondary_soft": "#e0e7ff",
    "accent": "#f59e0b",
    "accent_dark": "#b45309",
    "accent_soft": "#fef3c7",
    "rose": "#e11d48",
    "rose_soft": "#ffe4e6",
    "success": "#15803d",
    "success_soft": "#dcfce7",
    "danger": "#b42318",
    "danger_soft": "#fee2e2",
    "info": "#0284c7",
    "info_soft": "#e0f2fe",
}


FONT = "Segoe UI"


def configure_style(root):
    root.configure(bg=COLORS["bg"])

    width = max(root.winfo_screenwidth(), 1)
    height = max(root.winfo_screenheight(), 1)
    scale = min(width / 1366, height / 768)
    root.tk.call("tk", "scaling", max(0.9, min(scale, 1.2)))

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", font=(FONT, 10), background=COLORS["bg"], foreground=COLORS["text"])
    style.configure("App.TFrame", background=COLORS["bg"])
    style.configure("Brand.TFrame", background=COLORS["brand"])
    style.configure("Surface.TFrame", background=COLORS["surface"])
    style.configure("Soft.TFrame", background=COLORS["surface_alt"])
    style.configure("PrimarySoft.TFrame", background=COLORS["primary_soft"])
    style.configure("SecondarySoft.TFrame", background=COLORS["secondary_soft"])
    style.configure("AccentSoft.TFrame", background=COLORS["accent_soft"])
    style.configure("InfoSoft.TFrame", background=COLORS["info_soft"])
    style.configure(
        "Card.TFrame",
        background=COLORS["surface"],
        borderwidth=1,
        relief="solid",
    )
    style.configure("TLabel", background=COLORS["surface"], foreground=COLORS["text"])
    style.configure("Muted.TLabel", background=COLORS["surface"], foreground=COLORS["muted"])
    style.configure("AppMuted.TLabel", background=COLORS["bg"], foreground=COLORS["muted"])
    style.configure("BrandTitle.TLabel", background=COLORS["brand"], foreground="#ffffff", font=(FONT, 22, "bold"))
    style.configure("BrandSubtitle.TLabel", background=COLORS["brand"], foreground="#cbd5e1")
    style.configure("Title.TLabel", background=COLORS["bg"], font=(FONT, 24, "bold"))
    style.configure("Hero.TLabel", background=COLORS["bg"], foreground=COLORS["brand"], font=(FONT, 30, "bold"))
    style.configure("Section.TLabel", background=COLORS["surface"], font=(FONT, 13, "bold"))
    style.configure("SoftSection.TLabel", background=COLORS["surface_alt"], font=(FONT, 13, "bold"))
    style.configure("Stat.TLabel", background=COLORS["surface"], font=(FONT, 20, "bold"))
    style.configure("PrimaryStat.TLabel", background=COLORS["primary_soft"], foreground=COLORS["primary_dark"], font=(FONT, 22, "bold"))
    style.configure("SecondaryStat.TLabel", background=COLORS["secondary_soft"], foreground=COLORS["secondary_dark"], font=(FONT, 22, "bold"))
    style.configure("AccentStat.TLabel", background=COLORS["accent_soft"], foreground=COLORS["accent_dark"], font=(FONT, 22, "bold"))
    style.configure("Success.TLabel", background=COLORS["surface"], foreground=COLORS["success"], font=(FONT, 12, "bold"))
    style.configure("Danger.TLabel", background=COLORS["surface"], foreground=COLORS["danger"], font=(FONT, 12, "bold"))
    style.configure("SuccessBadge.TLabel", background=COLORS["success_soft"], foreground=COLORS["success"], font=(FONT, 12, "bold"))
    style.configure("DangerBadge.TLabel", background=COLORS["danger_soft"], foreground=COLORS["danger"], font=(FONT, 12, "bold"))

    style.configure("TButton", font=(FONT, 10, "bold"), padding=(14, 8))
    style.configure("Primary.TButton", background=COLORS["primary"], foreground="#ffffff")
    style.map(
        "Primary.TButton",
        background=[("active", COLORS["primary_dark"]), ("disabled", "#9aa8b5")],
        foreground=[("disabled", "#eef3f8")],
    )
    style.configure("Secondary.TButton", background=COLORS["secondary"], foreground="#ffffff")
    style.map("Secondary.TButton", background=[("active", COLORS["secondary_dark"])])
    style.configure("Accent.TButton", background=COLORS["accent"], foreground="#111827")
    style.map("Accent.TButton", background=[("active", COLORS["accent_dark"])], foreground=[("active", "#ffffff")])
    style.configure("Danger.TButton", background=COLORS["danger_soft"], foreground=COLORS["danger"])
    style.configure("Ghost.TButton", background=COLORS["surface_alt"], foreground=COLORS["text"])

    style.configure("TEntry", fieldbackground="#ffffff", bordercolor=COLORS["border"], lightcolor=COLORS["border"])
    style.configure("TCombobox", fieldbackground="#ffffff", bordercolor=COLORS["border"], lightcolor=COLORS["border"])
    style.configure(
        "Treeview",
        rowheight=30,
        background=COLORS["surface"],
        fieldbackground=COLORS["surface"],
        foreground=COLORS["text"],
        bordercolor=COLORS["border"],
    )
    style.configure(
        "Treeview.Heading",
        background=COLORS["surface_alt"],
        foreground=COLORS["text"],
        font=(FONT, 10, "bold"),
    )
    style.map("Treeview", background=[("selected", COLORS["primary"])], foreground=[("selected", "#ffffff")])
    style.configure("TNotebook", background=COLORS["surface"], borderwidth=0)
    style.configure("TNotebook.Tab", padding=(16, 8), font=(FONT, 10, "bold"))
    style.configure("TLabelframe", background=COLORS["surface"], bordercolor=COLORS["border"])
    style.configure("TLabelframe.Label", background=COLORS["surface"], foreground=COLORS["text"], font=(FONT, 11, "bold"))

    return style


def maximize(root):
    root.geometry("1180x760")
    root.minsize(980, 660)
    try:
        root.state("zoomed")
    except tk.TclError:
        pass


def set_window_icon(root):
    icon_path = ASSETS_DIR / "app_icon.ico"
    if not icon_path.exists():
        return

    try:
        root.iconbitmap(str(icon_path))
    except tk.TclError:
        pass


def create_logo_mark(parent, size=72, background=None):
    bg = background or COLORS["brand"]
    scale = size / 72
    canvas = tk.Canvas(parent, width=size, height=size, bg=bg, highlightthickness=0)

    def s(value):
        return value * scale

    canvas.create_oval(s(4), s(4), s(68), s(68), fill=COLORS["primary_soft"], outline="#ffffff", width=max(1, int(s(2))))
    canvas.create_polygon(
        s(36), s(8),
        s(60), s(19),
        s(60), s(37),
        s(52), s(55),
        s(36), s(66),
        s(20), s(55),
        s(12), s(37),
        s(12), s(19),
        fill=COLORS["secondary"],
        outline=COLORS["secondary_dark"],
        width=max(1, int(s(1))),
    )
    canvas.create_polygon(
        s(36), s(14),
        s(54), s(22),
        s(54), s(37),
        s(48), s(50),
        s(36), s(58),
        s(24), s(50),
        s(18), s(37),
        s(18), s(22),
        fill=COLORS["primary"],
        outline="",
    )
    canvas.create_polygon(
        s(20), s(30),
        s(31), s(27),
        s(36), s(31),
        s(41), s(27),
        s(52), s(30),
        s(52), s(45),
        s(41), s(43),
        s(36), s(47),
        s(31), s(43),
        s(20), s(45),
        fill="#ffffff",
        outline="",
    )
    canvas.create_line(s(36), s(31), s(36), s(47), fill=COLORS["border"], width=max(1, int(s(2))))
    canvas.create_line(s(25), s(35), s(32), s(34), fill=COLORS["border"], width=max(1, int(s(2))))
    canvas.create_line(s(40), s(34), s(47), s(35), fill=COLORS["border"], width=max(1, int(s(2))))
    canvas.create_line(
        s(28), s(47),
        s(34), s(53),
        s(47), s(38),
        fill=COLORS["accent"],
        width=max(2, int(s(5))),
        capstyle="round",
        joinstyle="round",
    )
    return canvas
