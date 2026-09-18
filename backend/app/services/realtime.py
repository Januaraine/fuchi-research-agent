"""实时事件系统（Phase 3）。

基于 WebSocket 的轻量事件总线：
- ConnectionManager 管理活跃连接、维护最近事件历史（供后加入 / REST 兜底）。
- realtime_loop 在后台周期性地产生「模拟系统动态」事件：
    * node_activity    —— 随机真实知识节点的活跃度 +1（真实持久化到数据库）
    * user_activity    —— 模拟用户 探索/搜索/打开 某个真实知识节点
    * trending_update  —— 根据持久化的 popularity 计算实时趋势榜
    * system_status    —— 偶尔的系统状态播报

说明：这里模拟的是「系统运行状态」（用户活动 / 访问量 / 趋势 / 系统事件），
而不是伪造知识本身——所有事件指向的都是 seed_data 里的真实世界知识。
"""
from __future__ import annotations

import asyncio
import random
import time

from fastapi import WebSocket

from .. import models
from ..database import SessionLocal

ACTIONS = ("explored", "searched", "opened")
SYSTEM_MESSAGES = (
    "Knowledge graph re-analysis complete.",
    "Trending scores recomputed.",
    "Activity index synchronized.",
    "Connection mesh healthy.",
    "Observatory uplink stable.",
)
HISTORY_LIMIT = 120


class ConnectionManager:
    def __init__(self) -> None:
        self.active: set[WebSocket] = set()
        self.history: list[dict] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.add(websocket)
        # 后加入的客户端先收到最近历史，避免空白等待。
        if self.history:
            await websocket.send_json(
                {"type": "history", "ts": time.time(), "data": {"events": self.history[-30:]}}
            )

    def disconnect(self, websocket: WebSocket) -> None:
        self.active.discard(websocket)

    async def broadcast(self, event: dict) -> None:
        self.history.append(event)
        if len(self.history) > HISTORY_LIMIT:
            self.history = self.history[-HISTORY_LIMIT:]
        stale: list[WebSocket] = []
        for ws in list(self.active):
            try:
                await ws.send_json(event)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self.disconnect(ws)


manager = ConnectionManager()


def _tick() -> list[dict]:
    """一轮事件生成（同步，运行于线程池）。返回本轮要广播的事件列表。"""
    events: list[dict] = []
    now = time.time()
    with SessionLocal() as db:
        nodes = db.query(models.KnowledgeNode).all()
        if not nodes:
            return events

        # 1) 知识活动：随机节点 popularity +delta（真实写入数据库）
        if random.random() < 0.65:
            n = random.choice(nodes)
            delta = round(random.uniform(0.5, 2.5), 2)
            n.popularity = round(n.popularity + delta, 2)
            db.commit()
            events.append(
                {
                    "type": "node_activity",
                    "ts": now,
                    "data": {
                        "node_id": n.id,
                        "name": n.name,
                        "category": n.category,
                        "activity_delta": delta,
                        "popularity": n.popularity,
                    },
                }
            )

        # 2) 用户活动：模拟多名用户对真实节点的行为
        if random.random() < 0.6:
            n = random.choice(nodes)
            events.append(
                {
                    "type": "user_activity",
                    "ts": now,
                    "data": {
                        "user_id": f"User #{random.randint(100, 9999)}",
                        "action": random.choice(ACTIONS),
                        "node_id": n.id,
                        "name": n.name,
                        "category": n.category,
                    },
                }
            )

        # 3) 系统状态：偶尔播报
        if random.random() < 0.12:
            events.append(
                {
                    "type": "system_status",
                    "ts": now,
                    "data": {"status": "live", "message": random.choice(SYSTEM_MESSAGES)},
                }
            )

        # 4) 趋势榜：按 popularity 实时重算
        top = (
            db.query(models.KnowledgeNode)
            .order_by(models.KnowledgeNode.popularity.desc())
            .limit(6)
            .all()
        )
        events.append(
            {
                "type": "trending_update",
                "ts": now,
                "data": {
                    "trending": [
                        {"id": x.id, "name": x.name, "category": x.category, "popularity": x.popularity}
                        for x in top
                    ]
                },
            }
        )
    return events


async def realtime_loop() -> None:
    """后台事件循环：周期性生成并广播事件。永不主动退出，除非被取消。"""
    while True:
        try:
            await asyncio.sleep(random.uniform(2.0, 3.2))
            events = await asyncio.to_thread(_tick)
            for ev in events:
                await manager.broadcast(ev)
        except asyncio.CancelledError:
            raise
        except Exception:
            # 单轮异常不应终止实时循环。
            await asyncio.sleep(1.0)
