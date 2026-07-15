# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0

"""
tools.py — Otonom Araştırma Agent'ı için Araç Seti
====================================================

Bu modül, otonom araştırma agent'ının kullandığı tüm tool'ları içerir:
- Arama simülasyonu (gerçek API yerine demo veriler)
- Plan oluşturma ve yönetme
- Artifact (rapor) oluşturma
- İlerleme takibi
"""

import datetime
import json


# ══════════════════════════════════════════════════════════════
# ARAŞTIRMA ARAÇLARI
# ══════════════════════════════════════════════════════════════

# Demo bilgi tabanı — gerçek uygulamada Google Search / web scraping
KNOWLEDGE_BASE = {
    "yapay zeka": (
        "Yapay zeka (AI), insan benzeri bilişsel işlevleri taklit eden "
        "bilgisayar sistemleridir. 1956'da Dartmouth Konferansı'nda terim "
        "olarak ortaya atılmıştır. Temel alt alanları: makine öğrenmesi, "
        "derin öğrenme, doğal dil işleme, bilgisayarlı görü."
    ),
    "makine öğrenmesi": (
        "Makine öğrenmesi (ML), veriden öğrenen algoritmaların geliştirilmesidir. "
        "Üç ana türü: denetimli öğrenme (labeled data), denetimsiz öğrenme "
        "(unlabeled data), pekiştirmeli öğrenme (reward-based). "
        "Popüler algoritmalar: Linear Regression, SVM, Random Forest, Neural Networks."
    ),
    "derin öğrenme": (
        "Derin öğrenme, çok katmanlı yapay sinir ağlarını kullanan makine "
        "öğrenmesi alt dalıdır. CNN (görüntü), RNN/LSTM (zaman serisi), "
        "Transformer (dil) mimarileri yaygındır. 2012'de AlexNet ile "
        "büyük atılım yapmıştır."
    ),
    "transformer": (
        "Transformer mimarisi, 2017'de 'Attention Is All You Need' makalesiyle "
        "tanıtıldı. Self-attention mekanizması sayesinde paralel işleme yapabilir. "
        "GPT, BERT, T5 gibi modellerin temelidir."
    ),
    "etik": (
        "Yapay zeka etiği; adalet, şeffaflık, hesap verebilirlik, gizlilik "
        "ve güvenlik konularını kapsar. Önyargı (bias), açıklanabilirlik "
        "(XAI), veri mahremiyeti temel tartışma alanlarıdır."
    ),
    "büyük dil modelleri": (
        "Large Language Models (LLM'ler), milyarlarca parametreye sahip "
        "transformer tabanlı modellerdir. GPT-4, Gemini, Claude, Llama "
        "popüler örneklerdir. 2020'lerde üretken AI devrimini başlatmışlardır."
    ),
    "pekiştirmeli öğrenme": (
        "Reinforcement Learning (RL), bir ajanın çevreyle etkileşime girerek "
        "ödül sinyalleri aracılığıyla optimal davranışı öğrendiği ML yaklaşımıdır. "
        "AlphaGo, otonom araçlar, robotik kontrol uygulama alanlarıdır. "
        "RLHF (RL from Human Feedback) ChatGPT'nin başarısında kritik rol oynamıştır."
    ),
    "bilgisayarlı görü": (
        "Computer Vision (CV), görüntü ve videodan anlam çıkaran AI alanıdır. "
        "Nesne tespiti (YOLO), yüz tanıma, segmentasyon (SAM), "
        "görüntü üretimi (Stable Diffusion) önemli uygulamalardır."
    ),
    "doğal dil işleme": (
        "NLP, insan dilini anlayan ve üreten AI sistemleridir. "
        "Duygu analizi, makine çevirisi, metin özetleme, soru cevaplama "
        "temel görevlerdir. BERT, GPT, T5 dönüm noktası modellerdir."
    ),
    "üretken ai": (
        "Generative AI, yeni içerik (metin, görüntü, ses, video) üreten "
        "yapay zeka sistemleridir. GAN'lar, Diffusion modeller, LLM'ler "
        "temel teknolojilerdir. 2022'de ChatGPT ve Stable Diffusion ile "
        "kamuoyunda büyük ilgi görmüştür."
    ),
}


def search_knowledge(query: str) -> dict:
    """Bilgi tabanında anlamsal arama yapar.

    Otonom araştırma sırasında, agent'ın bilgi toplamak için
    kullandığı temel araçtır. Gerçek uygulamada Google Search API
    veya vektör veritabanı kullanılır.

    Args:
        query (str): Aranacak konu veya anahtar kelimeler.

    Returns:
        dict: "results" listesinde eşleşen bilgiler, "count" ile sonuç sayısı.
    """
    query_lower = query.lower()
    results = []

    for topic, content in KNOWLEDGE_BASE.items():
        # Basit anahtar kelime eşleşmesi
        if any(word in content.lower() or word in topic.lower()
               for word in query_lower.split()):
            results.append({
                "topic": topic,
                "content": content,
                "relevance": "high" if topic.lower() in query_lower else "medium",
            })

    return {
        "status": "success",
        "query": query,
        "count": len(results),
        "results": results if results else [
            {"topic": "genel", "content": f"'{query}' hakkında spesifik bilgi bulunamadı. "
                                           "Daha spesifik anahtar kelimeler deneyin."}
        ],
    }


# ══════════════════════════════════════════════════════════════
# PLANLAMA ARAÇLARI
# ══════════════════════════════════════════════════════════════

# Agent'ın oluşturduğu planı hafızada tutmak için global state
_current_plan = {}


def create_research_plan(topic: str, subtopics: str) -> dict:
    """Bir araştırma planı oluşturur.

    Otonom agent, kullanıcının verdiği konuyu alt başlıklara böler
    ve bir araştırma planı oluşturur.

    Args:
        topic (str): Ana araştırma konusu.
        subtopics (str): Virgülle ayrılmış alt konu listesi.
            Örn: "Tarihçe, Temel Kavramlar, Uygulamalar, Gelecek"

    Returns:
        dict: Oluşturulan plan detayları.
    """
    global _current_plan

    subtopic_list = [s.strip() for s in subtopics.split(",") if s.strip()]
    plan = {
        "topic": topic,
        "subtopics": subtopic_list,
        "total_steps": len(subtopic_list),
        "current_step": 0,
        "status": "planning",
        "created_at": datetime.datetime.now().isoformat(),
    }
    _current_plan = plan

    plan_summary = "\n".join(
        f"  {i+1}. {s}" for i, s in enumerate(subtopic_list)
    )
    return {
        "status": "success",
        "message": f"📋 Araştırma planı oluşturuldu:\n{plan_summary}",
        "plan": plan,
    }


def get_plan_status() -> dict:
    """Mevcut araştırma planının durumunu döndürür.

    Returns:
        dict: Plan durumu.
    """
    if not _current_plan:
        return {"status": "error", "message": "Henüz bir plan oluşturulmadı."}

    return {
        "status": "success",
        "plan": _current_plan,
        "progress": f"{_current_plan['current_step']}/{_current_plan['total_steps']}",
    }


def advance_plan_step() -> dict:
    """Araştırma planında bir sonraki adıma geçer.

    Returns:
        dict: Güncel adım bilgisi.
    """
    global _current_plan

    if not _current_plan:
        return {"status": "error", "message": "Henüz bir plan oluşturulmadı."}

    _current_plan["current_step"] += 1
    step = _current_plan["current_step"]
    total = _current_plan["total_steps"]

    if step > total:
        _current_plan["status"] = "completed"
        return {"status": "success", "message": "✅ Tüm adımlar tamamlandı!"}

    current_subtopic = _current_plan["subtopics"][step - 1]
    return {
        "status": "success",
        "current_step": step,
        "current_subtopic": current_subtopic,
        "progress": f"{step}/{total}",
        "next": _current_plan["subtopics"][step] if step < total else None,
    }


# ══════════════════════════════════════════════════════════════
# ARTIFACT (RAPOR) ARAÇLARI
# ══════════════════════════════════════════════════════════════

_generated_report = ""


def save_report_section(section_title: str, content: str) -> dict:
    """Rapora bir bölüm ekler.

    Args:
        section_title (str): Bölüm başlığı.
        content (str): Bölüm içeriği (Markdown formatında).

    Returns:
        dict: Kaydetme durumu.
    """
    global _generated_report
    section = f"\n## {section_title}\n\n{content}\n"
    _generated_report += section
    return {
        "status": "success",
        "message": f"📝 '{section_title}' bölümü rapora eklendi.",
        "report_length": len(_generated_report),
    }


def get_full_report() -> dict:
    """Tam raporu döndürür.

    Returns:
        dict: Raporun tam metni ve istatistikleri.
    """
    if not _generated_report:
        return {"status": "error", "message": "Henüz rapor içeriği yok."}

    return {
        "status": "success",
        "report": _generated_report,
        "length_chars": len(_generated_report),
        "sections": _generated_report.count("## "),
    }


# ══════════════════════════════════════════════════════════════
# İLERLEME & DURUM ARAÇLARI
# ══════════════════════════════════════════════════════════════

def log_progress(message: str) -> dict:
    """Araştırma ilerlemesini loglar.

    Args:
        message (str): Log mesajı.

    Returns:
        dict: Log durumu.
    """
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"  [{timestamp}] {message}")
    return {"status": "success", "timestamp": timestamp, "message": message}
