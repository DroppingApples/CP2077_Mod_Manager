import unittest

from model import ModSearchResult, search_mods


class TestSearchAndDownload(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_search_wellknown_mod_top_result(self):
        input = "Cyber Engine Tweaks"
        expected: dict[str, str] = {"name": "Cyber Engine Tweaks", "scoped_id": "107"}
        actual: ModSearchResult = search_mods(input)[0]
        self.assertDictEqual(expected, actual)

    def test_search_lesser_known_mod_top_result(self):
        input = "Immersive Third Person - True First Person Camera - Compatibility Fix"
        expected: dict[str, str] = {
            "name": "Immersive Third Person - True First Person Camera - Compatibility Fix",
            "scoped_id": "33471",
        }
        actual: ModSearchResult = search_mods(input)[0]
        self.assertDictEqual(expected, actual)

    def test_feature_two(self):
        pass


if __name__ == "__main__":
    unittest.main()
