import os
import re
import uuid
import json
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

try:
    from supabase import create_client
except ImportError:
    create_client = None

# Initialize Supabase client if credentials exist
SUPABASE_URL = getattr(settings, 'SUPABASE_URL', None)
SUPABASE_KEY = getattr(settings, 'SUPABASE_SERVICE_KEY', None)
SUPABASE_BUCKET = getattr(settings, 'SUPABASE_BUCKET', 'media')

supabase = None
if SUPABASE_URL and SUPABASE_KEY and create_client:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as err:
        print(f"[Supabase Init Warning] {err}")


def upload_to_supabase(file):
    """
    Uploads file to Supabase S3 bucket if available, else falls back to local media storage.
    """
    if not file:
        return None

    filename = f"{uuid.uuid4().hex[:10]}_{file.name}"

    if supabase:
        try:
            file_content = file.read()
            supabase.storage.from_(SUPABASE_BUCKET).upload(
                filename,
                file_content,
                {"content-type": getattr(file, 'content_type', 'image/jpeg')}
            )
            return supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename)
        except Exception as e:
            print(f"[Supabase Upload Warning] {e}. Falling back to local storage.")

    try:
        saved_path = default_storage.save(f"uploads/{filename}", ContentFile(file.read()))
        return f"{settings.MEDIA_URL}{saved_path}"
    except Exception as e:
        print(f"[Local Storage Error] {e}")
        return None


def scrape_website(url):
    """
    Scrapes key elements (title, headings, meta tags, and paragraphs) from the target URL.
    """
    if not url:
        return {"summary": "Modern digital product landing page content"}

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, timeout=7, headers=headers)
        if response.status_code != 200:
            return {"summary": "Modern digital product landing page content"}

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else "Brand Web Page"
        
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if meta_tag and meta_tag.get("content"):
            meta_desc = meta_tag.get("content").strip()

        headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3']) if h.get_text(strip=True)]
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if len(p.get_text(strip=True)) > 20]

        summary_text = f"Page Title: {title}\n"
        if meta_desc:
            summary_text += f"Description: {meta_desc}\n"
        if headings:
            summary_text += f"Key Headlines: {' | '.join(headings[:6])}\n"
        if paragraphs:
            summary_text += f"Body Highlights: {' '.join(paragraphs[:8])}\n"

        return {
            "title": title,
            "summary": summary_text,
            "headings": headings[:6],
            "paragraphs": paragraphs[:6]
        }

    except Exception as e:
        print(f"[Scraper Warning] Failed to scrape {url}: {e}")
        return {"summary": "Modern digital product landing page content"}


def calculate_cro_score(html_code):
    """
    Evaluates generated HTML against Conversion Rate Optimization (CRO) benchmarks.
    Returns (score_out_of_100, list_of_feedback_strings).
    """
    score = 50
    feedback = []

    if not html_code:
        return 0, ["No HTML content generated."]

    if re.search(r'<(h1|h2)[^>]*>', html_code, re.I):
        score += 15
        feedback.append("✅ Clear, high-prominence headline detected in Hero section.")
    else:
        feedback.append("⚠️ Missing strong H1 headline for initial visitor retention.")

    if re.search(r'href=["\']#?["\']|button|bg-indigo|bg-blue|bg-emerald|bg-pink|bg-rose', html_code, re.I):
        score += 15
        feedback.append("✅ Call-To-Action (CTA) buttons strategically positioned.")
    else:
        feedback.append("⚠️ Add prominent, high-contrast CTA buttons above the fold.")

    if re.search(r'testimonial|rating|star|review|trusted by|clients', html_code, re.I):
        score += 10
        feedback.append("✅ Social proof / reviews included to build customer trust.")
    else:
        feedback.append("💡 Consider adding customer testimonials or trust logos.")

    if 'viewport' in html_code and 'w-full' in html_code:
        score += 10
        feedback.append("✅ Mobile-responsive viewport and flexible containers configured.")

    if re.search(r'grid|flex-col|grid-cols', html_code, re.I):
        score += 10
        feedback.append("✅ Modern grid layout used for features and benefit breakdown.")

    score = min(100, max(65, score))
    return score, feedback


def clean_markdown(text):
    """Strips markdown backticks ```html ... ``` if returned by LLMs."""
    if not text:
        return ""

    match = re.search(r"```html(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    match = re.search(r"```(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return text.strip()


def generate_personalized_page(ad_text, landing_content, logo_url=None, variant='standard'):
    """
    Generates tailored, high-converting landing page HTML based on ad creative & target site data.
    Supports OpenAI API, Mistral API, and dynamic fallback generator.
    """
    logo_src = logo_url if logo_url else "https://placehold.co/180x60/6366f1/ffffff?text=Advera+AI"
    mistral_key = getattr(settings, 'MISTRAL_API_KEY', '')
    openai_key = getattr(settings, 'OPENAI_API_KEY', '')

    variant_instruction = {
        'high_urgency': "Emphasize limited time urgency, countdown badges, bold discount tags, and high-visibility action CTAs.",
        'social_proof': "Include prominent star ratings, customer testimonial cards, trust badges, and user numbers.",
        'minimalist': "Use sleek dark-mode aesthetics, generous padding, elegant glassmorphism effects, and crisp typography.",
        'standard': "Clean modern SaaS layout with hero, feature grid, testimonials, and responsive footer."
    }.get(variant, "Modern SaaS layout with strong conversion principles.")

    prompt = f"""
You are an expert Conversion Rate Optimization (CRO) Lead & Top-Tier Frontend Engineer.

INPUT DATA:
- Ad Text / Copy: {ad_text}
- Scraped Web Content: {landing_content}
- Style Variant Target: {variant_instruction}
- Brand Logo URL: {logo_src}

STRICT SPECIFICATION:
1. Return ONLY pure, executable HTML code. Do NOT wrap inside markdown.
2. Must start with <!DOCTYPE html> and include Tailwind CSS CDN (<script src="https://cdn.tailwindcss.com"></script>).
3. Include Navbar with Logo (<img src="{logo_src}" class="h-10 w-auto" alt="Logo">), Hero Section, Feature Grid, Social Proof / Reviews section, and Footer.
4. Design Style: Premium modern web app, sleek gradients, rounded buttons, smooth hover transitions.
"""

    # 1. Try OpenAI API if key available
    if openai_key and openai_key != 'your_openai_api_key_here':
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 4000
                },
                timeout=25
            )
            if response.status_code == 200:
                raw_html = response.json()['choices'][0]['message']['content']
                cleaned = clean_markdown(raw_html)
                if len(cleaned) > 200:
                    return cleaned
            else:
                print(f"[OpenAI API Error {response.status_code}] {response.text}")
        except Exception as e:
            print(f"[OpenAI API Exception] {e}")

    # 2. Try Mistral API if key available
    if mistral_key:
        try:
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {mistral_key}", "Content-Type": "application/json"},
                json={
                    "model": "mistral-small-latest",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 4096
                },
                timeout=25
            )
            if response.status_code == 200:
                raw_html = response.json()['choices'][0]['message']['content']
                cleaned = clean_markdown(raw_html)
                if len(cleaned) > 200:
                    return cleaned
            else:
                print(f"[Mistral API Error {response.status_code}] {response.text}")
        except Exception as e:
            print(f"[Mistral API Exception] {e}")

    # 3. Dynamic High-Converting HTML Generator (tailored to user inputs)
    return get_fallback_landing_page(ad_text, landing_content, logo_src, variant)


def get_fallback_landing_page(ad_text, landing_content, logo_src, variant):
    """
    Generates a unique, dynamic, pixel-perfect Tailwind landing page using submitted ad text & scraped content.
    """
    # Extract dynamic headline from ad_text or content
    clean_ad = ad_text.strip() if ad_text else ""
    if clean_ad and len(clean_ad) > 5:
        headline = clean_ad.split('\n')[0]
        if len(headline) > 90:
            headline = headline[:90] + "..."
    else:
        headline = "Accelerate Your Business with Next-Gen Intelligence"

    # Extract dynamic subtext
    if isinstance(landing_content, dict):
        summary_str = landing_content.get("summary", "")
        headings = landing_content.get("headings", [])
    else:
        summary_str = str(landing_content)
        headings = []

    subtext = "Experience a tailored solution designed specifically for your goals. Match your campaign promise directly with an optimized, high-converting landing experience."
    if len(summary_str) > 50:
        lines = [line.strip() for line in summary_str.split('\n') if 'Description:' in line or 'Body' in line]
        if lines:
            subtext = lines[0].replace('Description:', '').replace('Body Highlights:', '').strip()[:180]

    # Theme variants styling
    if variant == 'high_urgency':
        badge = "🔥 LIMITED TIME OFFER — EXPIRES SOON"
        primary_btn = "bg-gradient-to-r from-rose-500 to-amber-500 hover:from-rose-600 hover:to-amber-600 text-white"
        accent_color = "text-amber-400"
        card_border = "border-amber-500/30"
        hero_tag = "Urgency & Conversion Focus"
    elif variant == 'social_proof':
        badge = "⭐ RATED 4.9/5 BY 10,000+ CUSTOMERS"
        primary_btn = "bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white"
        accent_color = "text-emerald-400"
        card_border = "border-emerald-500/30"
        hero_tag = "Social Proof & Verified Trust"
    elif variant == 'minimalist':
        badge = "🌿 SLEEK & MODERN PERFORMANCE"
        primary_btn = "bg-slate-100 text-slate-950 hover:bg-white font-bold"
        accent_color = "text-slate-300"
        card_border = "border-slate-700"
        hero_tag = "Minimalist Precision"
    else:
        badge = "🚀 POWERED BY ADVERA AI"
        primary_btn = "bg-gradient-to-r from-indigo-500 via-purple-600 to-pink-500 hover:from-indigo-600 hover:to-pink-600 text-white"
        accent_color = "text-indigo-400"
        card_border = "border-indigo-500/30"
        hero_tag = "Personalized Campaign Page"

    # Dynamic features
    feature_1_title = headings[0] if len(headings) > 0 else "Instant Alignment"
    feature_2_title = headings[1] if len(headings) > 1 else "CRO Optimized Layout"
    feature_3_title = headings[2] if len(headings) > 2 else "Seamless Customer Flow"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{headline}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
    </style>
</head>
<body class="bg-slate-950 text-slate-100 antialiased min-h-screen flex flex-col justify-between">

    <!-- NAVBAR -->
    <nav class="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-3">
            <img src="{logo_src}" alt="Logo" class="h-9 w-auto rounded-md shadow-sm">
        </div>
        <div class="hidden md:flex items-center space-x-8 text-sm font-semibold text-slate-300">
            <a href="#features" class="hover:text-white transition">Features</a>
            <a href="#proof" class="hover:text-white transition">Reviews</a>
            <a href="#cta" class="hover:text-white transition">Offer</a>
        </div>
        <div>
            <a href="#cta" class="{primary_btn} font-bold text-xs sm:text-sm px-5 py-2.5 rounded-full shadow-lg transition-all transform hover:-translate-y-0.5">
                Claim Offer Now →
            </a>
        </div>
    </nav>

    <!-- HERO SECTION -->
    <header class="relative pt-16 pb-16 px-6 text-center max-w-5xl mx-auto flex-1 flex flex-col justify-center items-center">
        <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-900 border {card_border} {accent_color} text-xs font-bold tracking-wide uppercase mb-6 shadow-sm">
            {badge}
        </div>
        
        <h1 class="text-3xl sm:text-6xl font-extrabold text-white tracking-tight leading-tight mb-6">
            {headline}
        </h1>
        
        <p class="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            {subtext}
        </p>

        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center w-full max-w-md">
            <a id="cta" href="#features" class="w-full sm:w-auto {primary_btn} font-extrabold px-8 py-4 rounded-xl shadow-xl transition-all transform hover:scale-105 text-center text-sm">
                Get Started Right Now
            </a>
            <a href="#features" class="w-full sm:w-auto bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 font-semibold px-6 py-4 rounded-xl transition text-center text-sm">
                Learn More
            </a>
        </div>
    </header>

    <!-- DYNAMIC FEATURES GRID -->
    <section id="features" class="py-16 px-6 bg-slate-900/40 border-y border-slate-800/80">
        <div class="max-w-6xl mx-auto">
            <div class="text-center mb-12">
                <span class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 block">{hero_tag}</span>
                <h2 class="text-2xl sm:text-3xl font-bold text-white mb-3">Key Highlights & Capabilities</h2>
                <p class="text-slate-400 text-sm">Tailored specifically to match your campaign goals.</p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 hover:{card_border} transition">
                    <div class="w-10 h-10 rounded-xl bg-slate-800 {accent_color} flex items-center justify-center font-bold text-lg mb-4">⚡</div>
                    <h3 class="text-lg font-bold text-white mb-2">{feature_1_title}</h3>
                    <p class="text-slate-400 text-xs sm:text-sm leading-relaxed">Matches visitor expectations directly with the promises made in your ad creative.</p>
                </div>
                <div class="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 hover:{card_border} transition">
                    <div class="w-10 h-10 rounded-xl bg-slate-800 {accent_color} flex items-center justify-center font-bold text-lg mb-4">🎯</div>
                    <h3 class="text-lg font-bold text-white mb-2">{feature_2_title}</h3>
                    <p class="text-slate-400 text-xs sm:text-sm leading-relaxed">Built with visual cues, high-contrast action triggers, and responsive layout hygiene.</p>
                </div>
                <div class="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 hover:{card_border} transition">
                    <div class="w-10 h-10 rounded-xl bg-slate-800 {accent_color} flex items-center justify-center font-bold text-lg mb-4">🛡️</div>
                    <h3 class="text-lg font-bold text-white mb-2">{feature_3_title}</h3>
                    <p class="text-slate-400 text-xs sm:text-sm leading-relaxed">Preserves brand continuity, typography, and logo branding automatically.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- PROOF & TESTIMONIAL SECTION -->
    <section id="proof" class="py-16 px-6 max-w-3xl mx-auto text-center">
        <h2 class="text-xl font-bold text-white mb-6">Proven Impact & User Trust</h2>
        <div class="p-8 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl">
            <div class="flex justify-center text-amber-400 text-sm mb-4">★★★★★</div>
            <p class="text-base italic text-slate-300 mb-6">
                "Directly linking custom ad copy to dedicated, personalized pages instantly improved visitor retention and doubled our conversion metrics."
            </p>
            <div class="flex items-center justify-center space-x-3">
                <div class="w-9 h-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-indigo-400 text-xs">AA</div>
                <div class="text-left">
                    <div class="text-xs font-bold text-white">Verified Customer</div>
                    <div class="text-[11px] text-slate-500">Advera AI Campaign Engine</div>
                </div>
            </div>
        </div>
    </section>

    <!-- FOOTER -->
    <footer class="border-t border-slate-900 py-6 px-6 text-center text-xs text-slate-500">
        <div class="max-w-6xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4">
            <p>© 2026 Powered by Advera AI. All rights reserved.</p>
            <div class="flex space-x-6">
                <a href="#" class="hover:text-slate-400">Privacy</a>
                <a href="#" class="hover:text-slate-400">Terms</a>
            </div>
        </div>
    </footer>

</body>
</html>"""
