from tkinter import *
from tkApp import TkinterApp, Editor, FileObject, CommandPanel
from pathlib import Path
import os

os.chdir(Path(__file__).parent)

class TurtleLab(TkinterApp):
    def __init__(self, root: Tk):
        root.title("Turtlelab IDE")
        root.iconbitmap("assets/turtle.ico")
        root.geometry("900x600")
        root.state("zoomed")

        state = {
            "panelVisible": False,
            "activeTab": None,
            "tabIdCounter": 1,
            "FileObjects": [],
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
        self.root.bind("<Control-n>", lambda e: self.menu_newFile())
        self.root.bind("<Control-o>", lambda e: self.menu_openFile())
        self.root.bind("<Control-k>", lambda e: self.menu_openFolder())
        self.root.bind("<Control-s>", lambda e: self.menu_save())
        self.root.bind("<Control-Shift-S>", lambda e: self.menu_saveAs())
        self.root.bind("<Control-Shift-P>", lambda e: self.toggleComponent("panel"))
        self.root.bind("<Escape>", lambda e: self.handleEscape())
        self.root.bind("<Control-w>", lambda e: self.rmTab(self.state["activeTab"]))


    def build_widget_tree(self):
        topBar = Frame(self.root, height=40, bd=2, relief="solid"); topBar.grid_propagate(False)
        mainframe = Frame(self.root, bd=2, relief="solid")
        statusBar = Frame(self.root, height=25, bd=2, relief="solid"); statusBar.pack_propagate(False)
        panel = CommandPanel(self.root)
        
        tabSpace = Frame(topBar, bd=2, relief="solid"); tabSpace.pack_propagate(False)
        configSpace = Frame(topBar, bd=2, relief="solid"); configSpace.pack_propagate(False)

        leftFrame = Frame(mainframe, bd=2, relief="solid")
        rightFrame = Frame(mainframe, bd=2, relief="solid")

        components = {
            "topBar": topBar,
            "mainframe": mainframe,
            "statusBar": statusBar,
            "tabSpace": tabSpace,
            "configSpace": configSpace,
            "leftFrame": leftFrame,
            "rightFrame": rightFrame,
            "panel": panel,
            "editorSpace": leftFrame, # Compatibility reasons
        }
        self.bind_to_self(
            components = components,
        )
        

    def build_layout(self, components: list[str]):
        if "all" in components:
            components += list(self.components.keys())
        if "topBar" in components:
            self.components["topBar"].pack(fill="x")
            self.components["topBar"].rowconfigure(0, weight=1)
            self.components["topBar"].columnconfigure(0, weight=5, uniform="2")
            self.components["topBar"].columnconfigure(1, weight=6, uniform="2")
        if "mainframe" in components:
            self.components["mainframe"].pack(fill="both", expand=True)
            self.components["mainframe"].rowconfigure(0, weight=1)
            self.components["mainframe"].columnconfigure(0, weight=5, uniform="1")
            self.components["mainframe"].columnconfigure(1, weight=6, uniform="1")
        if "statusBar" in components:
            self.components["statusBar"].pack(side="bottom", fill="x")
        if "tabSpace" in components:
            self.components["tabSpace"].grid(row=0, column=0, sticky="nsew")
        if "configSpace" in components:
            self.components["configSpace"].grid(row=0, column=1, sticky="nsew")
        if "leftFrame" in components:
            self.components["leftFrame"].grid(row=0, column=0, sticky="nsew")
        if "rightFrame" in components:
            self.components["rightFrame"].grid(row=0, column=1, sticky="nsew")
        if "panel" in components and "all" not in components:
            self.components["panel"].display()



    def toggleComponent(self, component: str):
        property = f"{component}Visible"
        try:
            self.state[property] = not self.state[property]
        except AttributeError as e:
            print(e, "This component cannot be toggled")

        if self.state[property]:
            self.build_layout([component])
        else:
            try:
                self.components[component].hide()
            except Exception:
                self.components[component].pack_forget()
                self.components[component].place_forget()
                self.components[component].grid_forget()


    #* ========= NORMAL FUNCTIONS ========= #*

    def add_tabSpaceBlock(self, id: int, textVar: StringVar, tabSpace: Frame):
        """ Create a tab block able of showing name and cross (closing icon), with basic events bound to it"""
        block = Frame(tabSpace, height=40, relief="solid", bd=1, bg="white")
        block.id = id
        f = Frame(block, height=35); f.pack(side="left")
        l = Label(f, textvariable=textVar, padx=10, bg=block.cget("bg"))
        l.pack(anchor="center")
        cross = Button(block, text="✖", command=lambda: self.rmTab(id), bg="white", width=1, height=1)
        cross.pack(side="right", fill="y")
        block.pack(side="left")
        
        block.bind("<ButtonPress-1>", lambda e: self.activateTab(id))
        l.bind("<ButtonPress-1>", lambda e: self.activateTab(id))

    def rm_tabSpaceBlock(self, id: int, tabSpace: Frame):
        """ Delete and remove that tab block"""
        for child in tabSpace.winfo_children():
            if child.id == id:
                child.destroy()
                
    def add_editorSpaceBlock(self, id: int, widget: Any, editorSpace: Frame):
        """ Takes the widget and assigns it the id as well as makes sure that it is a child of editorSpace frame """
        assert widget in editorSpace.winfo_children()
        widget.id = id

    def rm_editorSpaceBlock(self, id: int, editorSpace: Frame):
        """ Removes and deletes the widget in editorSpace """
        for child in editorSpace.winfo_children():
            if child.id == id:
                child.destroy()

    # editorSpaceBlock + tabSpaceBlock = Tab
    def createTab(self, id: int, nameVar: StringVar, widget: Any):
        if id is None: return
        self.add_tabSpaceBlock(id, nameVar, self.components["tabSpace"])
        self.add_editorSpaceBlock(id, widget, self.components["editorSpace"])

    def rmTab(self, id: int):
        if id is None: return
        self.state["activeTab"] = None
        try:
            self.rm_editorSpaceBlock(id, self.components["editorSpace"])
        except Exception: # The block refused to be removed
            return
        self.rm_tabSpaceBlock(id, self.components["tabSpace"])

    def activateTab(self, id: int):
        if id is None: return
        if tabId := self.state["activeTab"]:
            self.deactivateTab(tabId)
        
        self.state["activeTab"] = id
        tabSpaceBlock = self.getTabSpaceWidget(id)
        editorSpaceBlock = self.getEditorSpaceWidget(id)

        tabSpaceBlock.configure(bg="#222121", bd=2, relief="raised")
        editorSpaceBlock.pack(fill="both", expand=True)

    def deactivateTab(self, id: int):
        if id is None: return
        self.state["activeTab"] = None
        tabSpaceBlock = self.getTabSpaceWidget(id)
        editorSpaceBlock = self.getEditorSpaceWidget(id)

        tabSpaceBlock.configure(bg="white", bd=1)
        editorSpaceBlock.pack_forget()

    def getTabSpaceWidget(self, tabId: int):
        if tabId is None: return
        for child in self.components["tabSpace"].winfo_children():
            if child.id == tabId:
                return child

    def getEditorSpaceWidget(self, tabId: int):
        if tabId is None: return
        for child in self.components["editorSpace"].winfo_children():
            if child.id == tabId:
                return child
            
    def getFileObject(self, id: int):
        for obj in self.state["FileObjects"]:
            if obj.id == id:
                return obj
    
    def handleEscape(self):
        if self.state["panelVisible"]:
            self.toggleComponent("panel")
        
    def getNewTabId(self) -> int:
        id = self.state["tabIdCounter"]
        self.state["tabIdCounter"] += 1
        return id
    
    def getCodeEditor(self) -> Editor:
        editor = Editor(self.components["editorSpace"])
        return editor

    def loadDirectory(self, path: Path):
        os.chdir(path)


    #* ========= MENU ========= #*
    def build_menu(self):

        self.set_menu(["File", "Edit"])
        self.fill_sub_menu (
            self.sub_menus["File"],
            {
                "New File": self.menu_newFile,
                "Open File": self.menu_openFile,
                "Open Folder": self.menu_openFolder,
                "Save": self.menu_save,
                "Save As": self.menu_saveAs,
            }
        )
        

    def menu_newFile(self):
        id = self.getNewTabId()
        editor = self.getCodeEditor()
        editor.focus()
        self.createTab(id, StringVar(value="New"), editor)
        self.activateTab(id)

    def menu_openFile(self):
        id = self.getNewTabId()
        filename, filepath, data = self.promptForFile()
        if not filename: return
        filename = StringVar(value=filename)
        editor = self.getCodeEditor()
        editor.insert("end", data)
        editor.focus()
        self.createTab(id, filename, editor)
        self.activateTab(id)
        self.state["FileObjects"].append(FileObject(id, filename, filepath, self.getTabSpaceWidget(id), editor))

    def menu_openFolder(self):
        path = self.promptForFolder()
        if not path: return
        self.loadDirectory(path)

    def menu_save(self):
        activeTabId = self.state["activeTab"]
        if not activeTabId: self.popMessageBox("info", "Save File", "Please select an appropriate file tab to save the file"); return
        for obj in self.state["FileObjects"]:
            if obj.id == activeTabId:
                obj.save()
                return
        # At this point, it means that the current active tab is not associated with a file object (either it is a new file or not a file at all)
        editorSpaceWidget = self.getEditorSpaceWidget(activeTabId)
        if type(editorSpaceWidget) == Editor:
            self.menu_saveAs()
        else:
            self.popMessageBox("info", "Save File", "Please select an appropriate file tab to save the file"); return

    def menu_saveAs(self):
        activeTabId = self.state["activeTab"]
        if not activeTabId: self.popMessageBox("info", "Save File", "Please select an appropriate file tab to save the file"); return
        name, path = self.promptForSaveAsFile()
        if not name: return
        name = StringVar(value=name)
        editor = self.getEditorSpaceWidget(activeTabId)
        # Change the name label of the tab block
        tabBlock = self.getTabSpaceWidget(activeTabId)
        tabBlockLabel = tabBlock.winfo_children()[0].winfo_children()[0].configure(textvariable=name)
        fileObj = FileObject(activeTabId, name, path, tabBlock, editor)
        fileObj.save()
        self.state["FileObjects"].append(fileObj)




def app():
    root = Tk()
    TurtleLab(root)
    root.mainloop()

#! Only for testing
app()