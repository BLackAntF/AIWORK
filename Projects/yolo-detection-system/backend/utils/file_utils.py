import os
import uuid
from werkzeug.utils import secure_filename


def allowed_file(filename, allowed_extensions):
    """检查文件扩展名是否允许

    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名集合

    Returns:
        bool: 是否允许
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file, upload_dir, prefix=''):
    """保存上传的文件

    Args:
        file: Flask file 对象
        upload_dir: 保存目录
        prefix: 文件名前缀

    Returns:
        tuple: (保存路径, 新文件名, 原始文件名)
    """
    os.makedirs(upload_dir, exist_ok=True)

    original_name = secure_filename(file.filename)
    ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else ''
    new_filename = f"{prefix}{uuid.uuid4().hex}.{ext}" if ext else f"{prefix}{uuid.uuid4().hex}"

    save_path = os.path.join(upload_dir, new_filename)
    file.save(save_path)

    return save_path, new_filename, original_name


def get_file_size(file_path):
    """获取文件大小（字节）

    Args:
        file_path: 文件路径

    Returns:
        int: 文件大小，不存在返回 0
    """
    return os.path.getsize(file_path) if os.path.exists(file_path) else 0


def get_relative_url(file_path, base_dir, url_prefix='/static'):
    """将绝对路径转换为 URL 相对路径

    Args:
        file_path: 文件绝对路径
        base_dir: 静态文件根目录
        url_prefix: URL 前缀

    Returns:
        str: 相对 URL
    """
    if not file_path:
        return None
    rel_path = os.path.relpath(file_path, base_dir)
    return f"{url_prefix}/{rel_path.replace(os.sep, '/')}"
