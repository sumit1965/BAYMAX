import threading
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import Callable, Dict, List, Optional


class BaymaxGUI:
    def __init__(self, on_register: Callable[[str, List[Dict[str, str]]], Dict], on_capture_faces: Callable[[str], None], on_confirm_taken: Callable[[], None]):
        self._root = tk.Tk()
        self._root.title("BAYMAX - Personal Healthcare Companion")
        self._root.geometry("520x640")
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Canvas face
        self._canvas = tk.Canvas(self._root, width=480, height=360, bg="#f4f6f8", highlightthickness=0)
        self._canvas.pack(pady=10)
        self._eyes = None
        self._connecting_line = None
        self._expression = "idle"  # idle, talking, alert, sad
        self._anim_phase = 0

        # Message label
        self._message_var = tk.StringVar(value="Hello. I am a Baymax-inspired healthcare companion.")
        self._message_label = tk.Label(self._root, textvariable=self._message_var, wraplength=440, justify=tk.CENTER, font=("Helvetica", 14))
        self._message_label.pack(pady=10)

        # Buttons
        btn_frame = tk.Frame(self._root)
        btn_frame.pack(pady=6)
        self._register_btn = tk.Button(btn_frame, text="Register User", command=self._open_register_dialog)
        self._register_btn.grid(row=0, column=0, padx=8)
        self._capture_btn = tk.Button(btn_frame, text="Capture Faces", command=self._open_capture_dialog)
        self._capture_btn.grid(row=0, column=1, padx=8)
        self._confirm_btn = tk.Button(btn_frame, text="Confirm Taken", command=on_confirm_taken)
        self._confirm_btn.grid(row=0, column=2, padx=8)

        self._on_register = on_register
        self._on_capture_faces = on_capture_faces

        # Registered users list
        self._users_listbox = tk.Listbox(self._root, width=60, height=8)
        self._users_listbox.pack(pady=8)

        # Animation loop
        self._draw_face()
        self._root.after(100, self._animate)

        # Thread-safe queueing
        self._tk_lock = threading.RLock()

    def mainloop(self) -> None:
        self._root.mainloop()

    def _on_close(self) -> None:
        self._root.quit()

    def _draw_face(self) -> None:
        self._canvas.delete("all")
        # Base head (rounded rectangle/ellipse)
        self._canvas.create_oval(40, 40, 440, 320, fill="#ffffff", outline="#e0e0e0", width=4)
        # Eyes coordinates
        left_eye_center = (200, 180)
        right_eye_center = (300, 180)
        eye_radius = 12
        # Expression adjustments
        if self._expression == "alert":
            eye_radius = 16
        elif self._expression == "sad":
            eye_radius = 10
        elif self._expression == "talking":
            eye_radius = 12 + int(2 * abs((self._anim_phase % 20) - 10) / 10)
        # Draw eyes
        self._canvas.create_oval(left_eye_center[0] - eye_radius, left_eye_center[1] - eye_radius,
                                 left_eye_center[0] + eye_radius, left_eye_center[1] + eye_radius,
                                 fill="#1a1a1a", outline="")
        self._canvas.create_oval(right_eye_center[0] - eye_radius, right_eye_center[1] - eye_radius,
                                 right_eye_center[0] + eye_radius, right_eye_center[1] + eye_radius,
                                 fill="#1a1a1a", outline="")
        # Connecting line style
        if self._expression == "sad":
            self._canvas.create_line(200, 200, 300, 170, fill="#1a1a1a", width=6)
        else:
            self._canvas.create_line(200, 180, 300, 180, fill="#1a1a1a", width=6)

    def _animate(self) -> None:
        self._anim_phase = (self._anim_phase + 1) % 1000
        if self._expression == "idle":
            # subtle idle motion
            if self._anim_phase % 30 == 0:
                self._draw_face()
        else:
            self._draw_face()
        self._root.after(100, self._animate)

    # Thread-safe UI updates
    def set_message(self, text: str) -> None:
        def _set():
            self._message_var.set(text)
        self._root.after(0, _set)

    def set_expression(self, expression: str) -> None:
        def _set():
            self._expression = expression
            self._draw_face()
        self._root.after(0, _set)

    def set_users(self, users: List[Dict]) -> None:
        def _set():
            self._users_listbox.delete(0, tk.END)
            for u in users:
                sched = ", ".join([f"{s.get('time')}:{s.get('label','Medicine')}" for s in u.get('schedule', [])])
                self._users_listbox.insert(tk.END, f"{u['name']} ({u['id'][:8]}) - {sched}")
        self._root.after(0, _set)

    def _open_register_dialog(self) -> None:
        dialog = tk.Toplevel(self._root)
        dialog.title("Register User")
        dialog.geometry("420x260")

        tk.Label(dialog, text="Name:").pack(anchor=tk.W, padx=10, pady=5)
        name_entry = tk.Entry(dialog, width=40)
        name_entry.pack(padx=10)

        tk.Label(dialog, text="Schedule (comma-separated HH:MM or HH:MM:Label)").pack(anchor=tk.W, padx=10, pady=5)
        sched_entry = tk.Entry(dialog, width=40)
        sched_entry.pack(padx=10)

        def on_submit():
            name = name_entry.get().strip()
            sched_text = sched_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Name is required")
                return
            schedule: List[Dict[str, str]] = []
            if sched_text:
                parts = [p.strip() for p in sched_text.split(",") if p.strip()]
                for p in parts:
                    sub = p.split(":")
                    if len(sub) >= 2:
                        hh, mm = sub[0], sub[1]
                        label = ":".join(sub[2:]) if len(sub) > 2 else "Medicine"
                        schedule.append({"time": f"{int(hh):02d}:{int(mm):02d}", "label": label or "Medicine"})
                    else:
                        messagebox.showerror("Error", f"Invalid time format: {p}")
                        return
            user = self._on_register(name, schedule)
            messagebox.showinfo("Registered", f"User {user['name']} created. Select and click 'Capture Faces' to add samples.")
            dialog.destroy()

        tk.Button(dialog, text="Submit", command=on_submit).pack(pady=12)

    def _open_capture_dialog(self) -> None:
        selection = self._users_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Select a user in the list first")
            return
        text = self._users_listbox.get(selection[0])
        # extract id inside parentheses
        start = text.find("(")
        end = text.find(")")
        user_id_short = text[start + 1 : end]
        # caller should map short id back; we pass short id and let on_capture perform search
        self._on_capture_faces(user_id_short)