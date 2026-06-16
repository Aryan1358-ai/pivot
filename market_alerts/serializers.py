from rest_framework import serializers
from .models import AlertRule,TriggeredAlert

class AlertRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model=AlertRule
        fields=['id', 'stock_symbol', 'price_threshold', 'condition', 'is_active', 'user']
        read_only_fields=['user']

class TriggeredAlertsSerializer(serializers.ModelSerializer):
    rule = AlertRuleSerializer(read_only=True)
    class Meta:
        model = TriggeredAlert

        fields=[ 'id', 'rule', 'triggered_price', 'triggered_at']


