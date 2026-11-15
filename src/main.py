import os

from model import ModSearchResult, search_mods, get_mod_file


def main() -> None:
    search_results: list[ModSearchResult] = search_mods("Immersive Third Person - True First Person Camera - Compatibility Fix", verbose=False)

    mod = get_mod_file(search_results[0])
    print(mod)



if __name__ == "__main__":
    main()
