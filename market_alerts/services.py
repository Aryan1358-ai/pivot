# writing all the business logic here ,  a script to fetch data from yfinance
import redis
import yfinance
import environ
env = environ.Env()
environ.Env.read_env()
redis_client=redis.Redis(host=env('REDIS_HOST'), port=env.int('REDIS_PORT'), db=0,decode_responses=True)
from django.core.mail import send_mail
CACHE_TTL_SECONDS=300

def fetch_and_cache_price(symbol:str)->float:
    ticker = yfinance.Ticker(symbol)
    price = ticker.fast_info['lastPrice']
    redis_client.set(f"price:{symbol}",price,ex=CACHE_TTL_SECONDS)
    return price

def get_cached_price(symbol:str)->float | None:
    cached = redis_client.get(f"price:{symbol}")

    if cached is None:
        return None
    return float(cached)

def send_alert_email(user, symbol, condition, threshold, current_price):
    subject=f"Pivot alert on {symbol} "
    if condition=='BELOW':
        con="dropped below"
    else:
        con="crossed above"
    message=f"Price has {con} {threshold}. Currently at {round(current_price,2)}"
    from_email=env('EMAIL_HOST_USER')
    recipient_list=[user.email]
    send_mail(subject,message,from_email,recipient_list,fail_silently=False)

def check_alert_condition(price , rule)->bool:
    if rule.condition=='BELOW' and price<=rule.price_threshold:
        return True
    if rule.condition=='ABOVE' and price>=rule.price_threshold:
        return True
    return False