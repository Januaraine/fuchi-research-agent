"""测试基类：每个测试方法使用独立的临时 SQLite 数据库，保证隔离与可重复。

临时库放在 backend/.tests_tmp/ 下（工作区内，沙箱可写；已被 .gitignore 忽略）。
注意：不使用 tempfile.mkdtemp()（在 DSH 沙箱下其创建的目录对 SQLite 不可见），
改用 uuid 手工创建目录。
"""
import shutil
import unittest
import uuid
from pathlib import Path
from unittest import mock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.seed import seed_db
from app.services import embedding_service

# backend/.tests_tmp（位于工作区内，确保沙箱下可写）
TMP_BASE = Path(__file__).resolve().parents[1] / ".tests_tmp"


class DBTestCase(unittest.TestCase):
    def setUp(self):
        TMP_BASE.mkdir(parents=True, exist_ok=True)
        self._tmp = str(TMP_BASE / f"test_{uuid.uuid4().hex}")
        Path(self._tmp).mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(
            f"sqlite:///{Path(self._tmp, 'test.db').as_posix()}",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        self.db = self.Session()
        seed_db(self.db)
        embedding_service.build_embeddings(self.db)
        # 强制走「无 LLM」路径，避免本机 .env 配置影响测试确定性。
        self._llm_patcher = mock.patch("app.services.llm.LLM_API_BASE", None)
        self._llm_patcher.start()

    def tearDown(self):
        self._llm_patcher.stop()
        self.db.close()
        self.engine.dispose()
        shutil.rmtree(self._tmp, ignore_errors=True)
