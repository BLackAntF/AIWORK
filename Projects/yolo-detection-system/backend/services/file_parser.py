import os
import re

ALLOWED_EXTENSIONS = {'txt', 'md', 'docx', 'pdf'}


def parse_file(file_path, original_filename=None):
    """解析文件内容

    Args:
        file_path: 文件路径
        original_filename: 原始文件名（用于提取标题）

    Returns:
        dict: {title, content, summary}
    """
    ext = file_path.rsplit('.', 1)[1].lower() if '.' in file_path else ''

    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件格式: {ext}")

    name_for_title = original_filename or os.path.basename(file_path)
    title = os.path.splitext(name_for_title)[0]
    content = ''
    
    try:
        if ext == 'txt':
            content = _parse_txt(file_path)
        elif ext == 'md':
            content = _parse_md(file_path)
        elif ext == 'docx':
            content = _parse_docx(file_path)
        elif ext == 'pdf':
            content = _parse_pdf(file_path)
    except Exception as e:
        raise ValueError(f"文件解析失败: {str(e)}")
    
    summary = content[:200] + '...' if len(content) > 200 else content
    
    return {
        'title': title,
        'content': content,
        'summary': summary
    }


def _parse_txt(file_path):
    """解析TXT文件"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def _parse_md(file_path):
    """解析Markdown文件"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    return content


def _parse_docx(file_path):
    """解析DOCX文件"""
    try:
        from docx import Document
        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return '\n'.join(paragraphs)
    except ImportError:
        raise ValueError("请安装 python-docx: pip install python-docx")


def _parse_pdf(file_path):
    """解析PDF文件"""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return '\n\n'.join(pages)
    except ImportError:
        raise ValueError("请安装 PyPDF2: pip install PyPDF2")


def clean_content(content):
    """清理文本内容"""
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = re.sub(r'\s{2,}', ' ', content)
    return content.strip()
