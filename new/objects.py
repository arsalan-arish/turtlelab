""" Contains objects used by application to group data """

class FileObject:
    def __init__(self, id, nameVar, filepath, tabBlock, editor):
        self.id = id
        self.nameVar = nameVar
        self.filepath = filepath
        self.tabBlock = tabBlock
        self.editor = editor

        #! For compatibility, the fileobject is connected to the editor as well
        self.editor.fileObject = self

        self.isSaved = BooleanVar(value=True)
        self.isSaved.trace_add("write", self.putModifiedSign)

        self.sign = Label(self.tabBlock, text="*", name="sign")

        self.editor.edit_modified(False)
        self.editor.bind("<<Modified>>", self.on_modified)

    def on_modified(self, *_):
        if self.editor.edit_modified():
            self.isSaved.set(False)
            self.editor.edit_modified(False)  # critical

    def save(self):
        data = self.editor.get("1.0", "end-1c")
        with open(self.filepath, "w") as f:
            f.write(data)

        self.isSaved.set(True)
        self.editor.edit_modified(False)  # reset after save

    def putModifiedSign(self, *_):
        if self.isSaved.get():
            self.sign.pack_forget()
        else:
            self.sign.pack(side="right")


class TabObject:
