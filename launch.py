import sys
from pathlib import Path

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root / "src"))

from uab.main import main

if __name__ == "__main__":
    main()