# -*- coding: utf-8 -*-
"""백엔드 라우트 분석 및 프론트엔드 매핑 확인"""
import sys
from collections import defaultdict

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from app.main import app

# 라우트 분류
routes_by_category = defaultdict(list)

for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        if route.path.startswith('/api/v1'):
            # OpenAPI 관련 제외
            if route.path in ['/openapi.json', '/docs', '/redoc']:
                continue
            
            # 카테고리 추출
            parts = route.path.split('/')
            if len(parts) >= 4:
                category = parts[3]  # /api/v1/[category]/...
            else:
                category = 'root'
            
            methods = ','.join(m for m in route.methods if m not in ['HEAD', 'OPTIONS'])
            route_info = {
                'path': route.path,
                'methods': methods,
                'name': route.name if hasattr(route, 'name') else 'unknown'
            }
            routes_by_category[category].append(route_info)

# 출력
print("\n=== Backend API Routes by Category ===\n")

categories_sorted = sorted(routes_by_category.items(), key=lambda x: len(x[1]), reverse=True)

for category, routes in categories_sorted:
    print(f"\n[{category.upper()}] - {len(routes)} endpoints")
    print("-" * 80)
    for route in sorted(routes, key=lambda r: r['path'])[:5]:  # 상위 5개만 표시
        print(f"  {route['methods']:15s} {route['path']}")
    if len(routes) > 5:
        print(f"  ... and {len(routes)-5} more")

print("\n\n=== Summary ===")
print(f"Total Categories: {len(categories_sorted)}")
print(f"Total Endpoints: {sum(len(r) for r in routes_by_category.values())}")

# 주요 기능 분류
print("\n\n=== Key Feature Groups ===")
feature_groups = {
    "Authentication & Users": ['auth', 'student'],
    "Learning Content": ['questions', 'subjects', 'curriculum', 'dynamic-subjects'],
    "Learning Progress": ['submit', 'dashboard', 'stats', 'unified-learning', 'mvp-learning'],
    "AI Features": ['ai-learning', 'ai-features', 'ai-curriculum', 'ai-teaching', 'ai-questions-phase10', 'ai-counseling', 'feedback'],
    "Code Execution": ['code-execution'],
    "Admin & Teacher": ['admin', 'teacher', 'teacher_groups'],
    "Payment": ['payment', 'subscriptions'],
    "Reviews & Achievements": ['review', 'achievement'],
    "Advanced": ['personalization', 'beta', 'monitoring', 'taxonomy']
}

for group_name, categories in feature_groups.items():
    count = sum(len(routes_by_category[cat]) for cat in categories if cat in routes_by_category)
    if count > 0:
        print(f"\n{group_name}: {count} endpoints")
        for cat in categories:
            if cat in routes_by_category:
                print(f"  - {cat}: {len(routes_by_category[cat])} endpoints")

