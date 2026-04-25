""" Contains objects used by application to group data """
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path


class FileObject:
    def __init__(self, id, nameVar, filepath, tabBlock, editor):
        self.id = id
        self.nameVar = nameVar
        self.filepath = filepath
        self.tabBlock = tabBlock
        self.editor = editor
        if filepath: self.trackModification()

        
    def trackModification(self):
        self.isSaved = BooleanVar(value=True)
        self.isSaved.trace_add("write", self.putModifiedSign)
        self.sign = Label(self.tabBlock, text="*", name="sign")
        self.editor.edit_modified(False)
        self.editor.bind("<<Modified>>", self.on_modified)

    def on_modified(self, *_):
        if self.editor.edit_modified():
            self.isSaved.set(False)
            self.editor.edit_modified(False) # critical

    def putModifiedSign(self, *_):
        if self.isSaved.get():
            self.sign.pack_forget()
        else:
            self.sign.pack(side="right")


    def save(self):
        if not self.filepath: 
            self.filepath = filedialog.asksaveasfilename(
                title="Save file as",
                defaultextension=".txt",
                initialdir=os.getcwd(),
            )
            if not self.filepath: return
            self.filepath = Path(self.filepath)
            self.nameVar.set(self.filepath.name)
            self.trackModification()
            
        data = self.editor.get("1.0", "end-1c")
        with open(self.filepath, "w") as f:
            f.write(data)

        self.isSaved.set(True)
        self.editor.edit_modified(False)



class TabObject:
    def __init__(self, id: int, nameVar: StringVar, tabSpace: Frame, widgets: list, isFile: bool, fileObject: FileObject | None,
                 globalActiveTabObj: list, globalTabObjects: list, onCrossIconPressFunction: function):
        self.id = id
        self.nameVar = nameVar
        self.tabSpace = tabSpace
        self.widgets = widgets
        self.activeTabObj = globalActiveTabObj
        self.TabObjects = globalTabObjects
        self.fileObject = fileObject
        
        self.TabObjects.append(self)
        self.addTabSpaceBlock(onCrossIconPressFunction)
        self.activate()

    def addTabSpaceBlock(self, onCrossPressFunction: function):
        """ Create a tab block able of showing name and cross (closing icon), with basic events bound to it"""

        block = ttk.Frame(self.tabSpace, height=self.tabSpace.winfo_height(), padding=2)
        label = ttk.Label(block, textvariable=self.nameVar, background="#c9c9c9", font=("Arial", 10, "bold"))
        cross = ttk.Button(block, text="x", width=1, command=lambda: onCrossPressFunction(self.id))

        block.pack(side="left")
        label.pack(side="left", anchor="center")
        cross.pack(side="right", fill="y")

        label.bind("<ButtonPress-1>", lambda e: self.activate())
        self.tabSpaceBlock = block

    def activate(self):
        if self.activeTabObj: 
            oldTab = self.activeTabObj[0]
            oldTab.deactivate()
        self.activeTabObj.append(self)
        self.tabSpaceBlock.configure(borderwidth=2, relief="raised")
        self.tabSpaceBlock.winfo_children()[0].configure(background="#CECECE")
        for widget in self.widgets:
            widget.display()

    def deactivate(self):
        self.activeTabObj.remove(self)
        self.tabSpaceBlock.configure(borderwidth=1, relief="solid")
        self.tabSpaceBlock.winfo_children()[0].configure(background="#ffffff")
        for widget in self.widgets:
            widget.hide()

    def garbage(self):
        self.tabSpaceBlock.pack_forget()
        [widget.hide() for widget in self.widgets]

    def recycle(self):
        self.tabSpaceBlock.pack(side="left")
        [widget.display() for widget in self.widgets]