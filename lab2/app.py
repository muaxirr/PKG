import os
import time
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ExifTags

class ImageMetadataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор графических файлов — Лабораторная работа №2")
        self.root.geometry("1000x600")

        # Верхняя панель управления
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X)

        self.btn_select = ttk.Button(control_frame, text="Выбрать папку", command=self.select_folder)
        self.btn_select.pack(side=tk.LEFT, padx=5)

        self.lbl_status = ttk.Label(control_frame, text="Папка не выбрана")
        self.lbl_status.pack(side=tk.LEFT, padx=10)

        # Таблица результатов
        columns = ("filename", "resolution", "dpi", "color_depth", "compression", "extra")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")

        self.tree.heading("filename", text="Имя файла")
        self.tree.heading("resolution", text="Размер (пикс)")
        self.tree.heading("dpi", text="Разрешение (DPI)")
        self.tree.heading("color_depth", text="Глубина цвета")
        self.tree.heading("compression", text="Сжатие")
        self.tree.heading("extra", text="Доп. информация")

        self.tree.column("filename", width=200)
        self.tree.column("resolution", width=120)
        self.tree.column("dpi", width=120)
        self.tree.column("color_depth", width=100)
        self.tree.column("compression", width=120)
        self.tree.column("extra", width=250)

        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        supported_exts = ('.jpg', '.jpeg', '.gif', '.tif', '.tiff', '.bmp', '.png', '.pcx')
        
        start_time = time.time()
        count = 0

        # Обход файлов (включая быстрый сканер os.walk)
        for root_dir, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(supported_exts):
                    full_path = os.path.join(root_dir, file)
                    info = self.extract_image_info(full_path, file)
                    if info:
                        self.tree.insert("", tk.END, values=info)
                        count += 1

        elapsed_time = time.time() - start_time
        self.lbl_status.config(text=f"Обработано файлов: {count} за {elapsed_time:.2f} сек.")

    def extract_image_info(self, file_path, file_name):
        try:
            with Image.open(file_path) as img:
                # 1. Размер изображения
                width, height = img.size
                resolution = f"{width} x {height}"

                # 2. Разрешение (DPI)
                dpi_info = img.info.get('dpi')
                if dpi_info:
                    dpi = f"{round(dpi_info[0])} x {round(dpi_info[1])}"
                else:
                    dpi = "Не задано"

                # 3. Глубина цвета (в битах на пиксель)
                mode_bpp = {
                    '1': "1 bit (Монохром)",
                    'L': "8 bit (Оттенки серого)",
                    'P': "8 bit (Палитра)",
                    'RGB': "24 bit (True Color)",
                    'RGBA': "32 bit (RGB + Альфа)",
                    'CMYK': "32 bit (Полноцветная печать)",
                    'I;16': "16 bit (Целые)",
                    'F': "32 bit (Float)"
                }
                color_depth = mode_bpp.get(img.mode, f"{img.mode}")

                # 4. Сжатие
                compression = img.info.get('compression', 'Неизвестно / Стандартное')
                if img.format == 'JPEG':
                    compression = "JPEG (C потерями)"
                elif img.format == 'PNG':
                    compression = "Deflate (Без потерь)"
                elif img.format == 'GIF':
                    compression = "LZW (Без потерь)"
                elif img.format == 'BMP':
                    compression = img.info.get('compression', 'Без сжатия')

                # 5. Дополнительная информация (на доп. баллы)
                extra = []
                if img.format == 'GIF':
                    palette = img.getpalette()
                    num_colors = len(palette) // 3 if palette else 0
                    extra.append(f"Цветов в палитре: {num_colors}")
                    if getattr(img, "is_animated", False):
                        extra.append(f"Кадров: {img.n_frames}")
                
                if img.format == 'JPEG':
                    if hasattr(img, 'quantization'):
                        extra.append(f"Матриц квантования: {len(img.quantization)}")
                    else:
                        extra.append("Матрицы квантования присутствуют")

                if img.format in ('TIFF', 'TIF'):
                    extra.append(f"Сжатие TIFF: {img.info.get('compression', 'None')}")

                extra_str = "; ".join(extra) if extra else "-"

                return (file_name, resolution, dpi, color_depth, compression, extra_str)

        except Exception as e:
            return (file_name, "Ошибка чтения", "-", "-", "-", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageMetadataApp(root)
    root.mainloop()