# pyright: ignore
from tkinter import *
from TkinterApp import TkinterApp, FileObject, Editor
from pathlib import Path
import os

os.chdir(Path(__file__).parent)

class TurtleLab(TkinterApp):
    WIDTH = 800
    HEIGHT = 600

    def __init__(self, root: Tk):
        
        centered_dimensions: str = self.getCenteredDimensions(self.WIDTH, self.HEIGHT, root)

        root.geometry(centered_dimensions)
        root.title("My GUI Program")
        root.iconbitmap()

        state = {
            "sidebarVisible": True,
            "panelVisible": True,
            "commandPanelVisible": False,
            "activeTab": None,
            "tabIdCounter": 1,
            "FileObjects": []
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
        # General shortcuts
        self.root.bind("<Control-Shift-P>", lambda e: self.toggleComponent("commandPanel"))
        self.root.bind("<Escape>", lambda e: self.handleEscape())
        self.root.bind("<Control-n>", lambda e: self.menu_newFile())
        self.root.bind("<Control-s>", lambda e: self.menu_save())
        self.root.bind("<Control-Shift-S>", lambda e: self.menu_saveAs())



    def build_widget_tree(self):
        mainframe = Frame(self.root, bg="grey")
        sideframe = Frame(self.root)
        statusBar = Frame(self.root, height=20, bg="red")
        commandPanel = Frame(self.root, height=400, width=530, bg="black"); commandPanel.pack_propagate(False)

        activityBar = Frame(sideframe, width=45);             activityBar.pack_propagate(False)
        sidebar = Frame(sideframe, width=280);                sidebar.pack_propagate(False)
        tabSpace = Frame(mainframe, height=35, bg="white");    tabSpace.pack_propagate(False)
        editorSpace = Frame(mainframe);                        editorSpace.pack_propagate(False)
        panel = Frame(mainframe, height=250, bg="purple");    panel.pack_propagate(False)

        b = Button(tabSpace, width=1, height=1, text="⬇", command=lambda: self.toggleComponent("panel")); b.pack(side="right"); b.id = None
        b = Button(tabSpace, width=1, height=1, text="⬅", command=lambda: self.toggleComponent("sidebar")); b.pack(side="right"); b.id = None
        commandPanel.childs = {}
        commandPanel.childs["entry"] = Entry(commandPanel)
        commandPanel.childs["entry"].place(relx=0.5, y=150, anchor="center", width=520)

        components = {
            "mainframe":   mainframe,
            "sideframe":   sideframe,
            "statusBar": statusBar,
            "commandPanel": commandPanel,
            "activityBar": activityBar,
            "sidebar":     sidebar,
            "tabSpace":  tabSpace,
            "editorSpace": editorSpace,
            "panel":       panel,
        }
        self.bind_to_self(
            components = components,
        )


    def build_layout(self, components: list[str]):
        if "all" in components:
            components += list(self.components.keys())
        if "statusBar" in components:
            self.components["statusBar"].pack(side="bottom", fill="x")
        if "sideframe" in components:
            self.components["sideframe"].pack(side="left", fill="y")
        if "mainframe" in components:
            self.components["mainframe"].pack(side="top", fill="both", expand=True)
        if "activityBar" in components:
            self.components["activityBar"].pack(side="left", fill="y")
        if "sidebar" in components:
            self.components["sidebar"].pack(side="left", fill="y")
        if "tabSpace" in components:
            self.components["tabSpace"].pack(side="top", fill="x")
        if "editorSpace" in components:
            self.components["editorSpace"].pack(side="top", fill="both", expand=True)
        if "panel" in components:
            self.components["panel"].pack(side="bottom", fill="x")
        if "commandPanel" in components and "all" not in components:
            self.components["commandPanel"].place(relx=0.5, rely=0.1, anchor="center")
            self.components["commandPanel"].childs["entry"].focus()


    def toggleComponent(self, component: str):
        property = f"{component}Visible"
        try:
            self.state[property] = not self.state[property]
        except AttributeError as e:
            print(e, "This component cannot be toggled")

        if self.state[property]:
            self.build_layout([component])
        else:
            self.components[component].pack_forget()
            self.components[component].place_forget()
            self.components[component].grid_forget()

    def add_tabSpaceBlock(self, id: int, textVar: StringVar, tabSpace: Frame):
        """ Create a tab block able of showing name and cross (closing icon), with basic events bound to it"""
        block = Frame(tabSpace, height=35, width=100, relief="solid", bd=1)
        block.pack_propagate(False)
        block.id = id
        f = Frame(block, width=80, height=35); f.pack(side="left"); f.pack_propagate(False)
        l = Label(f, textvariable=textVar, padx=10)
        l.pack(anchor="center")
        cross = Button(block, text="✖", command=lambda: (self.deactivateTab(id), self.rmTab(id)), bg="white", width=1, height=1)
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
        self.add_tabSpaceBlock(id, nameVar, self.components["tabSpace"])
        self.add_editorSpaceBlock(id, widget, self.components["editorSpace"])

    def rmTab(self, id: int):
        self.rm_tabSpaceBlock(id, self.components["tabSpace"])
        self.rm_editorSpaceBlock(id, self.components["editorSpace"])

    def activateTab(self, id: int):
        if tabId := self.state["activeTab"]:
            self.deactivateTab(tabId)
        
        self.state["activeTab"] = id
        tabSpaceBlock = [child for child in self.components["tabSpace"].winfo_children() if child.id == id].pop()
        editorSpaceBlock = [child for child in self.components["editorSpace"].winfo_children() if child.id == id].pop()

        tabSpaceBlock.configure(bg="grey", bd=2, relief="raised")
        editorSpaceBlock.pack(fill="both", expand=True)

    def deactivateTab(self, id: int):
        self.state["activeTab"] = None
        tabSpaceBlock = [child for child in self.components["tabSpace"].winfo_children() if child.id == id].pop()
        editorSpaceBlock = [child for child in self.components["editorSpace"].winfo_children() if child.id == id].pop()

        tabSpaceBlock.configure(bg="white", bd=1)
        editorSpaceBlock.pack_forget()


    def handleEscape(self):
        if self.state["commandPanelVisible"]:
            self.toggleComponent("commandPanel")
            self.components["commandPanel"].childs["entry"].delete(0, "end")
        
    def getNewTabId(self) -> int:
        id = self.state["tabIdCounter"]
        self.state["tabIdCounter"] += 1
        return id

    def getCodeEditor(self) -> Editor:
        editor = Editor(self.components["editorSpace"])
        return editor

    def loadDirectory(self, path: Path):
        os.chdir(path)


    def build_menu(self):
        """This contains the code related to menu"""
        self.set_menu(["File"])

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
        self.state["FileObjects"].append(FileObject(id, filename, filepath, editor))

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
        editorSpaceWidget = [child for child in self.components["editorSpace"].winfo_children() if child.id == activeTabId].pop()
        if type(editorSpaceWidget) == Editor:
            self.menu_saveAs()
        else:
            self.popMessageBox("info", "Save File", "Please select an appropriate file tab to save the file")

    def menu_saveAs(self):
        activeTabId = self.state["activeTab"]
        if not activeTabId: self.popMessageBox("info", "Save File", "Please select an appropriate file tab to save the file"); return
        name, path = self.promptForSaveAsFile()
        if not name: return
        name = StringVar(value=name)
        editor = [child for child in self.components["editorSpace"].winfo_children() if child.id == activeTabId].pop()
        # Change the name label of the tab block
        tabBlock = [child for child in self.components["tabSpace"].winfo_children() if child.id == activeTabId].pop()
        tabBlockLabel = tabBlock.winfo_children()[0].winfo_children()[0].configure(textvariable=name)
        fileObj = FileObject(activeTabId, name, path, editor)
        fileObj.save()
        self.state["FileObjects"].append(fileObj)



def main():
    root = Tk()
    TurtleLab(root)
    root.mainloop()

main()