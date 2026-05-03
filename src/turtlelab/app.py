import os
from pathlib import Path
from tkinter import *
from tkinter import messagebox

from .tkApp import TkinterApp
from .objects import FileObject, TabObject
from .exceptions import TabRefusedToClose
from .widgets import (
    TopBar,
    Mainframe,
    StatusBar,
    TabSpace,
    ConfigSpace,
    LeftFrame,
    RightFrame,
    SideBarButton,
    SideBar,

    CommandPanel,
    Editor,
    TurtleCanvas,
)


class TurtleLab(TkinterApp):
    def __init__(self, root: Tk):
        root.title("Turtlelab IDE")
        iconpath = str(Path(__file__).parent) + str(Path("/assets/turtle.ico"))
        root.iconbitmap(iconpath)
        root.geometry("900x600")
        root.state("zoomed")
        root.tk.call('tk', 'fontchooser', 'show')
        # root.resizable(False, False)
        # root.protocol("WM_DELETE_WINDOW", callable)
        # root.attributes(fullscreen=True, alpha=0.5)
 
        state = {
            "panelVisible": False,
            "sideBarVisible": False,
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
        b = self.root.bind
        b("<Control-n>", lambda e: self.newFile())
        b("<Control-o>", lambda e: self.openFile())
        b("<Control-k>", lambda e: self.openFolder())
        b("<Control-s>", lambda e: self.save())
        b("<Control-Shift-P>", lambda e: self.toggleComponent("panel"))
        b("<Escape>", lambda e: self.handleEscape())
        b("<Control-w>", lambda e: self.removeTabObject(self.state["activeTabObj"][0].id) if self.state["activeTabObj"] else None)
        b("<Control-Shift-T>", lambda e: self.reOpenLastClosedTab())
        
        b("<<ExecuteCode>>", lambda e: self.execute())


    def build_widget_tree(self):
        topBar = TopBar(self.root)
        mainframe = Mainframe(self.root)
        statusBar = StatusBar(self.root)
        panel = CommandPanel(self.root)

        sideBarButton = SideBarButton(topBar, lambda: self.toggleComponent("sideBar"))
        tabSpace = TabSpace(topBar)
        configSpace = ConfigSpace(topBar)

        sideBar = SideBar(mainframe)
        leftFrame = LeftFrame(mainframe)
        rightFrame = RightFrame(mainframe)

        components = {
            "topBar":    topBar,
            "mainframe": mainframe,
            "statusBar": statusBar,
            "panel":     panel,

            "sideBarButton": sideBarButton,
            "tabSpace":      tabSpace,
            "configSpace":   configSpace,

            "sideBar":    sideBar,
            "leftFrame":  leftFrame,
            "rightFrame": rightFrame,
        }
        # The order of these components is critical
        self.bind_to_self(
            components = components,
        )


    def build_layout(self, components: list[str]):
        if "all" in components:
            components = list(self.components.keys()); components.remove("panel"); components.remove("sideBar")
        for component in components:
            self.components[component].display()


    def toggleComponent(self, component: str):
        property = f"{component}Visible"
        try:
            self.state[property] = not self.state[property]
        except AttributeError as e:
            print(e, "This component cannot be toggled")

        if self.state[property]:
            self.components["mainframe"].event_generate(f"<<{component}display>>")
            self.components[component].display()
        else:
            self.components["mainframe"].event_generate(f"<<{component}hide>>")
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
                ("New File" , "Ctrl-N"): self.newFile,
                ("Open File", "Ctrl-O"): self.openFile,
                ("Open Folder", "Ctrl-K"): self.openFolder,
                ("Save", "Ctrl-S"): self.save,
                ("--", None)  : None,
                ("Open Recent Tab", "Ctrl-Shift-T"): self.reOpenLastClosedTab,
            }
        )
        self.fill_sub_menu (
            self.sub_menus["Run"],
            {
                ("Execute ▶️", "Ctrl-Enter"): self.execute,
            }
        )
        

    def newFile(self):
        id = self.getNewId()
        canvas = TurtleCanvas(self.components["rightFrame"])
        editor = Editor(self.components["leftFrame"]); editor.focus()
        name = StringVar(value="New File")
        fileObj = FileObject(id, name, None, editor)
        tab = TabObject(id, name, self.components["tabSpace"], [editor, canvas], True, fileObj,
                        self.state["activeTabObj"], self.state["TabObjects"], self.removeTabObject)
        tab.activate()

    def openFile(self, filepath: Path | None = None):
        id = self.getNewId()
        if not filepath:
            filename, filepath, data = self.promptForFile()
            if not filename: return
        else:
            filename = filepath.name
            data = filepath.read_text()

        filename = StringVar(value=filename)
        editor = Editor(self.components["leftFrame"]); editor.insert("end", data); editor.focus()
        canvas = TurtleCanvas(self.components["rightFrame"])
        fileObj = FileObject(id, filename, filepath, editor)
        tab = TabObject(id, filename, self.components["tabSpace"], [editor, canvas], True, fileObj,
                        self.state["activeTabObj"], self.state["TabObjects"], self.removeTabObject)
        tab.activate()

    def openFolder(self):
        path = self.promptForFolder()
        if not path: return
        self.loadDirectory(path)

    def save(self):
        try:
            activeTab = self.state["activeTabObj"][0]
        except IndexError:
            return
        if not activeTab.isFile: messagebox.showinfo("Save File", "Please select an appropriate file tab to save the file"); return
        activeTab.fileObject.save()

    def reOpenLastClosedTab(self):
        try: 
            oldTabObj = self.state["OldTabObjects"].pop()
        except Exception:
            return
        self.state["TabObjects"].append(oldTabObj)
        oldTabObj.recycle()
        oldTabObj.activate()

    def execute(self):
        try:
            activeTab = self.state["activeTabObj"][0]
        except IndexError:
            return
        if not activeTab.isFile: messagebox.showinfo("Run File", "Please select an appropriate file tab to execute the file"); return
        code = activeTab.fileObject.save(returnString=True)
        if not code: return
        canvas = activeTab.widgets[1] # See the protocol on __init__ function of TabObject Class
        canvas.execute(code)



def App(filepath: Path | None):
    root = Tk()
    app = TurtleLab(root)
    if filepath:
        app.openFile(filepath)
    root.mainloop()
    