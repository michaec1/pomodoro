# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Pomodoro timer with two implementations:
- `pomodoro.html` — single-file web app (HTML + CSS + JS, no build step, open directly in a browser)
- `pomodoro.py` — Windows-only Python desktop app using tkinter and `winsound`

## Running

```bash
# Web version — just open in browser
start pomodoro.html

# Python desktop version (Windows only, requires Python 3.x with tkinter)
python pomodoro.py
```

## Architecture

Both implementations share the same three-mode model (`work` / `short_break` / `long_break`) and session-cycle logic: every 4 completed work sessions triggers a long break instead of a short break. The `--accent` CSS variable (and its Python equivalent, the arc/button color) dynamically changes per mode.

**HTML version** (`pomodoro.html`): All logic lives in a single `<script>` block. The ring progress indicator is an SVG `<circle>` with `stroke-dashoffset` driven by `timeLeft / totalSeconds`. The `MODES` object is the single source of truth for labels, durations, and colors. Keyboard shortcuts (`Space`, `R`, `S`) are handled by a single `keydown` listener that guards against firing inside `<input>` elements.

**Python version** (`pomodoro.py`): `PomodoroApp` is a single class. The ring is drawn on a `tk.Canvas` using `create_arc` with a clockwise `extent` sweep. Ticking uses `root.after(1000, self._tick)` (stored in `self.after_id`) so it can be cancelled cleanly on pause/reset/skip. Settings open as a modal `tk.Toplevel` with `grab_set()`.

## Key Details

- The `<title>` tag in `pomodoro.html` uses the date-stamped format `🍅 20260506番茄鐘`; the running title is updated dynamically via `document.title`.
- The Python version beeps using `winsound.MessageBeep` — this will not work on macOS/Linux.
- Timer duration settings (1–120 minutes) are validated in both versions before applying.
- The deployed URL is `https://michaec1.github.io/pomodoro/pomodoro.html`.
