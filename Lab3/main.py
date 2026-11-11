import time
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import raster_algos 

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class RasterizationApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Лабораторная №3 - Базовые растровые алгоритмы")
        self.geometry("1400x850")
        self.minsize(1100, 700)
        
        self.cell_size = 20
        self.grid_color = "#333333"
        self.axis_color = "#AAAAAA"
        self.pixel_color = "#00FFCC"
        
        self.drawn_shapes_pixels = []
        self.click_state = 0 
        
        self.setup_ui()
        self.draw_grid_and_axes()

    def setup_ui(self):
        # ЛЕВАЯ ПАНЕЛЬ
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=10)
        self.sidebar.pack(side="left", fill="y", padx=15, pady=15)

        ctk.CTkLabel(self.sidebar, text="Настройки", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        self.algo_var = ctk.StringVar(value="Брезенхем (Линия)")
        algos = ["Пошаговый (Линия)", "ЦДА (Линия)", "Брезенхем (Линия)", "Брезенхем (Окружность)", "Ву (Сглаживание) - Бонус"]
        self.algo_menu = ctk.CTkOptionMenu(self.sidebar, values=algos, variable=self.algo_var, command=self.on_algo_change)
        self.algo_menu.pack(pady=10, padx=20, fill="x")

        # Зум от 2 до 50
        ctk.CTkLabel(self.sidebar, text="Масштаб (Zoom 2-50):", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0))
        self.slider_scale = ctk.CTkSlider(self.sidebar, from_=2, to=50, command=self.on_scale_change)
        self.slider_scale.set(self.cell_size)
        self.slider_scale.pack(pady=5, padx=20, fill="x")

        self.coords_frame = ctk.CTkFrame(self.sidebar)
        self.coords_frame.pack(pady=10, padx=20, fill="x")

        self.lbl_x0 = ctk.CTkLabel(self.coords_frame, text="X0:")
        self.lbl_x0.grid(row=0, column=0, padx=5, pady=5)
        self.ent_x0 = ctk.CTkEntry(self.coords_frame, width=50)
        self.ent_x0.grid(row=0, column=1, padx=5, pady=5)
        self.ent_x0.insert(0, "0")

        self.lbl_y0 = ctk.CTkLabel(self.coords_frame, text="Y0:")
        self.lbl_y0.grid(row=0, column=2, padx=5, pady=5)
        self.ent_y0 = ctk.CTkEntry(self.coords_frame, width=50)
        self.ent_y0.grid(row=0, column=3, padx=5, pady=5)
        self.ent_y0.insert(0, "0")

        self.lbl_x1 = ctk.CTkLabel(self.coords_frame, text="X1:")
        self.lbl_x1.grid(row=1, column=0, padx=5, pady=5)
        self.ent_x1 = ctk.CTkEntry(self.coords_frame, width=50)
        self.ent_x1.grid(row=1, column=1, padx=5, pady=5)
        self.ent_x1.insert(0, "15")

        self.lbl_y1 = ctk.CTkLabel(self.coords_frame, text="Y1:")
        self.lbl_y1.grid(row=1, column=2, padx=5, pady=5)
        self.ent_y1 = ctk.CTkEntry(self.coords_frame, width=50)
        self.ent_y1.grid(row=1, column=3, padx=5, pady=5)
        self.ent_y1.insert(0, "10")

        ctk.CTkLabel(self.sidebar, text="ЛКМ по сетке = выбрать точки", text_color="gray", font=ctk.CTkFont(size=11)).pack(pady=0)

        self.btn_draw = ctk.CTkButton(self.sidebar, text="✏️ Нарисовать", command=self.draw_shape)
        self.btn_draw.pack(pady=10, padx=20, fill="x")

        self.btn_clear = ctk.CTkButton(self.sidebar, text="🗑 Очистить", command=self.clear_canvas, fg_color="#883333", hover_color="#552222")
        self.btn_clear.pack(pady=5, padx=20, fill="x")

        self.lbl_time = ctk.CTkLabel(self.sidebar, text="Время: 0 ns", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00FFCC")
        self.lbl_time.pack(pady=10, padx=20)

        # Текстовое поле для журнала шагов
        ctk.CTkLabel(self.sidebar, text="Ход алгоритма (Лог):", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0))
        self.textbox_log = ctk.CTkTextbox(self.sidebar, height=250)
        self.textbox_log.pack(pady=5, padx=20, fill="both", expand=True)

        # ПРАВАЯ ПАНЕЛЬ (ХОЛСТ)
        self.canvas_frame = ctk.CTkFrame(self, corner_radius=10)
        self.canvas_frame.pack(side="right", fill="both", expand=True, padx=(0, 15), pady=15)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#1E1E1E", highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.canvas.bind("<Configure>", lambda e: self.redraw_all())
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def on_algo_change(self, choice):
        self.click_state = 0 
        if choice == "Брезенхем (Окружность)":
            self.lbl_x0.configure(text="Xc:")
            self.lbl_y0.configure(text="Yc:")
            self.lbl_x1.configure(text="R:")
            self.ent_x1.delete(0, 'end'); self.ent_x1.insert(0, "10")
            self.lbl_y1.grid_remove(); self.ent_y1.grid_remove()
        else:
            self.lbl_x0.configure(text="X0:"); self.lbl_y0.configure(text="Y0:")
            self.lbl_x1.configure(text="X1:")
            self.lbl_y1.grid(row=1, column=2, padx=5, pady=5)
            self.ent_y1.grid(row=1, column=3, padx=5, pady=5)

    def on_scale_change(self, value):
        self.cell_size = int(value)
        self.redraw_all()

    def on_canvas_click(self, event):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        grid_x = round((event.x - cx) / self.cell_size)
        grid_y = round((cy - event.y) / self.cell_size)

        if self.click_state == 0:
            self.ent_x0.delete(0, 'end'); self.ent_x0.insert(0, str(grid_x))
            self.ent_y0.delete(0, 'end'); self.ent_y0.insert(0, str(grid_y))
            self.click_state = 1
        else:
            if self.algo_var.get() == "Брезенхем (Окружность)":
                try:
                    xc, yc = int(self.ent_x0.get()), int(self.ent_y0.get())
                    r = int(((grid_x - xc)**2 + (grid_y - yc)**2)**0.5)
                    self.ent_x1.delete(0, 'end'); self.ent_x1.insert(0, str(r))
                except ValueError: pass
            else:
                self.ent_x1.delete(0, 'end'); self.ent_x1.insert(0, str(grid_x))
                self.ent_y1.delete(0, 'end'); self.ent_y1.insert(0, str(grid_y))
            self.click_state = 0
            self.draw_shape()

    def redraw_all(self):
        self.canvas.delete("all")
        self.draw_grid_and_axes()
        for shape_pixels in self.drawn_shapes_pixels:
            self.render_pixels_to_canvas(shape_pixels)

    def draw_grid_and_axes(self):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w < 10 or h < 10: return
        self.cx, self.cy = w // 2, h // 2

        if self.cell_size >= 5:
            for i in range(self.cx % self.cell_size, w, self.cell_size):
                self.canvas.create_line(i, 0, i, h, fill=self.grid_color, tags="grid")
            for i in range(self.cy % self.cell_size, h, self.cell_size):
                self.canvas.create_line(0, i, w, i, fill=self.grid_color, tags="grid")

        self.canvas.create_line(0, self.cy, w, self.cy, fill=self.axis_color, width=2, tags="axis")
        self.canvas.create_line(self.cx, 0, self.cx, h, fill=self.axis_color, width=2, tags="axis")

        step = max(1, 50 // self.cell_size) 
        for x in range(self.cx + self.cell_size * step, w, self.cell_size * step):
            self.canvas.create_text(x, self.cy + 10, text=str((x - self.cx) // self.cell_size), fill=self.axis_color)
        for x in range(self.cx - self.cell_size * step, 0, -self.cell_size * step):
            self.canvas.create_text(x, self.cy + 10, text=str((x - self.cx) // self.cell_size), fill=self.axis_color)
        for y in range(self.cy + self.cell_size * step, h, self.cell_size * step):
            self.canvas.create_text(self.cx - 15, y, text=str(-(y - self.cy) // self.cell_size), fill=self.axis_color)
        for y in range(self.cy - self.cell_size * step, 0, -self.cell_size * step):
            self.canvas.create_text(self.cx - 15, y, text=str(-(y - self.cy) // self.cell_size), fill=self.axis_color)

    def draw_pixel(self, x, y, color=None):
        if color is None: color = self.pixel_color
        px, py = self.cx + x * self.cell_size, self.cy - y * self.cell_size
        self.canvas.create_rectangle(px, py - self.cell_size, px + self.cell_size, py, fill=color, outline="#111111", tags="shape")

    def render_pixels_to_canvas(self, points):
        for pt in points:
            if len(pt) == 2:
                self.draw_pixel(pt[0], pt[1])
            else:
                intensity = max(0.0, min(1.0, pt[2]))
                hex_color = f"#{int(0*intensity):02x}{int(255*intensity):02x}{int(204*intensity):02x}"
                self.draw_pixel(pt[0], pt[1], color=hex_color)

    def clear_canvas(self):
        self.drawn_shapes_pixels.clear()
        self.redraw_all()
        self.lbl_time.configure(text="Время: 0 ns")
        self.textbox_log.delete("1.0", tk.END)

    def draw_shape(self):
        algo = self.algo_var.get()
        try:
            x0, y0, x1 = int(self.ent_x0.get()), int(self.ent_y0.get()), int(self.ent_x1.get())
            y1 = int(self.ent_y1.get()) if algo != "Брезенхем (Окружность)" else 0
        except ValueError:
            messagebox.showerror("Ошибка", "Координаты должны быть целыми числами")
            return

        start_time = time.perf_counter_ns()
        if algo == "Пошаговый (Линия)": points = raster_algos.algo_step(x0, y0, x1, y1)
        elif algo == "ЦДА (Линия)": points = raster_algos.algo_dda(x0, y0, x1, y1)
        elif algo == "Брезенхем (Линия)": points = raster_algos.algo_bresenham_line(x0, y0, x1, y1)
        elif algo == "Брезенхем (Окружность)": points = raster_algos.algo_bresenham_circle(x0, y0, x1)
        elif algo == "Ву (Сглаживание) - Бонус": points = raster_algos.algo_wu_line(x0, y0, x1, y1)
        end_time = time.perf_counter_ns()
        
        self.lbl_time.configure(text=f"Время расчета: {end_time - start_time} ns")
        
        log_text = raster_algos.generate_log(algo, x0, y0, x1, y1)
        self.textbox_log.delete("1.0", tk.END)
        self.textbox_log.insert("1.0", log_text)

        self.drawn_shapes_pixels.append(points)
        self.render_pixels_to_canvas(points)

if __name__ == "__main__":
    app = RasterizationApp()
    app.mainloop()