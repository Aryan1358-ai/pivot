from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AlertRule,TriggeredAlert
from .services import get_cached_price, fetch_and_cache_price
from .serializers import AlertRuleSerializer,TriggeredAlertsSerializer
# Create your views here.
@api_view(['GET'])
def get_price(request,symbol):
    price=get_cached_price(symbol)
    if price is None:
        price=fetch_and_cache_price(symbol)

    return Response({
        "symbol":symbol,
        "price": price
    })

class AlertRuleViewSet(viewsets.ModelViewSet):
    serializer_class = AlertRuleSerializer
    queryset = AlertRule.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return AlertRule.objects.filter(user=self.request.user)


class TriggeredAlertViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TriggeredAlertsSerializer
    queryset=TriggeredAlert.objects.all()

    def get_queryset(self):
        return TriggeredAlert.objects.filter(rule__user=self.request.user)

