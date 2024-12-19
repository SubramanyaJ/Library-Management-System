from django.core.management.base import BaseCommand
from libraryweb.models import LateFees
from django.db import transaction

class Command(BaseCommand):
    help = 'Update late fees for all borrowed books'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            updated_count = 0
            for late_fee in LateFees.objects.all():
                late_fee.calculate_fees()
                late_fee.save()
                updated_count += 1
        self.stdout.write(self.style.SUCCESS(f"Updated late fees for {updated_count} entries."))