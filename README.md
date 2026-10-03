<h1 align="center">🚀 Advera AI</h1>

<p align="center">
  <b>AI-powered landing page personalization — turn ad creatives into high-converting pages, automatically.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Live-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Backend-Django-darkgreen?style=for-the-badge&logo=django" />
  <img src="https://img.shields.io/badge/AI-OpenAI%20%2F%20Mistral-black?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Database-Supabase%20%2F%20PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" />
  <img src="https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
</p>

<p align="center">
  <a href="#-overview">Overview</a> •
  <a href="#-features">Features</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-how-it-works">How It Works</a>
</p>

---

## 📌 Overview

**Advera AI** is an AI-powered landing page personalization platform. Feed it an ad creative, marketing copy, and a target URL — it analyzes the ad and existing web content, then generates an optimized, custom landing page designed to convert.

Instead of manually rebuilding landing pages for every campaign, Advera AI applies AI and **Conversion Rate Optimization (CRO)** principles automatically, so each page matches the intent and messaging of the ad that drives traffic to it — a technique known to significantly lift conversion rates over generic, one-size-fits-all pages.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎨 **AI-Generated Landing Pages** | Auto-builds custom pages from ad creatives and marketing text |
| 🎯 **CRO Benchmark Engine** | Evaluates generated pages with a 1-100 conversion score and tips |
| 📱 **Device Viewport Switcher** | Toggle between Desktop, Tablet (768px), and Mobile (375px) previews |
| 💻 **Interactive Code Editor** | Edit HTML source live in-browser and apply changes directly |
| 📢 **Ad Creative Analysis** | Extracts intent, tone, and key messaging from ad content |
| 🌐 **Website Content Extraction** | Pulls existing site content to keep pages on-brand and consistent |
| 📊 **Dashboard & History** | Tracks all past generated pages, scores, and deletion controls |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.13, Django 6.0 |
| **Frontend** | HTML5, Tailwind CSS, JavaScript |
| **AI Engine** | Mistral AI / OpenAI API (with Zero-Downtime Fallback Generator) |
| **Database & Storage** | Supabase PostgreSQL & S3 Storage (with SQLite local fallback) |

---

## ⚙️ How It Works

1. **Input** — Provide an ad creative, marketing copy, target URL, and choose an optimization variant (`Standard`, `High Urgency`, `Social Proof`, `Minimalist`).
2. **Analysis** — Advera AI analyzes the ad's messaging, tone, and intent, and extracts relevant content from the target site.
3. **Generation & Scoring** — The AI engine generates a custom landing page aligned with the ad's promise and assigns a 1-100 CRO benchmark rating.
4. **Deploy & Track** — Preview on Desktop/Mobile, edit HTML live, download code, or access anytime from the Dashboard.

---

## 🔧 Installation

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/Tanish-o9/Advera-AI.git
cd Advera-AI

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Start the development server
python manage.py runserver
```

The app will be available at `http://127.0.0.1:8000/`.

---

<p align="center">Made with ❤️ by <a href="https://github.com/Tanish-o9">Tanish Kumar</a></p>
