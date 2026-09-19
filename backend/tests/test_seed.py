from app import models
from app.seed import seed_db

from .base import DBTestCase


class TestSeed(DBTestCase):
    def test_seed_counts(self):
        self.assertEqual(self.db.query(models.KnowledgeNode).count(), 119)
        self.assertGreaterEqual(self.db.query(models.KnowledgeRelation).count(), 200)

    def test_seed_idempotent(self):
        result = seed_db(self.db)
        self.assertTrue(result["skipped"])
        self.assertEqual(self.db.query(models.KnowledgeNode).count(), 119)

    def test_node_fields_present(self):
        node = self.db.get(models.KnowledgeNode, "transformer")
        self.assertIsNotNone(node)
        self.assertTrue(node.name)
        self.assertTrue(node.category)
        self.assertTrue(node.description)
        self.assertTrue(node.source)
