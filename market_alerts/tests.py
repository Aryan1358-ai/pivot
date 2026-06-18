from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .services import check_alert_condition
from decimal import Decimal
from unittest.mock import patch
from .services import get_cached_price

from .consumer import run_alert_checker
from .models import AlertRule
# Create your tests here.
# no matter who you claim to be in the request body, the rule gets assigned to whoever is actually logged in."
class AlertRuleTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1=User.objects.create_user(username='user1',password='pass123')
        self.user2=User.objects.create_user(username='user2',password='pass123')
        self.client.force_authenticate(user=self.user1)

    def test_rule_is_created_for_authenticated_user(self):
        response = self.client.post('/api/alert-rules/', {
            'stock_symbol': 'RELIANCE.NS',
            'price_threshold': '2800.00',
            'condition': 'BELOW'
        })
        self.assertEqual(response.status_code, 201)
        rule = AlertRule.objects.get(stock_symbol='RELIANCE.NS')
        self.assertEqual(rule.user, self.user1)
# Checking if the user can see only his rules and not other user's rules
    def test_user_can_only_see_own_rules(self):
    # Create a rule for user1
     AlertRule.objects.create(
        user=self.user1,
        stock_symbol='RELIANCE.NS',
        price_threshold=2800,
        condition='BELOW',
        is_active=True
    )
    # Create a rule for user2
     AlertRule.objects.create(
        user=self.user2,
        stock_symbol='TCS.NS',
        price_threshold=3000,
        condition='ABOVE',
        is_active=True
    )
    # client is authenticated as user1
     response = self.client.get('/api/alert-rules/')
     self.assertEqual(response.status_code, 200)
    # Assert only 1 rule is returned (user1's), not 2
     self.assertEqual(len(response.data), 1)
     self.assertEqual(response.data[0]['stock_symbol'], 'RELIANCE.NS')

    def test_below_condition_triggers(self):
        rule = AlertRule.objects.create(
            user=self.user1,
            stock_symbol='RELIANCE.NS',
            price_threshold=3000,
            condition='BELOW',
            is_active=True
        )
        # Should trigger — price is below threshold
        self.assertTrue(check_alert_condition(Decimal('2800'), rule))
        # Should NOT trigger — price is above threshold
        self.assertFalse(check_alert_condition(Decimal('3500'), rule))

# what @patch does: it temporarily replaces redis_client in your services module with a
# fake object (mock_redis) for the duration of that test.
# You control exactly what mock_redis.get() returns — so you can test both cases
# (None and a value) without Redis being involved at all.

class CacheTests(TestCase):
    @patch('market_alerts.services.redis_client')
    def test_cache_miss_returns_none(self, mock_redis):
        mock_redis.get.return_value = None
        result = get_cached_price('RELIANCE.NS')
        self.assertIsNone(result)

    @patch('market_alerts.services.redis_client')
    def test_cache_hit_returns_float(self, mock_redis):
        mock_redis.get.return_value = '1293.0'
        result = get_cached_price('RELIANCE.NS')
        self.assertEqual(result, 1293.0)
        self.assertIsInstance(result, float)