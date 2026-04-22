from tkinter import *
from tkinter import ttk, filedialog, messagebox
from abc import ABC, abstractmethod
from pathlib import Path
import os
import subprocess
import threading


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



class Terminal(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.text = Text(self, bg="white", insertbackground="black", font=("Cascadia Code", 14))
        self.text.pack(fill="both", expand=True)

        self.process = subprocess.Popen(
            ["cmd" if os.name == "nt" else "bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        self.show_prompt()
        self.history = []
        self.history_index = -1
        self.prompt_index = "end-1c"

        threading.Thread(target=self.read_output, daemon=True).start()

        # Key bindings
        self.text.bind("<Return>", self.send_input)
        self.text.bind("<Up>", self.prev_command)
        self.text.bind("<Down>", self.next_command)
        self.text.bind("<Control-Left>", self.ctrl_left)
        self.text.bind("<Control-Right>", self.ctrl_right)
        self.text.bind("<Key>", self.restrict_cursor)

    # ---------------- OUTPUT ----------------
    def read_output(self):
        for line in self.process.stdout:
            self.text.insert("end", line)
            self.text.see("end")
            self.prompt_index = self.text.index("end-1c")

    def show_prompt(self):
        prompt = f"{os.getcwd()}>"
        self.text.insert("end", prompt)
        self.text.see("end")
        self.prompt_index = self.text.index("end-1c")

    # ---------------- INPUT ----------------
    def send_input(self, event):
        line = self.text.get(self.prompt_index, "end-1c")

        if line.strip():
            self.history.append(line)
        self.history_index = len(self.history)

        self.text.delete(self.prompt_index, "end-1c")

        self.process.stdin.write(line + "\n")
        self.process.stdin.flush()

        self.text.insert("end", "\n")

        # wait a bit before showing next prompt
        self.after(50, self.show_prompt)

        return "break"

    # ---------------- HISTORY ----------------
    def prev_command(self, event):
        if self.history:
            self.history_index = max(0, self.history_index - 1)
            self.replace_current_line(self.history[self.history_index])
        return "break"

    def next_command(self, event):
        if self.history:
            self.history_index = min(len(self.history), self.history_index + 1)
            if self.history_index < len(self.history):
                self.replace_current_line(self.history[self.history_index])
            else:
                self.replace_current_line("")
        return "break"

    def replace_current_line(self, text):
        self.text.delete(self.prompt_index, "end-1c")
        self.text.insert("end", text)

    # ---------------- CTRL WORD NAV ----------------
    def ctrl_left(self, event):
        pos = self.text.index("insert")
        while True:
            prev = self.text.index(f"{pos} -1c")
            char = self.text.get(prev)
            if char == " " or prev <= self.prompt_index:
                break
            pos = prev
        self.text.mark_set("insert", pos)
        return "break"

    def ctrl_right(self, event):
        pos = self.text.index("insert")
        end = self.text.index("end-1c")
        while True:
            if pos >= end:
                break
            char = self.text.get(pos)
            pos = self.text.index(f"{pos} +1c")
            if char == " ":
                break
        self.text.mark_set("insert", pos)
        return "break"

    # ---------------- CURSOR LOCK ----------------
    def restrict_cursor(self, event):
        if self.text.compare("insert", "<", self.prompt_index):
            self.text.mark_set("insert", "end-1c")
