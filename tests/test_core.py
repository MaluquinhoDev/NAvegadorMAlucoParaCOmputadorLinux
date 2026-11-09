import unittest

from app.core import HOME_URL, HIGH_PRESSURE_SUSPEND_AFTER_SECONDS, CRITICAL_PRESSURE_SUSPEND_AFTER_SECONDS, MAX_RESIDENT_TABS, MAX_TABS, SUSPEND_AFTER_SECONDS, can_create_tab, is_youtube_shorts, memory_pressure_level, normalize_input, search_url


class BrowserCoreTests(unittest.TestCase):
    def test_empty_input_opens_home(self):
        self.assertEqual(normalize_input("  "), HOME_URL)

    def test_url_without_scheme_gets_https(self):
        self.assertEqual(normalize_input("example.com"), "https://example.com")

    def test_search_text_uses_search_engine(self):
        self.assertEqual(normalize_input("python listas"), "https://duckduckgo.com/?q=python+listas")

    def test_search_engine_selection(self):
        self.assertEqual(normalize_input("python listas", "Google"), "https://www.google.com/search?q=python+listas")
        self.assertEqual(normalize_input("python listas", "Startpage"), "https://www.startpage.com/sp/search?query=python+listas")

    def test_unknown_search_engine_falls_back_safely(self):
        self.assertEqual(search_url("linux mint", "unknown"), "https://duckduckgo.com/?q=linux+mint")

    def test_unsupported_scheme_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_input("javascript:alert(1)")

    def test_low_memory_tab_limits(self):
        self.assertEqual(MAX_TABS, 12)
        self.assertEqual(MAX_RESIDENT_TABS, 3)
        self.assertEqual(SUSPEND_AFTER_SECONDS, 180)
        self.assertEqual(HIGH_PRESSURE_SUSPEND_AFTER_SECONDS, 120)
        self.assertEqual(CRITICAL_PRESSURE_SUSPEND_AFTER_SECONDS, 90)
        self.assertTrue(can_create_tab(MAX_TABS - 1))
        self.assertFalse(can_create_tab(MAX_TABS))

    def test_memory_pressure_normal_when_resources_are_available(self):
        meminfo = "MemTotal: 4000000 kB\nMemAvailable: 1500000 kB\n"
        psi = "some avg10=0.00 avg60=0.00 avg300=0.00 total=0\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=0\n"
        self.assertEqual(memory_pressure_level(meminfo, psi), "normal")

    def test_memory_pressure_high_requires_low_memory_and_psi(self):
        meminfo = "MemAvailable: 450000 kB\n"
        psi = "some avg10=3.00 avg60=1.00 avg300=0.50 total=100\nfull avg10=0.10 avg60=0.10 avg300=0.10 total=10\n"
        self.assertEqual(memory_pressure_level(meminfo, psi), "high")

    def test_memory_pressure_critical_requires_full_stalls(self):
        meminfo = "MemAvailable: 300000 kB\n"
        psi = "some avg10=9.00 avg60=4.00 avg300=2.00 total=100\nfull avg10=1.20 avg60=0.50 avg300=0.20 total=50\n"
        self.assertEqual(memory_pressure_level(meminfo, psi), "critical")

    def test_missing_or_malformed_psi_fails_safe(self):
        self.assertEqual(memory_pressure_level("MemAvailable: 100000 kB", ""), "normal")
        self.assertEqual(memory_pressure_level("invalid", "some avg10=99.0"), "normal")

    def test_shorts_detection(self):
        self.assertTrue(is_youtube_shorts("https://www.youtube.com/shorts/abc"))
        self.assertFalse(is_youtube_shorts("https://www.youtube.com/watch?v=abc"))


if __name__ == "__main__":
    unittest.main()
