from tkinter import *
from tkinter import ttk

from .models import CriptoValueModel
from .views import CriptoValueView
from . import __author__


# Standard screen resolutions
VGA = (640, 480)   # SCREEN_SIZE[0]
SVGA = (800, 600)   # SCREEN_SIZE[1]
XGA = (1024, 768)  # SCREEN_SIZE[2]
XVGA = (1280, 1024)  # SCREEN_SIZE[3]

SCREEN_SIZE = (VGA, SVGA, XGA, XVGA)


class CriptoValueController(Tk):
    # API window
    resize = 0
    WIDTH = SCREEN_SIZE[resize][1]
    HEIGHT = SCREEN_SIZE[resize][0]

    def __init__(self):
        super().__init__()
        # Initialize a root Tkinter object
        self.geometry('+%d+%d' % (self.WIDTH*1.8, self.HEIGHT//3))
        self.resizable(False, False)
        self.grid_propagate(False)
        self.iconbitmap('resources/img/logo_7z.ico')
        self.wm_title("Coin API")
        self.bind('<Escape>', lambda event: self.destroy())

        self.view = CriptoValueView(self, self.WIDTH, self.HEIGHT, self.execute)
        self.view.pack()
        self.model = CriptoValueModel()

        self.mainloop()

    def execute(self):
        self.model.input = self.view.input_coin
        self.model.output = self.view.output_coin
        self.model.get_value()
        self.view.set_value(self.model.value, self.model.json_dict)

    def __del__(self):
        print(__author__)
