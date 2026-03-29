"""PDF 生成工具模块"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path


def markdown_to_pdf(markdown_content: str, pdf_path: str):
    """将 markdown 内容转换为 PDF 文件"""
    html_content = markdown.markdown(
        markdown_content, extensions=["tables", "fenced_code"]
    )

    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Model Output</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    css = CSS(
        string="""
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        h1, h2, h3, h4, h5, h6 { color: #333; margin-top: 20px; }
        pre { background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }
        code { background-color: #f5f5f5; padding: 2px 4px; border-radius: 2px; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        blockquote { border-left: 4px solid #ddd; margin: 0; padding-left: 16px; color: #666; }
    """
    )

    html_doc = HTML(string=full_html)
    html_doc.write_pdf(pdf_path, stylesheets=[css])


def create_pdf_filename(case_num: int, model_name: str, use_rag: bool) -> str:
    """创建 PDF 文件名"""
    rag_status = "RAG" if use_rag else "No-RAG"
    return f"case{case_num}_{model_name}_{rag_status}.pdf"


def ensure_pdfs_directory():
    """确保 PDFs 目录存在"""
    pdfs_dir = Path("PDFs")
    pdfs_dir.mkdir(exist_ok=True)
    return pdfs_dir
