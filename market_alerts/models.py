from django.db import models
from django.contrib.auth.models import User


class AlertRule(models.Model):
    CONDITION_CHOICES = [
        ('ABOVE', 'Goes Above'),
        ('BELOW', 'Drops Below')
    ]

    # Links the alert to a specific user
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # The stock ticker (e.g., AAPL or RELIANCE.NS)
    stock_symbol = models.CharField(max_length=20)

    # The target price to watch for
    price_threshold = models.DecimalField(max_digits=10, decimal_places=2)

    # Whether we are looking for a breakout above or drop below the threshold
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)

    # Lets users turn alerts on/off without deleting them
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.stock_symbol} {self.condition} {self.price_threshold}"

class TriggeredAlert(models.Model):
    rule=models.ForeignKey(AlertRule, on_delete=models.CASCADE)
    triggered_price = models.DecimalField(max_digits=10, decimal_places=2)
    triggered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rule} @ {self.triggered_price} on {self.triggered_at}"
