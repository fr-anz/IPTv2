import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from scripts.clean_dataset import main


if __name__ == "__main__":
    main()
