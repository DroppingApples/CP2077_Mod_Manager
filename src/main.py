import os

from model import search_for_mods


def main() -> None:
    search_for_mods("Torrent", verbose=True)


if __name__ == "__main__":
    main()
