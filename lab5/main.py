import tkinter as tk

EPS = 1e-7

def eps_equal(a, b):
    return abs(a - b) < EPS

def eps_less(a, b):
    return (b - a) > EPS

def eps_greater(a, b):
    return (a - b) > EPS

# --- 2. АЛГОРИТМ САЗЕРЛЕНДА-КОЭНА ---
INSIDE = 0  # 0000
LEFT   = 1  # 0001
RIGHT  = 2  # 0010
BOTTOM = 4  # 0100
TOP    = 8  # 1000

def compute_code(x, y, rect):
    code = INSIDE
    if eps_less(x, rect['xmin']):
        code |= LEFT
    elif eps_greater(x, rect['xmax']):
        code |= RIGHT
    if eps_less(y, rect['ymin']):
        code |= BOTTOM
    elif eps_greater(y, rect['ymax']):
        code |= TOP
    return code

def cohen_sutherland_clip(x1, y1, x2, y2, rect):
    code1 = compute_code(x1, y1, rect)
    code2 = compute_code(x2, y2, rect)
    accept = False

    while True:
        if not (code1 | code2):
            accept = True
            break
        elif code1 & code2:
            break
        else:
            x, y = 0.0, 0.0
            outcode = code1 if code1 else code2

            if outcode & TOP:
                x = x1 + (x2 - x1) * (rect['ymax'] - y1) / (y2 - y1)
                y = rect['ymax']
            elif outcode & BOTTOM:
                x = x1 + (x2 - x1) * (rect['ymin'] - y1) / (y2 - y1)
                y = rect['ymin']
            elif outcode & RIGHT:
                y = y1 + (y2 - y1) * (rect['xmax'] - x1) / (x2 - x1)
                x = rect['xmax']
            elif outcode & LEFT:
                y = y1 + (y2 - y1) * (rect['xmin'] - x1) / (x2 - x1)
                x = rect['xmin']

            if outcode == code1:
                x1, y1 = x, y
                code1 = compute_code(x1, y1, rect)
            else:
                x2, y2 = x, y
                code2 = compute_code(x2, y2, rect)

    if accept:
        return x1, y1, x2, y2
    return None

# --- ГРАФИЧЕСКИЙ ИНТЕРФЕЙС (TKINTER) ---
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Лабораторная работа №5 - Вариант 1 (Сазерленд-Коэн)")
        self.geometry("800x600")

        self.canvas = tk.Canvas(self, bg="#121212")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.rect = {'xmin': 150.0, 'ymin': 100.0, 'xmax': 550.0, 'ymax': 400.0}
        self.segments = [
            (80.0, 200.0, 650.0, 300.0),
            (200.0, 50.0, 350.0, 500.0),
            (50.0, 50.0, 120.0, 100.0),
            (300.0, 150.0, 450.0, 350.0)
        ]

        self.drag_data = {"x": 0, "y": 0, "is_dragging": False}

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.draw()

    def on_press(self, event):
        if self.rect['xmin'] <= event.x <= self.rect['xmax'] and self.rect['ymin'] <= event.y <= self.rect['ymax']:
            self.drag_data["is_dragging"] = True
            self.drag_data["x"] = event.x - self.rect['xmin']
            self.drag_data["y"] = event.y - self.rect['ymin']

    def on_drag(self, event):
        if self.drag_data["is_dragging"]:
            w = self.rect['xmax'] - self.rect['xmin']
            h = self.rect['ymax'] - self.rect['ymin']
            self.rect['xmin'] = float(event.x - self.drag_data["x"])
            self.rect['ymin'] = float(event.y - self.drag_data["y"])
            self.rect['xmax'] = self.rect['xmin'] + w
            self.rect['ymax'] = self.rect['ymin'] + h
            self.draw()

    def on_release(self, event):
        self.drag_data["is_dragging"] = False

    def draw(self):
        self.canvas.delete("all")

        # 1. Отрисовка исходных отрезков (серый)
        for x1, y1, x2, y2 in self.segments:
            self.canvas.create_line(x1, y1, x2, y2, fill="#555555", width=2)

        # 2. Отрисовка рамки отсечения (голубой)
        self.canvas.create_rectangle(
            self.rect['xmin'], self.rect['ymin'], self.rect['xmax'], self.rect['ymax'],
            outline="#00e5ff", width=2
        )

        # 3. Отрисовка обрезанных отрезков (зеленый)
        for x1, y1, x2, y2 in self.segments:
            clipped = cohen_sutherland_clip(x1, y1, x2, y2, self.rect)
            if clipped:
                cx1, cy1, cx2, cy2 = clipped
                self.canvas.create_line(cx1, cy1, cx2, cy2, fill="#00ff66", width=3)

if __name__ == "__main__":
    app = Application()
    app.mainloop()