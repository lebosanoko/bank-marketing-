"""Validate presence of the locally supplied UCI dataset."""
from pathlib import Path

from src.config import DATA_PATH


def main() -> None:
    path = Path(DATA_PATH)
    if not path.is_file():
        raise FileNotFoundError(f"Placez le fichier Bank Marketing bank-full.csv dans {path}")
    print(f"Dataset trouvé : {path} ({path.stat().st_size:,} octets)")


if __name__ == "__main__":
    main()
