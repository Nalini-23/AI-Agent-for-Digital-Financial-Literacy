"""
Multilingual Support Module for Digital Financial Literacy Agent
Handles language detection, translation, and language-aware responses.
"""

from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

# Supported languages with display names and ISO codes
SUPPORTED_LANGUAGES: dict[str, dict] = {
    "en": {"name": "English", "native": "English", "flag": "🇬🇧"},
    "hi": {"name": "Hindi", "native": "हिंदी", "flag": "🇮🇳"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "flag": "🇮🇳"},
    "te": {"name": "Telugu", "native": "తెలుగు", "flag": "🇮🇳"},
    "bn": {"name": "Bengali", "native": "বাংলা", "flag": "🇮🇳"},
    "mr": {"name": "Marathi", "native": "मराठी", "flag": "🇮🇳"},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી", "flag": "🇮🇳"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "flag": "🇮🇳"},
    "ml": {"name": "Malayalam", "native": "മലയാളം", "flag": "🇮🇳"},
    "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ", "flag": "🇮🇳"},
}

# Financial terms that should NOT be translated (kept as-is)
FINANCIAL_TERMS_NO_TRANSLATE = {
    "UPI", "NEFT", "RTGS", "IMPS", "OTP", "PIN", "ATM", "EMI", "SIP",
    "KYC", "PAN", "PPF", "NPS", "EPF", "FD", "RD", "ELSS", "NBFC",
    "RBI", "SEBI", "NPCI", "IRDAI", "AMFI", "DICGC",
}


def detect_language(text: str) -> str:
    """
    Detect the language of the input text.

    Args:
        text: Input text string

    Returns:
        ISO language code (e.g., 'en', 'hi', 'ta')
    """
    try:
        from langdetect import detect, DetectorFactory
        DetectorFactory.seed = 42  # For reproducibility
        detected = detect(text)
        # Map to supported languages, default to English
        return detected if detected in SUPPORTED_LANGUAGES else "en"
    except Exception:
        return "en"


def translate_text(text: str, target_lang: str, source_lang: str = "auto") -> str:
    """
    Translate text to the target language.

    Args:
        text: Source text
        target_lang: Target ISO language code
        source_lang: Source ISO language code or "auto" for detection

    Returns:
        Translated text (or original if translation fails/not needed)
    """
    if target_lang == "en" or target_lang == source_lang:
        return text

    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(
            source=source_lang if source_lang != "auto" else "auto",
            target=target_lang,
        )
        translated = translator.translate(text)
        return translated if translated else text
    except Exception:
        return text


def translate_query_to_english(query: str, detected_lang: str) -> str:
    """
    Translate a user query to English for RAG retrieval.
    English is used as the retrieval language since the knowledge base is primarily in English.

    Args:
        query: User's query in any language
        detected_lang: Detected language code

    Returns:
        Query translated to English
    """
    if detected_lang == "en":
        return query
    return translate_text(query, target_lang="en", source_lang=detected_lang)


def translate_response(response: str, target_lang: str) -> str:
    """
    Translate the agent's English response to the user's preferred language.

    Args:
        response: English response from the LLM
        target_lang: User's preferred language code

    Returns:
        Translated response
    """
    if target_lang == "en":
        return response
    return translate_text(response, target_lang=target_lang, source_lang="en")


def get_language_instruction(lang_code: str) -> str:
    """
    Generate a system instruction for the LLM to respond in the desired language.

    Args:
        lang_code: ISO language code

    Returns:
        Instruction string for the LLM prompt
    """
    lang_info = SUPPORTED_LANGUAGES.get(lang_code, SUPPORTED_LANGUAGES["en"])
    if lang_code == "en":
        return "Respond in clear, simple English. Use everyday language, not financial jargon."
    return (
        f"The user's preferred language is {lang_info['name']} ({lang_info['native']}). "
        f"Respond in {lang_info['name']} using simple, easy-to-understand language. "
        f"Keep financial terms like UPI, SIP, EMI, KYC, OTP, PAN in their original form. "
        f"If a term doesn't have a clear translation, explain it in {lang_info['name']}."
    )


def get_greeting(lang_code: str) -> str:
    """Return a culturally appropriate greeting in the user's language."""
    greetings = {
        "en": "Hello! I'm your Digital Financial Literacy Assistant. How can I help you today?",
        "hi": "नमस्ते! मैं आपका डिजिटल वित्तीय साक्षरता सहायक हूं। आज मैं आपकी कैसे मदद कर सकता हूं?",
        "ta": "வணக்கம்! நான் உங்கள் டிஜிட்டல் நிதி கல்வி உதவியாளர். இன்று உங்களுக்கு எப்படி உதவலாம்?",
        "te": "నమస్కారం! నేను మీ డిజిటల్ ఆర్థిక అక్షరాస్యత సహాయకుడిని. ఈ రోజు నేను మీకు ఎలా సహాయపడగలను?",
        "bn": "নমস্কার! আমি আপনার ডিজিটাল আর্থিক সাক্ষরতা সহকারী। আজ আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
        "mr": "नमस्कार! मी तुमचा डिजिटल आर्थिक साक्षरता सहाय्यक आहे. आज मी तुम्हाला कशी मदत करू?",
        "gu": "નમસ્તે! હું તમારો ડિજિટલ નાણાકીય સાક્ષરતા સહાયક છું. આજે હું તમને કેવી રીતે મદદ કરી શકું?",
        "kn": "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಡಿಜಿಟಲ್ ಹಣಕಾಸು ಸಾಕ್ಷರತೆ ಸಹಾಯಕ. ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
        "ml": "നമസ്കാരം! ഞാൻ നിങ്ങളുടെ ഡിജിറ്റൽ ഫിനാൻഷ്യൽ ലിറ്ററസി അസിസ്റ്റന്റ് ആണ്. ഇന്ന് ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കാം?",
        "pa": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਤੁਹਾਡਾ ਡਿਜੀਟਲ ਵਿੱਤੀ ਸਾਖਰਤਾ ਸਹਾਇਕ ਹਾਂ। ਅੱਜ ਮੈਂ ਤੁਹਾਡੀ ਕਿਵੇਂ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?",
    }
    return greetings.get(lang_code, greetings["en"])
