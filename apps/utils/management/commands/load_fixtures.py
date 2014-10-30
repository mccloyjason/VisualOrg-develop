from django.core.management.base import BaseCommand

from apps.utils.load_fixtures import load_fixtures


class Command(BaseCommand):
    def handle(self, name, *args, **kwargs):
        """Loads the script located at folkroar.fixture_scripts.<name>"""
        load_fixtures(name)
