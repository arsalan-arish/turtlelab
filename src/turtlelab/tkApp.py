from tkinter import *
from tkinter import filedialog, messagebox
from abc import ABC, abstractmethod
from pathlib import Path
import os


class TkinterApp(ABC):
    """ Defines a clean interface to create a scalable Tkinter Application """

    @abstractmethod
    def __init__(self, root: Tk):
        """Set initial config, and call appropriate methods"""

    @abstractmethod
    def bind_events(self):
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
        """Avoid 'self' hell, just give kwargs of which object to assign to which attribute of self"""
        for name, value in kwargs.items():
            setattr(self, name, value)

    def set_menu(self, options: list[str]):
        """ A clean function to create a root menu and add submenus (options) to it """
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
        """ A clean function to fill a sub menu with options """
        for name, func in optionsAndFunctions.items():
            sub_menu.add_cascade(label=name, command=func)

    def promptForFile(self) -> (str, Path, str):
        """ Prompt the os filedialog, and return (name, path, data) of the file to read"""
        filepath = filedialog.askopenfilename(
            filetypes=[("All files", "*.*")],
            initialdir=os.getcwd()
        )
        if not filepath: return None, None, None
        with open(filepath, "r") as f:
            return (Path(filepath).name, Path(filepath), f.read())
        
    def promptForFolder(self) -> Path:
        """ Prompt the os filedialog, and return folderpath """
        folderpath = filedialog.askdirectory(
            mustexist=True,
            initialdir=os.getcwd(),
        )
        if not folderpath: return None
        return Path(folderpath)

    def promptForSaveAsFile(self) -> (str, Path):
        """ Prompt the os filedialog, and return (name, path) of file to create and save """
        filepath = filedialog.asksaveasfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            defaultextension=".txt",
            initialdir=os.getcwd(),
            title="Save file as"
        )
        if not filepath: return None, None
        return (Path(filepath).name, Path(filepath))