import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import LandingPage
from .utils import (
    scrape_website,
    generate_personalized_page,
    upload_to_supabase,
    calculate_cro_score
)


def home(request):
    """Renders the generator homepage with template variants."""
    return render(request, "index.html", {
        "variants": LandingPage.VARIANT_CHOICES
    })


def generate(request):
    """Processes user inputs, scrapes target URL, generates landing page, scores CRO, and saves to DB."""
    if request.method == "POST":
        try:
            ad_text = request.POST.get("ad_text", "").strip()
            ad_link = request.POST.get("ad_link", "").strip()
            url = request.POST.get("url", "").strip()
            variant = request.POST.get("variant", "standard")
            
            ad_image_file = request.FILES.get("ad_image")
            logo_file = request.FILES.get("logo")

            if not url:
                return render(request, "result.html", {
                    "error": "Target Landing Page URL is required."
                })

            if ad_link:
                ad_text += f"\nAd Reference Link: {ad_link}"

            # Upload Assets
            ad_image_url = upload_to_supabase(ad_image_file) if ad_image_file else None
            logo_url = upload_to_supabase(logo_file) if logo_file else None

            if ad_image_url:
                ad_text += f"\nAd Image Asset: {ad_image_url}"

            # Scrape Target Page
            scrape_data = scrape_website(url)
            landing_content = scrape_data.get("summary", "Modern Product Content")

            # Generate HTML Code
            html_code = generate_personalized_page(
                ad_text=ad_text,
                landing_content=landing_content,
                logo_url=logo_url,
                variant=variant
            )

            # Calculate CRO Benchmark Score
            cro_score, feedback_list = calculate_cro_score(html_code)

            # Persist to Database
            page_title = scrape_data.get("title") or "AI Personalized Page"
            landing_page = LandingPage.objects.create(
                title=page_title,
                target_url=url,
                ad_text=ad_text,
                ad_image_url=ad_image_url,
                logo_url=logo_url,
                variant=variant,
                generated_html=html_code,
                cro_score=cro_score,
                cro_feedback=json.dumps(feedback_list)
            )

            return redirect("page_detail", page_id=landing_page.id)

        except Exception as e:
            return render(request, "result.html", {
                "error": f"Generation Error: {str(e)}"
            })

    return redirect("home")


def page_detail(request, page_id):
    """Displays saved landing page preview, live code editor, and CRO analysis scorecard."""
    page = get_object_or_404(LandingPage, id=page_id)
    
    try:
        feedback_list = json.loads(page.cro_feedback)
    except Exception:
        feedback_list = []

    return render(request, "result.html", {
        "page": page,
        "html_code": page.generated_html,
        "cro_score": page.cro_score,
        "cro_feedback": feedback_list
    })


def history(request):
    """Dashboard view of all generated landing pages."""
    pages = LandingPage.objects.all()
    return render(request, "history.html", {
        "pages": pages
    })


def delete_page(request, page_id):
    """Deletes a saved landing page."""
    if request.method == "POST":
        page = get_object_or_404(LandingPage, id=page_id)
        page.delete()
    return redirect("history")