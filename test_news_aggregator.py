#!/usr/bin/env python3
"""Test script to validate the news aggregator and format"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from news_aggregator import fetch_all_news, fetch_news_by_source
from datetime import datetime

def validate_article(article):
    """Validate article structure"""
    required_fields = ['title', 'datetime', 'link', 'source', 'type']
    
    for field in required_fields:
        if field not in article:
            return False, f"Missing field: {field}"
    
    # Validate datetime format
    try:
        datetime.strptime(article['datetime'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return False, f"Invalid datetime format: {article['datetime']}"
    
    # Validate link format
    if not (article['link'].startswith('http://') or article['link'].startswith('https://')):
        return False, f"Invalid link format: {article['link']}"
    
    # Validate source
    if article['source'] not in ['wallstreetcn', 'reuters']:
        return False, f"Unknown source: {article['source']}"
    
    # Validate type
    if article['type'] not in ['article', 'live', 'theme', 'chart']:
        return False, f"Unknown type: {article['type']}"
    
    return True, "OK"

def test_aggregator():
    """Test the news aggregator"""
    print("Testing News Aggregator")
    print("=" * 60)
    
    # Test 1: Fetch all news
    print("\n1. Testing fetch_all_news()...")
    items = fetch_all_news(use_cache=False)
    print(f"   ✓ Found {len(items)} articles")
    
    # Test 2: Validate article format
    print("\n2. Validating article format...")
    invalid_count = 0
    for i, item in enumerate(items):
        valid, msg = validate_article(item)
        if not valid:
            print(f"   ✗ Article {i}: {msg}")
            invalid_count += 1
    
    if invalid_count == 0:
        print(f"   ✓ All {len(items)} articles are valid")
    else:
        print(f"   ✗ {invalid_count} articles have validation errors")
    
    # Test 3: Test source-specific fetch
    print("\n3. Testing source-specific fetch...")
    try:
        wscn_items = fetch_news_by_source('wallstreetcn', use_cache=False)
        print(f"   ✓ WallStreetCN: {len(wscn_items)} articles")
    except Exception as e:
        print(f"   ✗ WallStreetCN error: {e}")
    
    try:
        reuters_items = fetch_news_by_source('reuters', use_cache=False)
        print(f"   ✓ Reuters: {len(reuters_items)} articles")
    except Exception as e:
        print(f"   ✗ Reuters error: {e}")
    
    # Test 4: Check data consistency
    print("\n4. Checking data consistency...")
    sources = {}
    for item in items:
        source = item['source']
        sources[source] = sources.get(source, 0) + 1
    
    print(f"   ✓ Source distribution: {sources}")
    
    # Test 5: Sample output
    print("\n5. Sample articles:")
    for i, item in enumerate(items[:3]):
        print(f"\n   Article {i+1}:")
        print(f"   - Title: {item['title'][:50]}...")
        print(f"   - Source: {item['source']}")
        print(f"   - Type: {item['type']}")
        print(f"   - Time: {item['datetime']}")
        print(f"   - Link: {item['link'][:60]}...")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!" if invalid_count == 0 else f"✗ {invalid_count} tests failed")

if __name__ == '__main__':
    test_aggregator()
