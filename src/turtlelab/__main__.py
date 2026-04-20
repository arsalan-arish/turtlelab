from .core import main
from sys import argv
from pathlib import Path

if len(argv) > 2:
    raise Exception("Only 1 argument is supported, which is filename to load")
filepath = Path.cwd() / argv[1] if len(argv) == 2 else None

if __name__ == "__main__":
    main(filepath)