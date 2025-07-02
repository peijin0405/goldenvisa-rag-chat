import requests
from bs4 import BeautifulSoup
from datetime import datetime

url = "https://www.globalcitizensolutions.com/golden-visa-portugal/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def extract_sections(soup):
    """提取所有section内容并去除重复段落"""
    sections = []
    seen_paragraphs = set()
    
    for i, section in enumerate(soup.find_all('section'), 1):
        section_data = {
            "section_number": i,
            "heading": "",
            "paragraphs": [],
            "lists": []
        }
        
        # 提取标题
        heading = section.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if heading:
            section_data["heading"] = heading.get_text(strip=True)
        
        # 提取段落(去重)
        for p in section.find_all('p'):
            text = p.get_text(strip=True)
            if text and text not in seen_paragraphs and len(text) > 20:
                seen_paragraphs.add(text)
                section_data["paragraphs"].append(text)
        
        # 提取列表(去重)
        seen_list_items = set()
        for ul in section.find_all('ul'):
            list_items = []
            for li in ul.find_all('li'):
                item = li.get_text(strip=True)
                if item and item not in seen_list_items:
                    seen_list_items.add(item)
                    list_items.append(item)
            if list_items:
                section_data["lists"].append(list_items)
        
        if section_data["paragraphs"] or section_data["lists"]:
            sections.append(section_data)
    return sections

def extract_special_sections(soup):
    """提取关键分类部分(Requirements, Benefits等)"""
    special_sections = {}
    target_headings = ["requirements", "benefits", "eligibility", "how to apply", "key points"]
    
    for h2 in soup.find_all(['h2', 'h3']):
        heading_text = h2.get_text(strip=True).lower()
        for target in target_headings:
            if target in heading_text:
                content = []
                next_node = h2.next_sibling
                
                while next_node and next_node.name not in ['h2', 'h3']:
                    if next_node.name == 'p':
                        text = next_node.get_text(strip=True)
                        if text:
                            content.append(text)
                    elif next_node.name == 'ul':
                        for li in next_node.find_all('li'):
                            text = li.get_text(strip=True)
                            if text:
                                content.append(text)
                    next_node = next_node.next_sibling
                
                if content:
                    special_sections[target] = content
                break
                
    return special_sections

def save_as_text(data, filename):
    """保存为文本文件"""
    with open(filename, 'w', encoding='utf-8') as file:
        # 写入元信息
        file.write("=== META INFORMATION ===\n")
        file.write(f"Title: {data['title']}\n")
        file.write(f"Last Updated: {data['last_updated']}\n")
        file.write(f"Source URL: {url}\n\n")
        
        # 写入关键分类信息
        file.write("=== KEY CATEGORIZED INFORMATION ===\n\n")
        for category, items in data["special_sections"].items():
            file.write(f"** {category.upper()} **\n")
            for item in items:
                file.write(f"- {item}\n")
            file.write("\n")
        
        # 写入section数据
        file.write("\n=== DETAILED CONTENT ===\n\n")
        for section in data["sections"]:
            file.write(f"=== Section {section['section_number']}: {section['heading']} ===\n\n")
            for para in section['paragraphs']:
                file.write(f"{para}\n\n")
            for lst in section['lists']:
                file.write("List Items:\n")
                for item in lst:
                    file.write(f"* {item}\n")
                file.write("\n")

try:
    # 获取页面内容
    print("Fetching webpage content...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 提取数据
    print("Extracting data...")
    data = {
        "title": soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sections": extract_sections(soup),
        "special_sections": extract_special_sections(soup)
    }
    
    # 保存数据为文本文件
    txt_filename = "portugal_golden_visa_info.txt"
    save_as_text(data, txt_filename)
    print(f"Data saved to {txt_filename}")
    
    # 保存HTML备份
    html_filename = "portugal_golden_visa_backup.html"
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"HTML backup saved to {html_filename}")
    
    # 打印摘要
    print("\nExtraction summary:")
    print(f"- Found {len(data['sections'])} sections")
    print(f"- Extracted {len(data['special_sections'])} key categories")
    print(f"- Total {sum(len(v) for v in data['special_sections'].values())} key points extracted")

except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
except Exception as e:
    print(f"Error occurred: {e}")