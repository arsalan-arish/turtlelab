from tkinter import *
from tkinter import filedialog, messagebox
from turtle import Turtle
import os
import traceback
from pathlib import Path
from TkinterApp import TkinterApp


class TurtleLab(TkinterApp):

    def __init__(self, root: Tk):
        root.title("My GUI Program")

        dwidth = root.winfo_screenwidth()
        dheight = root.winfo_screenheight()
        wwidth = 800
        wheight = 600
        center_x = int(dwidth/2 - wwidth / 2) - 35   # 248
        center_y = int(dheight/2 - wheight / 2) - 20 # 64
        root.geometry(f"{wwidth}x{wheight}+{center_x}+{center_y}")

        state = {
            "sidebarVisible": True,
            "panelVisible": True,
        }

        self.bind_to_self(
            root=root,
            display_width = dwidth,
            display_height = dheight,
            window_width = wwidth,
            window_height = wheight,
            state = state,
        )

        self.build_menu()
        self.build_widget_tree()
        self.build_layout()


    def build_widget_tree(self):
        mainframe = Frame(self.root, bg="grey")
        sideframe = Frame(self.root, bg="black")
        status_bar = Frame(self.root, height=20, bg="red")

        activity_bar = Frame(sideframe, width=45);            activity_bar.pack_propagate(False)
        sidebar = Frame(sideframe, width=280);                sidebar.pack_propagate(False)
        editor_top = Frame(mainframe, height=30, bg="grey"); editor_top.pack_propagate(False)
        editor = Text(mainframe)
        panel = Frame(mainframe, height=350, bg="purple");    panel.pack_propagate(False)

        Button(editor_top, width=1, height=1, command=self.togglePanel).pack(side="right")
        Button(editor_top, width=1, height=1, command=self.toggleSidebar).pack(side="right")

        self.bind_to_self(
            mainframe = mainframe,
            sideframe = sideframe,
            status_bar = status_bar,
            editor_top = editor_top,
            editor = editor,
            panel = panel, 
            sidebar = sidebar,
            activity_bar = activity_bar,
        )

    def build_layout(self):
        self.status_bar.pack(side="bottom", fill="x")
        self.sideframe.pack(side="left", fill="y")
        self.mainframe.pack(side="top", fill="both", expand=True)

        self.activity_bar.pack(side="left", fill="y")
        self.sidebar.pack(side="left", fill="y")

        self.editor_top.pack(side="top", fill="x")
        self.editor.pack(side="top", fill="both", expand=True)
        self.panel.pack(side="bottom", fill="x")

    
    #! =================== UTILITIES FUNCTIONS START HERE =================== #!
    def toggleSidebar(self):
        self.state["sidebarVisible"] = not self.state["sidebarVisible"]
        if self.state["sidebarVisible"]:
            self.sidebar.pack(side="left", fill="y")
        else:
            self.sidebar.pack_forget()

    def togglePanel(self):
        self.state["panelVisible"] = not self.state["panelVisible"]
        if self.state["panelVisible"]:
            self.panel.pack(side="bottom", fill="x")
        else:
            self.panel.pack_forget()
        
    #! =================== MENU UTILITIES FUNCTIONS START HERE =================== #!

    def build_menu(self):
        """This contains the code related to menu"""
        self.set_menu(["File", "Edit", "View", "Help"])

        self.fill_sub_menu(
            self.sub_menus["File"],
            {
                "Save": self.menu_save,
                "Save As": self.menu_saveAs,
                "New File": self.menu_newFile,
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

    def menu_save(self):
        pass
    def menu_saveAs(self):
        pass
    def menu_newFile(self):
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