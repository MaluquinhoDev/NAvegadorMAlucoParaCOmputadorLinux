import unittest

from app.core import HOME_URL, MAX_RESIDENT_TABS, MAX_TABS, SUSPEND_AFTER_SECONDS, can_create_tab, is_youtube_shorts, normalize_input


class BrowserCoreTests(unittest.TestCase):
    def test_empty_input_opens_home(self):
        self.assertEqual(normalize_input("  "), HOME_URL)

    def test_url_without_scheme_gets_https(self):
        self.assertEqual(normalize_input("example.com"), "https://example.com")

    def test_search_text_uses_search_engine(self):
        self.assertEqual(normalize_input("python listas"), "https://duckduckgo.com/?q=python+listas")

    def test_unsupported_scheme_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_input("javascript:alert(1)")

    def test_low_memory_tab_limits(self):
        self.assertEqual(MAX_TABS, 12)
        self.assertEqual(MAX_RESIDENT_TABS, 3)
        self.assertEqual(SUSPEND_AFTER_SECONDS, 180)
        self.assertTrue(can_create_tab(MAX_TABS - 1))
        self.assertFalse(can_create_tab(MAX_TABS))

    def test_shorts_detection(self):
        self.assertTrue(is_youtube_shorts("https://www.youtube.com/shorts/abc"))
        self.assertFalse(is_youtube_shorts("https://www.youtube.com/watch?v=abc"))


if __name__ == "__main__":
    unittest.main()
