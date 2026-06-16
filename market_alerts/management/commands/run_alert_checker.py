from django.core.management.base import BaseCommand
from market_alerts.consumer import run_alert_checker

class Command(BaseCommand):
    help = "Runs the Kafka consumer that checks price updates against alert rules"

    def handle(self, *args, **options):
        run_alert_checker()