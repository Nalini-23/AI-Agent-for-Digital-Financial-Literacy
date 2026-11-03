"""
Scam Checker Module for Digital Financial Literacy Agent
Analyzes a pasted SMS/message and returns:
  - risk_level: HIGH / MEDIUM / LOW
  - red_flags: list of specific red flags found
  - scam_type: identified category of scam
  - verdict: one-line summary
  - actions: what the user should do
  - helplines: emergency numbers

Uses rule-based pattern matching first (fast, offline),
then IBM Granite for nuanced analysis and explanation.
"""

from __future__ import annotations
import re

# ── Red-flag pattern library ──────────────────────────────────────────────────

RED_FLAG_PATTERNS: list[dict] = [
    # OTP / PIN harvesting
    {
        "id": "otp_share",
        "pattern": r"\botp\b|\bone.?time.?pass|\bverification.?code\b|\bsecret.?code\b",
        "flag": "Asks for OTP / one-time password",
        "severity": "HIGH",
    },
    {
        "id": "upi_pin",
        "pattern": r"\bupi.?pin\b|\benter.{0,20}pin\b|\bshare.{0,20}pin\b|\bsend.{0,20}pin\b",
        "flag": "Asks for UPI PIN (banks/NPCI never ask for this)",
        "severity": "HIGH",
    },
    {
        "id": "cvv",
        "pattern": r"\bcvv\b|\bcard.?number\b|\bexpiry\b|\bdebit.?card\b|\bcredit.?card.?details\b",
        "flag": "Requests card number / CVV / expiry date",
        "severity": "HIGH",
    },
    {
        "id": "aadhaar_leak",
        "pattern": r"\baadhaar\b.{0,30}(share|send|provide|enter|verify|update)\b|\b(share|send|provide|enter|verify|update)\b.{0,30}\baadhaar\b",
        "flag": "Asks to share Aadhaar number over message/call",
        "severity": "HIGH",
    },
    {
        "id": "kyc_urgency",
        "pattern": r"\bkyc\b.{0,40}(expire|block|suspend|deactivat|urgent|immediately|today|24.hour|48.hour)\b|(expire|block|suspend|deactivat|urgent|immediately|today|24.hour|48.hour).{0,40}\bkyc\b",
        "flag": "KYC update demanded with urgency or account-block threat",
        "severity": "HIGH",
    },
    {
        "id": "remote_access",
        "pattern": r"\banydesk\b|\bteamviewer\b|\bquicksupp\b|\bscreen.share\b|\bremote.access\b|\binstall.{0,20}app\b",
        "flag": "Asks to install remote access / screen-sharing app",
        "severity": "HIGH",
    },
    {
        "id": "fake_prize",
        "pattern": r"\b(won|winner|selected|congratulation|lucky).{0,40}(prize|reward|lottery|crore|lakh|cash|gift)\b",
        "flag": "Fake prize / lottery / cashback claim",
        "severity": "HIGH",
    },
    {
        "id": "processing_fee",
        "pattern": r"\b(pay|send|transfer|deposit).{0,30}(fee|charge|tax|processing|registration|activation|unlock|release)\b",
        "flag": "Upfront fee required to claim prize or loan",
        "severity": "HIGH",
    },
    {
        "id": "fake_refund",
        "pattern": r"\brefund\b.{0,30}(approve|process|click|link|otp|pin|scan)\b|(approve|process|click|link|otp|pin|scan).{0,30}\brefund\b",
        "flag": "Refund requires clicking link / OTP / PIN entry",
        "severity": "HIGH",
    },
    {
        "id": "suspicious_link",
        "pattern": r"https?://(?!(?:npci|rbi|sbi|hdfcbank|icicibank|axisbank|paytm|phonepe|googlepay|gov\.in|nic\.in)[./])\S+\.(xyz|top|club|tk|ml|ga|cf|work|shop|click|link|online|site|website|info|biz)\b",
        "flag": "Suspicious / unofficial website link (not a known bank or govt domain)",
        "severity": "HIGH",
    },
    {
        "id": "impersonate_bank",
        "pattern": r"\b(rbi|reserve bank|npci|sbi|hdfc|icici|axis|kotak|paytm|phonepe).{0,50}(officer|executive|helpline|customer.?care|team|calling|representative)\b",
        "flag": "Claims to be calling from RBI/bank (official bodies never call asking for credentials)",
        "severity": "HIGH",
    },
    {
        "id": "impersonate_govt",
        "pattern": r"\b(income.?tax|it.?department|cbi|police|court|legal.?notice|arrest|fir)\b.{0,60}(call|send|pay|settle|fine|penalty)\b",
        "flag": "Impersonates govt/law enforcement to create fear",
        "severity": "HIGH",
    },
    {
        "id": "account_block_threat",
        "pattern": r"\b(account|wallet|upi|sim).{0,30}(block|suspend|deactivat|clos|freez).{0,30}(click|link|call|update|verify|immediately|urgent)\b",
        "flag": "Threatens account block unless you act immediately",
        "severity": "HIGH",
    },
    {
        "id": "urgent_click",
        "pattern": r"\b(click|tap|open|visit).{0,20}(link|url|here|below|immediately|now|urgent)\b",
        "flag": "Urgently pushes user to click a link",
        "severity": "MEDIUM",
    },
    {
        "id": "collect_request_trick",
        "pattern": r"\b(approve|accept|confirm).{0,30}(request|payment|collect|receive)\b.{0,30}(money|refund|cashback|prize|reward)\b",
        "flag": "Tricks user into 'approving' a UPI collect request (this sends money, not receives it)",
        "severity": "HIGH",
    },
    {
        "id": "loan_guarantee",
        "pattern": r"\b(instant|guaranteed|pre.?approved|no.?document|paperless).{0,20}loan\b",
        "flag": "Instant / guaranteed / no-document loan offer (likely fake loan app scam)",
        "severity": "MEDIUM",
    },
    {
        "id": "investment_returns",
        "pattern": r"\b(guaranteed|assured|fixed|daily|weekly).{0,20}(return|profit|income|earning|interest).{0,20}(\d{1,3}%|per.?day|per.?week|per.?month)\b",
        "flag": "Promises guaranteed high returns (illegal in India — SEBI violation)",
        "severity": "HIGH",
    },
    {
        "id": "whatsapp_group_invest",
        "pattern": r"\b(join|add|invite).{0,30}(whatsapp|telegram|group|channel).{0,30}(profit|earn|invest|stock|trade|forex|crypto)\b",
        "flag": "Investment scheme promoted via WhatsApp/Telegram group",
        "severity": "HIGH",
    },
    {
        "id": "personal_info_request",
        "pattern": r"\b(send|share|provide|enter|reply).{0,20}(pan|passport|driving.?licen|bank.?account|ifsc|account.?number)\b",
        "flag": "Requests sensitive personal / financial identity documents",
        "severity": "MEDIUM",
    },
]

SCAM_TYPE_MAP = {
    "otp_share": "OTP / Credential Harvesting",
    "upi_pin": "UPI PIN Fraud",
    "cvv": "Card Fraud",
    "aadhaar_leak": "Identity Theft",
    "kyc_urgency": "Fake KYC / Account Block Threat",
    "remote_access": "Remote Access / Screen Sharing Scam",
    "fake_prize": "Fake Lottery / Prize Scam",
    "processing_fee": "Advance Fee Fraud",
    "fake_refund": "Fake Refund Scam",
    "suspicious_link": "Phishing Link",
    "impersonate_bank": "Bank Impersonation",
    "impersonate_govt": "Government Impersonation",
    "account_block_threat": "Account Block Threat",
    "urgent_click": "Phishing / Urgency Manipulation",
    "collect_request_trick": "UPI Collect Request Scam",
    "loan_guarantee": "Fake Loan App Scam",
    "investment_returns": "Investment Fraud / Ponzi Scheme",
    "whatsapp_group_invest": "Social Media Investment Scam",
    "personal_info_request": "Identity / Data Harvesting",
}

# ── Rule-based scanner ────────────────────────────────────────────────────────

def rule_scan(message: str) -> dict:
    """
    Fast offline rule-based scan of a message.
    Returns matched flags with severity and scam types.
    """
    text = message.lower()
    matched: list[dict] = []
    seen_ids: set[str] = set()

    for pattern_def in RED_FLAG_PATTERNS:
        if re.search(pattern_def["pattern"], text, re.IGNORECASE):
            if pattern_def["id"] not in seen_ids:
                matched.append({
                    "flag": pattern_def["flag"],
                    "severity": pattern_def["severity"],
                    "scam_type": SCAM_TYPE_MAP.get(pattern_def["id"], "Financial Fraud"),
                    "pattern_id": pattern_def["id"],
                })
                seen_ids.add(pattern_def["id"])

    return {"matches": matched, "count": len(matched)}


def compute_risk_level(matches: list[dict]) -> str:
    """Compute overall risk level from matched patterns."""
    if not matches:
        return "LOW"
    high_count = sum(1 for m in matches if m["severity"] == "HIGH")
    medium_count = sum(1 for m in matches if m["severity"] == "MEDIUM")
    if high_count >= 1:
        return "HIGH"
    if medium_count >= 2:
        return "HIGH"
    if medium_count == 1:
        return "MEDIUM"
    return "LOW"


# ── IBM Granite analysis ──────────────────────────────────────────────────────

SCAM_ANALYSIS_PROMPT = """You are a cybersecurity expert specializing in Indian financial fraud detection.

A user has shared the following suspicious message for analysis:

--- MESSAGE START ---
{message}
--- MESSAGE END ---

Pre-scan found these red flags: {flags_text}

Analyze this message and respond ONLY in this exact JSON format (no other text before or after):
{{
  "verdict": "one sentence summary of whether this is a scam and why",
  "scam_type": "most likely scam category name",
  "confidence": "HIGH or MEDIUM or LOW",
  "explanation": "2-3 sentences explaining the scam tactics being used",
  "red_flags": ["flag 1", "flag 2", "flag 3"],
  "actions": ["action 1", "action 2", "action 3"],
  "safe_message": "one sentence of reassurance or advice"
}}"""


def analyze_with_granite(message: str, pre_scan_flags: list[str], granite_client) -> dict:
    """Use IBM Granite to deeply analyze the message and enrich the result."""
    flags_text = "; ".join(pre_scan_flags) if pre_scan_flags else "None detected by pattern scan"
    prompt = SCAM_ANALYSIS_PROMPT.format(
        message=message[:1500],  # cap to avoid token overflow
        flags_text=flags_text,
    )
    try:
        raw = granite_client.generate(prompt, max_tokens=500)
        # Extract JSON from response
        import json
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass
    return {}


# ── Main entry point ──────────────────────────────────────────────────────────

STANDARD_ACTIONS = {
    "HIGH": [
        "Do NOT click any links or call numbers in the message",
        "Do NOT share OTP, UPI PIN, CVV, Aadhaar, or any password with anyone",
        "Call the National Cyber Crime Helpline: 1930 immediately",
        "Report online at cybercrime.gov.in",
        "Block the sender's number",
        "If you already shared details, contact your bank's fraud helpline NOW",
    ],
    "MEDIUM": [
        "Do NOT respond to this message or click any links",
        "Do NOT share any personal or financial information",
        "Verify by calling the official helpline of the institution (from their website)",
        "Report at cybercrime.gov.in if you feel threatened",
        "Block the sender",
    ],
    "LOW": [
        "This message appears low-risk but stay cautious",
        "Never share OTP, PIN, or passwords with anyone",
        "When in doubt, call the official customer care number from the back of your card or official website",
    ],
}

HELPLINES = [
    {"name": "National Cyber Crime Helpline", "number": "1930", "note": "Call immediately for any financial fraud"},
    {"name": "Cyber Crime Portal (Online)", "number": "cybercrime.gov.in", "note": "File complaint online"},
    {"name": "RBI Helpline", "number": "14440", "note": "For banking related complaints"},
    {"name": "TRAI DND (Stop spam SMS)", "number": "1909", "note": "Register to block promotional messages"},
]


def check_scam(message: str, granite_client=None) -> dict:
    """
    Full scam check pipeline.

    Args:
        message: The suspicious SMS/message text pasted by user
        granite_client: GraniteClient instance (optional; enriches analysis with IBM AI)

    Returns:
        Dict with risk_level, red_flags, scam_type, verdict, actions, helplines, granite_analysis
    """
    if not message or not message.strip():
        return {"error": "No message provided"}

    message = message.strip()

    # Step 1: Fast rule-based scan
    scan = rule_scan(message)
    matches = scan["matches"]
    risk_level = compute_risk_level(matches)

    red_flags = [m["flag"] for m in matches]
    scam_types = list(dict.fromkeys(m["scam_type"] for m in matches))  # deduplicated
    scam_type = scam_types[0] if scam_types else "Unknown / Unsure"

    # Step 2: IBM Granite deep analysis (if available)
    granite_result: dict = {}
    if granite_client:
        granite_result = analyze_with_granite(message, red_flags, granite_client)
        # Merge Granite findings into red flags
        if granite_result.get("red_flags"):
            for gf in granite_result["red_flags"]:
                if gf not in red_flags:
                    red_flags.append(gf)
        if granite_result.get("scam_type"):
            scam_type = granite_result["scam_type"]
        # Override risk level if Granite is more confident
        if granite_result.get("confidence") == "HIGH" and risk_level != "HIGH":
            risk_level = "HIGH"

    # Step 3: Build verdict
    if granite_result.get("verdict"):
        verdict = granite_result["verdict"]
    elif risk_level == "HIGH":
        verdict = f"HIGH RISK — This message shows strong signs of {scam_type}. Do not engage."
    elif risk_level == "MEDIUM":
        verdict = f"MEDIUM RISK — This message has suspicious elements typical of {scam_type}. Verify before acting."
    else:
        verdict = "LOW RISK — No major red flags detected, but always stay cautious with unsolicited messages."

    # Step 4: Explanation
    explanation = granite_result.get("explanation", "")

    # Step 5: Actions
    actions = STANDARD_ACTIONS[risk_level]

    return {
        "risk_level": risk_level,
        "verdict": verdict,
        "scam_type": scam_type,
        "red_flags": red_flags,
        "explanation": explanation,
        "actions": actions,
        "helplines": HELPLINES,
        "pattern_matches": len(matches),
        "granite_enhanced": bool(granite_result),
    }
