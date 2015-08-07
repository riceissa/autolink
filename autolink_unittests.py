import unittest
import autolink as al
from generate_test_html import TEST_CASES

class TestGetFiletypeLink(unittest.TestCase):
    def test_one(self):
        self.assertEqual(al.get_filetype_link("The Biodeterminist's Guide to Parenting", "http://issarice.com", "markdown"), "[The Biodeterminist's Guide to Parenting](http://issarice.com)")
        self.assertEqual(al.get_filetype_link("something.dotcom", "https://google.com/", "markdown"), "[something\.dotcom](https://google.com/)")
        self.assertEqual(al.get_filetype_link("Issa Rice | Issa Rice", "https://google.com/", "markdown"), "[Issa Rice | Issa Rice](https://google.com/)")

    def test_messy_title(self):
        self.assertEqual(al.messy_title_parse("20.1. html — HyperText Markup Language support &mdash; Python 3.4.3 documentation"), "20.1. html — HyperText Markup Language support &mdash; Python 3.4.3 documentation")

if __name__ == "__main__":
    unittest.main()
