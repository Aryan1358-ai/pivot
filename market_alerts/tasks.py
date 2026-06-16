from celery import shared_task
from .producer import run_price_producer

@shared_task
def fetch_prices_task():
    run_price_producer()