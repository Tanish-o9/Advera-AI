from django.contrib import admin
from .models import LandingPage


@admin.register(LandingPage)
class LandingPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'variant', 'cro_score', 'target_url', 'created_at')
    list_filter = ('variant', 'created_at')
    search_fields = ('title', 'target_url', 'ad_text')
