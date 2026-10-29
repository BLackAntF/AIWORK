# -*- coding: utf-8 -*-
"""utils/params.py 参数解析工具单元测试

运行: python tests/test_params_utils.py
覆盖：非法整数回退、越界收敛、分页口径一致性（不再抛 ValueError 变 500）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from utils.params import parse_int_arg, parse_pagination, to_int

app = create_app()
results = []


def check(name, condition, detail=''):
    results.append((name, condition, detail))
    print(f"[{'PASS' if condition else 'FAIL'}] {name}{'' if condition else ' ' + detail}")


def test_to_int():
    check('to_int 正常数字', to_int('12') == 12)
    check('to_int 非数字回退默认', to_int('abc', 5) == 5)
    check('to_int 空串回退默认', to_int('', 3) == 3)
    check('to_int None 回退默认', to_int(None, 7) == 7)
    check('to_int 支持浮点字符串失败回退', to_int('1.5', 2) == 2)


def test_parse_int_arg():
    with app.test_request_context('/?limit=abc&page=0&size=999'):
        check('parse_int_arg 非数字回退', parse_int_arg('limit', 5) == 5)
        check('parse_int_arg 低于下限收敛', parse_int_arg('page', 1, min_value=1) == 1)
        check('parse_int_arg 高于上限收敛', parse_int_arg('size', 20, max_value=100) == 100)
        check('parse_int_arg 缺省值', parse_int_arg('missing', 9) == 9)


def test_parse_pagination():
    with app.test_request_context('/?page=abc&page_size=xyz'):
        check('分页非法值回退默认', parse_pagination() == (1, 20))
    with app.test_request_context('/?page=2&page_size=10'):
        check('分页正常解析', parse_pagination() == (2, 10))
    with app.test_request_context('/?page=0&page_size=1000'):
        check('分页 page 自愈为 1、超限 page_size 回退', parse_pagination() == (1, 20))
    with app.test_request_context('/?page_size=12'):
        check('分页自定义默认值', parse_pagination(default_page_size=12) == (1, 12))


def test_no_500_on_bad_query():
    client = app.test_client()
    resp = client.get('/api/knowledge/list?page=abc&page_size=xyz')
    body = resp.get_json()
    check('非法分页不再 500，返回正常业务码', body is not None and body.get('code') == 0,
          f'实际: {body and body.get("code")}')


if __name__ == '__main__':
    test_to_int()
    test_parse_int_arg()
    test_parse_pagination()
    test_no_500_on_bad_query()

    failed = [r for r in results if not r[1]]
    print(f"\n结果: {len(results) - len(failed)} passed, {len(failed)} failed")
    sys.exit(1 if failed else 0)
