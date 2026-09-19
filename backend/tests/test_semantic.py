from app import models
from app.services import embedding_service

from .base import DBTestCase


class TestSemantic(DBTestCase):
    def test_embeddings_built_for_all_nodes(self):
        self.assertEqual(self.db.query(models.NodeEmbedding).count(), 119)

    def test_semantic_search_finds_concept_without_exact_name(self):
        hits = embedding_service.semantic_search(
            self.db, "machines that understand images and video", 3
        )
        self.assertTrue(hits)
        self.assertEqual(hits[0]["id"], "computer-vision")

    def test_semantic_search_translation(self):
        hits = embedding_service.semantic_search(
            self.db, "translating text from one language to another", 3
        )
        self.assertTrue(hits)
        self.assertEqual(hits[0]["id"], "machine-translation")

    def test_recommend_excludes_self(self):
        recs = embedding_service.recommend(self.db, "transformer", 5)
        self.assertTrue(recs)
        self.assertTrue(all(r["id"] != "transformer" for r in recs))

    def test_ensure_embeddings_no_rebuild_when_fresh(self):
        self.assertFalse(embedding_service.ensure_embeddings(self.db))
