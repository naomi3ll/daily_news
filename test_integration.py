#!/usr/bin/env python3
"""
完整集成测试 - 验证整个系统的端到端功能
"""
import sys
import os
import re

sys.path.insert(0, os.path.dirname(__file__))

from news_aggregator import fetch_all_news
from scripts.generate_news_page import render_html

def test_end_to_end():
    """测试端到端流程"""
    print("\n" + "="*70)
    print("完整集成测试 - 端到端流程")
    print("="*70)
    
    # 步骤 1: 获取新闻
    print("\n[1/5] 正在从所有来源获取新闻...")
    items = fetch_all_news(use_cache=False)
    print(f"     ✓ 成功获取 {len(items)} 条新闻")
    
    if not items:
        print("     ✗ 没有获取到新闻，测试失败")
        return False
    
    # 步骤 2: 验证数据格式
    print("\n[2/5] 验证数据格式...")
    required_fields = {'title', 'datetime', 'link', 'source', 'type'}
    errors = []
    
    for i, item in enumerate(items):
        missing = required_fields - set(item.keys())
        if missing:
            errors.append(f"Article {i}: missing fields {missing}")
    
    if errors:
        print(f"     ✗ 发现 {len(errors)} 个格式错误")
        for error in errors[:5]:
            print(f"       - {error}")
        return False
    else:
        print(f"     ✓ 所有 {len(items)} 条新闻格式正确")
    
    # 步骤 3: 检查数据一致性
    print("\n[3/5] 检查数据一致性...")
    issues = []
    
    for i, item in enumerate(items):
        # 检查链接格式
        if not (item['link'].startswith('http://') or item['link'].startswith('https://')):
            issues.append(f"Article {i}: invalid URL format")
        
        # 检查日期格式
        if not re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', item['datetime']):
            issues.append(f"Article {i}: invalid datetime format")
        
        # 检查来源
        if item['source'] not in ['wallstreetcn', 'reuters']:
            issues.append(f"Article {i}: unknown source '{item['source']}'")
    
    if issues:
        print(f"     ✗ 发现 {len(issues)} 个一致性问题")
        for issue in issues[:5]:
            print(f"       - {issue}")
        return False
    else:
        print("     ✓ 数据一致性检查通过")
    
    # 步骤 4: 生成 HTML
    print("\n[4/5] 生成 HTML 页面...")
    try:
        html = render_html(items)
        
        # 验证 HTML 有效性
        checks = [
            ('<!DOCTYPE', '<html>' in html),
            ('head 标签', '<head>' in html),
            ('body 标签', '<body>' in html),
            ('title 标签', '<title>' in html),
            ('style 标签', '<style>' in html),
            ('script 标签', '<script>' in html),
            ('搜索框', 'searchInput' in html),
            ('筛选按钮', 'data-filter' in html),
            ('新闻卡片', 'class=\'card\'' in html),
            ('来源部分', 'source-section' in html),
            ('主题切换', 'themeToggle' in html),
        ]
        
        html_size = len(html)
        print(f"     ✓ HTML 生成成功，大小：{html_size/1024:.1f} KB")
        
        failed_checks = [name for name, result in checks if not result]
        if failed_checks:
            print(f"     ⚠ 警告：缺少以下 HTML 元素：{', '.join(failed_checks)}")
            return False
        else:
            print(f"     ✓ 所有 HTML 元素验证通过")
            
    except Exception as e:
        print(f"     ✗ HTML 生成失败：{e}")
        return False
    
    # 步骤 5: 统计信息
    print("\n[5/5] 生成统计信息...")
    
    sources = {}
    for item in items:
        source = item['source']
        sources[source] = sources.get(source, 0) + 1
    
    types = {}
    for item in items:
        type_ = item['type']
        types[type_] = types.get(type_, 0) + 1
    
    print(f"     总计：{len(items)} 条新闻")
    print(f"     按来源分布：")
    for source, count in sorted(sources.items()):
        print(f"       - {source}: {count} 条")
    print(f"     按类型分布：")
    for type_, count in sorted(types.items()):
        print(f"       - {type_}: {count} 条")
    
    # 最终结果
    print("\n" + "="*70)
    print("✓ 所有测试通过！端到端流程正常工作")
    print("="*70 + "\n")
    
    return True

def show_sample_articles(count=3):
    """显示示例新闻"""
    print("\n" + "="*70)
    print("示例新闻")
    print("="*70)
    
    items = fetch_all_news(use_cache=False)
    
    for i, item in enumerate(items[:count], 1):
        print(f"\n[{i}] {item['source'].upper()} - {item['type']}")
        print(f"    标题：{item['title']}")
        print(f"    时间：{item['datetime']}")
        print(f"    链接：{item['link'][:60]}...")
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    success = test_end_to_end()
    
    if success:
        show_sample_articles(3)
        sys.exit(0)
    else:
        sys.exit(1)
