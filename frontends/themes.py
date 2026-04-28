"""
GenericAgent Theme Engine
6 complete color schemes for web (CSS variables) and desktop (Tkinter ttk).
Each theme defines a full palette affecting every UI element, not just fg/bg.
"""

from __future__ import annotations
from typing import Dict, Any
from dataclasses import dataclass, field


@dataclass
class ThemeColors:
    name: str
    label: str
    description: str

    page_bg: str
    container_bg: str
    surface_bg: str
    elevated_bg: str
    hover_bg: str
    active_bg: str

    text_primary: str
    text_secondary: str
    text_tertiary: str
    text_muted: str
    text_inverse: str

    accent_primary: str
    accent_hover: str
    accent_muted: str
    accent_text: str

    border_default: str
    border_focus: str
    border_subtle: str
    divider: str

    input_bg: str
    input_border: str
    input_focus_border: str
    input_placeholder: str

    btn_primary_bg: str
    btn_primary_hover: str
    btn_primary_text: str
    btn_secondary_bg: str
    btn_secondary_hover: str
    btn_secondary_text: str
    btn_ghost_hover: str
    btn_danger_bg: str
    btn_danger_hover: str

    chat_user_bg: str
    chat_user_border: str
    chat_user_text: str
    chat_agent_bg: str
    chat_agent_border: str
    chat_agent_text: str

    code_bg: str
    code_border: str
    code_text: str
    code_keyword: str
    code_string: str
    code_comment: str
    code_number: str
    code_function: str

    success: str
    success_bg: str
    warning: str
    warning_bg: str
    error: str
    error_bg: str
    info: str
    info_bg: str

    scrollbar_thumb: str
    scrollbar_track: str
    scrollbar_hover: str

    shadow_sm: str
    shadow_md: str
    shadow_lg: str
    shadow_xl: str

    tooltip_bg: str
    tooltip_text: str
    badge_bg: str
    badge_text: str

    link_color: str
    link_hover: str
    selection_bg: str
    selection_text: str

    titlebar_bg: str
    titlebar_border: str
    titlebar_text: str

    sidebar_bg: str
    sidebar_border: str
    sidebar_text: str
    sidebar_hover: str
    sidebar_active: str

    icon_color: str
    icon_hover: str

    overlay_bg: str
    skeleton_bg: str
    skeleton_shimmer: str


TRAE_DARK: ThemeColors = ThemeColors(
    name="trae_dark",
    label="Solo Dark",
    description="Trae SOLO original – deep-space black with indigo accents",

    page_bg="#09090d",
    container_bg="#0f0f17",
    surface_bg="#161622",
    elevated_bg="#1c1c2c",
    hover_bg="#222236",
    active_bg="#282840",

    text_primary="#e8e8f0",
    text_secondary="#9898b8",
    text_tertiary="#6a6a8a",
    text_muted="#48486a",
    text_inverse="#0f0f17",

    accent_primary="#6366f1",
    accent_hover="#818cf8",
    accent_muted="rgba(99,102,241,0.15)",
    accent_text="#c7d2fe",

    border_default="#2a2a3c",
    border_focus="#6366f1",
    border_subtle="#1e1e30",
    divider="#1e1e32",

    input_bg="#13131f",
    input_border="#2a2a3c",
    input_focus_border="#6366f1",
    input_placeholder="#5a5a7a",

    btn_primary_bg="#6366f1",
    btn_primary_hover="#5558e8",
    btn_primary_text="#ffffff",
    btn_secondary_bg="#1c1c2c",
    btn_secondary_hover="#252538",
    btn_secondary_text="#9898b8",
    btn_ghost_hover="rgba(99,102,241,0.08)",
    btn_danger_bg="#dc2626",
    btn_danger_hover="#b91c1c",

    chat_user_bg="#1c1c2c",
    chat_user_border="#2a2a3c",
    chat_user_text="#e8e8f0",
    chat_agent_bg="#12121e",
    chat_agent_border="#1e1e32",
    chat_agent_text="#e8e8f0",

    code_bg="#0d0d1a",
    code_border="#1e1e32",
    code_text="#e8e8f0",
    code_keyword="#c084fc",
    code_string="#6ee7b7",
    code_comment="#5a5a6a",
    code_number="#f9a8d4",
    code_function="#818cf8",

    success="#22c55e",
    success_bg="rgba(34,197,94,0.10)",
    warning="#f59e0b",
    warning_bg="rgba(245,158,11,0.10)",
    error="#ef4444",
    error_bg="rgba(239,68,68,0.10)",
    info="#3b82f6",
    info_bg="rgba(59,130,246,0.10)",

    scrollbar_thumb="#2a2a3c",
    scrollbar_track="#0f0f17",
    scrollbar_hover="#3a3a50",

    shadow_sm="0 1px 2px rgba(0,0,0,0.4)",
    shadow_md="0 4px 8px rgba(0,0,0,0.5)",
    shadow_lg="0 8px 24px rgba(0,0,0,0.6)",
    shadow_xl="0 16px 48px rgba(0,0,0,0.7)",

    tooltip_bg="#1c1c2c",
    tooltip_text="#e8e8f0",
    badge_bg="rgba(99,102,241,0.15)",
    badge_text="#818cf8",

    link_color="#818cf8",
    link_hover="#a5b4fc",
    selection_bg="rgba(99,102,241,0.30)",
    selection_text="#ffffff",

    titlebar_bg="#0d0d15",
    titlebar_border="#1e1e32",
    titlebar_text="#e8e8f0",

    sidebar_bg="#0d0d15",
    sidebar_border="#1e1e32",
    sidebar_text="#9898b8",
    sidebar_hover="#181828",
    sidebar_active="rgba(99,102,241,0.12)",

    icon_color="#9898b8",
    icon_hover="#e8e8f0",

    overlay_bg="rgba(0,0,0,0.7)",
    skeleton_bg="#1c1c2c",
    skeleton_shimmer="#2a2a3c",
)


MIDNIGHT: ThemeColors = ThemeColors(
    name="midnight",
    label="Midnight Blue",
    description="Deep navy palette with cyan highlights – calm and focused",

    page_bg="#0b1120",
    container_bg="#111827",
    surface_bg="#1a2744",
    elevated_bg="#1f3056",
    hover_bg="#243b64",
    active_bg="#2a4478",

    text_primary="#e2e8f0",
    text_secondary="#94a3b8",
    text_tertiary="#64748b",
    text_muted="#475569",
    text_inverse="#0b1120",

    accent_primary="#06b6d4",
    accent_hover="#22d3ee",
    accent_muted="rgba(6,182,212,0.15)",
    accent_text="#a5f3fc",

    border_default="#1e3a5f",
    border_focus="#06b6d4",
    border_subtle="#152644",
    divider="#152644",

    input_bg="#0f1d34",
    input_border="#1e3a5f",
    input_focus_border="#06b6d4",
    input_placeholder="#506080",

    btn_primary_bg="#0e7490",
    btn_primary_hover="#0891b2",
    btn_primary_text="#ffffff",
    btn_secondary_bg="#1a2744",
    btn_secondary_hover="#1f3056",
    btn_secondary_text="#94a3b8",
    btn_ghost_hover="rgba(6,182,212,0.08)",
    btn_danger_bg="#b91c1c",
    btn_danger_hover="#991b1b",

    chat_user_bg="#1a2744",
    chat_user_border="#1e3a5f",
    chat_user_text="#e2e8f0",
    chat_agent_bg="#111b33",
    chat_agent_border="#152644",
    chat_agent_text="#e2e8f0",

    code_bg="#091424",
    code_border="#152644",
    code_text="#e2e8f0",
    code_keyword="#67e8f9",
    code_string="#86efac",
    code_comment="#475569",
    code_number="#fda4af",
    code_function="#7dd3fc",

    success="#10b981",
    success_bg="rgba(16,185,129,0.10)",
    warning="#f59e0b",
    warning_bg="rgba(245,158,11,0.10)",
    error="#ef4444",
    error_bg="rgba(239,68,68,0.10)",
    info="#06b6d4",
    info_bg="rgba(6,182,212,0.10)",

    scrollbar_thumb="#1e3a5f",
    scrollbar_track="#0b1120",
    scrollbar_hover="#2a4a78",

    shadow_sm="0 1px 2px rgba(0,0,0,0.4)",
    shadow_md="0 4px 8px rgba(0,0,0,0.5)",
    shadow_lg="0 8px 24px rgba(0,0,0,0.6)",
    shadow_xl="0 16px 48px rgba(0,0,0,0.7)",

    tooltip_bg="#1a2744",
    tooltip_text="#e2e8f0",
    badge_bg="rgba(6,182,212,0.15)",
    badge_text="#22d3ee",

    link_color="#22d3ee",
    link_hover="#67e8f9",
    selection_bg="rgba(6,182,212,0.30)",
    selection_text="#ffffff",

    titlebar_bg="#0a1328",
    titlebar_border="#152644",
    titlebar_text="#e2e8f0",

    sidebar_bg="#0a1328",
    sidebar_border="#152644",
    sidebar_text="#94a3b8",
    sidebar_hover="#162240",
    sidebar_active="rgba(6,182,212,0.12)",

    icon_color="#94a3b8",
    icon_hover="#e2e8f0",

    overlay_bg="rgba(0,0,0,0.7)",
    skeleton_bg="#1a2744",
    skeleton_shimmer="#1f3056",
)


FOREST: ThemeColors = ThemeColors(
    name="forest",
    label="Forest",
    description="Rich green tones – organic, calm, and grounded",

    page_bg="#071208",
    container_bg="#0d1f0f",
    surface_bg="#142a15",
    elevated_bg="#19331b",
    hover_bg="#1e3d21",
    active_bg="#244727",

    text_primary="#d1e8d2",
    text_secondary="#81a984",
    text_tertiary="#5a7a5d",
    text_muted="#3d553f",
    text_inverse="#071208",

    accent_primary="#22c55e",
    accent_hover="#4ade80",
    accent_muted="rgba(34,197,94,0.15)",
    accent_text="#bbf7d0",

    border_default="#1e3d21",
    border_focus="#22c55e",
    border_subtle="#132913",
    divider="#132913",

    input_bg="#0b1a0c",
    input_border="#1e3d21",
    input_focus_border="#22c55e",
    input_placeholder="#4a6a4d",

    btn_primary_bg="#15803d",
    btn_primary_hover="#16a34a",
    btn_primary_text="#ffffff",
    btn_secondary_bg="#142a15",
    btn_secondary_hover="#19331b",
    btn_secondary_text="#81a984",
    btn_ghost_hover="rgba(34,197,94,0.08)",
    btn_danger_bg="#b91c1c",
    btn_danger_hover="#991b1b",

    chat_user_bg="#142a15",
    chat_user_border="#1e3d21",
    chat_user_text="#d1e8d2",
    chat_agent_bg="#0d1a0e",
    chat_agent_border="#132913",
    chat_agent_text="#d1e8d2",

    code_bg="#051006",
    code_border="#132913",
    code_text="#d1e8d2",
    code_keyword="#86efac",
    code_string="#6ee7b7",
    code_comment="#3d553f",
    code_number="#f9a8d4",
    code_function="#4ade80",

    success="#22c55e",
    success_bg="rgba(34,197,94,0.10)",
    warning="#d97706",
    warning_bg="rgba(217,119,6,0.10)",
    error="#dc2626",
    error_bg="rgba(220,38,38,0.10)",
    info="#15803d",
    info_bg="rgba(21,128,61,0.10)",

    scrollbar_thumb="#1e3d21",
    scrollbar_track="#0d1f0f",
    scrollbar_hover="#2a5030",

    shadow_sm="0 1px 2px rgba(0,0,0,0.4)",
    shadow_md="0 4px 8px rgba(0,0,0,0.5)",
    shadow_lg="0 8px 24px rgba(0,0,0,0.6)",
    shadow_xl="0 16px 48px rgba(0,0,0,0.7)",

    tooltip_bg="#142a15",
    tooltip_text="#d1e8d2",
    badge_bg="rgba(34,197,94,0.15)",
    badge_text="#4ade80",

    link_color="#4ade80",
    link_hover="#86efac",
    selection_bg="rgba(34,197,94,0.30)",
    selection_text="#ffffff",

    titlebar_bg="#091408",
    titlebar_border="#132913",
    titlebar_text="#d1e8d2",

    sidebar_bg="#091408",
    sidebar_border="#132913",
    sidebar_text="#81a984",
    sidebar_hover="#111f12",
    sidebar_active="rgba(34,197,94,0.12)",

    icon_color="#81a984",
    icon_hover="#d1e8d2",

    overlay_bg="rgba(0,0,0,0.7)",
    skeleton_bg="#142a15",
    skeleton_shimmer="#1e3d21",
)


SUNSET: ThemeColors = ThemeColors(
    name="sunset",
    label="Sunset",
    description="Warm rose and amber hues – creative and energetic",

    page_bg="#1a0f14",
    container_bg="#24151a",
    surface_bg="#331e26",
    elevated_bg="#3d2430",
    hover_bg="#472a38",
    active_bg="#533040",

    text_primary="#fce4ec",
    text_secondary="#d4a0b8",
    text_tertiary="#9e6e82",
    text_muted="#6e4a58",
    text_inverse="#1a0f14",

    accent_primary="#f472b6",
    accent_hover="#f9a8d4",
    accent_muted="rgba(244,114,182,0.15)",
    accent_text="#fce7f3",

    border_default="#3d2430",
    border_focus="#f472b6",
    border_subtle="#2b1722",
    divider="#2b1722",

    input_bg="#1c1016",
    input_border="#3d2430",
    input_focus_border="#f472b6",
    input_placeholder="#6e4a58",

    btn_primary_bg="#be185d",
    btn_primary_hover="#db2777",
    btn_primary_text="#ffffff",
    btn_secondary_bg="#331e26",
    btn_secondary_hover="#3d2430",
    btn_secondary_text="#d4a0b8",
    btn_ghost_hover="rgba(244,114,182,0.08)",
    btn_danger_bg="#991b1b",
    btn_danger_hover="#7f1d1d",

    chat_user_bg="#331e26",
    chat_user_border="#3d2430",
    chat_user_text="#fce4ec",
    chat_agent_bg="#1f1217",
    chat_agent_border="#2b1722",
    chat_agent_text="#fce4ec",

    code_bg="#120a0f",
    code_border="#2b1722",
    code_text="#fce4ec",
    code_keyword="#f9a8d4",
    code_string="#6ee7b7",
    code_comment="#6e4a58",
    code_number="#fcd34d",
    code_function="#f472b6",

    success="#4ade80",
    success_bg="rgba(74,222,128,0.10)",
    warning="#fbbf24",
    warning_bg="rgba(251,191,36,0.10)",
    error="#f87171",
    error_bg="rgba(248,113,113,0.10)",
    info="#f472b6",
    info_bg="rgba(244,114,182,0.10)",

    scrollbar_thumb="#3d2430",
    scrollbar_track="#1a0f14",
    scrollbar_hover="#533040",

    shadow_sm="0 1px 2px rgba(0,0,0,0.4)",
    shadow_md="0 4px 8px rgba(0,0,0,0.5)",
    shadow_lg="0 8px 24px rgba(0,0,0,0.6)",
    shadow_xl="0 16px 48px rgba(0,0,0,0.7)",

    tooltip_bg="#331e26",
    tooltip_text="#fce4ec",
    badge_bg="rgba(244,114,182,0.15)",
    badge_text="#f9a8d4",

    link_color="#f9a8d4",
    link_hover="#fce7f3",
    selection_bg="rgba(244,114,182,0.30)",
    selection_text="#ffffff",

    titlebar_bg="#140c10",
    titlebar_border="#2b1722",
    titlebar_text="#fce4ec",

    sidebar_bg="#140c10",
    sidebar_border="#2b1722",
    sidebar_text="#d4a0b8",
    sidebar_hover="#1d1116",
    sidebar_active="rgba(244,114,182,0.12)",

    icon_color="#d4a0b8",
    icon_hover="#fce4ec",

    overlay_bg="rgba(0,0,0,0.7)",
    skeleton_bg="#331e26",
    skeleton_shimmer="#3d2430",
)


LIGHT: ThemeColors = ThemeColors(
    name="light",
    label="Light Paper",
    description="Clean, bright, paper-like – maximum readability",

    page_bg="#f8f9fa",
    container_bg="#ffffff",
    surface_bg="#f1f3f5",
    elevated_bg="#ffffff",
    hover_bg="#e9ecef",
    active_bg="#dee2e6",

    text_primary="#1a1b1e",
    text_secondary="#5c5f66",
    text_tertiary="#868e96",
    text_muted="#adb5bd",
    text_inverse="#ffffff",

    accent_primary="#4263eb",
    accent_hover="#5c7cfa",
    accent_muted="rgba(66,99,235,0.10)",
    accent_text="#dbe4ff",

    border_default="#dee2e6",
    border_focus="#4263eb",
    border_subtle="#e9ecef",
    divider="#e9ecef",

    input_bg="#ffffff",
    input_border="#dee2e6",
    input_focus_border="#4263eb",
    input_placeholder="#adb5bd",

    btn_primary_bg="#4263eb",
    btn_primary_hover="#3b5bdb",
    btn_primary_text="#ffffff",
    btn_secondary_bg="#f1f3f5",
    btn_secondary_hover="#e9ecef",
    btn_secondary_text="#1a1b1e",
    btn_ghost_hover="rgba(66,99,235,0.06)",
    btn_danger_bg="#e03131",
    btn_danger_hover="#c92a2a",

    chat_user_bg="#e7f5ff",
    chat_user_border="#bee0f5",
    chat_user_text="#1a1b1e",
    chat_agent_bg="#ffffff",
    chat_agent_border="#dee2e6",
    chat_agent_text="#1a1b1e",

    code_bg="#f1f3f5",
    code_border="#dee2e6",
    code_text="#1a1b1e",
    code_keyword="#7c3aed",
    code_string="#059669",
    code_comment="#868e96",
    code_number="#e64980",
    code_function="#4263eb",

    success="#2b8a3e",
    success_bg="rgba(43,138,62,0.08)",
    warning="#e67700",
    warning_bg="rgba(230,119,0,0.08)",
    error="#c92a2a",
    error_bg="rgba(201,42,42,0.08)",
    info="#1971c2",
    info_bg="rgba(25,113,194,0.08)",

    scrollbar_thumb="#dee2e6",
    scrollbar_track="#f8f9fa",
    scrollbar_hover="#ced4da",

    shadow_sm="0 1px 2px rgba(0,0,0,0.04)",
    shadow_md="0 4px 8px rgba(0,0,0,0.06)",
    shadow_lg="0 8px 24px rgba(0,0,0,0.08)",
    shadow_xl="0 16px 48px rgba(0,0,0,0.10)",

    tooltip_bg="#1a1b1e",
    tooltip_text="#ffffff",
    badge_bg="rgba(66,99,235,0.10)",
    badge_text="#4263eb",

    link_color="#4263eb",
    link_hover="#3b5bdb",
    selection_bg="rgba(66,99,235,0.20)",
    selection_text="#1a1b1e",

    titlebar_bg="#ffffff",
    titlebar_border="#dee2e6",
    titlebar_text="#1a1b1e",

    sidebar_bg="#f8f9fa",
    sidebar_border="#dee2e6",
    sidebar_text="#5c5f66",
    sidebar_hover="#e9ecef",
    sidebar_active="rgba(66,99,235,0.08)",

    icon_color="#5c5f66",
    icon_hover="#1a1b1e",

    overlay_bg="rgba(0,0,0,0.3)",
    skeleton_bg="#e9ecef",
    skeleton_shimmer="#f1f3f5",
)


MONOCHROME: ThemeColors = ThemeColors(
    name="monochrome",
    label="Monochrome",
    description="Pure grayscale – maximum focus, zero distraction",

    page_bg="#0a0a0a",
    container_bg="#111111",
    surface_bg="#1a1a1a",
    elevated_bg="#222222",
    hover_bg="#2a2a2a",
    active_bg="#333333",

    text_primary="#ffffff",
    text_secondary="#999999",
    text_tertiary="#666666",
    text_muted="#444444",
    text_inverse="#0a0a0a",

    accent_primary="#ffffff",
    accent_hover="#e0e0e0",
    accent_muted="rgba(255,255,255,0.08)",
    accent_text="#ffffff",

    border_default="#2a2a2a",
    border_focus="#ffffff",
    border_subtle="#1a1a1a",
    divider="#1a1a1a",

    input_bg="#111111",
    input_border="#2a2a2a",
    input_focus_border="#ffffff",
    input_placeholder="#555555",

    btn_primary_bg="#ffffff",
    btn_primary_hover="#e0e0e0",
    btn_primary_text="#0a0a0a",
    btn_secondary_bg="#1a1a1a",
    btn_secondary_hover="#222222",
    btn_secondary_text="#999999",
    btn_ghost_hover="rgba(255,255,255,0.06)",
    btn_danger_bg="#444444",
    btn_danger_hover="#555555",

    chat_user_bg="#1a1a1a",
    chat_user_border="#2a2a2a",
    chat_user_text="#ffffff",
    chat_agent_bg="#111111",
    chat_agent_border="#1a1a1a",
    chat_agent_text="#ffffff",

    code_bg="#0d0d0d",
    code_border="#1a1a1a",
    code_text="#ffffff",
    code_keyword="#cccccc",
    code_string="#999999",
    code_comment="#555555",
    code_number="#888888",
    code_function="#aaaaaa",

    success="#888888",
    success_bg="rgba(136,136,136,0.10)",
    warning="#aaaaaa",
    warning_bg="rgba(170,170,170,0.10)",
    error="#666666",
    error_bg="rgba(102,102,102,0.10)",
    info="#777777",
    info_bg="rgba(119,119,119,0.10)",

    scrollbar_thumb="#2a2a2a",
    scrollbar_track="#0a0a0a",
    scrollbar_hover="#3a3a3a",

    shadow_sm="0 1px 2px rgba(0,0,0,0.5)",
    shadow_md="0 4px 8px rgba(0,0,0,0.6)",
    shadow_lg="0 8px 24px rgba(0,0,0,0.7)",
    shadow_xl="0 16px 48px rgba(0,0,0,0.8)",

    tooltip_bg="#1a1a1a",
    tooltip_text="#ffffff",
    badge_bg="rgba(255,255,255,0.10)",
    badge_text="#cccccc",

    link_color="#cccccc",
    link_hover="#ffffff",
    selection_bg="rgba(255,255,255,0.25)",
    selection_text="#0a0a0a",

    titlebar_bg="#0d0d0d",
    titlebar_border="#1a1a1a",
    titlebar_text="#ffffff",

    sidebar_bg="#0d0d0d",
    sidebar_border="#1a1a1a",
    sidebar_text="#999999",
    sidebar_hover="#151515",
    sidebar_active="rgba(255,255,255,0.08)",

    icon_color="#999999",
    icon_hover="#ffffff",

    overlay_bg="rgba(0,0,0,0.8)",
    skeleton_bg="#1a1a1a",
    skeleton_shimmer="#2a2a2a",
)


ALL_THEMES: list[ThemeColors] = [TRAE_DARK, MIDNIGHT, FOREST, SUNSET, LIGHT, MONOCHROME]
THEME_MAP: Dict[str, ThemeColors] = {t.name: t for t in ALL_THEMES}
DEFAULT_THEME = "trae_dark"

THEME_PRESETS: Dict[str, Dict[str, str]] = {
    "trae_dark": {
        "label": "Solo Dark",
        "badge": "#6366f1",
        "desc": "Trae SOLO original",
    },
    "midnight": {
        "label": "Midnight Blue",
        "badge": "#06b6d4",
        "desc": "Calm and focused",
    },
    "forest": {
        "label": "Forest",
        "badge": "#22c55e",
        "desc": "Organic and grounded",
    },
    "sunset": {
        "label": "Sunset",
        "badge": "#f472b6",
        "desc": "Creative and energetic",
    },
    "light": {
        "label": "Light Paper",
        "badge": "#4263eb",
        "desc": "Maximum readability",
    },
    "monochrome": {
        "label": "Monochrome",
        "badge": "#999999",
        "desc": "Zero distraction",
    },
}


def theme_to_css_variables(t: ThemeColors) -> str:
    """Generate a complete CSS custom-properties block for a theme."""
    lines = []
    lines.append(f"/* ---- {t.label} ({t.name}) ---- */")
    for field_name, _ in t.__dataclass_fields__.items():
        if field_name in ("name", "label", "description"):
            continue
        value = getattr(t, field_name)
        css_name = f"--ga-{field_name.replace('_', '-')}"
        lines.append(f"  {css_name}: {value};")
    return "\n".join(lines)


def theme_to_css_full(t: ThemeColors) -> str:
    """Generate a full <style> block with all CSS variables and base styles."""
    vars_block = theme_to_css_variables(t)
    return f"""<style id="ga-theme">
:root {{
{vars_block}
}}
.stApp {{
    background-color: var(--ga-page-bg) !important;
    color: var(--ga-text-primary) !important;
}}
[data-testid="collapsedControl"],
button[data-testid="stSidebarCollapsedControl"],
[data-testid="stToolbar"],
[data-testid="stDeployButton"],
[data-testid="stHeaderMoreOptions"],
[data-testid="stMainMenu"],
[data-testid="stMainMenuButton"] {{
    display: none !important;
}}
[data-testid="stAppViewContainer"],
[data-testid="stAppScrollToBottomContainer"],
[data-testid="stMainBlockContainer"],
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"] {{
    background: var(--ga-page-bg) !important;
    color: var(--ga-text-primary) !important;
}}
header[data-testid="stHeader"] {{
    background: var(--ga-titlebar-bg) !important;
    display: none !important;
}}
section[data-testid="stSidebar"] {{
    background-color: var(--ga-sidebar-bg) !important;
    border-right: 1px solid var(--ga-sidebar-border) !important;
    display: none !important;
    width: 0 !important;
    min-width: 0 !important;
    padding: 0 !important;
    border: none !important;
}}
section[data-testid="stSidebar"] * {{
    color: var(--ga-sidebar-text) !important;
}}
.stChatMessage {{
    background-color: transparent !important;
}}
div[data-testid="stChatMessage"] {{
    border-radius: 14px !important;
    padding: 12px 16px !important;
    margin: 8px 0 !important;
}}
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
    background: var(--ga-chat-user-bg) !important;
    border: 1px solid var(--ga-chat-user-border) !important;
}}
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {{
    background: var(--ga-chat-agent-bg) !important;
    border: 1px solid var(--ga-chat-agent-border) !important;
}}
[data-testid="stChatMessage"] [data-testid^="stChatMessageAvatar"] {{
    margin-top: 2px !important;
}}
textarea[data-testid="stChatInputTextArea"] {{
    background-color: var(--ga-input-bg) !important;
    border: 1px solid var(--ga-input-border) !important;
    border-radius: 14px !important;
    color: var(--ga-text-primary) !important;
}}
textarea[data-testid="stChatInputTextArea"]:focus {{
    border-color: var(--ga-input-focus-border) !important;
    box-shadow: 0 0 0 2px var(--ga-accent-muted) !important;
}}
textarea[data-testid="stChatInputTextArea"]::placeholder {{
    color: var(--ga-input-placeholder) !important;
}}
[data-testid="stBottom"] {{
    border-top: 1px solid var(--ga-border-subtle) !important;
}}
[data-testid="stBottomBlockContainer"] {{
    padding-top: 0.8rem !important;
    padding-bottom: 1rem !important;
}}
[data-testid="stChatInput"] {{
    background: var(--ga-container-bg) !important;
    border: 1px solid var(--ga-border-default) !important;
    border-radius: 18px !important;
    box-shadow: var(--ga-shadow-md) !important;
    padding: 8px 10px !important;
}}
[data-testid="stChatInput"] > div {{
    padding: 0 !important;
    min-height: 0 !important;
    display: flex !important;
    align-items: center !important;
    height: auto !important;
}}
[data-testid="stChatInput"] > div > div {{
    display: flex !important;
    align-items: center !important;
    height: auto !important;
    min-height: 0 !important;
}}
[data-testid="stChatInput"] > div > div:first-child {{
    flex: 1 1 auto !important;
    align-self: center !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 10px !important;
    width: 100% !important;
}}
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="base-input"] {{
    background: transparent !important;
}}
[data-testid="stChatInputSubmitButton"] {{
    background: var(--ga-btn-primary-bg) !important;
    color: var(--ga-btn-primary-text) !important;
    border-radius: 12px !important;
    border: none !important;
    min-width: 42px !important;
    min-height: 42px !important;
}}
[data-testid="stChatInputSubmitButton"]:hover:not(:disabled) {{
    background: var(--ga-btn-primary-hover) !important;
}}
[data-testid="stChatInputSubmitButton"]:disabled {{
    background: var(--ga-accent-muted) !important;
    color: var(--ga-text-muted) !important;
}}
.stButton > button {{
    background-color: var(--ga-btn-secondary-bg) !important;
    color: var(--ga-btn-secondary-text) !important;
    border: 1px solid var(--ga-border-default) !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}}
.stButton > button:hover {{
    background-color: var(--ga-btn-secondary-hover) !important;
    border-color: var(--ga-border-focus) !important;
    color: var(--ga-text-primary) !important;
}}
.stButton > button:disabled {{
    opacity: 0.45 !important;
    cursor: not-allowed !important;
    box-shadow: none !important;
}}
.stButton > button[kind="primary"] {{
    background-color: var(--ga-btn-primary-bg) !important;
    color: var(--ga-btn-primary-text) !important;
    border: none !important;
}}
.stButton > button[kind="primary"]:hover {{
    background-color: var(--ga-btn-primary-hover) !important;
    color: var(--ga-btn-primary-text) !important;
}}
.stSelectbox > div > div {{
    background-color: var(--ga-input-bg) !important;
    border-color: var(--ga-input-border) !important;
    color: var(--ga-text-primary) !important;
}}
.stSelectbox > div > div > div {{
    color: var(--ga-text-primary) !important;
}}
div[data-baseweb="select"] > div {{
    background: var(--ga-input-bg) !important;
    border: 1px solid var(--ga-input-border) !important;
    border-radius: 12px !important;
    min-height: 44px !important;
}}
div[data-baseweb="select"] * {{
    color: var(--ga-text-primary) !important;
}}
div[data-baseweb="select"] svg {{
    fill: var(--ga-text-secondary) !important;
}}
.stTextInput > div > div > input {{
    background-color: var(--ga-input-bg) !important;
    border-color: var(--ga-input-border) !important;
    color: var(--ga-text-primary) !important;
}}
.stTextInput > div > div > input::placeholder {{
    color: var(--ga-input-placeholder) !important;
}}
.stNumberInput > div > div > input {{
    background-color: var(--ga-input-bg) !important;
    border-color: var(--ga-input-border) !important;
    color: var(--ga-text-primary) !important;
}}
div.stMarkdown {{
    color: var(--ga-text-primary) !important;
}}
p, span, label, div {{
    color: var(--ga-text-primary) !important;
}}
small, .stCaption {{
    color: var(--ga-text-secondary) !important;
}}
a {{
    color: var(--ga-link-color) !important;
}}
a:hover {{
    color: var(--ga-link-hover) !important;
}}
code {{
    background: var(--ga-code-bg) !important;
    color: var(--ga-code-text) !important;
    border: 1px solid var(--ga-code-border) !important;
    border-radius: 4px !important;
    padding: 2px 6px !important;
}}
pre {{
    background: var(--ga-code-bg) !important;
    border: 1px solid var(--ga-code-border) !important;
    border-radius: 8px !important;
}}
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {{
    gap: 0 !important;
}}
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}
::-webkit-scrollbar-track {{
    background: var(--ga-scrollbar-track) !important;
}}
::-webkit-scrollbar-thumb {{
    background: var(--ga-scrollbar-thumb) !important;
    border-radius: 4px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: var(--ga-scrollbar-hover) !important;
}}
::selection {{
    background: var(--ga-selection-bg) !important;
    color: var(--ga-selection-text) !important;
}}
.ga-topbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 16px;
    background: var(--ga-titlebar-bg);
    border-bottom: 1px solid var(--ga-titlebar-border);
    position: sticky;
    top: 0;
    z-index: 100;
}}
.ga-topbar-title {{
    font-size: 15px;
    font-weight: 600;
    color: var(--ga-titlebar-text);
    letter-spacing: -0.01em;
}}
.ga-theme-selector {{
    display: flex;
    align-items: center;
    gap: 8px;
}}
.ga-theme-dot {{
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}}
.ga-toolbar {{
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: var(--ga-container-bg);
    border-bottom: 1px solid var(--ga-border-subtle);
}}
.ga-toolbar-btn {{
    background: none;
    border: 1px solid var(--ga-border-default);
    color: var(--ga-text-secondary);
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.15s;
}}
.ga-toolbar-btn:hover {{
    background: var(--ga-hover-bg);
    color: var(--ga-text-primary);
    border-color: var(--ga-border-focus);
}}
.ga-empty-state {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 400px;
    color: var(--ga-text-muted);
    text-align: center;
}}
.ga-empty-state-icon {{
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.4;
}}
.ga-empty-state-title {{
    font-size: 18px;
    font-weight: 600;
    color: var(--ga-text-secondary);
    margin-bottom: 8px;
}}
.ga-empty-state-desc {{
    font-size: 14px;
    color: var(--ga-text-muted);
    max-width: 400px;
    line-height: 1.5;
}}
.ga-tool-tag {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 500;
    background: var(--ga-badge-bg);
    color: var(--ga-badge-text);
    border: 1px solid var(--ga-border-subtle);
}}
.ga-divider {{
    height: 1px;
    background: var(--ga-divider);
    margin: 8px 0;
}}
.ga-panel {{
    background: var(--ga-surface-bg);
    border: 1px solid var(--ga-border-default);
    border-radius: 10px;
    padding: 12px;
    margin: 8px 0;
}}
.ga-panel-title {{
    font-size: 13px;
    font-weight: 600;
    color: var(--ga-text-secondary);
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}
</style>"""


def get_theme_css(theme_name: str) -> str:
    """Get full CSS for a theme by name."""
    t = THEME_MAP.get(theme_name, TRAE_DARK)
    return theme_to_css_full(t)


def get_theme_colors(theme_name: str) -> ThemeColors:
    """Get ThemeColors dataclass instance by name."""
    return THEME_MAP.get(theme_name, TRAE_DARK)


def get_theme_tk(theme_name: str) -> Dict[str, str]:
    """Get flat color dict for Tkinter ttk styling."""
    t = get_theme_colors(theme_name)
    return {
        "page_bg": t.page_bg,
        "container_bg": t.container_bg,
        "surface_bg": t.surface_bg,
        "elevated_bg": t.elevated_bg,
        "hover_bg": t.hover_bg,
        "active_bg": t.active_bg,
        "text_primary": t.text_primary,
        "text_secondary": t.text_secondary,
        "text_tertiary": t.text_tertiary,
        "text_muted": t.text_muted,
        "text_inverse": t.text_inverse,
        "accent_primary": t.accent_primary,
        "accent_hover": t.accent_hover,
        "accent_muted": t.accent_muted,
        "accent_text": t.accent_text,
        "border_default": t.border_default,
        "border_focus": t.border_focus,
        "border_subtle": t.border_subtle,
        "divider": t.divider,
        "input_bg": t.input_bg,
        "input_border": t.input_border,
        "input_focus_border": t.input_focus_border,
        "btn_primary_bg": t.btn_primary_bg,
        "btn_primary_hover": t.btn_primary_hover,
        "btn_primary_text": t.btn_primary_text,
        "btn_secondary_bg": t.btn_secondary_bg,
        "btn_secondary_hover": t.btn_secondary_hover,
        "btn_secondary_text": t.btn_secondary_text,
        "btn_ghost_hover": t.btn_ghost_hover,
        "btn_danger_bg": t.btn_danger_bg,
        "btn_danger_hover": t.btn_danger_hover,
        "chat_user_bg": t.chat_user_bg,
        "chat_user_border": t.chat_user_border,
        "chat_user_text": t.chat_user_text,
        "chat_agent_bg": t.chat_agent_bg,
        "chat_agent_border": t.chat_agent_border,
        "chat_agent_text": t.chat_agent_text,
        "code_bg": t.code_bg,
        "code_text": t.code_text,
        "success": t.success,
        "success_bg": t.success_bg,
        "warning": t.warning,
        "warning_bg": t.warning_bg,
        "error": t.error,
        "error_bg": t.error_bg,
        "info": t.info,
        "info_bg": t.info_bg,
        "link_color": t.link_color,
        "scrollbar_thumb": t.scrollbar_thumb,
        "scrollbar_track": t.scrollbar_track,
        "scrollbar_hover": t.scrollbar_hover,
        "selection_bg": t.selection_bg,
        "selection_text": t.selection_text,
        "titlebar_bg": t.titlebar_bg,
        "titlebar_border": t.titlebar_border,
        "titlebar_text": t.titlebar_text,
        "sidebar_bg": t.sidebar_bg,
        "sidebar_border": t.sidebar_border,
        "sidebar_text": t.sidebar_text,
        "sidebar_hover": t.sidebar_hover,
        "sidebar_active": t.sidebar_active,
        "icon_color": t.icon_color,
        "icon_hover": t.icon_hover,
    }
