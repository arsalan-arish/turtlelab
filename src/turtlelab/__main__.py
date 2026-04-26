from .app import App
import sys
from pathlib import Path

def main():
    argv = sys.argv[1:]
    if len(argv) > 1:
        raise Exception("Only 1 argument is supported, which is filename to load")
    if len(argv) == 1: 
        filepath = Path.cwd() / argv[0]
        print(filepath)
        if not filepath.exists():
            with open(filepath, "w"): pass
        if not filepath.is_file():
            raise Exception("Please give a valid file name")
    else: 
        filepath = None
    
    App(filepath)

if __name__ == "__main__":
    main()