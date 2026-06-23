"""
将页面设计图.html 中的每个 Mermaid 图表导出为 PNG
"""
import os
import sys
import asyncio
from playwright.async_api import async_playwright

OUTPUT_DIR = r"c:\Users\ASUS\Desktop\demo\uniapp-demo\设计图PNG"
HTML_PATH = r"c:\Users\ASUS\Desktop\demo\uniapp-demo\页面设计图.html"

# 每个图表的标题和文件名
CHARTS = [
    ("1.1-首页组件关系图", "首页组件关系图"),
    ("1.2-首页数据流图", "首页数据流图"),
    ("1.3-首页状态图", "首页状态图"),
    ("2.1-控制页面组件关系图", "控制页面组件关系图"),
    ("2.2-控制页面数据流图", "控制页面数据流图"),
    ("2.3-控制页面状态图", "控制页面状态图"),
    ("3-页面间数据流总图", "页面间数据流总图"),
]

async def export_charts():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        
        # 读取HTML内容
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        await page.set_content(html_content)
        
        # 等待Mermaid渲染完成
        await page.wait_for_timeout(3000)
        
        # 获取所有mermaid图表元素
        chart_elements = await page.query_selector_all(".mermaid")
        
        print(f"找到 {len(chart_elements)} 个图表")
        
        for i, (chart_id, chart_name) in enumerate(CHARTS):
            if i >= len(chart_elements):
                print(f"跳过 {chart_name}: 索引超出")
                continue
            
            element = chart_elements[i]
            
            # 获取元素位置和大小
            box = await element.bounding_box()
            if box is None:
                print(f"跳过 {chart_name}: 无法获取位置")
                continue
            
            # 截图
            output_path = os.path.join(OUTPUT_DIR, f"{chart_id}.png")
            await page.screenshot(
                path=output_path,
                clip={
                    "x": box["x"],
                    "y": box["y"],
                    "width": box["width"],
                    "height": box["height"],
                }
            )
            print(f"✅ 已导出: {chart_name} -> {output_path}")
        
        await browser.close()
    
    print(f"\n🎉 全部完成！共导出 {len(CHARTS)} 张PNG图片到: {OUTPUT_DIR}")

if __name__ == "__main__":
    asyncio.run(export_charts())
