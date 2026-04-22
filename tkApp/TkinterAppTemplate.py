from tkinter import *
from TkinterApp import TkinterApp

class App(TkinterApp):
    def __init__(self, root: Tk):
        pass
        # First set initial config
        # then bind it to self
        # then call the methods 
        # e.g =>
        """
        root.title("My GUI Program")

        self.bind_to_self (
            root = root,
        )

        self.build_menu()
        self.bind_events()
        self.build_widget_tree()
        self.build_layout(["all"])
        """

    def bind_events(self):
        pass
        # Bind general shortcuts to root
        # e.g => 
        """
        self.root.bind("<Control-s>", lambda e: self.menu_save())
        """

    def build_widget_tree(self):
        pass
        # All the main UI Frame Widgets will be made here with their respective hierarchies and properties
        # They will be stored in components dict which will be bound to self
        # e.g =>
        """
        mainframe = Frame(self.root, bg="grey")
        tabSpace = Frame(mainframe, height=35, bg="white");    tabSpace.pack_propagate(False)
        components = {
            "mainframe":   mainframe,
            "tabSpace":  tabSpace,
        }
        self.bind_to_self(
            components = components,
        )
        """

    def build_layout(self, components: list[str]):
        pass
        # The UI Widgets will be projected onto the screen with the geometry manager
        # This function accepts components list, so later on individual components can also be reconstructed
        # For that, it will follow this if statements style
        # e.g =>
        """
        if "all" in components:
            components += list(self.components.keys())
        if "statusBar" in components:
            self.components["statusBar"].pack(side="bottom", fill="x")
        if "sideframe" in components:
            self.components["sideframe"].pack(side="left", fill="y")
        if "commandPanel" in components and "all" not in components:
            self.components["commandPanel"].place(relx=0.5, rely=0.1, anchor="center")
        """

    def toggleComponent(self, component: str):
        pass
        # The components which are togglable, can be toggled to show/hide 
        # A standard example is below
        # e.g =>
        """
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
        """


    #* ========= NORMAL FUNCTIONS ========= #*
    # Normal functions to manage the application
    # e.g =>
    """
    def rm_tabSpaceBlock(self, id: int, tabSpace: Frame):
        for child in tabSpace.winfo_children():
            if child.id == id:
                child.destroy()

    def ....
    """


    #* ========= MENU ========= #*
    def build_menu(self):
        pass
        # The menu will be built here. All the functions of menu will be below it with 'menu_' prefix
        # e.g => 
        """
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
        """




#* Main entrypoint function of application
"""
def main():
    root = Tk()
    TurtleLab(root)
    root.mainloop()

main()
"""