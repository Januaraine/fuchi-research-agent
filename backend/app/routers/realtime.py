import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..services.realtime import manager

router = APIRouter(tags=["realtime"])


@router.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    """实时事件通道：客户端连接后即可收到后端广播的事件流。

    客户端可发送 `ping` 文本，服务端回 `pong`（心跳）。
    """
    await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            if message == "ping":
                await websocket.send_json({"type": "pong", "ts": time.time(), "data": {}})
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        manager.disconnect(websocket)


@router.get("/api/realtime/history")
def realtime_history():
    """最近事件历史（REST 兜底，便于页面初次加载时直接渲染 Activity Feed）。"""
    return {"events": manager.history[-50:]}
