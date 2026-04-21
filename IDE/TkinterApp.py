from tkinter import *
from tkinter import ttk, filedialog, messagebox
from abc import ABC, abstractmethod
from pathlib import Path
import os


class TkinterApp(ABC):

    @abstractmethod
    def __init__(self, root: Tk):
        """Set initial config, and call appropriate methods"""

    @abstractmethod
    def bind_shortcuts(self):
        """Bind all the shortcuts to their respective functions"""

    @abstractmethod
    def build_widget_tree(self):
        """Create widget objects in hierarchy"""

    @abstractmethod
    def build_layout(self, components: list[str]):
        """Place widgets on the screen"""

    @abstractmethod
    def toggleComponent(self, component: str):
        """Show/Hide the visual appearance of component on screen"""

    @abstractmethod
    def build_menu(self):
        """Create the menu and submenus, binding with their appropriate functions"""


    #! =================== UTILITIES FUNCTIONS START HERE =================== #!
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

    def open_file(self) -> str:
        filepath = filedialog.askopenfilename(
            filetypes=[("All files", "*.*")],
            initialdir=os.getcwd()
        )
        if not filepath: return
        with open(filepath, "r") as f:
            return f.read()

    def save_as(self, data: str):
        filepath = filedialog.asksaveasfilename(
            filetypes=[("All files", "*.*")],
            initialdir=os.getcwd(),
            title="Save file as"
        )
        if not filepath: return
        with open(filepath, "w") as f:
            f.write(data)

    def getCenteredDimensions(self, width, height, root) -> str:
        dwidth = root.winfo_screenwidth()
        dheight = root.winfo_screenheight()
        center_x = int(dwidth/2 - width / 2) - 25
        center_y = int(dheight/2 - height / 2) - 35 
        return f"{width}x{height}+{center_x}+{center_y}"
