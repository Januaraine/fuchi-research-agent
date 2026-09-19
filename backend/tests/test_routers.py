from app import schemas
from app.routers import agent as agent_router
from app.routers import graph as graph_router
from app.routers import nodes as nodes_router
from app.routers import rag as rag_router
from app.routers import search as search_router
from app.routers import semantic as semantic_router
from app.routers import stats as stats_router

from .base import DBTestCase


class TestStatsRouter(DBTestCase):
    def test_health(self):
        self.assertEqual(stats_router.health()["status"], "ok")

    def test_stats(self):
        s = stats_router.stats(db=self.db)
        self.assertEqual(s.nodes, 119)
        self.assertGreater(s.relations, 200)
        self.assertIn("field", s.categories)


class TestNodesRouter(DBTestCase):
    def test_get_node(self):
        d = nodes_router.get_node("transformer", db=self.db)
        self.assertEqual(d.name, "Transformer")
        self.assertTrue(d.description)
        self.assertTrue(d.outgoing or d.incoming)
        self.assertTrue(d.related)

    def test_get_node_not_found(self):
        from fastapi import HTTPException

        with self.assertRaises(HTTPException):
            nodes_router.get_node("does-not-exist", db=self.db)


class TestGraphRouter(DBTestCase):
    def test_full_graph(self):
        g = graph_router.get_graph(db=self.db)
        self.assertEqual(len(g.nodes), 119)
        self.assertGreater(len(g.edges), 200)

    def test_neighbors(self):
        g = graph_router.get_neighbors("transformer", db=self.db)
        self.assertGreater(len(g.nodes), 1)
        self.assertGreater(len(g.edges), 0)


class TestSearchRouter(DBTestCase):
    def test_search_hits(self):
        res = search_router.search("transformer", db=self.db)
        self.assertTrue(any("ransformer" in n.name for n in res))


class TestSemanticRouter(DBTestCase):
    def test_compare(self):
        c = semantic_router.compare("machines that understand images", db=self.db)
        self.assertEqual(c.semantic[0].id, "computer-vision")
        self.assertGreater(len(c.semantic), 0)


class TestRagRouter(DBTestCase):
    def test_rag_query(self):
        out = rag_router.rag_query(schemas.RagQueryIn(question="What is BERT?"), db=self.db)
        self.assertEqual(out["status"], "retrieval_ready_no_llm")
        self.assertTrue(out["retrieved"])


class TestAgentRouter(DBTestCase):
    def test_agent_query(self):
        out = agent_router.agent_query(
            schemas.AgentQueryIn(question="Transformer 和计算机视觉有什么关系？"), db=self.db
        )
        self.assertIn(out["status"], ("no_llm", "completed"))
        self.assertTrue(out["steps"])
        self.assertTrue(out["evidence"])

    def test_agent_runs(self):
        agent_router.agent_query(schemas.AgentQueryIn(question="什么是 BERT？"), db=self.db)
        runs = agent_router.agent_runs(db=self.db)
        self.assertEqual(len(runs), 1)
