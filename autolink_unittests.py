import unittest
import autolink as al
from generate_test_html import TEST_CASES

class TestGetFiletypeLink(unittest.TestCase):
  def test_one(self):
      self.assertEqual(al.get_filetype_link("The Biodeterminist&#39;s Guide to Parenting", "http://issarice.com", "markdown"), "[The Biodeterminist's Guide to Parenting](http://issarice.com)")
      self.assertEqual(al.get_filetype_link("something.dotcom", "https://google.com/", "markdown"), "[something\.dotcom](https://google.com/)")
      self.assertEqual(al.get_filetype_link("Issa Rice | Issa Rice", "https://google.com/", "markdown"), "[Issa Rice | Issa Rice](https://google.com/)")

if __name__ == "__main__":
    unittest.main()
