from django.core.cache import cache
from web.models import Config

def get_config(key=''):
    if not cache.get(key):
        config = Config.objects.first()
        value = getattr(config, key)
        cache.set(key, value, timeout=30)
    return cache.get(key)
