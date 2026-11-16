"""Deterministic zero-CDN CSS compiler (WCAG AA/AAA Light+Dark themes + Tailwind utility subset) for ExploreALS v1.1 public web export."""
from __future__ import annotations

import re

PUBLIC_PREFLIGHT_AND_THEME_CSS = """:root, [data-theme="light"] {
  color-scheme: light;
  --background: #f8fafc;
  --content: #eef2f6;
  --card: #ffffff;
  --card-border: #e2e8f0;
  --border: #cbd5e1;
  --foreground: #0f172a;
  --muted-foreground: #475569;
  --primary: #1d4ed8;
  --primary-foreground: #ffffff;
  --link: #1d4ed8;
  --success: #166534;
  --warning: #92400e;
  --error: #b91c1c;
  --tw-ring-color: var(--primary);
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --background: #0b1120;
    --content: #172136;
    --card: #111827;
    --card-border: #1e293b;
    --border: #334155;
    --foreground: #f1f5f9;
    --muted-foreground: #94a3b8;
    --primary: #60a5fa;
    --primary-foreground: #08101d;
    --link: #60a5fa;
    --success: #34d399;
    --warning: #fbbf24;
    --error: #f87171;
    --tw-ring-color: var(--primary);
  }
}
[data-theme="dark"] {
  color-scheme: dark;
  --background: #0b1120;
  --content: #172136;
  --card: #111827;
  --card-border: #1e293b;
  --border: #334155;
  --foreground: #f1f5f9;
  --muted-foreground: #94a3b8;
  --primary: #60a5fa;
  --primary-foreground: #08101d;
  --link: #60a5fa;
  --success: #34d399;
  --warning: #fbbf24;
  --error: #f87171;
  --tw-ring-color: var(--primary);
}
*, *::before, *::after { box-sizing: border-box; border-width: 0; border-style: solid; border-color: var(--border); }
html { line-height: 1.5; -webkit-text-size-adjust: 100%; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
body { margin: 0; line-height: inherit; }
h1, h2, h3, h4, p, ul, ol { margin: 0; }
h1, h2, h3, h4 { font-size: inherit; font-weight: inherit; }
ul, ol { padding: 0; list-style: none; }
a { color: inherit; text-decoration: inherit; }
b, strong { font-weight: 600; }
button, input, select { font: inherit; color: inherit; margin: 0; padding: 0; background-color: transparent; }
button, select { text-transform: none; }
input::placeholder { color: var(--muted-foreground); opacity: 0.85; }
:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
details > summary.flex > span:first-child::before { content: "\\25B8\\00A0"; }
details[open] > summary.flex > span:first-child::before { content: "\\25BE\\00A0"; }
table { border-collapse: collapse; width:100%; text-indent: 0; border-color: inherit; }
th, td { padding: 6px 8px; vertical-align: top; }
input[type="range"] { accent-color: var(--primary); cursor: pointer; }
svg { display: block; vertical-align: middle; }"""

SPACE_REM = {
    "0": "0px", "px": "1px", "0.5": "0.125rem", "1": "0.25rem", "1.5": "0.375rem", "2": "0.5rem",
    "2.5": "0.625rem", "3": "0.75rem", "3.5": "0.875rem", "4": "1rem", "6": "1.5rem", "auto": "auto",
}
MEDIA_BP = {"sm": "640px", "md": "768px", "lg": "1024px", "xl": "1280px"}


def _esc_sel(cls: str) -> str:
    return "." + re.sub(r"([^A-Za-z0-9_-])", r"\\\1", cls)


def _rule_for_base(b: str) -> tuple[int, str, str]:
    """Return (priority_order, suffix_selector, declarations) or raise ValueError."""
    static_map: dict[str, tuple[int, str]] = {
        "kpi-btn": (1, ""), "tab-btn": (1, ""), "rep-mode-btn": (1, ""),
        "antialiased": (5, "-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale"),
        "block": (10, "display:block"), "inline-block": (10, "display:inline-block"),
        "flex": (10, "display:flex"), "grid": (10, "display:grid"), "table-cell": (10, "display:table-cell"),
        "hidden": (12, "display:none"),
        "relative": (14, "position:relative"), "absolute": (14, "position:absolute"), "sticky": (14, "position:sticky"),
        "top-0": (15, "top:0px"), "top-2": (15, "top:0.5rem"), "top-3": (15, "top:0.75rem"), "top-4": (15, "top:1rem"),
        "bottom-0": (15, "bottom:0px"), "left-0": (15, "left:0px"), "right-0": (15, "right:0px"), "inset-0": (15, "inset:0px"),
        "z-10": (16, "z-index:10"), "z-20": (16, "z-index:20"),
        "flex-1": (18, "flex:1 1 0%"), "flex-col": (18, "flex-direction:column"),
        "flex-wrap": (18, "flex-wrap:wrap"), "flex-nowrap": (18, "flex-wrap:nowrap"),
        "shrink-0": (18, "flex-shrink:0"),
        "items-start": (19, "align-items:flex-start"), "items-center": (19, "align-items:center"), "items-baseline": (19, "align-items:baseline"),
        "justify-between": (19, "justify-content:space-between"),
        "grid-cols-1": (20, "grid-template-columns:repeat(1,minmax(0,1fr))"),
        "grid-cols-2": (20, "grid-template-columns:repeat(2,minmax(0,1fr))"),
        "grid-cols-3": (20, "grid-template-columns:repeat(3,minmax(0,1fr))"),
        "grid-cols-4": (20, "grid-template-columns:repeat(4,minmax(0,1fr))"),
        "grid-cols-6": (20, "grid-template-columns:repeat(6,minmax(0,1fr))"),
        "grid-cols-12": (20, "grid-template-columns:repeat(12,minmax(0,1fr))"),
        "grid-cols-[228px_minmax(0,1fr)]": (20, "grid-template-columns:228px minmax(0,1fr)"),
        "w-full": (24, "width:100%"), "w-auto": (24, "width:auto"), "h-auto": (24, "height:auto"),
        "min-w-0": (25, "min-width:0px"), "min-h-0": (25, "min-height:0px"),
        "max-w-[1440px]": (26, "max-width:1440px"), "max-w-[260px]": (26, "max-width:260px"),
        "min-w-[140px]": (26, "min-width:140px"), "min-w-[180px]": (26, "min-width:180px"), "min-w-[200px]": (26, "min-width:200px"),
        "min-h-[520px]": (26, "min-height:520px"),
        "max-h-[290px]": (26, "max-height:290px"), "max-h-[420px]": (26, "max-height:420px"), "max-h-none": (27, "max-height:none"),
        "max-h-[68vh]": (26, "max-height:68vh"), "max-h-[74vh]": (26, "max-height:74vh"),
        "max-h-[calc(100vh-1.5rem)]": (26, "max-height:calc(100vh - 1.5rem)"),
        "overflow-hidden": (28, "overflow:hidden"), "overflow-x-auto": (28, "overflow-x:auto"), "overflow-y-auto": (28, "overflow-y:auto"),
        "truncate": (28, "overflow:hidden;text-overflow:ellipsis;white-space:nowrap"),
        "break-words": (28, "overflow-wrap:break-word"), "whitespace-nowrap": (28, "white-space:nowrap"),
        "list-disc": (29, "list-style-type:disc"),
        "rounded-sm": (40, "border-radius:0.125rem"), "rounded": (40, "border-radius:0.25rem"),
        "rounded-lg": (40, "border-radius:0.5rem"), "rounded-full": (40, "border-radius:9999px"),
        "border": (42, "border-width:1px"), "border-2": (43, "border-width:2px"),
        "border-t": (44, "border-top-width:1px"), "border-r": (44, "border-right-width:1px"), "border-b": (44, "border-bottom-width:1px"),
        "border-b-0": (45, "border-bottom-width:0px"), "border-l-2": (45, "border-left-width:2px"), "border-l-4": (45, "border-left-width:4px"),
        "border-dashed": (46, "border-style:dashed"), "border-collapse": (46, "border-collapse:collapse"),
        "font-mono": (55, 'font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace'),
        "text-xs": (56, "font-size:0.75rem;line-height:1rem"), "text-sm": (56, "font-size:0.875rem;line-height:1.25rem"),
        "text-base": (56, "font-size:1rem;line-height:1.5rem"), "text-lg": (56, "font-size:1.125rem;line-height:1.75rem"),
        "font-normal": (57, "font-weight:400"), "font-medium": (57, "font-weight:500"),
        "font-semibold": (57, "font-weight:600"), "font-bold": (57, "font-weight:700"), "italic": (57, "font-style:italic"),
        "leading-snug": (58, "line-height:1.375"), "leading-relaxed": (58, "line-height:1.625"),
        "tabular-nums": (58, "font-variant-numeric:tabular-nums"),
        "text-left": (59, "text-align:left"), "text-center": (59, "text-align:center"), "text-right": (59, "text-align:right"),
        "align-top": (59, "vertical-align:top"), "align-middle": (59, "vertical-align:middle"),
        "underline": (60, "text-decoration-line:underline"), "decoration-dotted": (61, "text-decoration-style:dotted"),
        "decoration-solid": (62, "text-decoration-style:solid"), "underline-offset-2": (61, "text-decoration-offset:2px;text-underline-offset:2px"),
        "opacity-40": (70, "opacity:0.4"), "opacity-45": (70, "opacity:0.45"), "opacity-80": (70, "opacity:0.8"),
        "shadow-sm": (72, "box-shadow:0 1px 2px 0 rgba(0,0,0,0.06)"),
        "ring-2": (73, "box-shadow:0 0 0 2px var(--tw-ring-color)"),
        "outline-none": (74, "outline:2px solid transparent;outline-offset:2px"),
        "transition": (75, "transition-property:color,background-color,border-color,box-shadow;transition-duration:150ms"),
        "rotate-45": (76, "transform:rotate(45deg)"),
        "cursor-pointer": (78, "cursor:pointer"), "cursor-help": (78, "cursor:help"),
        "select-none": (78, "user-select:none"), "pointer-events-none": (78, "pointer-events:none"),
        "divide-y": (80, "border-top-width:1px"),
    }
    if b in static_map:
        p, d = static_map[b]
        suf = " > :not([hidden]) ~ :not([hidden])" if b == "divide-y" else ""
        return p, suf, d
    if m := re.fullmatch(r"col-span-(\d+)", b):
        return 21, "", f"grid-column:span {m.group(1)} / span {m.group(1)}"
    if (m := re.fullmatch(r"(w|h)-(px|0\.5|1|1\.5|2|2\.5|3|4)", b)):
        prop = "width" if m.group(1) == "w" else "height"
        return 24, "", f"{prop}:{SPACE_REM[m.group(2)]}"
    if (m := re.fullmatch(r"gap(?:-(x|y))?-(0\.5|1|1\.5|2|2\.5|3)", b)):
        ax, v = m.group(1), SPACE_REM[m.group(2)]
        prop = "column-gap" if ax == "x" else ("row-gap" if ax == "y" else "gap")
        return (23 if ax else 22), "", f"{prop}:{v}"
    if (m := re.fullmatch(r"(p|m)(x|y|t|r|b|l)?-(0|0\.5|1|1\.5|2|2\.5|3|3\.5|4|6|auto)", b)):
        pm = "padding" if m.group(1) == "p" else "margin"
        side, v = m.group(2), SPACE_REM[m.group(3)]
        if not side:
            return 30, "", f"{pm}:{v}"
        if side in ("x", "y"):
            a, c = ("left", "right") if side == "x" else ("top", "bottom")
            return 31, "", f"{pm}-{a}:{v};{pm}-{c}:{v}"
        smap = {"t": "top", "r": "right", "b": "bottom", "l": "left"}
        return 32, "", f"{pm}-{smap[side]}:{v}"
    if (m := re.fullmatch(r"space-y-(0\.5|1|1\.5|2|2\.5|3|3\.5)", b)):
        v = SPACE_REM[m.group(1)]
        return 35, " > :not([hidden]) ~ :not([hidden])", f"margin-top:{v}"
    if (m := re.fullmatch(r"(bg|text|border|border-l|divide|accent|ring)-\[(var\(--[a-z-]+\))\]", b)):
        kind, var = m.group(1), m.group(2)
        if kind == "bg":
            return 50, "", f"background-color:{var}"
        if kind == "text":
            return 51, "", f"color:{var}"
        if kind == "border":
            return 47, "", f"border-color:{var}"
        if kind == "border-l":
            return 48, "", f"border-left-color:{var}"
        if kind == "divide":
            return 81, " > :not([hidden]) ~ :not([hidden])", f"border-color:{var}"
        if kind == "accent":
            return 77, "", f"accent-color:{var}"
        return 72, "", f"--tw-ring-color:{var}"
    raise ValueError(f"Unmapped Tailwind utility token in public web compiler: {b!r}")


def compile_public_css(class_tokens: set[str]) -> str:
    base_rules: list[tuple[int, str]] = []
    media_rules: dict[str, list[tuple[int, str]]] = {k: [] for k in MEDIA_BP}
    for tok in sorted(class_tokens):
        parts = tok.split(":")
        prefix = parts[0] if len(parts) == 2 else ""
        base = parts[-1]
        prio, suf, decl = _rule_for_base(base)
        if not decl:
            continue
        sel = _esc_sel(tok)
        if prefix in MEDIA_BP:
            media_rules[prefix].append((prio, f"  {sel}{suf} {{{decl}}}"))
        elif prefix in ("hover", "focus"):
            base_rules.append((prio + 100, f"{sel}:{prefix}{suf} {{{decl}}}"))
        elif prefix == "last":
            base_rules.append((prio + 100, f"{sel}:last-child{suf} {{{decl}}}"))
        elif not prefix:
            base_rules.append((prio, f"{sel}{suf} {{{decl}}}"))
        else:
            raise ValueError(f"Unsupported variant prefix in {tok!r}")
    lines = [PUBLIC_PREFLIGHT_AND_THEME_CSS.rstrip()]
    lines.extend(r for _, r in sorted(base_rules, key=lambda x: x[0]))
    for bp_k in ("sm", "md", "lg", "xl"):
        if media_rules[bp_k]:
            lines.append(f"@media (min-width: {MEDIA_BP[bp_k]}) {{")
            lines.extend(r for _, r in sorted(media_rules[bp_k], key=lambda x: x[0]))
            lines.append("}")
    return "\n".join(lines)
