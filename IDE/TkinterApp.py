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

    def promptForFile(self) -> (str, Path, str):
        filepath = filedialog.askopenfilename(
            filetypes=[("All files", "*.*")],
            initialdir=os.getcwd()
        )
        if not filepath: return None, None, None
        with open(filepath, "r") as f:
            return (Path(filepath).name, Path(filepath), f.read())
        
    def promptForFolder(self) -> Path:
        folderpath = filedialog.askdirectory(
            mustexist=True,
            initialdir=os.getcwd(),
        )
        if not folderpath: return None
        return Path(folderpath)

    def promptForSaveAsFile(self) -> (str, Path):
        filepath = filedialog.asksaveasfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            defaultextension=".txt",
            initialdir=os.getcwd(),
            title="Save file as"
        )
        if not filepath: return None, None
        return (Path(filepath).name, Path(filepath))

    def popMessageBox(self, level: str, title: str, msg: str):
        match(level):
            case "info":
                messagebox.showinfo(title, msg)
            case "warning":
                messagebox.showwarning(title, msg)
            case "error":
                messagebox.showerror(title, msg)
        
    def getCenteredDimensions(self, width, height, root) -> str:
        dwidth = root.winfo_screenwidth()
        dheight = root.winfo_screenheight()
        center_x = int(dwidth/2 - width / 2) - 25
        center_y = int(dheight/2 - height / 2) - 35 
        return f"{width}x{height}+{center_x}+{center_y}"

    def add_tabSpaceBlock(self, id: int, textVar: StringVar):
        tabSpace = self.components["tabSpace"]
        block = Frame(tabSpace, height=35, width=100, relief="solid", bd=1)
        block.pack_propagate(False)
        block.id = id
        f = Frame(block); f.pack(side="left")
        l = Label(f, textvariable=textVar, padx=10)
        cross = Button(block, text="✖", command=lambda: self.rmTab(id), bg="white", width=1, height=1)
        l.pack(anchor="center")
        cross.pack(side="right", anchor="center", fill="y")
        block.pack(side="left")
        
        block.bind("<ButtonPress-1>", lambda e: self.activateTab(id))
        l.bind("<ButtonPress-1>", lambda e: self.activateTab(id))

    def rm_tabSpaceBlock(self, id: int):
        tabSpace = self.components["tabSpace"]
        for child in tabSpace.winfo_children():
            if child.id == id:
                child.pack_forget()
                child.destroy()
                
    def add_editorSpaceBlock(self, id: int, widget: Any):
        editorSpace = self.components["editorSpace"]
        assert widget in editorSpace.winfo_children()
        widget.id = id

    def rm_editorSpaceBlock(self, id: int):
        editorSpace = self.components["editorSpace"]
        for child in editorSpace.winfo_children():
            if child.id == id:
                child.destroy()

class FileObject:
    def __init__(self, id: int, nameVar: StringVar, filepath: Path, editor: Text):
        """id is synced with the tab id, editor is the instance of the Text widget object that holds the file content"""
        self.id = id
        self.nameVar = nameVar
        self.filepath = filepath
        self.editor = editor

    def save(self):
        data = self.editor.get("1.0", "end-1c")
        with open(self.filepath, "w") as f:
            f.write(data)
    

class Editor(Text):
    def __init__(self):
        super().__init__(self.components["editorSpace"], font=("Cascadia Code", 14), wrap="word", undo=True)
        

        # editor.bind("<Return>", self._smart_indent)
        # editor.bind("<Tab>", self._tab)
        # editor.bind("<Control-Return>", self.run_code)