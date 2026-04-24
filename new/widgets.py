""" Contains all the widgets used in the widget tree inside the application 
______________________________________________________________
|    tabSpace                |        configSpace             | => tabSpace + configSpace = topBar
|____________________________|________________________________|
|                            |                                |
|                            |                                |
|                            |                                |
|                            |                                |
|     leftFrame              |         rightFrame             | => leftFrame + rightFrame = mainframe
|                            |                                |
|                            |                                |
|                            |                                |
|____________________________|________________________________|
|_________________________statusBar___________________________|

commandPanel => VSCode style 
"""

from tkinter import ttk
from tkinter import *
from turtle import Turtle, RawTurtle, TurtleScreen

class TopBar(ttk.Frame):
    def __init__(self, root: Tk):
        super().__init__(root, height=40, bd=1, relief="solid")
        self.grid_propagate(False)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=5, uniform="topBar")
        self.columnconfigure(1, weight=6, uniform="topBar")

    def display(self):
        self.pack(fill="x")
        
    def hide(self):
        self.pack_forget()

class Mainframe(ttk.Frame):
    def __init__(self, root: Tk):
        super().__init__(root, bd=1, relief="solid")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=5, uniform="1")
        self.columnconfigure(1, weight=6, uniform="1")

    def display(self):
        self.pack(fill="both", expand=True)
        
    def hide(self):
        self.pack_forget()

class StatusBar(ttk.Frame):
    def __init__(self, root: Tk):
        super().__init__(root, height=25, bd=1, relief="solid")
        self.pack_propagate(False)

    def display(self):
        self.pack(side="bottom", fill="x")

    def hide(self):
        self.pack_forget()


class TabSpace(ttk.Frame):
    def __init__(self, root: Tk):
        super().__init__(root, bd=1, relief="solid")
        self.pack_propagate(False)

    def display(self):
        self.grid(row=0, column=0, sticky="nsew")
        
    def hide(self):
        self.grid_forget()

class ConfigSpace(ttk.Frame):
    def __init__(self, root: Tk):
        super().__init__(root, bd=1, relief="solid")
        self.pack_propagate(False)

    def display(self):
        self.grid(row=0, column=1, sticky="nsew")

    def hide(self):
        self.grid_forget()


class LeftFrame(ttk.Frame):
    def __init__(self, root: Tk):
        super().__init__(root, bd=1, relief="solid")
    
    def display(self):
        self.grid(row=0, column=0, sticky="nsew")

    def hide(self):
        self.grid_forget()

class RightFrame(ttk.Frame):
    def __init__(self, root: Tk):
        super().__init__(root, bd=1, relief="solid")

    def display(self):
        self.grid(row=0, column=1, sticky="nsew")

    def hide(self):
        self.grid_forget()


class CommandPanel(ttk.Frame):
    def __init__(self, root: Tk):
        super().__init__(root, height=400, width=530, bg="black")
        self.pack_propagate(False)

        entryFrame = Frame(self, height=30, width=520)
        entryFrame.pack_propagate(False)
        entryFrame.place(relx=0.5, y=150, anchor="center", width=520)
        entry = Entry(entryFrame)
        entry.pack()

        self.childs = {
            "entryFrame": entryFrame,
            "entry": entry,
        }

    def display(self):
        self.place(relx=0.5, rely=0.1, anchor="center")
        self.childs["entry"].focus()

    def hide(self):
        self.place_forget()
        self.childs["entry"].delete(0, "end")



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
        except AttributeError: # which means that the editor is of a new unsaved file
            super().destroy(); return
        if not fileObject.isSaved.get():
            ans = messagebox.askyesnocancel("TurtleLab IDE", f"Do you want to save changes you made to {fileObject.nameVar.get()}", detail="Or they will be lost", default='cancel')
            if ans is None: raise Exception("The editor block refused to destroy as user said")
            if ans: fileObject.save()
        super().destroy()

    def display(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()



class TurtleCanvas(Canvas):
    """A tk Canvas with turtle embedded"""
    def __init__(self, root: Tk):
        super().__init__(root, bg="blue")

    def setupNewTurtle(self):
        self.delete("all")
        self.screen = TurtleScreen(self)
        self.t = RawTurtle(self.screen)
        self.t.shape("arrow")
        self.screen.update()

    def display(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()