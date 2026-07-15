#!/usr/bin/env python3
# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0

"""
Otonom Araştırma Agent'ı — İnteraktif Demo
===========================================================

Bu script, otonom araştırma agent'ını interaktif modda çalıştırır.

Kullanım:
    python run.py

Özellikler:
  - Streaming yanıt (anlık akış)
  - Session state yönetimi
  - Callback tabanlı monitoring
  - İnteraktif kullanıcı deneyimi
"""

import asyncio
import os
import sys

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ python-dotenv yüklü değil. pip install python-dotenv")
    sys.exit(1)

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)


def check_api_key():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "PASTE_YOUR_GEMINI_API_KEY_HERE":
        print("\n⚠️  GOOGLE_API_KEY ayarlanmamış!")
        print("   senior/.env dosyasına API anahtarınızı yazın.")
        return False
    return True


async def run_interactive():
    """İnteraktif araştırma döngüsü."""
    from agent import root_agent
    from callbacks import reset_session_stats, get_session_stats

    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="senior_ara",
        session_service=session_service,
        auto_create_session=True,
    )

    user_id = "researcher_user"
    session = await session_service.create_session(
        app_name="senior_ara",
        user_id=user_id,
    )

    print("\n" + "=" * 65)
    print("  🚀 OTONOM ARAŞTIRMA AGENT'I (ARA)")
    print("  Google ADK — Otonom Araştırma Agent'ı")
    print("=" * 65)
    print("\n  Bu agent, verdiğiniz konuyu:")
    print("  1. Alt başlıklara böler (Planla)")
    print("  2. Her başlığı derinlemesine araştırır (Araştır)")
    print("  3. Profesyonel rapor formatına dönüştürür (Yaz)")
    print("  4. Kalite kontrolünden geçirir (Denetle)")
    print("  5. Sonucu size sunar (Sun)")
    print("\n  💡 Örnek konu: 'Yapay zeka etiği'")
    print("  💡 Çıkmak için: 'quit' veya Ctrl+C\n")

    reset_session_stats()

    while True:
        try:
            user_input = input("  🧠 Araştırma konusu > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  👋 Görüşmek üzere!")
            break

        if user_input.lower() in ("quit", "exit", "q", "çıkış"):
            print("  👋 Görüşmek üzere!")
            break

        if not user_input:
            continue

        print(f"\n  ⏳ '{user_input}' konusu araştırılıyor...\n")

        content = types.Content(
            role="user",
            parts=[types.Part.from_text(
                text=f"Lütfen aşağıdaki konuyu otonom olarak araştır:\n\n"
                     f"KONU: {user_input}\n\n"
                     f"Adım adım planla, araştır, raporla, denetle ve sun."
            )],
        )

        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=content,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            if event.partial:
                                print(part.text, end="", flush=True)
                            else:
                                print(part.text)

            # Session sonrası istatistikler
            stats = get_session_stats()
            print(f"\n  📊 Oturum: {stats['tool_calls']} tool çağrısı, "
                  f"{stats['elapsed_seconds']}sn\n")

            # Yeni konu için sıfırla
            reset_session_stats()

        except Exception as e:
            print(f"\n  ❌ Hata: {e}")
            print("  Lütfen API anahtarınızı ve bağlantınızı kontrol edin.")


async def main():
    load_env()
    if not check_api_key():
        return
    await run_interactive()


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))
    asyncio.run(main())
