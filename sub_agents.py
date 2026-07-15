# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0

"""
sub_agents.py — Uzman Alt Agent'lar
====================================

Bu modül, otonom araştırma sisteminin alt agent'larını tanımlar:
- Araştırmacı (Researcher): Derinlemesine araştırma yapar
- Yazar (Writer): Araştırma sonuçlarını rapor formatına dönüştürür
- Denetçi (Reviewer): Rapor kalitesini kontrol eder
"""

from google.adk.agents import Agent
# Hem adk web (package import) hem python run.py (script import) için:
try:
    from .tools import (
        search_knowledge, create_research_plan, get_plan_status,
        advance_plan_step, save_report_section, get_full_report, log_progress,
    )
except ImportError:
    from tools import (
        search_knowledge, create_research_plan, get_plan_status,
        advance_plan_step, save_report_section, get_full_report, log_progress,
    )


# ══════════════════════════════════════════════════════════════
# ALT AGENT 1: ARAŞTIRMACI (Researcher)
# ══════════════════════════════════════════════════════════════

arastirmaci = Agent(
    model="gemini-flash-latest",
    name="arastirmaci",
    description=(
        "Derinlemesine araştırma yapan ve sonucu hemen rapora kaydeden uzman agent."
    ),
    instruction=(
        "Sen bir KIDEMLİ ARAŞTIRMA ANALİSTİSİN. Görevin:\n\n"
        "1. Sana verilen alt konuyu search_knowledge ile ARAŞTIR.\n"
        "2. İlk aramada yeterli bilgi gelmezse, farklı anahtar kelimelerle TEKRAR ARA.\n"
        "3. Araştırma sonucunu HEMEN save_report_section ile KAYDET.\n"
        "   - section_title: alt konunun adı\n"
        "   - content: araştırma bulguların (Markdown formatında)\n"
        "4. Son olarak kısa bir özet ver:\n"
        "   '✅ [alt konu] araştırıldı ve rapora eklendi.'\n\n"
        "⚠️ save_report_section'ı ASLA UNUTMA! Araştırma bittiğinde hemen çağır.\n"
        "Türkçe, akademik ve objektif ol."
    ),
    tools=[search_knowledge, save_report_section, log_progress],
)


# ══════════════════════════════════════════════════════════════
# ALT AGENT 2: YAZAR (Writer)
# ══════════════════════════════════════════════════════════════

yazar = Agent(
    model="gemini-flash-latest",
    name="yazar",
    description=(
        "Araştırma sonuçlarını profesyonel rapor formatına dönüştüren uzman agent."
    ),
    instruction=(
        "Sen bir TEKNİK YAZARSIN. Görevin:\n\n"
        "1. Sana verilen araştırma sonucunu PROFESYONEL bir formata dönüştür.\n"
        "2. save_report_section ile rapora EKLE.\n"
        "3. Aşağıdaki markdown formatını KULLAN:\n\n"
        "   ## [Bölüm Başlığı]\n"
        "   ### Genel Bakış\n"
        "   [2-3 cümle özet]\n"
        "   ### Detaylı Analiz\n"
        "   [Detaylı açıklama, maddeler halinde]\n"
        "   ### Öne Çıkan Noktalar\n"
        "   - Nokta 1\n"
        "   - Nokta 2\n"
        "   ### Sonuç\n"
        "   [1-2 cümle sonuç]\n\n"
        "4. Akademik ama AKICI bir dil kullan.\n"
        "5. Her zaman Türkçe yaz.\n"
        "6. Bölüm başlığını clear ve descriptive yap."
    ),
    tools=[save_report_section, log_progress],
)


# ══════════════════════════════════════════════════════════════
# ALT AGENT 3: DENETÇİ (Reviewer)
# ══════════════════════════════════════════════════════════════

denetci = Agent(
    model="gemini-flash-latest",
    name="denetci",
    description="Rapor kalitesini kontrol eden, eksikleri tespit eden denetçi agent.",
    instruction=(
        "Sen bir KALİTE DENETÇİSİSİN. Görevin:\n\n"
        "1. get_full_report ile mevcut raporu OKU.\n"
        "2. Aşağıdaki kriterlere göre DEĞERLENDİR:\n"
        "   - Kapsam: Tüm alt konular yeterince ele alınmış mı?\n"
        "   - Derinlik: Analizler yeterince detaylı mı?\n"
        "   - Yapı: Bölümler mantıklı bir sırada mı?\n"
        "   - Dil: Akademik dil tutarlı mı?\n"
        "3. Değerlendirme sonucunu şu formatta RAPORLA:\n\n"
        "   📋 DENETİM RAPORU\n"
        "   ✅ KAPSAM: [yeterli/yetersiz] — [açıklama]\n"
        "   ✅ DERİNLİK: [yeterli/yetersiz] — [açıklama]\n"
        "   ✅ YAPI: [uygun/düzeltilmeli] — [açıklama]\n"
        "   ✅ DİL: [uygun/düzeltilmeli] — [açıklama]\n"
        "   🔄 ÖNERİ: [onaylandı/revize edilmeli] — [gerekçe]\n\n"
        "Her zaman Türkçe yanıt ver. Yapıcı ve spesifik ol."
    ),
    tools=[get_full_report, log_progress],
)
