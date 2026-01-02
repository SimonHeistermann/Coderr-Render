from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.apps import apps

class Command(BaseCommand): 
    """Clear all entries in tables excpect superusrs and staff"""
    help = 'Clears all data except superusers and staff'

    def handle(self, *args, **kwargs):
        for model in apps.get_models():
            if model == User:
                model.objects.exclude(is_superuser=True).exclude(is_staff=True).delete()
            else:
                model.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('✅ Cleared all data except superusers.'))