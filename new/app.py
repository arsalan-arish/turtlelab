import os
from pathlib import Path
from tkinter import *
from tkinter import messagebox

from tkApp import TkinterApp
from objects import FileObject, TabObject
from exceptions import TabRefusedToClose
from widgets import (
    TopBar,
    Mainframe,
    StatusBar,
    TabSpace,
    ConfigSpace,
    LeftFrame,
    RightFrame,
    CommandPanel,
    Editor,
    TurtleCanvas,
)

os.chdir(Path(__file__).parent)

class TurtleLab(TkinterApp):
    def __init__(self, root: Tk):
        root.title("Turtlelab IDE")
        root.iconbitmap("assets/turtle.ico")
        root.geometry("900x600")
        root.state("zoomed")
 
        state = {
            "panelVisible": False,
            "uniqueIdCounter": 1,

            #* All below state variables are automatically managed by:
            #* - TabObject instances
            #* - removeTabObject method
            #* - reOpenLastClosedTab method
            #! hence they should not modified anywhere else
            "TabObjects":    [],
            "OldTabObjects": [],
            "activeTabObj":  [],
            #! Only 1 activeTabObj. A list is only used so that its mutable ref can be passed to TabObject, and it can mutate it itself when it activates and deactivates
        }

        self.bind_to_self (
            root = root,
            state = state,
        )
        self.build_menu()
        self.bind_events()
        self.build_widget_tree()
        self.build_layout(["all"])
        

    def bind_events(self):
        self.root.bind("<Control-n>", lambda e: self.newFile())
        self.root.bind("<Control-o>", lambda e: self.openFile())
        self.root.bind("<Control-k>", lambda e: self.openFolder())
        self.root.bind("<Control-s>", lambda e: self.save())
        self.root.bind("<Control-Shift-S>", lambda e: self.saveAs())
        self.root.bind("<Control-Shift-P>", lambda e: self.toggleComponent("panel"))
        self.root.bind("<Escape>", lambda e: self.handleEscape())
        self.root.bind("<Control-w>", lambda e: self.removeTabObject(self.state["activeTabObj"][0].id) if self.state["activeTabObj"] else None)
        self.root.bind("<Control-Shift-T>", lambda e: self.reOpenLastClosedTab())


    def build_widget_tree(self):
        topBar = TopBar(self.root)
        mainframe = Mainframe(self.root)
        statusBar = StatusBar(self.root)
        panel = CommandPanel(self.root)

        tabSpace = TabSpace(topBar)
        configSpace = ConfigSpace(topBar)

        leftFrame = LeftFrame(mainframe)
        rightFrame = RightFrame(mainframe)

        components = {
            "topBar": topBar,
            "mainframe": mainframe,
            "statusBar": statusBar,
            "panel": panel,
            "tabSpace": tabSpace,
            "configSpace": configSpace,
            "leftFrame": leftFrame,
            "rightFrame": rightFrame,
        }
        # The order of these components is critical
        self.bind_to_self(
            components = components,
        )


    def build_layout(self, components: list[str]):
        if "all" in components:
            components = list(self.components.keys()); components.remove("panel")
        for component in components:
            self.components[component].display()


    def toggleComponent(self, component: str):
        property = f"{component}Visible"
        try:
            self.state[property] = not self.state[property]
        except AttributeError as e:
            print(e, "This component cannot be toggled")

        if self.state[property]:
            self.components[component].display()
        else:
            self.components[component].hide()


    def removeTabObject(self, id: int):
        if id is None: return
        for i in range(len(self.state["TabObjects"])):
            if self.state["TabObjects"][i].id == id:
                self.state["OldTabObjects"].append(self.state["TabObjects"][i])
                self.state["TabObjects"][i].garbage()
                del self.state["TabObjects"][i]
                break


    def handleEscape(self):
        if self.state["panelVisible"]:
            self.toggleComponent("panel")

    def getNewId(self) -> int:
        id = self.state["uniqueIdCounter"]
        self.state["uniqueIdCounter"] += 1
        return id

    #* ========= NORMAL FUNCTIONS ========= #*

    def loadDirectory(self):
        pass

    #* ========= MENU ========= #*
    def build_menu(self):

        self.set_menu(["File", "Edit", "Run"])
        self.fill_sub_menu (
            self.sub_menus["File"],
            {
                "New File": self.newFile,
                "Open File": self.openFile,
                "Open Folder": self.openFolder,
                "Save": self.save,
                "Save As": self.saveAs,
                "Open Last Closed Tab": self.reOpenLastClosedTab,
            }
        )
        self.fill_sub_menu (
            self.sub_menus["Run"],
            {
                "Execute current file": self.execute,
            }
        )
        

    def newFile(self):
        id = self.getNewId()
        canvas = TurtleCanvas(self.components["rightFrame"])
        editor = Editor(self.components["leftFrame"]); editor.focus()
        name = StringVar(value="New File")
        tab = TabObject(id, name, self.components["tabSpace"], [editor, canvas], True, None,
                        self.state["activeTabObj"], self.state["TabObjects"], self.removeTabObject)
        fileObj = FileObject(id, name, None, tab.tabSpaceBlock, editor)
        tab.fileObject = fileObj
        tab.activate()

    def openFile(self):
        id = self.getNewId()
        filename, filepath, data = self.promptForFile()
        if not filename: return
        filename = StringVar(value=filename)
        editor = Editor(self.components["leftFrame"]); editor.insert("end", data); editor.focus()
        canvas = TurtleCanvas(self.components["rightFrame"])
        tab = TabObject(id, filename, self.components["tabSpace"], [editor, canvas], True, None,
                        self.state["activeTabObj"], self.state["TabObjects"], self.removeTabObject)
        fileObj = FileObject(id, filename, filepath, tab.tabSpaceBlock , editor)
        tab.fileObject = fileObj
        tab.activate()

    def openFolder(self):
        path = self.promptForFolder()
        if not path: return
        self.loadDirectory(path)

    def save(self):
        activeTab = self.state["activeTabObj"][0]
        if not activeTab: messagebox.showinfo("Save File", "Please select an appropriate file tab to save the file"); return
        if not activeTab.fileObject: messagebox.showinfo("Save File", "Please select an appropriate file tab to save the file"); return
        activeTab.fileObject.save()
            

    def saveAs(self):
        pass

    def reOpenLastClosedTab(self):
        try: 
            oldTabObj = self.state["OldTabObjects"].pop()
        except Exception:
            return
        self.state["TabObjects"].append(oldTabObj)
        oldTabObj.recycle()
        oldTabObj.activate()

    def execute(self):
        pass

def app():
    root = Tk()
    TurtleLab(root)
    root.mainloop()

#! Only for testing
app()


"""
     activeTab = self.state["activeTab"]
            if not activeTab: messagebox.showinfo("Save File", "Please select an appropriate file tab to save the file"); return
            name, path = self.promptForSaveAsFile()
            if not name: return
            name = StringVar(value=name)
            editor = self.getEditorSpaceWidgetFromId(activeTabId)
            # Change the name label of the tab block
            tabBlock = self.getTabSpaceWidgetFromId(activeTabId)
            tabBlockLabel = tabBlock.winfo_children()[0].winfo_children()[0].configure(textvariable=name)
            fileObj = FileObject(activeTabId, name, path, tabBlock, editor)
            fileObj.save()
            self.state["FileObjects"].append(fileObj)
"""