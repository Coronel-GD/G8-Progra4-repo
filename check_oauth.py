import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djecommerce.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

print('=== SITES ===')
for s in Site.objects.all():
    print(f'{s.id}: {s.domain} - {s.name}')

print('\n=== SOCIAL APPS ===')
for app in SocialApp.objects.all():
    sites = list(app.sites.values_list('domain', flat=True))
    print(f'{app.provider}: {app.name}')
    print(f'  Client ID: {app.client_id[:20]}...')
    print(f'  Sites: {sites}')
