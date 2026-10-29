# -*- coding: utf-8 -*-
"""SQLite 数据库自动备份脚本

使用 sqlite3 在线备份 API（backup），在应用运行、存在并发写入时也能得到一致快照，
避免直接复制文件导致的半写状态。

用法:
    python backup_db.py                 # 备份到 backups/，默认保留最近 14 份
    python backup_db.py --keep 30       # 指定保留份数
    python backup_db.py --dir D:\\bak    # 指定备份目录

建议用 Windows 任务计划程序每日执行一次（示例见 docs/功能清单与操作手册）。
"""
import argparse
import os
import sqlite3
import sys
import time
from config import BASE_DIR, Config

DEFAULT_BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
DEFAULT_KEEP = 14


def _resolve_db_path() -> str:
    """从 SQLAlchemy URI 解析出 SQLite 文件路径

    Returns:
        str: 数据库文件绝对路径

    Raises:
        SystemExit: 当前配置不是 SQLite 时退出
    """
    uri = Config.SQLALCHEMY_DATABASE_URI
    prefix = 'sqlite:///'
    if not uri.startswith(prefix):
        raise SystemExit(f'[FAIL] 仅支持 SQLite 备份，当前配置: {uri}')
    return os.path.abspath(uri[len(prefix):])


def backup(db_path: str, backup_dir: str) -> str:
    """执行一次在线备份

    Args:
        db_path: 源数据库路径
        backup_dir: 备份目录

    Returns:
        str: 备份文件路径
    """
    if not os.path.exists(db_path):
        raise SystemExit(f'[FAIL] 数据库文件不存在: {db_path}')

    os.makedirs(backup_dir, exist_ok=True)
    stamp = time.strftime('%Y%m%d_%H%M%S')
    target = os.path.join(backup_dir, f'app_{stamp}.db')

    src = sqlite3.connect(db_path)
    dst = sqlite3.connect(target)
    try:
        with dst:
            src.backup(dst)
    finally:
        src.close()
        dst.close()

    size_mb = os.path.getsize(target) / 1024 / 1024
    print(f'[OK] 备份完成: {target} ({size_mb:.2f} MB)')
    return target


def prune(backup_dir: str, keep: int) -> None:
    """只保留最近 keep 份备份，其余删除

    Args:
        backup_dir: 备份目录
        keep: 保留份数
    """
    if keep < 1:
        return
    files = sorted(
        (os.path.join(backup_dir, f) for f in os.listdir(backup_dir)
         if f.startswith('app_') and f.endswith('.db')),
        key=os.path.getmtime,
        reverse=True
    )
    for stale in files[keep:]:
        os.remove(stale)
        print(f'[清理] 删除过期备份: {os.path.basename(stale)}')
    print(f'[INFO] 当前保留备份 {min(len(files), keep)} 份')


def main() -> int:
    parser = argparse.ArgumentParser(description='SQLite 数据库备份')
    parser.add_argument('--dir', default=DEFAULT_BACKUP_DIR, help='备份目录')
    parser.add_argument('--keep', type=int, default=DEFAULT_KEEP, help='保留份数')
    args = parser.parse_args()

    db_path = _resolve_db_path()
    print(f'[INFO] 源数据库: {db_path}')
    try:
        backup(db_path, args.dir)
    except sqlite3.Error as exc:
        print(f'[FAIL] 备份失败: {exc}')
        return 1

    prune(args.dir, args.keep)
    return 0


if __name__ == '__main__':
    sys.exit(main())
