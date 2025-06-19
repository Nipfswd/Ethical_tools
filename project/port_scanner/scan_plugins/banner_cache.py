# scan_plugins/banner_cache.py

import json
import os

CACHE_FILE = 'banner_cache.json'
_cache = {}

def load_cache():
    global _cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            _cache = json.load(f)

def save_cache():
    with open(CACHE_FILE, 'w') as f:
        json.dump(_cache, f)

def on_open_port(ip, port, scan_data):
    load_cache()
    h = scan_data.get('banner_hash')
    if not h:
        return {}

    seen_before = _cache.get(h)
    if not seen_before:
        _cache[h] = {'ip': ip, 'port': port}
        save_cache()
        return {'banner_seen_before': False}
    else:
        return {'banner_seen_before': True}
