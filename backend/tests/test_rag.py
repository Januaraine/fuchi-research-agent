from app.services.rag_service import RAGService

from .base import DBTestCase


class TestRAG(DBTestCase):
    def test_query_no_llm_returns_retrieval(self):
        r = RAGService(self.db).query("What is the transformer architecture?")
        self.assertEqual(r["status"], "retrieval_ready_no_llm")
        self.assertTrue(r["retrieved"])
        self.assertIsNone(r["answer"])
        self.assertTrue(r["context"])

    def test_query_retrieves_relevant_nodes(self):
        r = RAGService(self.db).query("ResNet and Transformer in computer vision")
        ids = {s["id"] for s in r["retrieved"]}
        self.assertTrue(ids & {"transformer", "resnet", "computer-vision", "vision-transformer"})

    def test_query_no_context(self):
        r = RAGService(self.db).query("qqzzxvwzy plmokn")
        self.assertEqual(r["status"], "no_context")
        self.assertEqual(r["retrieved"], [])
        self.assertIsNone(r["answer"])

    def test_retrieve_returns_tuples_with_score(self):
        hits = RAGService(self.db).retrieve("neural networks", k=5)
        self.assertTrue(hits)
        for node, score in hits:
            self.assertTrue(hasattr(node, "id"))
            self.assertIsInstance(score, float)
