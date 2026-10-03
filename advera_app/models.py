from django.db import models


class LandingPage(models.Model):
    VARIANT_CHOICES = [
        ('standard', 'Standard Modern SaaS'),
        ('high_urgency', 'High Urgency / Conversion Focus'),
        ('social_proof', 'Social Proof & Trust Heavy'),
        ('minimalist', 'Minimalist & Clean'),
    ]

    title = models.CharField(max_length=255, default="Generated Landing Page")
    target_url = models.URLField(max_length=500)
    ad_text = models.TextField(blank=True, default="")
    ad_image_url = models.URLField(max_length=500, blank=True, null=True)
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    variant = models.CharField(max_length=50, choices=VARIANT_CHOICES, default='standard')
    
    generated_html = models.TextField()
    cro_score = models.IntegerField(default=85)
    cro_feedback = models.TextField(blank=True, default="[]")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
