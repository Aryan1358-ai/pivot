
from kafka import KafkaConsumer
import json

from decimal import Decimal
from .services import send_alert_email, check_alert_condition
from .models import AlertRule,TriggeredAlert
import environ
env=environ.Env()
environ.Env.read_env()
consumer=KafkaConsumer(
    "price-updates",
    bootstrap_servers=env('KAFKA_BOOTSTRAP_SERVERS'),
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="latest",
    group_id="alert-checker-group",

)

def run_alert_checker():
    print("Listening for Price Updates....")
    for message in consumer:
        data=message.value
        symbol=data["symbol"]
        price=Decimal(str(data["price"]))
        existing_rules=AlertRule.objects.filter(stock_symbol=symbol,is_active=True)
        for rule in existing_rules:
            if check_alert_condition(price,rule):
                if rule.condition=='ABOVE':
                    print(f"Alert price triggered , price above: {rule.price_threshold}")
                elif rule.condition == 'BELOW':
                    print(f"Alert price triggered , price below: {rule.price_threshold}")
                TriggeredAlert.objects.create(
                    rule=rule,
                    triggered_price=price,

                )
                send_alert_email(rule.user, symbol, rule.condition, rule.price_threshold, price)

                rule.is_active=False
                rule.save()




                