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

    def popMessageBox(self, level: str, title: str, msg: str):
        """ Show a messagebox message """
        match(level):
            case "info":
                messagebox.showinfo(title, msg)
            case "warning":
                messagebox.showwarning(title, msg)
            case "error":
                messagebox.showerror(title, msg)


#! ========== The classes below are prebuilt components that can optionally be used in an application ========== #!

class FileObject:
    def __init__(self, id, nameVar, filepath, tabBlock, editor):
        self.id = id
        self.nameVar = nameVar
        self.filepath = filepath
        self.tabBlock = tabBlock
        self.editor = editor

        #! For compatibility, the fileobject is connected to the editor as well
        self.editor.fileObject = self

        self.isSaved = BooleanVar(value=True)
        self.isSaved.trace_add("write", self.putModifiedSign)

        self.sign = Label(self.tabBlock, text="*", name="sign")

        self.editor.edit_modified(False)
        self.editor.bind("<<Modified>>", self.on_modified)

    def on_modified(self, *_):
        if self.editor.edit_modified():
            self.isSaved.set(False)
            self.editor.edit_modified(False)  # critical

    def save(self):
        data = self.editor.get("1.0", "end-1c")
        with open(self.filepath, "w") as f:
            f.write(data)

        self.isSaved.set(True)
        self.editor.edit_modified(False)  # reset after save

    def putModifiedSign(self, *_):
        if self.isSaved.get():
            self.sign.pack_forget()
        else:
            self.sign.pack(side="right")


class Editor(Text):
    """ An extended Text widget with smart features (methods) to function as a code editor"""

    def __init__(self, parent):
        super().__init__(parent, font=("Cascadia Code", 14), wrap="word", undo=True)
        self.bind("<Return>", lambda e: self.smart_indent())
        self.bind("<Tab>", lambda e: self.tab())
        
    def smart_indent(self):
        self.insert("insert", "\n")
        line_start = self.get("insert-1c linestart", "insert-1c")
        indent = len(line_start) - len(line_start.lstrip())
        self.insert("insert", " " * indent)
        return "break"

    def tab(self):
        self.insert("insert", "    ")
        return "break"
    
    def destroy(self):
        try:
            fileObject = self.fileObject #! Specially given by FileObject class __init__
        except AttributeError as e: # which means that the editor is of a new unsaved file
            super().destroy(); return
        if not fileObject.isSaved.get():
            ans = messagebox.askyesnocancel("TurtleLab IDE", f"Do you want to save changes you made to {fileObject.nameVar.get()}", detail="Or they will be lost", default='cancel')
            if ans is None: raise Exception("The editor block refused to destroy as user said")
            if ans: fileObject.save()
        super().destroy()


class CommandPanel(Frame):
    """ A commandpanel that should be given root of application """
    def __init__(self, root: Tk):
        super().__init__(root, height=400, width=530, bg="black")
        self.pack_propagate(False)

        entryFrame = Frame(self, height=30,width=520)
        entryFrame.pack_propagate(False)
        entryFrame.pack(side="left")
        entry = Entry(entryFrame)
        entry.pack()
        # entry.place(relx=0.5, y=150, anchor="center", width=520)


        self.childs = {}
        self.childs["entryFrame"] = entryFrame
        self.childs["entry"] = entry

    def display(self):
        self.place(relx=0.5, rely=0.1, anchor="center")
        self.childs["entry"].focus()

    def hide(self):
        self.place_forget()
        self.childs["entry"].delete(0, "end")
