import cv2
import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

def linear_contrast_stretching(img, c=0, d=255):
    img_float = img.astype(np.float32)
    a_val = np.min(img_float)
    b_val = np.max(img_float)
    if b_val == a_val:
        return img
    result = ((img_float - a_val) / (b_val - a_val)) * (d - c) + c
    return np.clip(result, 0, 255).astype(np.uint8)

def histogram_equalization_grayscale(img):
    return cv2.equalizeHist(img)

def histogram_equalization_rgb_channels(img):
    b, g, r = cv2.split(img)
    return cv2.merge([cv2.equalizeHist(b), cv2.equalizeHist(g), cv2.equalizeHist(r)])

def histogram_equalization_hsv_brightness(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v_eq = cv2.equalizeHist(v)
    return cv2.cvtColor(cv2.merge([h, s, v_eq]), cv2.COLOR_HSV2BGR)

def pixelwise_addition(img1, img2, alpha=1.0, beta=1.0, gamma=0):
    return cv2.addWeighted(img1, alpha, img2, beta, gamma)

def pixelwise_subtraction(img1, img2):
    return cv2.subtract(img1, img2)

def pixelwise_inversion(img):
    return cv2.bitwise_not(img)

def pixelwise_log_transform(img, c=30.0):
    img_float = img.astype(np.float32)
    result = c * np.log1p(img_float)
    result = (result / result.max()) * 255
    return result.astype(np.uint8)

def pixelwise_gamma_correction(img, gamma=1.0):
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(img, table)


def plot_histograms(original, stretched, eq_rgb, eq_hsv, title="Гистограммы"):
    fig, axes = plt.subplots(2, 4, figsize=(20, 8))
    images = [original, stretched, eq_rgb, eq_hsv]
    titles = ["Оригинал", "Линейное контрастирование",
              "Эквализация RGB", "Эквализация HSV (V)"]
    for i, (img, t) in enumerate(zip(images, titles)):
        axes[0, i].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        axes[0, i].set_title(t)
        axes[0, i].axis('off')
        colors = ['b', 'g', 'r']
        for j, color in enumerate(colors):
            hist = cv2.calcHist([img], [j], None, [256], [0, 256])
            axes[1, i].plot(hist, color=color)
        axes[1, i].set_title(f"Гистограмма: {t}")
        axes[1, i].set_xlim([0, 256])
    plt.suptitle(title, fontsize=14)
    plt.tight_layout()
    plt.show()


class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа 3 — Обработка изображений")
        self.root.geometry("1200x800")

        self.original_img = None
        self.second_img = None
        self.processed_img = None

        self._create_menu()
        self._create_interface()

    def _create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Открыть изображение 1", command=self._open_image1)
        file_menu.add_command(label="Открыть изображение 2", command=self._open_image2)
        file_menu.add_separator()
        file_menu.add_command(label="Сохранить результат", command=self._save_result)
        file_menu.add_command(label="Выход", command=self.root.quit)

    def _create_interface(self):
        # Панель управления
        control_frame = Frame(self.root, width=320, bg="#f0f0f0")
        control_frame.pack(side=LEFT, fill=Y, padx=5, pady=5)

        Label(control_frame, text="Методы обработки", font=("Arial", 12, "bold"),
              bg="#f0f0f0").pack(pady=10)

        Label(control_frame, text="Гистограмма и контраст",
              font=("Arial", 10, "bold"), bg="#f0f0f0").pack(pady=(10, 5))

        Button(control_frame, text="Линейное контрастирование",
               command=self._apply_linear_contrast, width=35).pack(pady=2)
        Button(control_frame, text="Эквализация гистограммы (серое)",
               command=self._apply_hist_eq_gray, width=35).pack(pady=2)
        Button(control_frame, text="Эквализация RGB каналов",
               command=self._apply_hist_eq_rgb, width=35).pack(pady=2)
        Button(control_frame, text="Эквализация HSV (яркость V)",
               command=self._apply_hist_eq_hsv, width=35).pack(pady=2)
        Button(control_frame, text="Сравнить все методы",
               command=self._compare_all, width=35).pack(pady=2)

        Label(control_frame, text="Поэлементные операции",
              font=("Arial", 10, "bold"), bg="#f0f0f0").pack(pady=(15, 5))

        Button(control_frame, text="Сложение изображений",
               command=self._apply_addition, width=35).pack(pady=2)
        Button(control_frame, text="Вычитание изображений",
               command=self._apply_subtraction, width=35).pack(pady=2)
        Button(control_frame, text="Инверсия",
               command=self._apply_inversion, width=35).pack(pady=2)
        Button(control_frame, text="Логарифмическое преобразование",
               command=self._apply_log_transform, width=35).pack(pady=2)

        gamma_frame = Frame(control_frame, bg="#f0f0f0")
        gamma_frame.pack(pady=5)
        Label(gamma_frame, text="Гамма:", bg="#f0f0f0").pack(side=LEFT)
        self.gamma_var = DoubleVar(value=1.0)
        Scale(gamma_frame, from_=0.1, to=5.0, resolution=0.1,
              orient=HORIZONTAL, variable=self.gamma_var,
              command=lambda v: self._apply_gamma()).pack(side=LEFT)

        # Область отображения
        display_frame = Frame(self.root)
        display_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=5, pady=5)

        self.canvas = Canvas(display_frame, bg="white")
        self.canvas.pack(fill=BOTH, expand=True)

    def _open_image1(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.png *.bmp *.jpeg *.tif")])
        if path:
            try:
                # Чтение с поддержкой кириллицы в пути
                img_array = np.fromfile(path, dtype=np.uint8)
                self.original_img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if self.original_img is not None:
                    self._display_image(self.original_img, "Оригинал")
                else:
                    messagebox.showerror("Ошибка", "Не удалось декодировать изображение!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")

    def _open_image2(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.png *.bmp *.jpeg *.tif")])
        if path:
            try:
                img_array = np.fromfile(path, dtype=np.uint8)
                self.second_img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if self.second_img is not None:
                    messagebox.showinfo("Успех", "Второе изображение загружено!")
                else:
                    messagebox.showerror("Ошибка", "Не удалось декодировать изображение!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")

    def _save_result(self):
        if self.processed_img is not None:
            path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
            if path:
                cv2.imencode('.png', self.processed_img)[1].tofile(path)
                messagebox.showinfo("Успех", "Изображение сохранено!")

    def _display_image(self, img, title=""):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)

        self.root.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width > 1 and canvas_height > 1:
            img_pil.thumbnail((canvas_width - 40, canvas_height - 40))

        self.photo = ImageTk.PhotoImage(img_pil)
        self.canvas.delete("all")
        self.canvas.create_image(20, 30, anchor=NW, image=self.photo)
        if title:
            self.canvas.create_text(canvas_width // 2, 15, text=title,
                                    font=("Arial", 12, "bold"))
        self.canvas.update()

    def _apply_linear_contrast(self):
        if self.original_img is None:
            messagebox.showwarning("Внимание", "Сначала откройте изображение!")
            return
        gray = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2GRAY)
        self.processed_img = linear_contrast_stretching(gray)
        self.processed_img = cv2.cvtColor(self.processed_img, cv2.COLOR_GRAY2BGR)
        self._display_image(self.processed_img, "Линейное контрастирование")

    def _apply_hist_eq_gray(self):
        if self.original_img is None:
            messagebox.showwarning("Внимание", "Сначала откройте изображение!")
            return
        gray = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2GRAY)
        self.processed_img = histogram_equalization_grayscale(gray)
        self.processed_img = cv2.cvtColor(self.processed_img, cv2.COLOR_GRAY2BGR)
        self._display_image(self.processed_img, "Эквализация гистограммы (серое)")

    def _apply_hist_eq_rgb(self):
        if self.original_img is None:
            messagebox.showwarning("Внимание", "Сначала откройте изображение!")
            return
        self.processed_img = histogram_equalization_rgb_channels(self.original_img)
        self._display_image(self.processed_img, "Эквализация RGB")

    def _apply_hist_eq_hsv(self):
        if self.original_img is None:
            messagebox.showwarning("Внимание", "Сначала откройте изображение!")
            return
        self.processed_img = histogram_equalization_hsv_brightness(self.original_img)
        self._display_image(self.processed_img, "Эквализация HSV (V)")

    def _compare_all(self):
        if self.original_img is None:
            messagebox.showwarning("Внимание", "Сначала откройте изображение!")
            return
        gray = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2GRAY)
        stretched = linear_contrast_stretching(gray)
        stretched_bgr = cv2.cvtColor(stretched, cv2.COLOR_GRAY2BGR)
        eq_rgb = histogram_equalization_rgb_channels(self.original_img)
        eq_hsv = histogram_equalization_hsv_brightness(self.original_img)
        plot_histograms(self.original_img, stretched_bgr, eq_rgb, eq_hsv,
                        "Сравнение методов контрастирования")

    def _apply_addition(self):
        if self.original_img is None or self.second_img is None:
            messagebox.showwarning("Внимание", "Откройте оба изображения!")
            return
        h, w = self.original_img.shape[:2]
        img2_resized = cv2.resize(self.second_img, (w, h))
        self.processed_img = pixelwise_addition(self.original_img, img2_resized, 0.5, 0.5)
        self._display_image(self.processed_img, "Сложение изображений")

    def _apply_subtraction(self):
        if self.original_img is None or self.second_img is None:
            messagebox.showwarning("Внимание", "Откройте оба изображения!")
            return
        h, w = self.original_img.shape[:2]
        img2_resized = cv2.resize(self.second_img, (w, h))
        self.processed_img = pixelwise_subtraction(self.original_img, img2_resized)
        self._display_image(self.processed_img, "Вычитание изображений")

    def _apply_inversion(self):
        if self.original_img is None:
            messagebox.showwarning("Внимание", "Сначала откройте изображение!")
            return
        self.processed_img = pixelwise_inversion(self.original_img)
        self._display_image(self.processed_img, "Инверсия")

    def _apply_log_transform(self):
        if self.original_img is None:
            messagebox.showwarning("Внимание", "Сначала откройте изображение!")
            return
        gray = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2GRAY)
        self.processed_img = pixelwise_log_transform(gray)
        self.processed_img = cv2.cvtColor(self.processed_img, cv2.COLOR_GRAY2BGR)
        self._display_image(self.processed_img, "Логарифмическое преобразование")

    def _apply_gamma(self):
        if self.original_img is None:
            return
        gamma = self.gamma_var.get()
        self.processed_img = pixelwise_gamma_correction(self.original_img, gamma)
        self._display_image(self.processed_img, f"Гамма-коррекция (γ={gamma:.1f})")


if __name__ == "__main__":
    root = Tk()
    app = ImageProcessingApp(root)
    root.mainloop()