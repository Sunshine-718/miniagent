import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import re

def file_to_pdf(input_file_path, pdf_file_path=None, font_name='SimSun', font_size=12, page_size=A4):
    """
    将文本文件（.txt, .md）转换为PDF，支持基本Markdown样式（#标题、-列表）和中文字体。
    
    参数:
        input_file_path: 字符串，源文件路径（支持 .txt 和 .md 格式）
        pdf_file_path: 字符串，输出PDF文件路径（可选，默认为同目录同名.pdf）
        font_name: 字符串，中文字体名称（默认为'SimSun'，需要对应字体文件）
        font_size: 整数，正文字体大小（默认为12）
        page_size: tuple，页面尺寸（默认为A4）
    
    返回:
        成功信息或错误信息字符串
    """
    try:
        # 1. 检查源文件
        if not os.path.exists(input_file_path):
            return f"错误：文件 '{input_file_path}' 不存在。"
        
        # 2. 检查文件格式
        _, ext = os.path.splitext(input_file_path)
        ext = ext.lower()
        if ext not in ['.txt', '.md']:
            return f"错误：不支持的文件格式 '{ext}'。目前仅支持 .txt 和 .md 文件。"
        
        # 3. 确定输出PDF路径
        if pdf_file_path is None:
            base_name = os.path.splitext(input_file_path)[0]
            pdf_file_path = base_name + '.pdf'
        
        # 4. 注册中文字体（尝试常见路径）
        # 注意：在Windows上，SimSun是系统字体，reportlab可能已内置支持，但为了保险，我们尝试注册
        # 如果字体注册失败，将使用默认字体（可能不支持中文）
        font_registered = False
        # 常见中文字体文件路径（Windows）
        font_paths = [
            'C:/Windows/Fonts/simsun.ttc',      # Windows 10/11
            'C:/Windows/Fonts/simsun.ttf',
            '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',  # Linux
            '/System/Library/Fonts/PingFang.ttc',  # macOS
        ]
        
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, fp))
                    font_registered = True
                    break
                except:
                    continue
        
        if not font_registered:
            # 尝试使用reportlab内置的Chinese字体（如果可用）
            try:
                from reportlab.lib.fonts import addMapping
                from reportlab.pdfbase.cidfonts import UnicodeCIDFont
                pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
                font_name = 'STSong-Light'
                font_registered = True
            except:
                pass
        
        # 如果仍然没有注册成功，使用默认字体（可能不支持中文）
        if not font_registered:
            print("警告：未找到中文字体文件，中文可能显示为方框。")
        
        # 5. 读取文本内容
        with open(input_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 6. 创建PDF文档
        doc = SimpleDocTemplate(pdf_file_path, pagesize=page_size,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
        
        # 7. 定义样式
        styles = getSampleStyleSheet()
        # 标题1样式
        title1_style = ParagraphStyle(
            'CustomTitle1',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=font_size + 8,
            spaceAfter=12,
            alignment=TA_CENTER
        )
        # 标题2样式
        title2_style = ParagraphStyle(
            'CustomTitle2',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=font_size + 4,
            spaceAfter=8,
            alignment=TA_LEFT
        )
        # 正文字体
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=font_size,
            spaceAfter=6,
            alignment=TA_LEFT
        )
        # 列表项样式
        bullet_style = ParagraphStyle(
            'CustomBullet',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=font_size,
            leftIndent=20,
            spaceAfter=4,
            alignment=TA_LEFT
        )
        
        # 8. 解析内容并构建Flowables
        flowables = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.rstrip()
            if not line:
                # 空行添加间距
                flowables.append(Spacer(1, 12))
                continue
            
            # 判断行类型
            if line.startswith('# '):
                # 一级标题
                text = line[2:].strip()
                flowables.append(Paragraph(text, title1_style))
            elif line.startswith('## '):
                # 二级标题
                text = line[3:].strip()
                flowables.append(Paragraph(text, title2_style))
            elif line.startswith('### '):
                # 三级标题（使用标题2样式但小一点）
                text = line[4:].strip()
                style = ParagraphStyle(
                    'CustomTitle3',
                    parent=title2_style,
                    fontSize=font_size + 2
                )
                flowables.append(Paragraph(text, style))
            elif line.startswith('- ') or line.startswith('* '):
                # 列表项
                text = line[2:].strip()
                # 使用ListFlowable或简单的Paragraph加缩进
                flowables.append(Paragraph('• ' + text, bullet_style))
            elif re.match(r'^\d+\.\s', line):
                # 数字列表项
                flowables.append(Paragraph(line, bullet_style))
            else:
                # 普通段落
                flowables.append(Paragraph(line, normal_style))
        
        # 9. 构建PDF
        doc.build(flowables)
        
        return f"成功：PDF已生成到 '{pdf_file_path}'。"
    
    except Exception as e:
        return f"错误：生成PDF时发生异常 - {str(e)}"

# 为了向后兼容，保留 txt_to_pdf 作为别名
def txt_to_pdf(txt_file_path, pdf_file_path=None, font_name='SimSun', font_size=12, page_size=A4):
    """
    将文本文件转换为PDF（兼容旧版本）。
    参数同 file_to_pdf。
    """
    return file_to_pdf(txt_file_path, pdf_file_path, font_name, font_size, page_size)

# 测试代码（当直接运行时）
if __name__ == "__main__":
    # 简单测试
    test_files = ["test.txt", "test.md"]
    for test_file in test_files:
        if os.path.exists(test_file):
            result = file_to_pdf(test_file, f"test_output_{test_file}.pdf")
            print(result)
        else:
            print(f"测试文件 {test_file} 不存在。")