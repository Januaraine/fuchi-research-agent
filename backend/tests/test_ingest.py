import unittest

from app.ingest import wikipedia
from app.ingest.pipeline import map_category


class TestWikipediaPure(unittest.TestCase):
    def test_slugify_strips_disambiguation(self):
        self.assertEqual(wikipedia.slugify("Transformer (deep learning)"), "transformer")

    def test_slugify_spaces(self):
        self.assertEqual(wikipedia.slugify("Machine learning"), "machine-learning")

    def test_slugify_underscores_and_case(self):
        self.assertEqual(
            wikipedia.slugify("Generative_adversarial_network"), "generative-adversarial-network"
        )

    def test_clean_extract_collapses_whitespace(self):
        self.assertEqual(wikipedia.clean_extract("  hello\n\n   world  "), "hello world")

    def test_clean_extract_truncates(self):
        out = wikipedia.clean_extract("word " * 300, max_len=100)
        self.assertLessEqual(len(out), 100)


class TestCategoryMapping(unittest.TestCase):
    def test_map_architecture(self):
        self.assertEqual(map_category(["Neural network architectures"]), "architecture")

    def test_map_field(self):
        self.assertEqual(map_category(["Deep learning", "Artificial intelligence"]), "field")

    def test_map_dataset(self):
        self.assertEqual(map_category(["Datasets in computer vision"]), "dataset")

    def test_map_default_concept(self):
        self.assertEqual(map_category(["Miscellaneous topics"]), "concept")


if __name__ == "__main__":
    unittest.main()
