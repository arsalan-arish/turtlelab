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

from tkinter import ttk, messagebox
from tkinter import *
from turtle import Turtle, RawTurtle, TurtleScreen
import traceback

"""
Protocol => Each widget must implement display() and hide() methods for itself
"""

class TopBar(ttk.Frame):
    def __init__(self, root: Tk):
        super().__init__(root, height=40, borderwidth=1, relief="solid")
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
        super().__init__(root, borderwidth=1, relief="solid")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=5, uniform="1")
        self.columnconfigure(1, weight=6, uniform="1")

    def display(self):
        self.pack(fill="both", expand=True)
        
    def hide(self):
        self.pack_forget()

class StatusBar(ttk.Frame):
    def __init__(self, root: Tk):
        super().__init__(root, height=25, borderwidth=1, relief="solid")
        self.pack_propagate(False)

    def display(self):
        self.pack(side="bottom", fill="x")

    def hide(self):
        self.pack_forget()


class TabSpace(ttk.Frame):
    def __init__(self, root: Tk):
        super().__init__(root, borderwidth=1, relief="solid")
        self.pack_propagate(False)

    def display(self):
        self.grid(row=0, column=0, sticky="nsew")
        
    def hide(self):
        self.grid_forget()

class ConfigSpace(ttk.Frame):
    def __init__(self, root: Tk):
        super().__init__(root, borderwidth=1, relief="solid")
        self.pack_propagate(False)

    def display(self):
        self.grid(row=0, column=1, sticky="nsew")

    def hide(self):
        self.grid_forget()


class LeftFrame(ttk.Frame):
    def __init__(self, root: Tk):
        super().__init__(root, borderwidth=1, relief="solid")
    
    def display(self):
        self.grid(row=0, column=0, sticky="nsew")

    def hide(self):
        self.grid_forget()

class RightFrame(ttk.Frame):
    def __init__(self, root: Tk):
        super().__init__(root, borderwidth=1, relief="solid")

    def display(self):
        self.grid(row=0, column=1, sticky="nsew")

    def hide(self):
        self.grid_forget()


class CommandPanel(ttk.Frame):
    def __init__(self, root: Tk):
        super().__init__(root, height=400, width=530)
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
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.setupNewTurtle()

    def setupNewTurtle(self):
        self.delete("all")
        self.s = TurtleScreen(self)
        self.t = RawTurtle(self.s)
        self.t.shape("arrow")
        self.s.update()

    def execute(self, code: str):
        def strip_comments(code: str) -> str:
            lines = []
            for line in code.splitlines():
                if "#" in line:
                    line = line.split("#", 1)[0]
                lines.append(line)
            return "\n".join(lines)
        code = strip_comments(code)
        
        if not code.strip(): return
        if "import turtle" in code or "from turtle" in code:
            messagebox.showerror(
                "Invalid Code",
                "Do NOT import turtle.\nUse the provided `t` and `s` which are Turtle and Screen objects respectively"
            ); return
        
        self.setupNewTurtle()
        try:
            exec(code, {
                "t": self.t,
                "s": self.s,
                "__builtins__": __builtins__,
            })
        except Exception:
            messagebox.showerror(
                "Execution Error",
                traceback.format_exc()
            ); return
        self.s.update()


    def display(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()