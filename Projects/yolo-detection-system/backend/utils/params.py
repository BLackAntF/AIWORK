"""查询参数解析工具

统一处理整数类查询参数：非法输入回退默认值，避免 int() 抛 ValueError
后被全局兜底成 500；分页参数在各接口间口径保持一致。
"""
from flask import request
from typing import Optional

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def to_int(value, default: Optional[int] = None) -> Optional[int]:
    """把任意值转为 int，失败时返回 default

    Args:
        value: 待转换的值（查询参数、JSON 字段等）
        default: 转换失败或空值时的回退值

    Returns:
        int | None: 转换结果或回退值
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_int_arg(key: str, default: int,
                  min_value: Optional[int] = None,
                  max_value: Optional[int] = None) -> int:
    """解析整数查询参数，非法值回退默认值，越界值收敛到边界

    Args:
        key: 查询参数名
        default: 缺省值
        min_value: 允许的最小值
        max_value: 允许的最大值

    Returns:
        int: 解析结果
    """
    value = to_int(request.args.get(key), default)
    if min_value is not None and value < min_value:
        return min_value
    if max_value is not None and value > max_value:
        return max_value
    return value


def parse_pagination(default_page_size: int = DEFAULT_PAGE_SIZE,
                     max_page_size: int = MAX_PAGE_SIZE) -> tuple:
    """解析 page / page_size

    超出范围的 page_size 回退为默认值（与既有接口行为一致）。

    Args:
        default_page_size: 每页默认条数
        max_page_size: 每页允许的最大条数

    Returns:
        tuple: (page, page_size)
    """
    page = parse_int_arg('page', 1, min_value=1)
    page_size = to_int(request.args.get('page_size'), default_page_size)
    if page_size < 1 or page_size > max_page_size:
        page_size = default_page_size
    return page, page_size
