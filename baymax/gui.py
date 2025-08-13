import tkinter as tk
from typing import Callable, Optional


class BaymaxGUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("BAYMAX - Personal Healthcare Companion")
        self.root.geometry("480x400")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=480, height=220, bg="white", highlightthickness=0)
        self.canvas.pack(pady=10)

        self.status_var = tk.StringVar(value="Idle")
        self.label = tk.Label(self.root, textvariable=self.status_var, font=("Arial", 14))
        self.label.pack(pady=6)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=6)
        self.btn_register = tk.Button(btn_frame, text="Register User")
        self.btn_register.grid(row=0, column=0, padx=6)
        self.btn_wake = tk.Button(btn_frame, text="Wake")
        self.btn_wake.grid(row=0, column=1, padx=6)
        self.btn_confirm = tk.Button(btn_frame, text="I took my medicine")
        self.btn_confirm.grid(row=0, column=2, padx=6)

        self._on_register: Optional[Callable[[], None]] = None
        self._on_wake: Optional[Callable[[], None]] = None
        self._on_confirm: Optional[Callable[[], None]] = None
        self.btn_register.configure(command=lambda: self._on_register and self._on_register())
        self.btn_wake.configure(command=lambda: self._on_wake and self._on_wake())
        self.btn_confirm.configure(command=lambda: self._on_confirm and self._on_confirm())

        self._draw_face_idle()

    def on_register(self, cb: Callable[[], None]) -> None:
        self._on_register = cb

    def on_wake(self, cb: Callable[[], None]) -> None:
        self._on_wake = cb

    def on_confirm(self, cb: Callable[[], None]) -> None:
        self._on_confirm = cb

    def set_status(self, text: str) -> None:
        self.status_var.set(text)
        self.root.update_idletasks()

    def _draw_face(self, eye_radius: int, bar_thickness: int, color: str = "black") -> None:
        self.canvas.delete("all")
        center_y = 110
        left_eye_center = (160, center_y)
        right_eye_center = (320, center_y)
        self.canvas.create_oval(
            left_eye_center[0] - eye_radius,
            left_eye_center[1] - eye_radius,
            left_eye_center[0] + eye_radius,
            left_eye_center[1] + eye_radius,
            fill=color,
            outline=color,
        )
        self.canvas.create_oval(
            right_eye_center[0] - eye_radius,
            right_eye_center[1] - eye_radius,
            right_eye_center[0] + eye_radius,
            right_eye_center[1] + eye_radius,
            fill=color,
            outline=color,
        )
        self.canvas.create_rectangle(
            left_eye_center[0] + eye_radius,
            center_y - bar_thickness // 2,
            right_eye_center[0] - eye_radius,
            center_y + bar_thickness // 2,
            fill=color,
            outline=color,
        )

    def _draw_face_idle(self) -> None:
        self._draw_face(eye_radius=14, bar_thickness=6, color="black")

    def set_expression_idle(self) -> None:
        self._draw_face_idle()

    def set_expression_talking(self) -> None:
        self._draw_face(eye_radius=14, bar_thickness=10, color="black")

    def set_expression_alert(self) -> None:
        self._draw_face(eye_radius=16, bar_thickness=12, color="red")

    def set_expression_sad(self) -> None:
        self._draw_face(eye_radius=10, bar_thickness=4, color="blue")

    def run(self) -> None:
        self.root.mainloop()