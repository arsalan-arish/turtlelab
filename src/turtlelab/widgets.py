""" Contains all the widgets used in the widget tree inside the application 
        _______________________________________________________________
Side => | B|  tabSpace               |        configSpace             | => tabSpace + configSpace = topBar
Bar     |__|_________________________|________________________________|
toggling|                            |                                |
button  |                            |                                |
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
    def __init__(self, parent):
        super().__init__(parent, height=40, borderwidth=1, relief="solid")
        self.grid_propagate(False)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=6, uniform="topBar")
        self.columnconfigure(2, weight=6, uniform="topBar")

    def display(self):
        self.pack(fill="x")
        
    def hide(self):
        self.pack_forget()

class Mainframe(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, borderwidth=1, relief="solid")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=20, uniform="mainframe")
        self.columnconfigure(2, weight=20, uniform="mainframe")
        self.bind("<<sideBardisplay>>", lambda e: (
            self.columnconfigure(0, weight=7, uniform="mainframe"),
            self.columnconfigure(1, weight=14, uniform="mainframe")
        ))
        self.bind("<<sideBarhide>>", lambda e: (
            self.columnconfigure(0, weight=0, uniform=""),
            self.columnconfigure(1, weight=20, uniform="mainframe")
        ))

    def display(self):
        self.pack(fill="both", expand=True)
        
    def hide(self):
        self.pack_forget()

class StatusBar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, height=25, borderwidth=1, relief="solid")
        self.pack_propagate(False)

    def display(self):
        self.pack(side="bottom", fill="x")

    def hide(self):
        self.pack_forget()


#* ======================================================= #*

class SideBarButton(Button):
    def __init__(self, parent, toggleFunction: function):
        super().__init__(parent, text="◨", font=("Arial", 20, "bold"), bg="white", command=self.toggle)
        self.toggleFunction = toggleFunction
        self.sideBarVisible = False

    def toggle(self):
        self.sideBarVisible = not self.sideBarVisible
        if self.sideBarVisible:
            self.configure(bg="#9b9b9b")
        else:
            self.configure(bg="white")
        self.toggleFunction()
    


    def display(self):
        self.grid(row=0, column=0)

    def hide(self):
        self.grid_forget()

class TabSpace(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, borderwidth=1, relief="solid")
        self.pack_propagate(False)

    def display(self):
        self.grid(row=0, column=1, sticky="nsew")
        
    def hide(self):
        self.grid_forget()

class ConfigSpace(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, borderwidth=1, relief="solid")
        self.pack_propagate(False)
        self.setupButtons()

    def setupButtons(self):
        animation = BooleanVar(value=True); animation.key = "animation"

        self.variables = [
            animation,

        ]
        self.buttons = [
            ttk.Checkbutton(self, text="Animations", onvalue=True, offvalue=False, variable=animation),

        ]

        for var in self.variables:
            var.trace_add("write", lambda *_, v=var: self.handleVariable(v))
        for button in self.buttons:
            button.pack(side="right")


    def handleVariable(self, var):
        """ Generate standardized virtual events """
        key = var.key
        value = var.get()
        if isinstance(var, BooleanVar):
            if value:
                self.event_generate(f"<<{key}enable>>")
            else:
                self.event_generate(f"<<{key}disable>>")
        elif isinstance(var, StringVar):
            pass


    def display(self):
        self.grid(row=0, column=2, sticky="nsew")

    def hide(self):
        self.grid_forget()


#* ======================================================= #*

class SideBar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, borderwidth=1, relief="solid")

    def display(self):
        self.grid(row=0, column=0, sticky="nsew")

    def hide(self):
        self.grid_forget()


class LeftFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, borderwidth=1, relief="solid")
    
    def display(self):
        self.grid(row=0, column=1, sticky="nsew")

    def hide(self):
        self.grid_forget()

class RightFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, borderwidth=1, relief="solid")

    def display(self):
        self.grid(row=0, column=2, sticky="nsew")

    def hide(self):
        self.grid_forget()


#* ======================================================= #*

class CommandPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, height=400, width=530)
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
        self.scrollBar = ttk.Scrollbar(parent, orient="vertical", command=self.yview)
        self.config(yscrollcommand=self.scrollBar.set)
        self.bind("<Return>", lambda e: self.smart_indent())
        self.bind("<Tab>", lambda e: self.tab())
        self.bind("<Control-Return>", lambda e: (self.event_generate("<<ExecuteCode>>"), "break")[-1])
        
    def smart_indent(self):
        self.insert("insert", "\n")
        line_start = self.get("insert-1c linestart", "insert-1c")
        indent = len(line_start) - len(line_start.lstrip())
        self.insert("insert", " " * indent)
        return "break"

    def tab(self):
        self.insert("insert", "    ")
        return "break"

    def display(self):
        self.scrollBar.pack(side="right", fill="y")
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()
        self.scrollBar.pack_forget()



class TurtleCanvas(Canvas):
    """A tk Canvas with turtle embedded"""
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.setupNewTurtle()

    def setupNewTurtle(self):
        self.delete("all")
        self.s = TurtleScreen(self)
        self.t = RawTurtle(self.s)

        self.t.shape("triangle")
        self.t.speed(0)
        self.t.penup()
        self.t.goto(140, -150)
        self.t.pendown()
        self.t.speed(3)

        # self.s.update()

    def execute(self, code: str):
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
        # self.s.update()


    def display(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()