from tkinter import *
from tkinter import ttk, filedialog, messagebox
from pathlib import Path


class TkinterApp:

    def bind_to_self(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

    def set_menu(self, options: list[str]):
        root_menu = Menu(self.root, tearoff=0)
        self.root.config(menu=root_menu)
        sub_menus = {}
        for option in options:
            sub_menus[option] = Menu(root_menu, tearoff=0)
            root_menu.add_cascade(label=option, menu=sub_menus[option])
        
        self.bind_to_self(
            menu = root_menu,
            sub_menus = sub_menus,
        )

    def fill_sub_menu(self, sub_menu: Menu, optionsAndFunctions: dict[str: function]):
        for name, func in optionsAndFunctions.items():
            sub_menu.add_cascade(label=name, command=func)

    