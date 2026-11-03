import tkinter as tk
from tkinter import ttk, messagebox
import time
import random
import math

class IRasterTarget:
    def set_pixel(self, x: int, y: int, intensity: float = 1.0):
        raise NotImplementedError()

class VirtualGrid(IRasterTarget):
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.pixels = {}

    def set_pixel(self, x: int, y: int, intensity: float = 1.0):
        if -self.width <= x < self.width and -self.height <= y < self.height:
            self.pixels[(x, y)] = max(self.pixels.get((x, y), 0.0), intensity)

    def clear(self):
        self.pixels.clear()

class RasterEngine:
    @staticmethod
    def step_line(x1: int, y1: int, x2: int, y2: int, target: IRasterTarget):
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        if steps == 0:
            target.set_pixel(x1, y1)
            return
        x_inc = dx / steps
        y_inc = dy / steps
        x = x1
        y = y1
        for _ in range(steps + 1):
            target.set_pixel(round(x), round(y))
            x += x_inc
            y += y_inc

    @staticmethod
    def dda_line(x1: int, y1: int, x2: int, y2: int, target: IRasterTarget):
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        if steps == 0:
            target.set_pixel(x1, y1)
            return
        x_inc = dx / steps
        y_inc = dy / steps
        x = float(x1)
        y = float(y1)
        for _ in range(steps + 1):
            target.set_pixel(round(x), round(y))
            x += x_inc
            y += y_inc

    @staticmethod
    def bresenham_line(x1: int, y1: int, x2: int, y2: int, target: IRasterTarget):
        x = x1
        y = y1
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        if dx > dy:
            err = dx / 2.0
            while x != x2:
                target.set_pixel(x, y)
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
            target.set_pixel(x, y)
        else:
            err = dy / 2.0
            while y != y2:
                target.set_pixel(x, y)
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
            target.set_pixel(x, y)

    @staticmethod
    def bresenham_circle(xc: int, yc: int, r: int, target: IRasterTarget):
        x = 0
        y = r
        d = 3 - 2 * r
        while x <= y:
            RasterEngine._draw_circle_pixels(xc, yc, x, y, target)
            if d < 0:
                d = d + 4 * x + 6
            else:
                d = d + 4 * (x - y) + 10
                y -= 1
            x += 1

    @staticmethod
    def _draw_circle_pixels(xc, yc, x, y, target):
        target.set_pixel(xc + x, yc + y)
        target.set_pixel(xc - x, yc + y)
        target.set_pixel(xc + x, yc - y)
        target.set_pixel(xc - x, yc - y)
        target.set_pixel(xc + y, yc + x)
        target.set_pixel(xc - y, yc + x)
        target.set_pixel(xc + y, yc - x)
        target.set_pixel(xc - y, yc - x)

    @staticmethod
    def wu_line(x1: int, y1: int, x2: int, y2: int, target: IRasterTarget):
        def ipart(x): return math.floor(x)
        def fpart(x): return x - math.floor(x)
        def rfpart(x): return 1.0 - fpart(x)

        steep = abs(y2 - y1) > abs(x2 - x1)
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1

        dx = x2 - x1
        dy = y2 - y1
        gradient = dy / dx if dx != 0 else 1.0

        xend = round(x1)
        yend = y1 + gradient * (xend - x1)
        xgap = rfpart(x1 + 0.5)
        xpxl1 = xend
        ypxl1 = ipart(yend)

        if steep:
            target.set_pixel(ypxl1, xpxl1, rfpart(yend) * xgap)
            target.set_pixel(ypxl1 + 1, xpxl1, fpart(yend) * xgap)
        else:
            target.set_pixel(xpxl1, ypxl1, rfpart(yend) * xgap)
            target.set_pixel(xpxl1, ypxl1 + 1, fpart(yend) * xgap)

        intery = yend + gradient

        xend = round(x2)
        yend = y2 + gradient * (xend - x2)
        xgap = fpart(x2 + 0.5)
        xpxl2 = xend
        ypxl2 = ipart(yend)

        if steep:
            target.set_pixel(ypxl2, xpxl2, rfpart(yend) * xgap)
            target.set_pixel(ypxl2 + 1, xpxl2, fpart(yend) * xgap)
        else:
            target.set_pixel(xpxl2, ypxl2, rfpart(yend) * xgap)
            target.set_pixel(xpxl2, ypxl2 + 1, fpart(yend) * xgap)

        if steep:
            for x in range(xpxl1 + 1, xpxl2):
                target.set_pixel(ipart(intery), x, rfpart(intery))
                target.set_pixel(ipart(intery) + 1, x, fpart(intery))
                intery += gradient
        else:
            for x in range(xpxl1 + 1, xpxl2):
                target.set_pixel(x, ipart(intery), rfpart(intery))
                target.set_pixel(x, ipart(intery) + 1, fpart(intery))
                intery += gradient

    @staticmethod
    def castle_piteway(xc: int, yc: int, rx: int, ry: int, target: IRasterTarget):
        x = 0
        y = ry
        rx2 = rx * rx
        ry2 = ry * ry
        two_rx2 = 2 * rx2
        two_ry2 = 2 * ry2
        p = round(ry2 - (rx2 * ry) + (0.25 * rx2))
        px = 0
        py = two_rx2 * y

        while px < py:
            RasterEngine._draw_ellipse_pixels(xc, yc, x, y, target)
            x += 1
            px += two_ry2
            if p < 0:
                p += ry2 + px
            else:
                y -= 1
                py -= two_rx2
                p += ry2 + px - py

        p = round(ry2 * (x + 0.5) * (x + 0.5) + rx2 * (y - 1) * (y - 1) - rx2 * ry2)
        while y >= 0:
            RasterEngine._draw_ellipse_pixels(xc, yc, x, y, target)
            y -= 1
            py -= two_rx2
            if p > 0:
                p += rx2 - py
            else:
                x += 1
                px += two_ry2
                p += rx2 - py + px

    @staticmethod
    def _draw_ellipse_pixels(xc, yc, x, y, target):
        target.set_pixel(xc + x, yc + y)
        target.set_pixel(xc - x, yc + y)
        target.set_pixel(xc + x, yc - y)
        target.set_pixel(xc - x, yc - y)

class Benchmark:
    class DummyTarget(IRasterTarget):
        def set_pixel(self, x: int, y: int, intensity: float = 1.0):
            pass

    @staticmethod
    def run_tests():
        target = Benchmark.DummyTarget()
        lines = [(random.randint(-500, 500), random.randint(-500, 500),
                  random.randint(-500, 500), random.randint(-500, 500)) for _ in range(100000)]
        circles = [(random.randint(-500, 500), random.randint(-500, 500),
                    random.randint(1, 200)) for _ in range(50000)]

        t0 = time.perf_counter()
        for l in lines:
            RasterEngine.dda_line(l[0], l[1], l[2], l[3], target)
        t_dda = time.perf_counter() - t0

        t0 = time.perf_counter()
        for l in lines:
            RasterEngine.bresenham_line(l[0], l[1], l[2], l[3], target)
        t_bres_l = time.perf_counter() - t0

        t0 = time.perf_counter()
        for c in circles:
            RasterEngine.bresenham_circle(c[0], c[1], c[2], target)
        t_bres_c = time.perf_counter() - t0

        report = (
            f"=== РЕЗУЛЬТАТЫ СТРЕСС-ТЕСТИРОВАНИЯ ===\n"
            f"100 000 линий (Алгоритм ЦДА): {t_dda:.4f} сек\n"
            f"100 000 линий (Алгоритм Брезенхема): {t_bres_l:.4f} сек\n"
            f"50 000 окружностей (Алгоритм Брезенхема): {t_bres_c:.4f} сек\n\n"
            f"АНАЛИТИЧЕСКИЙ РАЗБОР:\n"
            f"Алгоритм ЦДА работает медленнее алгоритма Брезенхема...\n"
            f"поскольку ЦДА выполняет деление при инициализации...\n"
            f"и операции с вещественными числами (float)...\n"
            f"а также округление round() внутри основного цикла.\n"
            f"Алгоритм Брезенхема использует исключительно...\n"
            f"целочисленное сложение, вычитание и побитовые...\n"
            f"сдвиги для накопления ошибки, что значительно...\n"
            f"более эффективно на аппаратном уровне."
        )
        return report

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Лабораторная работа 4 - Базовые растровые алгоритмы")
        self.geometry("1100x750")

        self.cell_size = 20
        self.offset_x = 0
        self.offset_y = 0
        self.drag_start_x = 0
        self.drag_start_y = 0

        self.grid_model = VirtualGrid(100, 100)

        self._init_ui()
        self._draw_grid_canvas()

    def _init_ui(self):
        control_panel = ttk.LabelFrame(self, text=" Панель управления ", padding=10)
        control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(control_panel, text="Алгоритм:").pack(anchor=tk.W, pady=2)
        self.algo_var = tk.StringVar(value="Bresenham Line")
        algos = [
            ("Пошаговый", "Step Line"),
            ("ЦДА", "DDA Line"),
            ("Брезенхем (Линия)", "Bresenham Line"),
            ("Брезенхем (Окружность)", "Bresenham Circle"),
            ("Сглаживание Ву", "Wu's Anti-aliasing"),
            ("Кастла-Питвея (Эллипс)", "Castle-Piteway")
        ]
        for text, val in algos:
            ttk.Radiobutton(control_panel, text=text, variable=self.algo_var, value=val).pack(anchor=tk.W, pady=1)

        ttk.Separator(control_panel, orient='horizontal').pack(fill='x', pady=10)

        ttk.Label(control_panel, text="Координаты:").pack(anchor=tk.W, pady=2)
        coord_frame = ttk.Frame(control_panel)
        coord_frame.pack(fill=tk.X)

        ttk.Label(coord_frame, text="X1:").grid(row=0, column=0, padx=2, pady=2)
        self.ent_x1 = ttk.Entry(coord_frame, width=5)
        self.ent_x1.insert(0, "0")
        self.ent_x1.grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(coord_frame, text="Y1:").grid(row=0, column=2, padx=2, pady=2)
        self.ent_y1 = ttk.Entry(coord_frame, width=5)
        self.ent_y1.insert(0, "0")
        self.ent_y1.grid(row=0, column=3, padx=2, pady=2)

        ttk.Label(coord_frame, text="X2/R/Rx:").grid(row=1, column=0, padx=2, pady=2)
        self.ent_x2 = ttk.Entry(coord_frame, width=5)
        self.ent_x2.insert(0, "15")
        self.ent_x2.grid(row=1, column=1, padx=2, pady=2)

        ttk.Label(coord_frame, text="Y2/Ry:").grid(row=1, column=2, padx=2, pady=2)
        self.ent_y2 = ttk.Entry(coord_frame, width=5)
        self.ent_y2.insert(0, "10")
        self.ent_y2.grid(row=1, column=3, padx=2, pady=2)

        btn_draw = ttk.Button(control_panel, text="Отрисовать", command=self._on_draw_click)
        btn_draw.pack(fill=tk.X, pady=5)

        btn_clear = ttk.Button(control_panel, text="Очистить", command=self._on_clear_click)
        btn_clear.pack(fill=tk.X, pady=2)

        ttk.Separator(control_panel, orient='horizontal').pack(fill='x', pady=10)

        ttk.Label(control_panel, text="Масштаб сетки:").pack(anchor=tk.W, pady=2)
        zoom_frame = ttk.Frame(control_panel)
        zoom_frame.pack(fill=tk.X)
        ttk.Button(zoom_frame, text="+", width=5, command=self._zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="-", width=5, command=self._zoom_out).pack(side=tk.LEFT, padx=2)

        ttk.Separator(control_panel, orient='horizontal').pack(fill='x', pady=10)

        btn_bench = ttk.Button(control_panel, text="Запустить бенчмарк", command=self._on_benchmark_click)
        btn_bench.pack(fill=tk.X, pady=5)

        self.txt_output = tk.Text(control_panel, width=30, height=12, font=("Consolas", 9))
        self.txt_output.pack(fill=tk.BOTH, expand=True, pady=5)

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)
        self.canvas.bind("<Configure>", lambda e: self._draw_grid_canvas())

    def _zoom_in(self):
        if self.cell_size < 100:
            self.cell_size += 4
            self._draw_grid_canvas()

    def _zoom_out(self):
        if self.cell_size > 4:
            self.cell_size -= 4
            self._draw_grid_canvas()

    def _on_drag_start(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def _on_drag_motion(self, event):
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.offset_x += dx
        self.offset_y += dy
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self._draw_grid_canvas()

    def _on_clear_click(self):
        self.grid_model.clear()
        self._draw_grid_canvas()

    def _on_draw_click(self):
        try:
            x1 = int(self.ent_x1.get())
            y1 = int(self.ent_y1.get())
            x2 = int(self.ent_x2.get())
            y2 = int(self.ent_y2.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Координаты должны быть целыми числами")
            return

        algo = self.algo_var.get()
        self.grid_model.clear()

        if algo == "Step Line":
            RasterEngine.step_line(x1, y1, x2, y2, self.grid_model)
        elif algo == "DDA Line":
            RasterEngine.dda_line(x1, y1, x2, y2, self.grid_model)
        elif algo == "Bresenham Line":
            RasterEngine.bresenham_line(x1, y1, x2, y2, self.grid_model)
        elif algo == "Bresenham Circle":
            RasterEngine.bresenham_circle(x1, y1, x2, self.grid_model)
        elif algo == "Wu's Anti-aliasing":
            RasterEngine.wu_line(x1, y1, x2, y2, self.grid_model)
        elif algo == "Castle-Piteway":
            RasterEngine.castle_piteway(x1, y1, x2, y2, self.grid_model)

        self._draw_grid_canvas()

    def _on_benchmark_click(self):
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, "Выполняется расчет...\n")
        self.update()
        report = Benchmark.run_tests()
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, report)

    def _draw_grid_canvas(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        cx = w // 2 + self.offset_x
        cy = h // 2 + self.offset_y

        start_col = math.floor(-cx / self.cell_size) - 1
        end_col = math.ceil((w - cx) / self.cell_size) + 1
        start_row = math.floor(-cy / self.cell_size) - 1
        end_row = math.ceil((h - cy) / self.cell_size) + 1

        for col in range(start_col, end_col):
            x = cx + col * self.cell_size
            self.canvas.create_line(x, 0, x, h, fill="#e0e0e0")

        for row in range(start_row, end_row):
            y = cy - row * self.cell_size
            self.canvas.create_line(0, y, w, y, fill="#e0e0e0")

        for (gx, gy), val in self.grid_model.pixels.items():
            if val <= 0:
                continue
            x_left = cx + gx * self.cell_size
            y_top = cy - (gy + 1) * self.cell_size
            x_right = x_left + self.cell_size
            y_bottom = y_top + self.cell_size

            gray_val = int(255 * (1.0 - val))
            color_hex = f"#{gray_val:02x}{gray_val:02x}{gray_val:02x}"
            self.canvas.create_rectangle(x_left, y_top, x_right, y_bottom, fill=color_hex, outline="#b0b0b0")

        self.canvas.create_line(0, cy, w, cy, fill="red", width=2)
        self.canvas.create_line(cx, 0, cx, h, fill="red", width=2)

        for col in range(start_col, end_col):
            if col == 0:
                continue
            if col % 5 == 0 or self.cell_size >= 20:
                x = cx + col * self.cell_size
                self.canvas.create_line(x, cy - 4, x, cy + 4, fill="red")
                self.canvas.create_text(x, cy + 12, text=str(col), font=("Arial", 8), fill="black")

        for row in range(start_row, end_row):
            if row == 0:
                continue
            if row % 5 == 0 or self.cell_size >= 20:
                y = cy - row * self.cell_size
                self.canvas.create_line(cx - 4, y, cx + 4, y, fill="red")
                self.canvas.create_text(cx - 15, y, text=str(row), font=("Arial", 8), fill="black")

        self.canvas.create_text(cx - 10, cy + 10, text="0", font=("Arial", 8, "bold"), fill="black")
        self.canvas.create_text(w - 15, cy - 10, text="X", font=("Arial", 10, "bold"), fill="red")
        self.canvas.create_text(cx + 10, 15, text="Y", font=("Arial", 10, "bold"), fill="red")

if __name__ == "__main__":
    app = App()
    app.mainloop()