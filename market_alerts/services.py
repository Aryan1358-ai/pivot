# writing all the business logic here ,  a script to fetch data from yfinance
import redis
import yfinance
import environ
from google import genai
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
    message=generate_alert_message(symbol, condition, threshold, current_price)
    from_email=env('EMAIL_HOST_USER')
    recipient_list=[user.email]
    send_mail(subject,message,from_email,recipient_list,fail_silently=False)

def check_alert_condition(price , rule)->bool:
    if rule.condition=='BELOW' and price<=rule.price_threshold:
        return True
    if rule.condition=='ABOVE' and price>=rule.price_threshold:
        return True
    return False


client = genai.Client(api_key=env('GEMINI_API_KEY'))
def generate_alert_message(symbol,condition,threshold,price):
    prompt=f"""  You are writing a one-line stock price alert notification for a user.

Given:
- Stock symbol: {symbol}
- Condition: {condition} (either "ABOVE" or "BELOW")
- Threshold price the user set: {threshold}
- Current triggered price: {price}

Write two or 3 sentences telling the user their alert fired.
- State the symbol, that it crossed their threshold, and the current price.
- Tone: clear and direct, like a financial terminal notification. Not casual, not robotic.
- Do NOT add disclaimers or investment advice.

Output ONLY the sentences, nothing else"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()