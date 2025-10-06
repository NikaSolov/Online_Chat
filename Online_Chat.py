from customtkinter import *
from socket import *
from threading import *
import base64
from tkinter import filedialog
from PIL import Image, ImageTk
import io
from customtkinter import set_appearance_mode, set_default_color_theme

class MainWindow(CTk):
#----------------------------------------------------------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        self.geometry("400x300")
        #-----меню
        self.menu_frame = CTkFrame(self, width = 30, height=300)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x = 0, y = 0)

        self.is_show_menu = False 
        self.speed_menu_animation = -5 

        self.btn = CTkButton(self, text = ">", command = self.show_menu, width = 30)
        self.btn.place(x = 0, y = 0)

        #----основна частина
        self.chat_field = CTkScrollableFrame(self)
        self.chat_field.place(x = 0, y = 0)

        self.message_entry = CTkEntry(self, 
                                      placeholder_text="Введіть повідомлення",                      
                                      height = 40)
        self.message_entry.place(x = 0, y = 0)

        self.message_entry.bind("<Return>", self.enter_press)

        self.send_button = CTkButton(self, text = ">", width = 50, height = 40, command=self.send_message)
        self.send_button.place(x = 0, y = 0)

        self.image_button = CTkButton(self, text = "Image", width = 50, height = 40, command=self.send_image)
        self.image_button.place(x = 0, y = 0)

        
        self.username = "Вероніка"
        try:
            self.sock = socket(AF_INET, SOCK_STREAM) 
            self.sock.connect(("4.tcp.eu.ngrok.io", 16452))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався/лась до чату!\n"
            self.sock.send(hello.encode("utf-8"))
            self.add_message(hello) 
            Thread(target = self.get_msg, daemon = True).start()
        except Exception as e:
            self.add_message(e)

        self.adaptive_ui()
#----------------------------------------------------------------------------------------------------------------------
            
    def enter_press(self, event):
        self.send_message()

     
    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"{self.username} : {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.message_entry.delete(0, END)

    def send_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.gif *.jpeg")])
        if file_path:
            with open(file_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
            data = f"IMAGE@{self.username}@{img_data}\n"
            try:
                self.sock.sendall(data.encode())
                self.display_image(img_data, self.username)
            except:
                pass

    def get_msg(self):
        buffer = ""
        while True:
            try:
                shmatok = self.sock.recv(10000)
                if not shmatok:
                    break
                buffer += shmatok.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()
    
    def handle_line(self, line):
        try:
            parts = line.split("@", 2)  
            msg_type = parts[0]
            if msg_type == "TEXT":
                if len(parts) >= 3:
                    author = parts[1]
                    message = parts[2]
                    self.add_message(f"{author}: {message}")
            elif msg_type == "IMAGE":
                if len(parts) >= 3:
                    author = parts[1]
                    img_data = parts[2]
                    try:
                        self.display_image(img_data, author)
                    except Exception as e:
                        self.add_message(f"[ERROR IMAGE]: {e}")
            else:
                self.add_message(line)
        except Exception as e:
            self.add_message(f"[ERROR HANDLE]: {e}")

        else:
            self.add_message(line)
    def add_message(self, text):
        label = CTkLabel(self.chat_field, text = text, anchor="w", wraplength=self.chat_field.winfo_width() - 20)
        label.pack(anchor="w", padx = 5, pady = 5)

    def display_image(self, base64_data, author):
        img_bytes = base64.b64decode(base64_data)
        img = Image.open(io.BytesIO(img_bytes))
        ctk_img = CTkImage(light_image=img, dark_image=img, size=(200,200))
        label = CTkLabel(self.chat_field, text=f"{author}:", image = ctk_img, compound="bottom")
        label.pack(anchor = "w", padx = 5, pady = 5)



    def show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_menu_animation *= -1
            self.btn.configure(text=">")
            self.my_menu_animation()
        else:
            self.is_show_menu = True
            self.speed_menu_animation *= -1
            self.btn.configure(text="<")
            self.my_menu_animation()

            self.label = CTkLabel(self.menu_frame, text = "Нік:")
            self.label.pack(pady = 30)

            self.entry = CTkEntry(self.menu_frame)
            self.entry.pack(pady = 20)

            self.change_nick = CTkButton(self.menu_frame, 
                                         text = "Змінити", 
                                         command = self.change_username)
        
            self.change_nick.pack() 

            self.theme_combo = CTkComboBox(self.menu_frame, values = ["Light", "Dark", "Blue", "Green"])
            self.theme_combo.pack(pady = 20)

            self.change_theme_btn = CTkButton(self.menu_frame, text = "Застосувати", command = self.change_theme)
            self.change_theme_btn.pack(pady = 20)
#--------------------------------------------------------------------
    def change_theme(self):
        theme = self.theme_combo.get().lower()
        if theme in ["light", "dark"]:
            set_appearance_mode(theme)                                             
        else:
            set_default_color_theme(theme)
        self.add_message(f"[SYSTEM] Тема змінена на {theme.capitalize()}")
#---------------------------------------------------------------------
    def change_username(self):
        new_username = self.entry.get().strip()
        if new_username and new_username != self.username:
            old_username = self.username
            self.username = new_username
            sys_msg = f"TEXT@{self.username}@[SYSTEM] {old_username} змінив/ла нік на {new_username}!\n"
            try:
                self.sock.send(sys_msg.encode())
                self.add_message(sys_msg)
            except:
                pass
        self.entry.delete(0, END)
    
    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())  # панель на всю висоту вікна
        self.chat_field.place(x=self.menu_frame.winfo_width()) # зсув чату праворуч від меню

        # підбираємо розміри чату
        self.chat_field.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width() - 20,  # «–20» — невеликий відступ
            height=self.winfo_height() - 40                                 # лишаємо місце під поле вводу
        )

        self.image_button.place(x = self.winfo_width() - 100, y = self.winfo_height() - 40)

        # розміщення кнопки «надіслати і»
        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)

        # розміщення поля вводу та його ширина
        self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
        self.message_entry.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width() - 100
        )

        self.after(50, self.adaptive_ui)  # кожні 50 мс оновлюємо компонування (простий responsive)

    def my_menu_animation(self):
        self.menu_frame.configure(width = self.menu_frame.winfo_width() + self.speed_menu_animation)

        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.my_menu_animation)
        elif self.menu_frame.winfo_width() >= 30 and not self.is_show_menu:
            self.after(10, self.my_menu_animation)
            if hasattr(self, "label") and self.label:
                self.label.destroy()
            if hasattr(self, "entry") and self.entry:
                self.entry.destroy()
            if hasattr(self, "change_nick") and self.change_nick:
                self.change_nick.destroy()
            if hasattr(self, "theme_combo") and self.theme_combo:
                self.theme_combo.destroy()
            if hasattr(self, "change_theme_btn") and self.change_theme_btn:
                self.change_theme_btn.destroy()
            

window = MainWindow()
window.mainloop()