import os
from pathlib import Path

from exceptions import TabRefusedToClose
from tkApp import TkinterApp
from objects import FileObject, TabObject
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
            "activeTab": None,
            "tabIdCounter": 1,
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
            components = list(self.components.keys()) - ["panel"]
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


    #* ========= NORMAL FUNCTIONS ========= #*

