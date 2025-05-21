import time
import logging

# Simple in-memory cache
cache = {}

def cache_data(key, data, expiry_seconds):
    """
    Cache data with an expiry time
    
    Args:
        key (str): Cache key
        data (any): Data to cache
        expiry_seconds (int): Seconds until expiration
    """
    expiry = time.time() + expiry_seconds
    cache[key] = {
        'data': data,
        'expiry': expiry
    }
    logging.debug(f"Cached data with key: {key}, expires in {expiry_seconds} seconds")

def get_cached_data(key):
    """
    Get data from cache if it exists and hasn't expired
    
    Args:
        key (str): Cache key
        
    Returns:
        any: Cached data or None if not found or expired
    """
    if key in cache:
        cache_item = cache[key]
        
        # Check if expired
        if time.time() < cache_item['expiry']:
            logging.debug(f"Cache hit for key: {key}")
            return cache_item['data']
        else:
            # Remove expired item
            logging.debug(f"Cache expired for key: {key}")
            del cache[key]
    
    logging.debug(f"Cache miss for key: {key}")
    return None

def clear_cache():
    """Clear all cached data"""
    cache.clear()
    logging.debug("Cache cleared")

def remove_expired():
    """Remove all expired items from cache"""
    current_time = time.time()
    keys_to_remove = []
    
    for key, cache_item in cache.items():
        if current_time > cache_item['expiry']:
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del cache[key]
    
    if keys_to_remove:
        logging.debug(f"Removed {len(keys_to_remove)} expired items from cache")
