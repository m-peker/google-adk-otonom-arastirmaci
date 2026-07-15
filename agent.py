# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0

"""
agent.py — Otonom Araştırma Orkestratörü (ARA)
================================================

2 uzman sub-agent + 1 orkestratör: Araştırmacı + Denetçi.
"""

from google.adk.agents import Agent

try:
    from .tools import (
        create_research_plan, get_plan_status, advance_plan_step,
        get_full_report, log_progress,
    )
    from .callbacks import (
        before_agent, after_agent, before_tool, after_tool,
    )
    from .sub_agents import arastirmaci, denetci
except ImportError:
    from tools import (
        create_research_plan, get_plan_status, advance_plan_step,
        get_full_report, log_progress,
    )
    from callbacks import (
        before_agent, after_agent, before_tool, after_tool,
    )
    from sub_agents import arastirmaci, denetci


root_agent = Agent(
    model="gemini-flash-latest",
    name="otonom_arastirmaci",
    description=(
        "🚀 2 uzman agent'lı otonom araştırma: "
        "Araştırmacı araştırır & raporlar, Denetçi kontrol eder."
    ),
    instruction=(
        "Sen bir araştırma orkestratörüsün. 3 uzman agent'ı yönetirsin:\n"
        "- arastirmaci: araştırır VE rapora kaydeder\n"
        "- denetci: raporu denetler, eksikleri söyler\n\n"

        "İŞ AKIŞIN:\n"
        "1. create_research_plan → konuyu 3-5 alt başlığa böl → ONAY AL.\n"
        "2. HER alt başlık için:\n"
        "   advance_plan_step → arastirmaci'yi çağır → sonraki alt konu.\n"
        "3. TÜMÜ bitince: denetci'yi çağır → sonucu göster.\n"
        "4. get_full_report → raporu kullanıcıya SUN.\n\n"

        "KURALLAR: Onaysız başlama. Her konuyu arastirmaci'ye ver. "
        "Bitince denetci'yi çağır. Türkçe."
    ),
    tools=[
        create_research_plan,
        get_plan_status,
        advance_plan_step,
        get_full_report,
        log_progress,
    ],
    sub_agents=[arastirmaci, denetci],
    before_agent_callback=before_agent,
    after_agent_callback=after_agent,
    before_tool_callback=before_tool,
    after_tool_callback=after_tool,
)
