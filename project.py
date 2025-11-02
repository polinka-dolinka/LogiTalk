from customtkinter import *
from socket import *
import threading


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.title("Chat")
        self.geometry('600x500')
        self.minsize(400, 300)

        # Параметри меню
        self.menu_visible = False
        self.menu_width = 200

        # --- Кнопка для показу/приховання меню ---
        self.menu_button = CTkButton(self, text='▶', width=30, command=self.toggle_menu)
        self.menu_button.grid(row=0, column=0, sticky="nw", padx=5, pady=5)

        # --- Меню ---
        self.menu_frame = CTkFrame(self, width=self.menu_width)
        self.menu_frame.grid(row=1, column=0, rowspan=3, sticky="ns")
        self.menu_frame.grid_propagate(False)  # Щоб фрейм не змінював розмір по вмісту

        self.menu_content = CTkFrame(self.menu_frame)
        self.menu_content.pack()  

        
        self.label = CTkLabel(self.menu_content, text='Ваше Ім`я')
        self.label.pack(pady=(0, 10))
        self.entry = CTkEntry(self.menu_content)
        self.entry.pack(pady=(0, 30))
        self.label_theme = CTkOptionMenu(self.menu_content, values=['Темна', 'Світла'], command=self.change_theme)
        self.label_theme.pack()

        # --- Чат ---
        self.chat_text = CTkTextbox(self, state='disabled', wrap='word')
        self.chat_text.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=5, pady=5)

        self.message_input = CTkEntry(self, placeholder_text='Введіть повідомлення:')
        self.message_input.grid(row=3, column=1, sticky="ew", padx=(5, 0), pady=5)

        self.send_button = CTkButton(self, text='▶', width=40, height=30, command=self.send_message)
        self.send_button.grid(row=3, column=2, sticky="e", padx=5, pady=5)

      
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)

   
        self.grid_columnconfigure(0, weight=0)  
        self.grid_columnconfigure(1, weight=1)  
        self.grid_columnconfigure(2, weight=0)  

        
        self.hide_menu()

        self.username = 'Невідомий користувач'
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('4.tcp.eu.ngrok.io', 12631))#tcp://4.tcp.eu.ngrok.io:12631
            hello = f'TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату. \n'
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f'Не вдалось доєднатись до сервера: {e}')


    def toggle_menu(self):
        if self.menu_visible:
            self.hide_menu()
        else:
            self.show_menu()

    def show_menu(self):
        self.menu_frame.grid()
        self.menu_visible = True
        self.menu_button.configure(text='◀')

    def hide_menu(self):
        self.menu_frame.grid_remove()
        self.menu_visible = False
        self.menu_button.configure(text='▶')

    def change_theme(self, value):
        if value == 'Темна':
            set_appearance_mode('dark')
        else:
            set_appearance_mode('light')

    def add_message(self, text):
        self.chat_text.configure(state='normal')
        self.chat_text.insert(END, text + '\n')
        self.chat_text.configure(state='disable')

    def send_message(self):
        message = self.message_input.get()
        new_name = self.entry.get()
        if new_name != self.username:
            self.username = new_name
            
        if message:
            self.add_message(f'{self.username}: {message} \n')
            data = f'TEXT@{self.username}@{message}\n'
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.message_input.delete(0, END)

    def recv_message(self):
        buffer = ''
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)#!!!!
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split('@', 3)
        msg_type = parts[0]
        if msg_type == 'TEXT':
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f'{author}: {message}')
        else:
            self.add_message(line)
        




if __name__ == "__main__":
    set_appearance_mode("dark")
    win = MainWindow()
    win.mainloop()
