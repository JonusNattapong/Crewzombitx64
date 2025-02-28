import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
from mistralai import Mistral
from dotenv import load_dotenv

# โหลดค่า API Key จากไฟล์ .env
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

# ฟังก์ชันการเช็ค robots.txt
def check_robots_txt(url):
    try:
        response = requests.get(url + "/robots.txt")
        response.raise_for_status()
        return "Disallow" not in response.text
    except Exception as e:
        print(f"Error checking robots.txt: {e}")
        return True  # Assume allowed if error

# ฟังก์ชันขูดข้อมูลจากเว็บไซต์
def scrape_content(url):
    if not check_robots_txt(url):
        print("Crawling disallowed by robots.txt")
        return None

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Handle GitHub repository pages
        if 'github.com' in url:
            # Get repository title
            title_elem = soup.find('strong', {'itemprop': 'name'})
            if not title_elem:
                title_elem = soup.find('h1', class_='d-flex')
            title = title_elem.text.strip() if title_elem else "No Title Found"

            # Get repository content
            content = []
            
            # Get repository description
            description = soup.find('p', {'class': 'f4'})
            if description:
                content.append(description.text.strip())

            # Get README content
            readme = soup.find('article', class_='markdown-body')
            if readme:
                content.extend(extract_content_from_element(readme))

        else:
            # Handle other websites as before
            title = soup.find('h1').text.strip() if soup.find('h1') else "No Title Found"
            content = []
            article = soup.find('article') or soup.find(class_='entry-content')
            if article:
                content = extract_content_from_element(article)

        return {
            "title": title,
            "text": "\n\n".join(content),
            "metadata": {
                "url": url,
                "crawled_at": datetime.now().isoformat()
            }
        }
    except Exception as e:
        print(f"Error scraping content: {e}")
        return None

# ฟังก์ชันในการแยกข้อมูลจาก HTML
def extract_content_from_element(element):
    content = []
    for child in element.children:
        if child.name == 'p':
            content.append(child.get_text(strip=True))
        elif child.name in ['h2', 'h3', 'h4', 'h5', 'h6']:
            content.append(f"{'#' * int(child.name[1])} {child.get_text(strip=True)}")
        elif child.name == 'ul' or child.name == 'ol':
            for li in child.find_all('li'):
                content.append(f"- {li.get_text(strip=True)}")
        elif child.string:
            content.append(child.string.strip())
    return content

# ฟังก์ชันสำหรับการสรุปข้อมูลโดยใช้ Mistral API
def summarize_with_mistral(content):
    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {
                    "role": "user",
                    "content": f"Please summarize the following content concisely:\n\n{content}"
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error with Mistral summarization: {e}")
        return "AI Summarization failed."

# ฟังก์ชันในการบันทึกข้อมูลในรูปแบบ JSON
def save_content_json(content, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)

# ฟังก์ชันในการบันทึกข้อมูลในรูปแบบ Markdown
def save_content_markdown(content, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# {content['title']}\n\n")
        f.write(f"URL: {content['metadata']['url']}\n\n")
        f.write(f"Crawled at: {content['metadata']['crawled_at']}\n\n")
        f.write(f"## Summary\n\n{content['summary']}\n\n")
        f.write(content['text'])

# ฟังก์ชันหลัก
def main():
    url = "https://originshq.com/blog/top-ai-llm-learning-resource-in-2025/#ib-toc-anchor-0"  # เปลี่ยน URL ตามที่ต้องการ
    content = scrape_content(url)

    if content:
        # สรุปข้อมูลโดยใช้ Mistral API
        summary = summarize_with_mistral(content['text'])

        # เพิ่ม summary ลงในข้อมูล
        content['summary'] = summary

        # บันทึกข้อมูลในรูปแบบ JSON และ Markdown
        save_content_json(content, "crawled_content7.json")
        save_content_markdown(content, "crawled_content7.md")
        print("Content has been successfully crawled, summarized, and saved.")
    else:
        print("No content was crawled.")

if __name__ == "__main__":
    main()
