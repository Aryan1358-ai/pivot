from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('alert-rules', AlertRuleViewSet, basename='alertrule')
router.register('triggered-alerts',TriggeredAlertViewSet, basename='triggeredalert')
urlpatterns = [
    path('get_price/<str:symbol>/',get_price,name='get_price'),
]+router.urls