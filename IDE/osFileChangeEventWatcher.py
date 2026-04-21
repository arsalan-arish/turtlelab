# 🧩 Minimal Windows OS event watcher (pure stdlib via ctypes)

# This is as small as it gets while still being real OS-driven:

import ctypes
import threading
import tkinter as tk

# --- Windows constants ---
FILE_LIST_DIRECTORY = 0x0001
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000

# --- Windows API setup ---
kernel32 = ctypes.windll.kernel32

CreateFileW = kernel32.CreateFileW
ReadDirectoryChangesW = kernel32.ReadDirectoryChangesW

# --- Watch function ---
def watch_directory(path, callback):
    handle = CreateFileW(
        path,
        FILE_LIST_DIRECTORY,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        None,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS,
        None
    )

    buffer = ctypes.create_string_buffer(1024)
    bytes_returned = ctypes.c_ulong()

    while True:
        success = ReadDirectoryChangesW(
            handle,
            ctypes.byref(buffer),
            len(buffer),
            True,  # recursive
            0x00000010,  # FILE_NOTIFY_CHANGE_LAST_WRITE
            ctypes.byref(bytes_returned),
            None,
            None
        )

        if success:
            callback("File changed!")

# --- Tkinter app ---
root = tk.Tk()
label = tk.Label(root, text="Waiting...")
label.pack()

def on_change(msg):
    # safely update UI from main thread
    root.after(0, lambda: label.config(text=msg))

# --- Start watcher in thread ---
threading.Thread(
    target=watch_directory,
    args=(".", on_change),
    daemon=True
).start()

root.mainloop()