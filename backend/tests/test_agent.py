import unittest

from app import models
from app.services.agent import AgentService

from .base import DBTestCase


class TestAgentTools(DBTestCase):
    def test_four_tools_registered(self):
        infos = AgentService.tool_infos()
        self.assertEqual({t["name"] for t in infos},
                         {"vector_search", "graph_search", "source_retrieve", "rag_answer"})

    def test_call_each_tool(self):
        svc = AgentService(self.db)
        self.assertTrue(svc._vector_search("transformer")["hits"])
        g = svc._graph_search("transformer")
        self.assertIn("relations", g)
        self.assertIn("transformer", g["center"])
        s = svc._source_retrieve("transformer")
        self.assertEqual(s["id"], "transformer")
        self.assertTrue(s["source_url"])
        r = svc._rag_answer("what is transformer?")
        self.assertEqual(r["status"], "retrieval_ready_no_llm")


class TestAgentFallback(DBTestCase):
    def test_relation_intent_uses_graph_search(self):
        r = AgentService(self.db).run("Transformer 和计算机视觉有什么关系？")
        self.assertEqual(r["status"], "no_llm")
        self.assertFalse(r["llm_used"])
        actions = [s["action"] for s in r["steps"]]
        self.assertIn("vector_search", actions)
        self.assertIn("graph_search", actions)
        self.assertIn("rag_answer", actions)
        self.assertTrue(r["answer"])
        self.assertTrue(r["evidence"])

    def test_run_persists_agent_run(self):
        r = AgentService(self.db).run("什么是 BERT？")
        self.assertTrue(r["run_id"] > 0)
        self.assertEqual(self.db.query(models.AgentRun).count(), 1)


class TestAgentParse(unittest.TestCase):
    def test_parse_action(self):
        self.assertEqual(
            AgentService._parse_action('{"action": "vector_search", "args": {"query": "x"}}')["action"],
            "vector_search",
        )

    def test_parse_action_final(self):
        parsed = AgentService._parse_action('{"action": "final", "answer": "ok", "evidence": ["a"]}')
        self.assertEqual(parsed["action"], "final")
        self.assertEqual(parsed["evidence"], ["a"])

    def test_parse_invalid_returns_none(self):
        self.assertIsNone(AgentService._parse_action("no json here at all"))
