import tkinter as tk
from tkinter import messagebox
import winsound
import math


class PomodoroApp:
    C_BG       = "#16213e"
    C_PANEL    = "#0f3460"
    C_ARC_BG   = "#2a3f5f"
    C_WHITE    = "#ffffff"
    C_GRAY     = "#8892a4"

    MODES = {
        "work":        {"label": "工作時間", "minutes": 25, "color": "#e94560"},
        "short_break": {"label": "短暫休息", "minutes": 5,  "color": "#0f9b58"},
        "long_break":  {"label": "長休息",   "minutes": 15, "color": "#1a73e8"},
    }

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("番茄鐘")
        self.root.geometry("400x580")
        self.root.resizable(False, False)
        self.root.configure(bg=self.C_BG)

        # Center on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - 400) // 2
        y = (self.root.winfo_screenheight() - 580) // 2
        self.root.geometry(f"400x580+{x}+{y}")

        self.mode              = "work"
        self.is_running        = False
        self.time_left         = self.MODES["work"]["minutes"] * 60
        self.total_time        = self.time_left
        self.completed_sessions = 0
        self.after_id          = None

        self._build()
        self._refresh()

    # ── UI construction ─────────────────────────────────────────────────────

    def _build(self):
        # Title
        tk.Label(self.root, text="🍅  番茄鐘", bg=self.C_BG, fg=self.C_WHITE,
                 font=("Segoe UI", 22, "bold")).pack(pady=(26, 0))

        # Mode tabs
        tab_frame = tk.Frame(self.root, bg=self.C_BG)
        tab_frame.pack(pady=14)
        self._mode_btns = {}
        for key, info in self.MODES.items():
            btn = tk.Button(
                tab_frame, text=info["label"],
                bg=self.C_PANEL, fg=self.C_GRAY,
                relief="flat", padx=14, pady=6,
                font=("Segoe UI", 10), cursor="hand2",
                command=lambda k=key: self._switch_mode(k),
            )
            btn.pack(side="left", padx=4)
            self._mode_btns[key] = btn

        # Canvas ring
        self._cv = tk.Canvas(self.root, width=280, height=280,
                             bg=self.C_BG, highlightthickness=0)
        self._cv.pack()

        m = 20  # margin
        self._cv.create_oval(m, m, 280-m, 280-m,
                             outline=self.C_ARC_BG, width=14, fill="")
        self._arc = self._cv.create_arc(m, m, 280-m, 280-m,
                                        start=90, extent=0,
                                        outline=self.MODES["work"]["color"],
                                        width=14, style="arc")
        self._time_txt   = self._cv.create_text(140, 128, text="25:00",
                                                fill=self.C_WHITE,
                                                font=("Segoe UI", 46, "bold"))
        self._status_txt = self._cv.create_text(140, 178, text="工作時間",
                                                fill=self.C_GRAY,
                                                font=("Segoe UI", 13))
        self._session_txt = self._cv.create_text(140, 208, text="第 1 回合",
                                                 fill=self.C_ARC_BG,
                                                 font=("Segoe UI", 10))

        # Session dots
        dot_frame = tk.Frame(self.root, bg=self.C_BG)
        dot_frame.pack(pady=8)
        self._dots = []
        for _ in range(4):
            lbl = tk.Label(dot_frame, text="●", bg=self.C_BG, fg=self.C_ARC_BG,
                           font=("Segoe UI", 18))
            lbl.pack(side="left", padx=7)
            self._dots.append(lbl)

        # Control buttons
        btn_frame = tk.Frame(self.root, bg=self.C_BG)
        btn_frame.pack(pady=16)

        self._start_btn = tk.Button(
            btn_frame, text="▶  開始",
            bg=self.MODES["work"]["color"], fg=self.C_WHITE,
            font=("Segoe UI", 14, "bold"),
            padx=28, pady=10, relief="flat", cursor="hand2",
            command=self._toggle,
        )
        self._start_btn.pack(side="left", padx=8)

        tk.Button(
            btn_frame, text="↺  重置",
            bg=self.C_PANEL, fg=self.C_WHITE,
            font=("Segoe UI", 14), padx=20, pady=10,
            relief="flat", cursor="hand2",
            command=self._reset,
        ).pack(side="left", padx=8)

        # Bottom links
        bottom = tk.Frame(self.root, bg=self.C_BG)
        bottom.pack(pady=4)
        tk.Button(bottom, text="⚙ 設定時間", bg=self.C_BG, fg=self.C_GRAY,
                  relief="flat", font=("Segoe UI", 10), cursor="hand2",
                  command=self._open_settings).pack(side="left", padx=12)
        tk.Button(bottom, text="⏭ 跳過", bg=self.C_BG, fg=self.C_GRAY,
                  relief="flat", font=("Segoe UI", 10), cursor="hand2",
                  command=lambda: self._finish(skip=True)).pack(side="left", padx=12)

    # ── Timer logic ──────────────────────────────────────────────────────────

    def _toggle(self):
        if self.is_running:
            self.is_running = False
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
            self._start_btn.config(text="▶  繼續")
        else:
            self.is_running = True
            self._start_btn.config(text="⏸  暫停")
            self._tick()

    def _tick(self):
        if not self.is_running:
            return
        if self.time_left <= 0:
            self._finish()
            return
        self.time_left -= 1
        self._refresh()
        self.after_id = self.root.after(1000, self._tick)

    def _finish(self, skip=False):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.is_running = False

        if not skip:
            self._beep()

        if self.mode == "work":
            self.completed_sessions += 1
            next_mode = "long_break" if self.completed_sessions % 4 == 0 else "short_break"
        else:
            next_mode = "work"

        self.mode       = next_mode
        self.time_left  = self.MODES[next_mode]["minutes"] * 60
        self.total_time = self.time_left
        self._start_btn.config(text="▶  開始")
        self._refresh()

        if not skip:
            self.root.lift()
            self.root.bell()
            messagebox.showinfo("番茄鐘",
                                f"時間到！\n切換到「{self.MODES[next_mode]['label']}」",
                                parent=self.root)

    def _reset(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.is_running = False
        self.time_left  = self.MODES[self.mode]["minutes"] * 60
        self.total_time = self.time_left
        self._start_btn.config(text="▶  開始")
        self._refresh()

    def _switch_mode(self, mode):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.is_running = False
        self.mode       = mode
        self.time_left  = self.MODES[mode]["minutes"] * 60
        self.total_time = self.time_left
        self._start_btn.config(text="▶  開始")
        self._refresh()

    def _beep(self):
        try:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            self.root.after(500, lambda: winsound.MessageBeep(winsound.MB_ICONEXCLAMATION))
            self.root.after(1000, lambda: winsound.MessageBeep(winsound.MB_ICONEXCLAMATION))
        except Exception:
            pass

    # ── Display refresh ──────────────────────────────────────────────────────

    def _refresh(self):
        color  = self.MODES[self.mode]["color"]
        m, s   = divmod(self.time_left, 60)
        ts     = f"{m:02d}:{s:02d}"
        frac   = (self.time_left / self.total_time) if self.total_time else 1.0
        extent = -frac * 359.9  # clockwise sweep

        self._cv.itemconfig(self._arc,        outline=color, extent=extent)
        self._cv.itemconfig(self._time_txt,   text=ts)
        self._cv.itemconfig(self._status_txt, text=self.MODES[self.mode]["label"])

        cycle    = self.completed_sessions // 4 + 1
        in_cycle = self.completed_sessions % 4
        self._cv.itemconfig(self._session_txt,
                            text=f"第 {cycle} 輪・{in_cycle}/4",
                            fill=self.C_GRAY if in_cycle else self.C_ARC_BG)

        # Mode tab highlights
        for k, btn in self._mode_btns.items():
            if k == self.mode:
                btn.config(bg=color, fg=self.C_WHITE)
            else:
                btn.config(bg=self.C_PANEL, fg=self.C_GRAY)

        # Start button accent color
        self._start_btn.config(bg=color, activebackground=color)

        # Session dots
        filled = self.completed_sessions % 4
        for i, dot in enumerate(self._dots):
            dot.config(fg=color if i < filled else self.C_ARC_BG)

        self.root.title(f"🍅 {ts}  {self.MODES[self.mode]['label']}")

    # ── Settings dialog ──────────────────────────────────────────────────────

    def _open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("設定")
        win.geometry("300x230")
        win.configure(bg=self.C_BG)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        # Center over parent
        win.update_idletasks()
        px, py = self.root.winfo_x(), self.root.winfo_y()
        win.geometry(f"300x230+{px+50}+{py+170}")

        fields = [
            ("工作時間 (分鐘)", "work"),
            ("短休時間 (分鐘)", "short_break"),
            ("長休時間 (分鐘)", "long_break"),
        ]
        entries = {}
        for i, (lbl, key) in enumerate(fields):
            tk.Label(win, text=lbl, bg=self.C_BG, fg=self.C_WHITE,
                     font=("Segoe UI", 11)).grid(row=i, column=0, padx=20, pady=10, sticky="w")
            var = tk.StringVar(value=str(self.MODES[key]["minutes"]))
            ent = tk.Entry(win, textvariable=var, width=6,
                           bg=self.C_PANEL, fg=self.C_WHITE,
                           insertbackground=self.C_WHITE,
                           font=("Segoe UI", 11), relief="flat")
            ent.grid(row=i, column=1, padx=10)
            entries[key] = var

        def save():
            try:
                for key, var in entries.items():
                    val = int(var.get())
                    if val < 1 or val > 120:
                        raise ValueError
                    self.MODES[key]["minutes"] = val
            except ValueError:
                messagebox.showerror("錯誤", "請輸入 1–120 之間的整數", parent=win)
                return
            win.destroy()
            self._reset()

        tk.Button(win, text="儲存", bg=self.MODES["work"]["color"], fg=self.C_WHITE,
                  font=("Segoe UI", 11, "bold"), padx=22, pady=7,
                  relief="flat", cursor="hand2",
                  command=save).grid(row=len(fields), column=0, columnspan=2, pady=18)

    # ── Entry point ──────────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    PomodoroApp().run()
