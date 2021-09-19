import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import pygame as pg
import datetime
import pickle

# from .settings import COINS, QUERY_LIMIT
from .settings import *


# Load music and sounds
pg.init()
pg.mixer.pre_init(44100, -16, 2, 512)
pg.mixer.init()

pg.mixer.music.load(f"resources/snd/music.wav")
pg.mixer.music.set_volume(0.5)
pg.mixer.music.play(-1, 0.0, 1000)

select_fx = pg.mixer.Sound('resources/snd/select.wav')
select_fx.set_volume(0.5)
coin_fx = pg.mixer.Sound('resources/snd/coin.wav')
coin_fx.set_volume(0.5)
confirm_fx = pg.mixer.Sound('resources/snd/confirm.wav')
confirm_fx.set_volume(0.5)
warning_fx = pg.mixer.Sound('resources/snd/warning.wav')
warning_fx.set_volume(0.5)
error_fx = pg.mixer.Sound('resources/snd/error.wav')
error_fx.set_volume(0.5)


class CriptoValueView(ttk.Frame):

    def __init__(self, parent, width, height, execute):
        super().__init__(parent, width=width, height=height)
        # Global parameters
        self.WIDTH = width
        self.HEIGHT = height

        self.is_valid = True
        self.process = 0
        self.graph = 0
        self.query_list = []
        self.messages = [
            "~ Welcome to Coin APP ~",
            "The calculation was successful",
            "Select the type of Input and Output Coins",
            "Select the type of Input Coin",
            "Select the type of Output Coin",
            "Select a different Coin type",
            "The Input Coin type is incorrect",
            "The Output Coin type is incorrect",
            "Query limit reached, wait 24 hours to access",
            ]

        self.menubar(parent)
        self.widgets(execute)

    def menubar(self, parent):
        self.menubar = tk.Menu(self)
        parent.config(menu=self.menubar, width=self.WIDTH, height=self.HEIGHT)

        self.menu_file = tk.Menu(self.menubar, tearoff=False)
        self.menu_file.add_command(label="New file", command=lambda: self.new_file(), accelerator="Ctrl+N")
        self.menu_file.add_command(label="Open file", command=lambda: self.open_file(), accelerator="Ctrl+O")
        self.menu_file.add_command(label="Save file", command=lambda: self.save_file(), accelerator="Ctrl+S")
        self.menu_file.add_command(label="Open file as...", command=lambda: self.open_file_as())
        self.menu_file.add_command(label="Save file as...", command=lambda: self.save_file_as())
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit", command=lambda: self.exit_api(parent), accelerator="Esc")
        self.menubar.add_cascade(label="File", menu=self.menu_file)

        self.menu_edit = tk.Menu(self.menubar, tearoff=False)
        self.menu_edit.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        self.menu_edit.add_command(label="Supr", command=self.supr, accelerator="Supr")
        self.menu_edit.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        self.menu_edit.add_separator()
        self.menu_edit.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        self.menu_edit.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        self.menu_edit.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        self.menubar.add_cascade(label="Edit", menu=self.menu_edit)

        self.menu_help = tk.Menu(self.menubar, tearoff=False)
        self.menu_help.add_command(label="Info", command=self.info, accelerator="Ctrl+I")
        self.menu_help.add_command(label="License", command=self.license, accelerator="Ctrl+L")
        self.menu_help.add_command(label="About...", command=self.about, accelerator="Ctrl+A")
        self.menubar.add_cascade(label="Help", menu=self.menu_help)

    def widgets(self, execute):
        # Header - Query preview box
        self.header = tk.Canvas(self, background="black")
        self.header.grid(column=0, row=0, columnspan=3, rowspan=3, padx=10, pady=15)
        # Info text
        self.info_text = tk.Label(self.header, text=self.messages[self.process], anchor='center', font=('arial',11), bg='black', fg='yellow')
        self.info_text.grid(column=0, row=0, columnspan=3, rowspan=1, padx=10, pady=10)
        # Query preview text
        self.query_text = tk.scrolledtext.ScrolledText(self.header, width=int(self.WIDTH//9.5), height=self.HEIGHT//80, font=('arial',11), bg='black', fg='white')
        self.query_text.grid(column=0, row=1, columnspan=3, rowspan=2, padx=10, pady=10)

        # Input area - input Combobox, input box
        self.input_area = ttk.LabelFrame(self, text=" Input Coin ")
        self.input_area.grid(column=1, row=3, rowspan=2, padx=20, pady=5, sticky='w')
        # Input Combobox
        self.input_value = tk.StringVar()
        self.input = ttk.Combobox(self.input_area, values=list(COINS.values()), textvariable=self.input_value, width=self.WIDTH//23)
        self.input.grid(column=0, row=0, padx=10, pady=10)
        # Input box
        self.input_data = tk.StringVar()
        self.input_box = ttk.Entry(self.input_area, textvariable=self.input_data)
        self.input_box.grid(column=0, row=1, padx=10, pady=10)

        # Command area - Exchange btn, Conversion btn
        self.command_area = ttk.Frame(self)
        self.command_area.grid(column=1, row=3, rowspan=2, padx=20, pady=5)
        # Exchange btn
        self.exchange_btn = ttk.Button(self.command_area, text="Exchange", cursor='hand2', command=lambda:self.exchange())
        self.exchange_btn.grid(column=0, row=0, padx=10, pady=10)
        # Next btn
        self.conversion_btn = ttk.Button(self.command_area, text="Calculate", cursor='hand2', command=lambda:self.commands(execute))
        self.conversion_btn.grid(column=0, row=1, padx=10, pady=10)

        # Event keys
        self.bind_all('<Control-Return>', self.event_keys)
        self.bind_all('<Return>', self.event_keys)

        # Output area - Output Combobox, Output box
        self.output_area = ttk.LabelFrame(self, text=" Output Coin ")
        self.output_area.grid(column=1, row=3, rowspan=2, padx=20, pady=5, sticky='e')
        # Output Combobox
        self.output_value = tk.StringVar()
        self.output = ttk.Combobox(self.output_area, values=list(COINS.values()), textvariable=self.output_value, width=self.WIDTH//23)
        self.output.grid(column=0, row=0, padx=10, pady=10)
        # Output box
        self.output_data = tk.StringVar()
        self.output_box = ttk.Entry(self.output_area, textvariable=self.output_data)
        self.output_box.grid(column=0, row=1, padx=10, pady=10)

        # Graphic area - Verified data
        self.graphic_area = ttk.LabelFrame(self, text=(f" Total conversions made {self.process}/100 "))
        self.graphic_area.grid(column=1, row=5, padx=20, pady=5, sticky='we')
        # Verified data
        self.verified_data = tk.Canvas(self.graphic_area, width=self.WIDTH, height=self.HEIGHT//40, background="silver")
        self.verified_data.grid(column=0, row=0, padx=5, pady=5, sticky='nsew')

        # Footer area - Date & Mark
        self.date = ttk.Label(self, text=datetime.datetime.now().date())
        self.date.grid(column=1, row=6, padx=10, pady=5, sticky='w')
        self.mark = ttk.Label(self, text="https://github.com/Seven-z01")
        self.mark.grid(column=1, row=6, padx=10, pady=5, sticky='e')

        self.init()

# Menubar - File
    def new_file(self):
        index = len(self.file_list)
        if self.file_list[-1] != '':
            file = open(f'file ({index-1}).csv', mode='r', encoding='utf-8')
        else:
            file = open('file.csv', mode='r', encoding='utf-8')
        content = file.read()
        self.scrolledtext.delete('1.0', 'end')
        self.scrolledtext.insert('1.0', content)
        self.file_list.append(file)
        file.close()

    def open_file(self):
        file = open('file.csv', mode='r', encoding='utf-8')
        content = file.read()
        file.close()
        self.scrolledtext.delete('1.0', 'end')
        self.scrolledtext.insert('1.0', content)

    def save_file(self):
        self.file_list.append(query_list)
        file = open('file.csv', mode='w', encoding='utf-8')
        file.write(self.scrolledtext.get('1.0', 'end'))
        file.close()
        messagebox.showinfo("Info", "The data was saved in the file")
        self.file_list.append(file)

    def open_file_as(self):
        filename = tk.filedialog.askopenfilename(initialdir='/', title="Open as...",
                                              filetypes=(('csv files', '*.csv'),
                                                         ('txt files', '*.txt'),
                                                         ('all files', '*.*')))
        if filename != '':
            file = open(filename, mode='r', encoding='utf-8')
            content = file.read()
            file.close()
            self.scrolledtext.delete('1.0', 'end')
            self.scrolledtext.insert('1.0', content)

    def save_file_as(self):
        filename = tk.filedialog.asksaveasfilename(initialdir='/', title="Save as...",
                                                filetypes=(('csv files', '*.csv'),
                                                           ('txt files', '*.txt'),
                                                           ('all files', '*.*')))
        if filename != '':
            file = open(filename, mode='w', encoding='utf-8')
            file.write(self.scrolledtext.get('1.0', 'end'))
            file.close()
            tk.messagebox.showinfo("Info", "The data was saved in the file")
            self.file_list.append(file)

    def exit_api(self, parent):
        msg = tk.messagebox.askquestion("Exit", "You want to exit the app?")
        if msg == 'yes':
            parent.destroy()

    # Menubar - Edit
    def undo(self):
        pass

    def supr(self):
        pass

    def redo(self):
        pass

    def cut(self):
        pass

    def copy(self):
        pass

    def paste(self):
        pass

    def info(self):
        pass

    def license(self):
        pass

    def about(self):
        pass

    def init(self):
        self.input.delete(0, 'end')
        self.input.insert(0, COINS['EUR'])
        self.output.delete(0, 'end')
        self.output.insert(0, COINS['USD'])
        self.input_box.delete(0, 'end')
        self.input_box.insert(0, 1)
        self.input_box.focus()
        self.output_box.delete(0, 'end')
        self.is_valid = False

    def reset(self):
        _input = COINS[self.input_coin]
        _output = COINS[self.output_coin]
        self.input.delete(0, 'end')
        self.input.insert(0, _input)
        self.output.delete(0, 'end')
        self.output.insert(0, _output)
        self.input_box.focus()
        self.is_valid = False

    def exchange(self):
        _input = self.input.get()
        _output = self.output.get()
        self.input.delete(0, 'end')
        self.input.insert(0, _output)
        self.output.delete(0, 'end')
        self.output.insert(0, _input)
        coin_fx.play()

    def commands(self, execute):
        self.validate()
        if self.is_valid:
            execute()
            self.bar_graph()
            self.reset()

    @property
    def input_coin(self):
        return self.input_value.get()[:3].upper()

    @property
    def output_coin(self):
        return self.output_value.get()[:3].upper()

    def set_value(self, value, value_dict):
        self.output_box.delete(0, 'end')
        self.output_box.insert(0, value)
        self.query_list.append(value_dict)
        self.query_text.delete('1.0', 'end')
        self.query_text.insert('1.0', self.query_list[self.process])
        self.info_text.config(text=self.messages[1], fg='green')
        self.process += 1
        confirm_fx.play()

    def invalid_data(self, msg):
        self.info_text.config(text=self.messages[msg], fg='red')
        self.graphic_area['text'] = " Invalid data "
        self.verified_data.create_rectangle(5, 5, self.graph - 2, 18, fill='red')
        error_fx.play()

    def validate(self):
        input_coin = self.input_coin
        output_coin = self.output_coin

        if input_coin == '' and output_coin == '':
            self.invalid_data(2)

        elif input_coin == '':
            self.invalid_data(3)

        elif output_coin == '':
            self.invalid_data(4)

        elif input_coin == output_coin:
            self.invalid_data(5)

        elif not input_coin in COINS.keys():
            self.invalid_data(6)

        elif not output_coin in COINS.keys():
            self.invalid_data(7)

        elif self.process >= QUERY_LIMIT:
            self.invalid_data(8)
            warning_fx.play()

        else: self.is_valid = True

    @property
    def graph_max(self):
        graph_max = float(self.verified_data['height']) * float(self.verified_data['height'])
        return graph_max

    def bar_graph(self):
        self.verified_data.delete('all')
        if self.process < QUERY_LIMIT:
            self.graph = self.graph_max - (self.graph_max - self.process)
        else:
            self.graph = self.graph_max

        self.graphic_area['text'] = (f" Total conversions made {self.process}/100 ")
        self.verified_data.create_rectangle(5, 5, self.graph - 2, 18, fill='blue')

    def event_keys(self, event):
        if event.keysym == 'Control-Return':
            self.exchange()
        if event.keysym == 'Return':
            self.commands()
