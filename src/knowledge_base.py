"""
Knowledge Base Builder for Digital Financial Literacy Agent
Populates the vector store with curated financial literacy content
covering UPI, scams, interest rates, budgeting, and personal finance.
"""

import os
import json
from typing import Any
from pathlib import Path

# ─────────────────────────────────────────────
# Curated Financial Literacy Knowledge Documents
# ─────────────────────────────────────────────

FINANCIAL_KNOWLEDGE_BASE: list[dict[str, Any]] = [

    # ── UPI (Unified Payments Interface) ──────────────────────────────────────
    {
        "id": "upi_001",
        "topic": "UPI",
        "title": "What is UPI and How It Works",
        "language": "en",
        "source": "NPCI (National Payments Corporation of India)",
        "content": """
UPI (Unified Payments Interface) is a real-time payment system developed by the National Payments Corporation of India (NPCI).
It enables instant money transfers between bank accounts through mobile devices.

Key features:
- Available 24x7, including bank holidays
- Transfer up to ₹1,00,000 per transaction (₹2,00,000 for verified merchants)
- Uses a Virtual Payment Address (VPA) like yourname@bank instead of bank account details
- Linked to your bank account – no separate wallet needed
- Regulated by RBI (Reserve Bank of India)

How to create a UPI ID:
1. Download a UPI-enabled app: PhonePe, Google Pay, Paytm, BHIM, or your bank's app
2. Register with your mobile number linked to your bank account
3. Choose a VPA (Virtual Payment Address) e.g., yourname@okaxis
4. Set a 4 or 6 digit UPI PIN – this is your transaction password

How to send money via UPI:
1. Open your UPI app
2. Tap 'Send Money' or 'Pay'
3. Enter the recipient's UPI ID, mobile number, or scan their QR code
4. Enter the amount
5. Add a note (optional)
6. Enter your UPI PIN to confirm
7. Transaction completes in seconds

Safe UPI practices:
- Never share your UPI PIN with anyone
- Your bank/NPCI will never ask for your UPI PIN
- Only enter PIN to SEND money, never to RECEIVE
- Verify recipient details before confirming
        """,
    },
    {
        "id": "upi_002",
        "topic": "UPI",
        "title": "UPI Safety and Common Mistakes",
        "language": "en",
        "source": "RBI Financial Literacy",
        "content": """
Common UPI scams and how to avoid them:

1. COLLECT REQUEST SCAM: Fraudsters send a collect/receive request saying "approve this to get your refund."
   WARNING: Approving a collect request means YOU are PAYING money, not receiving it.
   Rule: You only need your UPI PIN to SEND money. Receiving money requires no PIN.

2. SCREEN SHARING SCAM: Fraudster poses as customer care and asks you to install AnyDesk or TeamViewer.
   They watch your screen to steal your UPI PIN and OTP.
   Rule: Never share your screen for any financial transaction.

3. FAKE QR CODE SCAM: A QR code is shared claiming it will help you receive money.
   Scanning and paying authenticates payment TO the scammer.
   Rule: QR codes are for paying, not receiving.

4. FAKE CASHBACK SCAM: "You won ₹5,000 cashback! Click here and enter your UPI PIN."
   Rule: Legitimate cashbacks are credited automatically. No PIN is needed.

Important UPI numbers to know:
- NPCI Helpline: 1800-120-1740
- RBI Helpline: 14440
- Cyber Crime Helpline: 1930

If you've been scammed:
1. Immediately call 1930 (National Cyber Crime Helpline)
2. Report at cybercrime.gov.in
3. Contact your bank's fraud helpline
4. File a police complaint with transaction details
        """,
    },
    {
        "id": "upi_hindi_001",
        "topic": "UPI",
        "title": "UPI क्या है और कैसे काम करता है",
        "language": "hi",
        "source": "NPCI India",
        "content": """
UPI (यूनिफाइड पेमेंट्स इंटरफेस) भारत में एक तत्काल भुगतान प्रणाली है।

UPI से पैसे कैसे भेजें:
1. PhonePe, Google Pay, BHIM या अपने बैंक का ऐप खोलें
2. 'पैसे भेजें' या 'Pay' पर क्लिक करें
3. प्राप्तकर्ता का UPI ID या मोबाइल नंबर दर्ज करें
4. राशि दर्ज करें
5. UPI PIN दर्ज करें
6. लेनदेन पूरा हो जाता है

महत्वपूर्ण सुरक्षा नियम:
- अपना UPI PIN किसी के साथ साझा न करें
- बैंक या NPCI कभी PIN नहीं मांगता
- पैसे प्राप्त करने के लिए PIN की जरूरत नहीं होती
- धोखाधड़ी होने पर 1930 पर कॉल करें
        """,
    },

    # ── Online Scam Prevention ────────────────────────────────────────────────
    {
        "id": "scam_001",
        "topic": "Online Scams",
        "title": "Types of Online Financial Scams in India",
        "language": "en",
        "source": "Ministry of Home Affairs, Cyber Crime Portal",
        "content": """
Common online financial scams in India and how to identify them:

1. PHISHING SCAMS
   How it works: You receive a fake email/SMS claiming to be from your bank or RBI, asking you to
   click a link and update your account details.
   Signs: Urgent language, misspelled domains (e.g., "rb1.org.in"), requests for OTP/password
   Safe practice: Banks NEVER ask for OTP, CVV, or password via email/SMS/call.

2. KYC FRAUD
   How it works: Call claiming your bank/Paytm/UPI account will be blocked unless you complete
   "KYC" by sharing your Aadhaar number, OTP, or installing an app.
   Signs: Urgency, pressure, unofficial phone numbers
   Safe practice: KYC is done at bank branches or through official banking apps only.

3. LOAN APP SCAMS
   How it works: Instant loan apps that ask for camera/contact/gallery permissions.
   They then demand high interest and threaten to send morphed photos to your contacts.
   Signs: No RBI registration, demands for upfront fees, excessive permissions
   Safe practice: Only borrow from RBI-registered banks/NBFCs. Check at rbi.org.in/scripts/BS_NBFCList.aspx

4. INVESTMENT FRAUD
   How it works: Promises of "guaranteed 30% monthly returns" via WhatsApp groups or Telegram.
   Signs: Guaranteed high returns, pressure to invest quickly, no SEBI registration
   Safe practice: Verify investment advisors on SEBI's website at sebi.gov.in. No legitimate investment
   guarantees returns.

5. LOTTERY / PRIZE SCAMS
   How it works: "You've won ₹50 lakh in the KBC lottery! Pay ₹5,000 processing fee."
   Signs: Unsolicited prize, upfront payment required, requests for personal details
   Safe practice: You cannot win a lottery you did not enter. Never pay to claim a prize.

6. FAKE CUSTOMER CARE NUMBERS
   How it works: Fraudsters post fake toll-free numbers on Google for Amazon, Flipkart, banks.
   Signs: Not on the official website, asks for remote access or payment
   Safe practice: Only use numbers from the official website or the back of your bank card.

Cyber Crime reporting:
- National Cyber Crime Helpline: 1930
- Online portal: cybercrime.gov.in
- Report fraud UPI transactions to your bank immediately (within 3 days for best results)
        """,
    },
    {
        "id": "scam_002",
        "topic": "Online Scams",
        "title": "How to Verify if a Financial Institution is Legitimate",
        "language": "en",
        "source": "RBI, SEBI, IRDAI",
        "content": """
How to verify financial institutions in India:

BANKS:
- All licensed banks are listed on RBI website: rbi.org.in
- Look for FDIC equivalent – your deposits up to ₹5,00,000 are insured by DICGC (Deposit Insurance
  and Credit Guarantee Corporation)
- Verify bank license at: rbi.org.in/Scripts/bs_ubdcomprehensive.aspx

NBFCs (Non-Banking Financial Companies / Loan Apps):
- Must be registered with RBI
- Check the list at: rbi.org.in/Scripts/BS_NBFCList.aspx
- Legitimate NBFCs do NOT charge upfront processing fees before disbursement

MUTUAL FUNDS & STOCK BROKERS:
- Must be registered with SEBI
- Check at: sebi.gov.in or scores.sebi.gov.in
- Verify advisor registration at AMFI: amfiindia.com

INSURANCE COMPANIES:
- Must be registered with IRDAI
- Check at: irdai.gov.in/ADMINCMS/cms/frmGeneral_Layout.aspx?page=PageNo3880

Red flags for fraudulent institutions:
- No physical address or only P.O. Box
- Promises guaranteed returns (illegal in India)
- Asks for money before providing service
- Not registered with RBI/SEBI/IRDAI
- Uses WhatsApp or Telegram as primary channel
- Pressure tactics: "Offer expires in 1 hour"
        """,
    },

    # ── Interest Rates ────────────────────────────────────────────────────────
    {
        "id": "interest_001",
        "topic": "Interest Rates",
        "title": "Understanding Interest Rates - A Complete Guide",
        "language": "en",
        "source": "RBI Financial Education",
        "content": """
Understanding interest rates in India:

TYPES OF INTEREST:

1. Simple Interest (SI)
   Formula: SI = (Principal × Rate × Time) / 100
   Example: ₹1,00,000 at 10% for 2 years = ₹20,000 interest
   Used for: Short-term loans, Fixed Deposits (sometimes)

2. Compound Interest (CI)
   Formula: CI = P × (1 + r/n)^(n×t) - P
   Interest is calculated on principal + accumulated interest
   Used for: Home loans, personal loans, credit cards, Fixed Deposits
   Note: Compound interest grows much faster than simple interest.

CURRENT TYPICAL INTEREST RATES IN INDIA (2024):

Home Loans: 8.5% - 10.5% per annum
Personal Loans: 10.5% - 24% per annum
Car Loans: 8.5% - 12% per annum
Education Loans: 8% - 15% per annum
Credit Card Outstanding: 24% - 48% per annum (very high!)
Savings Account: 2.5% - 7% per annum
Fixed Deposits: 5.5% - 8% per annum
PPF (Public Provident Fund): 7.1% per annum (government-backed)

SAFE INTEREST RATE FOR A LOAN:
- Home loan: Up to 10% is standard from banks. Avoid above 15%.
- Personal loan: 10.5% - 18% from bank/licensed NBFC is acceptable.
- Anything above 30% should be treated with extreme caution.
- Moneylenders claiming 2% to 5% per MONTH = 24% to 60% per year – this is predatory.

HOW TO COMPARE LOANS – Use EMI Calculator:
EMI Formula: EMI = P × r × (1+r)^n / ((1+r)^n - 1)
Where: P = Principal, r = monthly rate (annual rate/12/100), n = number of months

Key metric to compare: APR (Annual Percentage Rate) – includes all fees
Always ask lenders for the TOTAL cost of the loan, not just the interest rate.

RBI REPO RATE (benchmark):
- Current repo rate is set by RBI's Monetary Policy Committee
- Floating-rate loans (like home loans) change when repo rate changes
- Check current rate at: rbi.org.in
        """,
    },
    {
        "id": "interest_002",
        "topic": "Interest Rates",
        "title": "Credit Cards and Hidden Charges",
        "language": "en",
        "source": "RBI Consumer Education",
        "content": """
Credit Card costs every user should know:

INTEREST CHARGES:
- Credit cards charge 24% - 48% annual interest (2% - 4% per month)
- Interest applies if you don't pay the FULL outstanding amount by due date
- Even paying the "minimum due" means remaining balance accumulates high interest
- Interest is calculated from the date of each transaction, not the statement date

HIDDEN FEES:
1. Annual Fee: ₹500 - ₹5,000 (many cards waive on achieving spending target)
2. Late Payment Fee: ₹100 - ₹1,300 depending on outstanding amount
3. Over-limit Fee: ₹500 - ₹600 if you exceed credit limit
4. Cash Advance Fee: 2.5% - 3.5% of amount + interest from day 1 (no grace period)
5. Foreign Transaction Fee: 1% - 3.5% per transaction
6. EMI conversion fee: 1% - 3%

SMART CREDIT CARD USAGE:
- Pay the FULL outstanding amount every month, not just minimum due
- Set up auto-pay for the full amount if possible
- Never use credit card for cash withdrawal (very expensive)
- Keep credit utilization below 30% of limit for good CIBIL score
- CIBIL score above 750 gets you lower interest rates on loans

Your CIBIL Score:
- Free annual check at: cibil.com (once per year free)
- Range: 300-900. Above 750 is good.
- Affected by: Payment history (35%), Credit utilization (30%), Length of history (15%)
        """,
    },

    # ── Budgeting ─────────────────────────────────────────────────────────────
    {
        "id": "budget_001",
        "topic": "Budgeting",
        "title": "Personal Budgeting - The 50/30/20 Rule",
        "language": "en",
        "source": "Financial Planning Standards Board India",
        "content": """
Personal Budgeting Guide for India:

THE 50/30/20 RULE (Recommended Framework):

50% – NEEDS (Essential Expenses)
- Rent/EMI
- Groceries and household essentials
- Utilities (electricity, water, internet, phone)
- Transportation to work
- Insurance premiums
- Minimum loan payments

30% – WANTS (Discretionary Expenses)
- Eating out and entertainment
- Shopping for non-essentials
- Subscriptions (OTT, gym)
- Holidays
- Gadgets and lifestyle

20% – SAVINGS AND INVESTMENTS
- Emergency fund (target: 6 months of expenses)
- Retirement savings (PPF, NPS, EPF top-up)
- Goal-based investments (mutual funds SIP, RD)
- Additional loan prepayment

STEP-BY-STEP BUDGETING:

Step 1: Calculate your TAKE-HOME income (after tax and PF deduction)
Step 2: List all FIXED expenses (EMI, rent, insurance premiums)
Step 3: List VARIABLE expenses (groceries, fuel, eating out)
Step 4: Categorize each expense into Needs/Wants/Savings
Step 5: Check if proportions are within 50/30/20
Step 6: Identify where to cut if overspending

BUDGETING TOOLS (Free):
- ET Money (Indian app)
- Walnut
- Money Manager
- Google Sheets / Excel

EMERGENCY FUND:
- Most critical financial safety net
- Target: 3-6 months of TOTAL monthly expenses (not income)
- Keep in: Liquid Fund or high-interest savings account (not FD – penalty for early withdrawal)
- Never invest emergency fund in stocks or mutual funds

EXAMPLE BUDGET (₹50,000 take-home):
Needs (₹25,000): Rent ₹12,000 + Food ₹6,000 + Travel ₹3,000 + Utilities ₹2,000 + Insurance ₹2,000
Wants (₹15,000): Eating out ₹4,000 + Entertainment ₹3,000 + Shopping ₹5,000 + Misc ₹3,000
Savings (₹10,000): SIP ₹5,000 + Emergency Fund ₹3,000 + PPF ₹2,000
        """,
    },
    {
        "id": "budget_002",
        "topic": "Budgeting",
        "title": "Government Savings Schemes in India",
        "language": "en",
        "source": "India Post, Ministry of Finance",
        "content": """
Best Government-Backed Savings Schemes in India:

1. PPF (Public Provident Fund)
   Interest Rate: 7.1% per annum (compounded annually, government-set quarterly)
   Lock-in: 15 years (partial withdrawal after 7 years)
   Investment: ₹500 - ₹1,50,000 per year
   Tax Benefit: EEE status – contribution, interest, and maturity all tax-free
   Best for: Long-term wealth creation, tax saving
   Where to open: Post office, State Bank of India, major banks

2. Sukanya Samriddhi Yojana (SSY)
   For: Girl child below 10 years
   Interest Rate: 8.2% per annum
   Lock-in: Until girl turns 21 (partial withdrawal at 18 for education)
   Investment: ₹250 - ₹1,50,000 per year
   Tax: Fully tax-free (EEE)

3. National Savings Certificate (NSC)
   Interest Rate: 7.7% per annum (compounded semi-annually, paid at maturity)
   Tenure: 5 years
   Minimum Investment: ₹1,000 (no maximum)
   Tax: Investment qualifies for 80C deduction (up to ₹1.5 lakh)

4. Post Office Monthly Income Scheme (POMIS)
   Interest Rate: 7.4% per annum paid monthly
   Tenure: 5 years
   Maximum Investment: ₹9 lakh (individual), ₹15 lakh (joint)
   Best for: Senior citizens needing regular income

5. Senior Citizen Savings Scheme (SCSS)
   For: Age 60+ (or 55+ for VRS retirees)
   Interest Rate: 8.2% per annum (quarterly payout)
   Maximum Investment: ₹30 lakh
   Tax: Investment qualifies for 80C; interest is taxable

6. NPS (National Pension System)
   For: Retirement savings
   Returns: Market-linked (historically 8-12% per annum)
   Tax benefit: Extra ₹50,000 deduction under 80CCD(1B) over and above 80C
   Lock-in: Until age 60

All government schemes can be opened at India Post offices (post.gov.in) or authorized banks.
        """,
    },

    # ── Personal Finance Management ───────────────────────────────────────────
    {
        "id": "pf_001",
        "topic": "Personal Finance",
        "title": "Building Financial Health - Complete Roadmap",
        "language": "en",
        "source": "SEBI Investor Education",
        "content": """
Complete Personal Finance Roadmap for India:

STEP 1: PROTECT (Insurance)
Before investing, ensure you are protected.

Life Insurance:
- Required if anyone depends on your income
- Buy TERM insurance only (NOT endowment or ULIP)
- Coverage: 10-15 times your annual income
- Example: Annual income ₹6 lakh → Cover ₹60-90 lakh
- Premium for ₹1 Cr cover, age 25, non-smoker: ~₹8,000-12,000/year
- Check: Policybazaar, Ditto Insurance for comparison

Health Insurance:
- Buy BEFORE you need it (pre-existing conditions have waiting periods)
- Minimum coverage: ₹5-10 lakh (individual); ₹10-15 lakh (family floater)
- Look for: Cashless hospitals, no co-pay, restoration benefit

STEP 2: BUILD EMERGENCY FUND
- Target: 6 months of total monthly expenses
- Keep in: High-yield savings account or liquid mutual fund
- Do NOT invest this in anything with lock-in or market risk

STEP 3: ELIMINATE HIGH-INTEREST DEBT
Pay off in this order (highest interest first):
1. Credit card outstanding (24-48% interest) – PAY IMMEDIATELY
2. Personal loans (18-24%)
3. Vehicle loans (8-12%)
4. Home loans (8.5-10.5%) – Low priority; tax benefit available

STEP 4: INVEST FOR GOALS
Short-term (< 3 years): FD, Recurring Deposit, Liquid Funds, Short-term Debt Funds
Medium-term (3-7 years): Debt Funds, Balanced Advantage Funds, NSC
Long-term (> 7 years): Equity Mutual Funds via SIP, PPF, NPS

STEP 5: TAX PLANNING (Section 80C)
Deductions up to ₹1,50,000 per year:
- EPF (automatically deducted from salary)
- PPF contributions
- ELSS Mutual Funds (shortest lock-in: 3 years, market returns)
- NSC, Tax-saving FD (5-year lock-in)
- Life insurance premium
- Home loan principal repayment
- Children's tuition fees

Section 80D: Health insurance premium (up to ₹25,000; ₹50,000 for seniors)
Section 24: Home loan interest (up to ₹2 lakh for self-occupied)
Section 80CCD(1B): Extra ₹50,000 for NPS

KEY FINANCIAL RATIOS:
Savings Rate: Savings / Income – Target: > 20%
Debt-to-Income Ratio: Monthly EMIs / Monthly Income – Keep below 40%
Emergency Fund Ratio: Liquid Assets / Monthly Expenses – Target: 6 months
        """,
    },
    {
        "id": "pf_002",
        "topic": "Personal Finance",
        "title": "SIP and Mutual Fund Basics",
        "language": "en",
        "source": "AMFI India, SEBI",
        "content": """
Systematic Investment Plan (SIP) and Mutual Funds Guide:

WHAT IS A MUTUAL FUND?
A mutual fund pools money from many investors and invests in stocks, bonds, or other securities.
Managed by professional fund managers regulated by SEBI.

WHAT IS SIP?
SIP (Systematic Investment Plan) allows you to invest a fixed amount (as low as ₹100/month) at
regular intervals (monthly/weekly) instead of a lump sum.

Benefits of SIP:
- Rupee Cost Averaging: You buy more units when market is low, fewer when high
- Power of Compounding: Small regular amounts grow significantly over time
- Disciplined saving: Auto-debit makes saving automatic
- Start small: Begin with ₹500/month

SIP POWER OF COMPOUNDING EXAMPLE:
₹5,000/month SIP at 12% annual return:
- After 10 years: ₹11.6 lakh invested → Grows to ~₹11.6 lakh (value ≈ ₹23.4 lakh)
- After 20 years: ₹12 lakh invested → Grows to ~₹49.9 lakh
- After 30 years: ₹18 lakh invested → Grows to ~₹1.76 Crore

TYPES OF MUTUAL FUNDS:
Equity Funds: Invest in stocks. High risk, high return (10-15% long-term). For goals 7+ years away.
Debt Funds: Invest in bonds. Low risk, moderate return (6-8%). For goals 1-3 years away.
Hybrid/Balanced Funds: Mix of equity and debt. Moderate risk. For goals 3-7 years away.
ELSS (Tax Saving): Equity fund with 3-year lock-in. Tax benefit under 80C.
Index Funds: Track Nifty50 or Sensex. Low cost, passive management. Good for beginners.

HOW TO START:
1. Complete KYC at any fund house or through apps like Zerodha Coin, Groww, Paytm Money
2. KYC requires: Aadhaar, PAN, bank account details
3. Choose fund based on goal, risk tolerance, and time horizon
4. Set up SIP with auto-debit from bank account
5. Review portfolio annually, not daily

RELIABLE RESOURCES:
- AMFI India (amfiindia.com): Fund ratings, NAV, fact sheets
- Value Research (valueresearchonline.com): Fund analysis
- SEBI Investor Education (investor.sebi.gov.in): Free courses
        """,
    },

    # ── Banking Basics ────────────────────────────────────────────────────────
    {
        "id": "banking_001",
        "topic": "Banking",
        "title": "Types of Bank Accounts and How to Choose",
        "language": "en",
        "source": "RBI Financial Literacy",
        "content": """
Guide to Bank Accounts in India:

SAVINGS ACCOUNT:
- Purpose: Day-to-day transactions and savings
- Interest: 2.5% - 7% per annum (varies by bank)
- Minimum balance: ₹0 (Zero Balance/BSBD accounts) to ₹10,000 (premium accounts)
- Features: Debit card, internet banking, UPI, ATM access
- Best for: Salary credit, daily expenses, emergency fund

ZERO BALANCE ACCOUNTS:
- BSBD (Basic Savings Bank Deposit) Account – free at all banks, mandated by RBI
- Jan Dhan Account – government scheme, zero balance, ₹10,000 overdraft facility, RuPay card
- Recommended for: Anyone without a bank account

CURRENT ACCOUNT:
- For: Businesses and traders (high transaction volume)
- No interest paid on balance
- Unlimited transactions allowed

FIXED DEPOSIT (FD):
- Guaranteed returns: 5.5% - 8% per annum (higher for senior citizens)
- Lock-in period: 7 days to 10 years
- Penalty for early withdrawal: Usually 0.5% - 1% reduction in rate
- Insurance: Up to ₹5 lakh per depositor per bank under DICGC
- Best for: Short-to-medium term savings, capital preservation

RECURRING DEPOSIT (RD):
- Monthly fixed amount deposited for a chosen tenure
- Interest similar to FD
- Minimum: ₹100/month
- Best for: Disciplined monthly saving with assured returns

HOW TO OPEN A BANK ACCOUNT (Documents required):
- PAN card (mandatory)
- Aadhaar card (KYC document)
- Passport-size photograph
- Initial deposit (if required)
- Can be done online via video KYC for most major banks

RIGHTS AS A BANK CUSTOMER:
- Right to a Basic Savings Account (zero balance) at any bank
- Right to a passbook / account statement
- Right to nominate a beneficiary
- Right to file grievance with Banking Ombudsman (free of charge) at rbi.org.in
        """,
    },

    # ── Multilingual Additions ─────────────────────────────────────────────────
    {
        "id": "scam_hindi_001",
        "topic": "Online Scams",
        "title": "ऑनलाइन वित्तीय धोखाधड़ी से कैसे बचें",
        "language": "hi",
        "source": "गृह मंत्रालय, साइबर क्राइम पोर्टल",
        "content": """
ऑनलाइन वित्तीय धोखाधड़ी के प्रकार और बचाव:

1. फर्जी KYC कॉल: कोई आपको कॉल करके कहता है कि आपका बैंक खाता बंद हो जाएगा।
   बचाव: बैंक कभी फोन पर OTP या Aadhaar नंबर नहीं मांगता।

2. लॉटरी स्कैम: "आपने ₹50 लाख जीते हैं, ₹5,000 प्रोसेसिंग फीस भेजें।"
   बचाव: जो लॉटरी आपने खरीदी ही नहीं, उसमें आप जीत नहीं सकते।

3. फर्जी लोन ऐप: बिना किसी कागजात के तुरंत लोन का वादा।
   बचाव: RBI पंजीकृत NBFC से ही लोन लें। rbi.org.in पर जांचें।

अगर धोखाधड़ी हो जाए:
- तुरंत 1930 पर कॉल करें (राष्ट्रीय साइबर हेल्पलाइन)
- cybercrime.gov.in पर ऑनलाइन शिकायत दर्ज करें
- अपने बैंक को तुरंत सूचित करें
        """,
    },
    {
        "id": "budget_tamil_001",
        "topic": "Budgeting",
        "title": "பட்ஜெட் திட்டமிடல் - அடிப்படை வழிகாட்டி",
        "language": "ta",
        "source": "SEBI முதலீட்டாளர் கல்வி",
        "content": """
வருமான மேலாண்மை - 50/30/20 விதி:

50% - அத்தியாவசிய செலவுகள் (வாடகை, உணவு, போக்குவரத்து)
30% - விரும்பிய செலவுகள் (பொழுதுபோக்கு, வெளியில் சாப்பிடுவது)
20% - சேமிப்பு மற்றும் முதலீடு

அவசர நிதி (Emergency Fund):
- குறைந்தது 6 மாத செலவுகளுக்கு சேமித்து வையுங்கள்
- நடப்பு கணக்கில் வையுங்கள், பங்குச் சந்தையில் இல்லை

SIP மூலம் முதலீடு:
- மாதம் ₹500 முதல் தொடங்கலாம்
- Groww, Zerodha Coin, Paytm Money ஆப்ஸ் பயன்படுத்தலாம்
        """,
    },

    # ── Additional English Depth Documents ────────────────────────────────────
    {
        "id": "banking_002",
        "topic": "Banking",
        "title": "NEFT, RTGS and IMPS - When to Use Which",
        "language": "en",
        "source": "RBI Payment Systems",
        "content": """
Bank Transfer Methods in India - Comparison Guide:

NEFT (National Electronic Funds Transfer):
- Settlement: In batches every 30 minutes, 24x7 (since December 2019)
- Minimum: No minimum; Maximum: No limit
- Charges: Free (RBI directive since January 2020 for online transfers)
- Use for: Regular non-urgent transfers, bill payments
- Note: NEFT uses IFSC code + Account number of recipient

RTGS (Real Time Gross Settlement):
- Settlement: Real-time (instantaneous)
- Minimum: Rs.2,00,000 (two lakh); No maximum limit
- Available: 24x7 since December 2020
- Charges: Free for online transactions (RBI directive)
- Use for: High-value urgent transfers (property payment, business)

IMPS (Immediate Payment Service):
- Settlement: Instant, 24x7 including holidays
- Minimum: Re.1; Maximum: Rs.5,00,000 per transaction
- Charges: Rs.2.5 - Rs.25 depending on amount (charged by banks)
- Use for: Urgent transfers any time, lower amounts
- Note: Can transfer using mobile number + MMID or account + IFSC

UPI (Unified Payments Interface):
- Settlement: Instant
- Maximum: Rs.1,00,000 per transaction (Rs.2,00,000 for verified merchants)
- Charges: Free
- Use for: Day-to-day transfers up to Rs.1 lakh

Quick Comparison:
- Speed: RTGS = IMPS = UPI (instant) > NEFT (30-min batch)
- Minimum amount: RTGS needs Rs.2 lakh; others have no minimum
- Cost: NEFT/RTGS/UPI are FREE; IMPS may have small charges
- Best for daily use: UPI (free, instant, mobile-friendly)
        """,
    },
    {
        "id": "interest_hindi_001",
        "topic": "Interest Rates",
        "title": "ब्याज दर को समझें - आसान गाइड",
        "language": "hi",
        "source": "RBI वित्तीय साक्षरता",
        "content": """
ब्याज दर क्या है?

जब आप बैंक से पैसे उधार लेते हैं, तो आपको मूल राशि के साथ अतिरिक्त पैसे देने होते हैं - यही ब्याज है।

भारत में सामान्य ब्याज दरें (2024):
- होम लोन: 8.5% - 10.5% प्रति वर्ष (सुरक्षित)
- पर्सनल लोन: 10.5% - 24% प्रति वर्ष
- क्रेडिट कार्ड: 24% - 48% प्रति वर्ष (बहुत महंगा!)
- बचत खाता: 2.5% - 7% प्रति वर्ष
- FD (फिक्स्ड डिपॉजिट): 5.5% - 8% प्रति वर्ष
- PPF: 7.1% प्रति वर्ष (सरकारी गारंटी)

सुरक्षित लोन ब्याज दर:
- बैंक से होम लोन: 10% तक ठीक है
- पर्सनल लोन: 18% तक स्वीकार्य
- 30% से अधिक ब्याज: खतरनाक और शोषणकारी हो सकता है

EMI कैलकुलेट करना:
अगर आप 5 लाख का लोन 10% पर 5 साल के लिए लेते हैं:
- मासिक EMI: लगभग ₹10,624
- कुल भुगतान: ₹6,37,480
- ब्याज में गया: ₹1,37,480

हमेशा कुल लागत (APR - Annual Percentage Rate) पूछें, सिर्फ ब्याज दर नहीं।
RBI वेबसाइट (rbi.org.in) पर वर्तमान दरें देखें।
        """,
    },
    {
        "id": "scam_telugu_001",
        "topic": "Online Scams",
        "title": "ఆన్‌లైన్ మోసాల నుండి ఎలా రక్షించుకోవాలి",
        "language": "te",
        "source": "సైబర్ క్రైమ్ పోర్టల్",
        "content": """
ఆన్‌లైన్ ఆర్థిక మోసాలు - జాగ్రత్తలు:

సాధారణ మోసాలు:
1. KYC మోసం: మీ బ్యాంక్ ఖాతా బ్లాక్ అవుతుందని భయపెట్టి OTP అడుగుతారు.
   జాగ్రత్త: బ్యాంక్ ఎప్పుడూ ఫోన్‌లో OTP అడగదు.

2. లాటరీ మోసం: "మీరు ₹50 లక్షలు గెలిచారు" అని చెప్పి ముందు డబ్బు అడుగుతారు.
   జాగ్రత్త: మీరు పాల్గొనని లాటరీలో మీరు గెలవలేరు.

3. UPI PIN మోసం: "డబ్బు స్వీకరించడానికి PIN నమోదు చేయండి" అంటారు.
   జాగ్రత్త: డబ్బు స్వీకరించడానికి PIN అవసరం లేదు; PIN నమోదు చేస్తే మీ డబ్బు పోతుంది.

మోసం జరిగితే:
- వెంటనే 1930 కి కాల్ చేయండి (జాతీయ సైబర్ నేర హెల్ప్‌లైన్)
- cybercrime.gov.in లో ఫిర్యాదు దాఖలు చేయండి
- మీ బ్యాంక్‌ని వెంటనే సంప్రదించండి
        """,
    },
    {
        "id": "pf_hindi_001",
        "topic": "Personal Finance",
        "title": "भारत में व्यक्तिगत वित्त प्रबंधन",
        "language": "hi",
        "source": "SEBI निवेशक शिक्षा",
        "content": """
व्यक्तिगत वित्त की 5 मूल बातें:

1. बीमा पहले (Insurance First)
   - टर्म लाइफ इंश्योरेंस: अपनी वार्षिक आय का 10-15 गुना कवरेज लें
   - स्वास्थ्य बीमा: कम से कम ₹5-10 लाख का कवरेज जरूरी
   - ULIP और एंडोमेंट प्लान से बचें - ये महंगे और कम रिटर्न देते हैं

2. आपातकालीन निधि (Emergency Fund)
   - 6 महीने के खर्चों के बराबर पैसे अलग रखें
   - बचत खाते या लिक्विड फंड में रखें

3. कर्ज प्रबंधन (Debt Management)
   - क्रेडिट कार्ड का पूरा बिल समय पर भरें (24-48% ब्याज बहुत महंगा है)
   - उच्च ब्याज वाले कर्ज पहले चुकाएं

4. निवेश (Investment)
   - SIP (Systematic Investment Plan): मासिक ₹500 से शुरू करें
   - PPF: सरकारी गारंटी + 7.1% ब्याज + टैक्स फ्री
   - NPS: रिटायरमेंट के लिए + अतिरिक्त ₹50,000 की टैक्स छूट

5. टैक्स बचत (Tax Saving - Section 80C)
   - EPF + PPF + ELSS + जीवन बीमा = अधिकतम ₹1,50,000 की छूट
   - 80D: स्वास्थ्य बीमा प्रीमियम (₹25,000 तक)

याद रखें: कोई भी "गारंटीड हाई रिटर्न" झूठ है। SEBI पंजीकृत सलाहकार से ही सलाह लें।
        """,
    },
    {
        "id": "upi_bengali_001",
        "topic": "UPI",
        "title": "UPI দিয়ে নিরাপদে টাকা পাঠানো",
        "language": "bn",
        "source": "NPCI ভারত",
        "content": """
UPI (ইউনিফাইড পেমেন্টস ইন্টারফেস) - বাংলায় গাইড:

UPI দিয়ে টাকা পাঠানোর পদ্ধতি:
1. PhonePe, Google Pay বা আপনার ব্যাংকের অ্যাপ খুলুন
2. 'টাকা পাঠান' বা 'Pay' এ ক্লিক করুন
3. প্রাপকের UPI ID বা মোবাইল নম্বর দিন
4. পরিমাণ লিখুন
5. UPI PIN দিয়ে নিশ্চিত করুন

গুরুত্বপূর্ণ নিরাপত্তা নিয়ম:
- আপনার UPI PIN কখনো কারো সাথে শেয়ার করবেন না
- ব্যাংক বা NPCI কখনো ফোনে PIN জিজ্ঞেস করে না
- টাকা পেতে কোনো PIN লাগে না - শুধু পাঠাতে লাগে
- সন্দেহজনক কিছু হলে 1930 নম্বরে কল করুন

সাধারণ UPI প্রতারণা:
- "Collect Request অনুমোদন করুন তাহলে টাকা পাবেন" - এটি মিথ্যা! অনুমোদন করলে আপনার টাকা যাবে
- QR কোড দিয়ে টাকা আসে না, শুধু যায়
- কেউ OTP বা PIN চাইলে সাথে সাথে ফোন রাখুন
        """,
    },
]


def save_knowledge_base(output_dir: str = "./data/knowledge_base") -> None:
    """Save the knowledge base documents to JSON files for later ingestion."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Group by topic
    by_topic: dict[str, list] = {}
    for doc in FINANCIAL_KNOWLEDGE_BASE:
        topic = doc["topic"].lower().replace(" ", "_")
        by_topic.setdefault(topic, []).append(doc)

    for topic, docs in by_topic.items():
        output_path = Path(output_dir) / f"{topic}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(docs)} documents -> {output_path}")

    # Also save all in one file
    all_path = Path(output_dir) / "all_documents.json"
    with open(all_path, "w", encoding="utf-8") as f:
        json.dump(FINANCIAL_KNOWLEDGE_BASE, f, ensure_ascii=False, indent=2)
    print(f"\nTotal: {len(FINANCIAL_KNOWLEDGE_BASE)} documents saved to {output_dir}")


if __name__ == "__main__":
    save_knowledge_base()
