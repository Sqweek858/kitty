#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brad TUI (compat entrypoint).

The old `brad_tui.py` rendered a full-screen animation by repeatedly moving the
cursor to HOME and rewriting the entire terminal. That behavior *causes*:
- disappearing command output
- broken cursor movement
- broken keybinds
- menu/suggestion panels flickering or "randomly" appearing

This entrypoint now delegates to the fixed interactive implementation in
`brad_tui_enhanced.py`.
"""


def main() -> None:
    try:
        from brad_tui_enhanced import main as enhanced_main
    except Exception as e:
        raise SystemExit(
            "Missing dependencies for the enhanced TUI.\n"
            "Run: python3 -m pip install prompt_toolkit\n"
            f"Details: {e}"
        )
    enhanced_main()


if __name__ == "__main__":
    main()
