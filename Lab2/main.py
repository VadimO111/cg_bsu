import cv2
import numpy as np
from PIL import Image
import customtkinter as ctk
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ImageProcessorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Лабораторная №2 - Вариант 8 (Обработка изображений)")
        self.geometry("1100x650")
        self.minsize(900, 500)
        self.cv_img = None
        self.processed_img = None
        self.setup_ui()

    def setup_ui(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=10)
        self.sidebar.pack(side="left", fill="y", padx=15, pady=15)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="Методы\nВариант 8", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20)

        self.btn_load = ctk.CTkButton(self.sidebar, text="📂 Загрузить фото", command=self.load_image)
        self.btn_load.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.sidebar, text="Фильтры:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 5))

        self.btn_sharp = ctk.CTkButton(self.sidebar, text="ВЧ Фильтр (Резкость)", command=self.apply_sharpen)
        self.btn_sharp.pack(pady=5, padx=20, fill="x")

        self.btn_thresh_basic = ctk.CTkButton(self.sidebar, text="Глобальный порог (T=127)", command=self.apply_basic_threshold)
        self.btn_thresh_basic.pack(pady=5, padx=20, fill="x")

        self.btn_thresh_otsu = ctk.CTkButton(self.sidebar, text="Глобальный порог (Otsu)", command=self.apply_otsu_threshold)
        self.btn_thresh_otsu.pack(pady=5, padx=20, fill="x")

        self.btn_save = ctk.CTkButton(self.sidebar, text="💾 Сохранить результат", command=self.save_image, fg_color="green", hover_color="darkgreen")
        self.btn_save.pack(pady=20, padx=20, fill="x", side="bottom")

        self.images_frame = ctk.CTkFrame(self, corner_radius=10)
        self.images_frame.pack(side="right", fill="both", expand=True, padx=(0, 15), pady=15)

        self.images_frame.grid_columnconfigure(0, weight=1)
        self.images_frame.grid_columnconfigure(1, weight=1)
        self.images_frame.grid_rowconfigure(1, weight=1)

        self.lbl_title_orig = ctk.CTkLabel(self.images_frame, text="Оригинал", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_title_orig.grid(row=0, column=0, pady=10)

        self.lbl_title_proc = ctk.CTkLabel(self.images_frame, text="Результат", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_title_proc.grid(row=0, column=1, pady=10)

        self.lbl_orig_img = ctk.CTkLabel(self.images_frame, text="Нет изображения")
        self.lbl_orig_img.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.lbl_proc_img = ctk.CTkLabel(self.images_frame, text="Нет результата")
        self.lbl_proc_img.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if file_path:
            img_array = np.fromfile(file_path, np.uint8)
            self.cv_img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            self.processed_img = self.cv_img.copy()
            self.update_images()

    def apply_sharpen(self):
        if self.cv_img is None: return
        kernel = np.array([[ 0, -1,  0],
                           [-1,  5, -1],
                           [ 0, -1,  0]])
        self.processed_img = cv2.filter2D(self.cv_img, -1, kernel)
        self.update_images()

    def apply_basic_threshold(self):
        if self.cv_img is None: return
        gray = cv2.cvtColor(self.cv_img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        self.processed_img = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        self.update_images()

    def apply_otsu_threshold(self):
        if self.cv_img is None: return
        gray = cv2.cvtColor(self.cv_img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        self.processed_img = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        self.update_images()

    def save_image(self):
        if self.processed_img is None:
            messagebox.showwarning("Ошибка", "Сначала обработайте изображение!")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")]
        )
        if file_path:
            cv2.imencode(file_path[-4:], self.processed_img)[1].tofile(file_path)
            messagebox.showinfo("Успех", "Изображение успешно сохранено!")

    def update_images(self):
        if self.cv_img is not None:
            self.display_image(self.cv_img, self.lbl_orig_img)
        if self.processed_img is not None:
            self.display_image(self.processed_img, self.lbl_proc_img)

    def display_image(self, cv_img, label_widget):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        widget_width = self.images_frame.winfo_width() // 2 - 40
        widget_height = self.images_frame.winfo_height() - 60
        if widget_width < 100 or widget_height < 100:
            widget_width, widget_height = 400, 400

        ctk_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(widget_width, widget_height))
        label_widget.configure(image=ctk_img, text="")
        label_widget.image = ctk_img

if __name__ == "__main__":
    app = ImageProcessorApp()
    app.mainloop()