"""Color palettes and font settings for each SudokuMaster theme.

The UI layer reads from THEMES[theme_name] to style every widget, so a
theme switch only requires re-applying these values, never a restart.
"""

THEMES = {
    "Dark": {
        "background": "#1b2333",
        "surface": "#242e42",
        "surface_alt": "#2c3750",
        "text_primary": "#eef1f8",
        "text_secondary": "#9aa5bd",
        "grid_line": "#3a4763",
        "box_line": "#c7d0e6",
        "cell_fixed_bg": "#2c3750",
        "cell_editable_bg": "#1b2333",
        "cell_selected_bg": "#3a5aa8",
        "cell_peer_bg": "#28324a",
        "cell_match_bg": "#3a4a3a",
        "cell_error_bg": "#5a2c34",
        "accent": "#4f8cff",
        "success": "#4caf7d",
        "danger": "#e05564",
        "button_bg": "#2c3750",
        "button_fg": "#eef1f8",
    },
    "Light": {
        "background": "#f4f6fb",
        "surface": "#ffffff",
        "surface_alt": "#e9edf7",
        "text_primary": "#1c2333",
        "text_secondary": "#5b6478",
        "grid_line": "#c3cbdc",
        "box_line": "#374260",
        "cell_fixed_bg": "#e9edf7",
        "cell_editable_bg": "#ffffff",
        "cell_selected_bg": "#a9c4ff",
        "cell_peer_bg": "#dde6fb",
        "cell_match_bg": "#cdeeda",
        "cell_error_bg": "#fbd3d8",
        "accent": "#2f6fed",
        "success": "#2f9e6b",
        "danger": "#d1414f",
        "button_bg": "#e9edf7",
        "button_fg": "#1c2333",
    },
    "Blue": {
        "background": "#0d2140",
        "surface": "#123259",
        "surface_alt": "#173e6d",
        "text_primary": "#eaf2ff",
        "text_secondary": "#9cbde3",
        "grid_line": "#2c5586",
        "box_line": "#d7e7ff",
        "cell_fixed_bg": "#173e6d",
        "cell_editable_bg": "#0d2140",
        "cell_selected_bg": "#3d7cd9",
        "cell_peer_bg": "#1a4a80",
        "cell_match_bg": "#2c5a4d",
        "cell_error_bg": "#6b2733",
        "accent": "#4fa3ff",
        "success": "#4fd19b",
        "danger": "#ff6b7a",
        "button_bg": "#173e6d",
        "button_fg": "#eaf2ff",
    },
    "Classic": {
        "background": "#fdf6e3",
        "surface": "#fffdf5",
        "surface_alt": "#f2e9c9",
        "text_primary": "#2b2417",
        "text_secondary": "#6f6650",
        "grid_line": "#a89f78",
        "box_line": "#2b2417",
        "cell_fixed_bg": "#f2e9c9",
        "cell_editable_bg": "#fffdf5",
        "cell_selected_bg": "#e7c873",
        "cell_peer_bg": "#f6ecc7",
        "cell_match_bg": "#cfe3b0",
        "cell_error_bg": "#eec2bd",
        "accent": "#b5842a",
        "success": "#4e8a4a",
        "danger": "#b03a3a",
        "button_bg": "#f2e9c9",
        "button_fg": "#2b2417",
    },
}

FONT_FAMILY = "Segoe UI"
MONO_FAMILY = "Consolas"

DEFAULT_THEME = "Dark"
DEFAULT_ACCENT = "#4f8cff"
