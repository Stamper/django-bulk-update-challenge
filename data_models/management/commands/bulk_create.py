from secrets import token_urlsafe

from django.core.management.base import BaseCommand
from data_models.models import DataModel


class Command(BaseCommand):
    help = 'Creates 100k rows'

    def handle(self, *args, **options):
        DataModel.objects.bulk_create(
            (
                DataModel(
                    text=token_urlsafe(75),
                    description=token_urlsafe(150)
                )
                for _ in range(100_000)
            )
        )
