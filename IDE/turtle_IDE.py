from tkinter import *
from TkinterApp import TkinterApp
from pathlib import Path
import json
import os

os.chdir(Path(__file__).parent)

class TurtleLab(TkinterApp):
    WIDTH = 800
    HEIGHT = 600
    SETTINGS_JSON_PATH = Path("settings.json")

    def __init__(self, root: Tk):
        
        centered_dimensions: str = self.getCenteredDimensions(self.WIDTH, self.HEIGHT, root)

        root.geometry(centered_dimensions)
        root.title("My GUI Program")
        root.iconbitmap()

        settings = json.loads(self.SETTINGS_JSON_PATH.read_text())
        state = {
            "sidebarVisible": True,
            "panelVisible": True,
            "commandPanelVisible": False,
            "tabSelected": None, # or id of the tabBlock-editorBlock pair (tab)
        }

        self.bind_to_self (
            root = root,
            state = state,
            settings = settings,
        )

        self.build_menu()
        self.bind_shortcuts()
        self.build_widget_tree()
        self.build_layout(["all"])
        self.add_tabSpaceBlock(1, "file")
        self.add_editorSpaceBlock(1, Text(self.components["editorSpace"]))
        self.activateTab(1)


    def bind_shortcuts(self):
        self.root.bind("<Control-Shift-P>", lambda e: self.toggleComponent("commandPanel"))
        self.root.bind("<Escape>", lambda e: self.handleEscape())


    def build_widget_tree(self):
        mainframe = Frame(self.root, bg="grey")
        sideframe = Frame(self.root)
        statusBar = Frame(self.root, height=20, bg="red")
        commandPanel = Frame(self.root, height=400, width=530, bg="black"); commandPanel.pack_propagate(False)

        activityBar = Frame(sideframe, width=45);             activityBar.pack_propagate(False)
        sidebar = Frame(sideframe, width=280);                sidebar.pack_propagate(False)
        tabSpace = Frame(mainframe, height=35, bg="grey");    tabSpace.pack_propagate(False)
        editorSpace = Frame(mainframe);                        editorSpace.pack_propagate(False)
        panel = Frame(mainframe, height=250, bg="purple");    panel.pack_propagate(False)

        Button(tabSpace, width=1, height=1, command=lambda: self.toggleComponent("panel")).pack(side="right")
        Button(tabSpace, width=1, height=1, command=lambda: self.toggleComponent("sidebar")).pack(side="right")
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

    
    def add_tabSpaceBlock(self, id: int, text: str):
        tabSpace = self.components["tabSpace"]
        block = Frame(tabSpace, height=35, width=100, relief="solid", bd=1)
        block.pack_propagate(False)
        block.id = id
        Label(block, text=text).pack(anchor="center")

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

    # editorSpaceBlock + tabSpaceBlock = Tab
    def activateTab(self, id: int):
        if tabId := self.state["tabSelected"]:
            self.deactivateTab(tabId)
        self.state["tabSelected"] = id
        tabSpaceBlock = [child for child in self.components["tabSpace"].winfo_children() if type(child) == Frame and child.id == id].pop()
        # This little type check (in the end) will make sure it does not consider the other two child buttons inside tabSpace Frame
        editorSpaceBlock = [child for child in self.components["editorSpace"].winfo_children() if child.id == id].pop()

        tabSpaceBlock.configure(bg="grey", bd=2)
        editorSpaceBlock.pack(fill="both", expand=True)

    def deactivateTab(self, id: int):
        self.state["tabSelected"] = None
        tabSpaceBlock = [child for child in self.components["tabSpace"].winfo_children() if child.id == id].pop()
        editorSpaceBlock = [child for child in self.components["editorSpace"].winfo_children() if child.id == id].pop()

        tabSpaceBlock.configure(bg="white", bd=1)
        editorSpaceBlock.pack_forget()

    def handleEscape(self):
        if self.state["commandPanelVisible"]:
            self.toggleComponent("commandPanel")
            self.components["commandPanel"].childs["entry"].delete(0, "end")
        
    #! =================== MENU UTILITIES FUNCTIONS START HERE =================== #!

    def build_menu(self):
        """This contains the code related to menu"""
        self.set_menu(["File", "Edit", "View", "Help"])

        self.fill_sub_menu(
            self.sub_menus["File"],
            {
                "New File": self.menu_newFile,
                "Open File": self.menu_openFile,
                "Save": self.menu_save,
                "Save As": self.menu_saveAs,
            }
        )
        self.fill_sub_menu(
            self.sub_menus["Edit"],
            {
                "Cut": self.menu_cut,
                "Copy": self.menu_copy,
                "Paste": self.menu_paste,
            }
        )

    def menu_newFile(self):
        pass
    def menu_openFile(self):
        pass
    def menu_save(self):
        pass
    def menu_saveAs(self):
        pass

    def menu_cut(self):
        pass
    def menu_copy(self):
        pass
    def menu_paste(self):
        pass






def main():
    root = Tk()
    TurtleLab(root)
    root.mainloop()

main()