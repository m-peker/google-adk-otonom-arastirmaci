# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0

"""
callbacks.py — Otonom Agent Callback'leri (ADK 2.x)
=====================================================

Callback İmzaları (ADK 2.x):
  before_agent(CallbackContext)           -> Optional[Content]
  after_agent(CallbackContext)            -> Optional[Content]
  before_tool(BaseTool, dict, Context)    -> Optional[dict]
  after_tool(BaseTool, dict, Context, dict) -> Optional[dict]
"""

import datetime
import time
from typing import Any, Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types


_session_stats = {
    "tool_calls": 0,
    "start_time": None,
    "errors": 0,
}


def reset_session_stats():
    global _session_stats
    _session_stats = {
        "tool_calls": 0,
        "start_time": time.time(),
        "errors": 0,
    }


def get_session_stats() -> dict:
    elapsed = time.time() - (_session_stats["start_time"] or time.time())
    return {**_session_stats, "elapsed_seconds": round(elapsed, 1)}


# ═══ AGENT CALLBACK'LERİ (CallbackContext alır) ═══

def before_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """Kullanıcı girdisini loglar, güvenlik filtresi uygular."""
    if _session_stats["start_time"] is None:
        _session_stats["start_time"] = time.time()

    user_input = callback_context.user_content
    if user_input and user_input.parts:
        text = "".join(p.text or "" for p in user_input.parts)
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*60}")
        print(f"📥 [{ts}] KULLANICI GİRDİSİ")
        print(f"   '{text[:120]}{'...' if len(text) > 120 else ''}'")
        print(f"{'='*60}")

        dangerous = ["rm -rf", "format c:", "del /f", "shutdown",
                     "eval(", "exec(", "__import__", "os.system"]
        for pattern in dangerous:
            if pattern in text.lower():
                print(f"  ⛔ GÜVENLİK: '{pattern}' tespit edildi!")
                return types.Content(
                    role="model",
                    parts=[types.Part.from_text(
                        text="⛔ Güvenlik ihlali: Bu komut çalıştırılamaz."
                    )],
                )
    return None


def after_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """Oturum istatistiklerini loglar."""
    stats = get_session_stats()
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n📊 [{ts}] OTURUM İSTATİSTİKLERİ")
    print(f"   Tool çağrısı: {stats['tool_calls']}")
    print(f"   Hata: {stats['errors']}")
    print(f"   Süre: {stats['elapsed_seconds']}sn")
    print(f"{'='*60}\n")
    return None


# ═══ TOOL CALLBACK'LERİ (ADK 2.x: BaseTool, dict, Context alır) ═══

def before_tool(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
) -> Optional[dict]:
    """Tool çağrısını loglar, kota kontrolü yapar (max 30)."""
    _session_stats["tool_calls"] += 1

    if _session_stats["tool_calls"] > 30:
        print(f"  ⚠️ Tool limiti aşıldı ({_session_stats['tool_calls']})")
        return {"status": "error", "message": "Tool limiti aşıldı."}

    tool_name = getattr(tool, 'name', str(tool))
    print(f"  🔧 [{tool_name}] çağrılıyor... (args: {args})")
    return None


def after_tool(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
    tool_response: dict,
) -> Optional[dict]:
    """Tool sonucunu kontrol eder, hata varsa loglar."""
    tool_name = getattr(tool, 'name', str(tool))

    if tool_response and isinstance(tool_response, dict):
        if tool_response.get("status") == "error":
            _session_stats["errors"] += 1
            print(f"  ❌ [{tool_name}] HATA: {tool_response.get('message', 'Bilinmeyen')}")
        else:
            print(f"  ✅ [{tool_name}] tamamlandı")
    return None
