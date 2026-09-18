"use client";

import { useEffect, useRef, useState } from "react";
import { WS_URL } from "./api";
import type { RealtimeEvent, TrendingItem } from "./types";

export interface RealtimeState {
  connected: boolean;
  events: RealtimeEvent[];
  trending: TrendingItem[];
}

/**
 * 连接后端 WebSocket 实时事件流，自动重连 + 心跳。
 * 返回当前连接状态、最近事件、实时趋势榜。
 */
export function useRealtime(maxEvents = 60): RealtimeState {
  const [state, setState] = useState<RealtimeState>({
    connected: false,
    events: [],
    trending: [],
  });
  const retryRef = useRef(0);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let closed = false;
    let retryTimer: ReturnType<typeof setTimeout> | null = null;
    let heartbeat: ReturnType<typeof setInterval> | null = null;

    const connect = () => {
      if (closed) return;
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        retryRef.current = 0;
        setState((s) => ({ ...s, connected: true }));
      };

      ws.onmessage = (ev) => {
        let event: RealtimeEvent;
        try {
          event = JSON.parse(ev.data) as RealtimeEvent;
        } catch {
          return;
        }
        if (event.type === "history") {
          const arr = (event.data?.events ?? []) as RealtimeEvent[];
          setState((s) => ({
            ...s,
            events: [...arr, ...s.events].slice(-maxEvents),
          }));
          return;
        }
        setState((s) => {
          const events = [...s.events, event].slice(-maxEvents);
          const trending =
            event.type === "trending_update" && Array.isArray(event.data?.trending)
              ? (event.data.trending as TrendingItem[])
              : s.trending;
          return { ...s, events, trending };
        });
      };

      ws.onclose = () => {
        setState((s) => ({ ...s, connected: false }));
        if (closed) return;
        const delay = Math.min(30000, 1000 * 2 ** retryRef.current);
        retryRef.current += 1;
        retryTimer = setTimeout(connect, delay);
      };

      ws.onerror = () => {
        ws.close();
      };
    };

    connect();

    heartbeat = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send("ping");
      }
    }, 25000);

    return () => {
      closed = true;
      if (retryTimer) clearTimeout(retryTimer);
      if (heartbeat) clearInterval(heartbeat);
      wsRef.current?.close();
    };
  }, [maxEvents]);

  return state;
}
