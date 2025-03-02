import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import urllib.parse
import os
from nltk.tokenize import sent_tokenize
import nltk

# Set ASCII colors for dark mode
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def print_disclaimer():
    """Print disclaimer and warning message"""
    print(f"\n{Colors.WARNING}⚠️ DISCLAIMER AND WARNING / คำเตือนและข้อจำกัดความรับผิดชอบ ⚠️{Colors.ENDC}")
    print(f"{Colors.WARNING}=" * 80)
    print(f"{Colors.BOLD}🔒 [EN] IMPORTANT DISCLAIMER:{Colors.ENDC}")
    print("This tool is for educational purposes only.")
    print("Users are fully responsible for their own actions.")
    print("The developers assume no liability and are not responsible for any misuse or damage.")
    print("\n🚫 By using this tool, you agree to:")
    print("1. Use it legally and ethically")
    print("2. Respect website terms of service")
    print("3. Not use for malicious purposes")
    print("4. Take full responsibility for your actions")
    
    print(f"\n{Colors.BOLD}🔒 [TH] คำเตือนสำคัญ:{Colors.ENDC}")
    print("โปรแกรมนี้ถูกพัฒนาขึ้นเพื่อการศึกษาเท่านั้น")
    print("ผู้ใช้ต้องรับผิดชอบต่อการกระทำทั้งหมดด้วยตนเอง")
    print("ผู้พัฒนาไม่รับผิดชอบต่อความเสียหายใดๆ ที่เกิดจากการใช้งานโปรแกรมนี้")
    print("\n⚠️ การใช้งานถือว่าคุณยอมรับเงื่อนไขต่อไปนี้:")
    print("1. ใช้งานอย่างถูกกฎหมายและมีจริยธรรม")
    print("2. เคารพข้อกำหนดการใช้งานของเว็บไซต์")
    print("3. ไม่ใช้เพื่อวัตถุประสงค์ที่เป็นอันตราย")
    print("4. รับผิดชอบต่อผลกระทบที่อาจเกิดขึ้นทั้งหมด")
    print(f"\n{Colors.FAIL}❗ การใช้งานผิดวัตถุประสงค์อาจมีความผิดทางกฎหมาย ❗{Colors.ENDC}")
    print(f"{Colors.WARNING}=" * 80 + f"{Colors.ENDC}\n")

def print_dark_ascii():
    """Print ASCII art in dark mode colors"""
    ascii_art = f"""{Colors.PURPLE}
███████╗ ██████╗ ███╗   ███╗██████╗ ██╗████████╗██╗  ██╗ ██████╗ ██╗  ██╗
╚══███╔╝██╔═══██╗████╗ ████║██╔══██╗██║╚══██╔══╝╚██╗██╔╝██╔════╝ ██║  ██║
  ███╔╝ ██║   ██║██╔████╔██║██████╔╝██║   ██║    ╚███╔╝ ███████╗ ███████║
 ███╔╝  ██║   ██║██║╚██╔╝██║██╔══██╗██║   ██║    ██╔██╗ ██╔═══██╗╚════██║
███████╗╚██████╔╝██║ ╚═╝ ██║██████╔╝██║   ██║   ██╔╝ ██╗╚██████╔╝     ██║
╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝      ╚═╝
{Colors.ENDC}"""
    print(ascii_art)

def check_robots_txt(url):
    """Check if crawling is allowed by robots.txt"""
    try:
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.netloc:
            parsed_url = urllib.parse.urlparse("http://" + url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        print(f"{Colors.DIM}🔍 Checking: {robots_url}{Colors.ENDC}")
        response = requests.get(robots_url)
        response.raise_for_status()
        
        return "Disallow: /" not in response.text
    except Exception as e:
        print(f"{Colors.WARNING}⚠️ Error checking robots.txt: {str(e)}{Colors.ENDC}")
        return True

def extract_content_from_element(element):
    """Extract formatted content from HTML elements"""
    content = []
    for child in element.children:
        if child.name == 'p':
            content.append(child.get_text(strip=True))
        elif child.name in ['h2', 'h3', 'h4', 'h5', 'h6']:
            content.append(f"{'#' * int(child.name[1])} {child.get_text(strip=True)}")
        elif child.name in ['ul', 'ol']:
            for li in child.find_all('li'):
                content.append(f"- {li.get_text(strip=True)}")
        elif child.string:
            content.append(child.string.strip())
    return content

def extract_readme_content(soup):
    """Extract README content from repository page"""
    content = []
    readme = soup.find('article', class_='markdown-body') or soup.find('div', class_='Box-body')
    
    if readme:
        print(f"{Colors.OKBLUE}📖 Extracting README content...{Colors.ENDC}")
        for unwanted in readme.find_all(['nav', 'footer', 'script', 'style']):
            unwanted.decompose()
        
        for element in readme.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol']):
            if element.parent.name not in ['nav', 'footer']:
                if element.name.startswith('h'):
                    header_text = element.get_text(strip=True)
                    if header_text:
                        content.append(f"{'#' * int(element.name[1])} {header_text}")
                elif element.name == 'p':
                    text = element.get_text(strip=True)
                    if text:
                        content.append(text)
                elif element.name in ['ul', 'ol']:
                    for li in element.find_all('li', recursive=False):
                        li_text = li.get_text(strip=True)
                        if li_text:
                            content.append(f"- {li_text}")
                            
        print(f"{Colors.OKGREEN}✨ Successfully extracted {len(content)} content blocks{Colors.ENDC}")
    
    return content

def scrape_content(url):
    """Main function for scraping content from URLs"""
    print(f"\n{Colors.HEADER}🔍 Starting to scrape: {url}{Colors.ENDC}")
    
    if not check_robots_txt(url):
        print(f"{Colors.FAIL}❌ Crawling disallowed by robots.txt{Colors.ENDC}")
        return None

    try:
        print(f"{Colors.OKBLUE}📡 Fetching content...{Colors.ENDC}")
        response = requests.get(url)
        response.raise_for_status()

        # Handle different content types
        if 'github.com' in url:
            soup = BeautifulSoup(response.text, 'html.parser')
            title_elem = soup.find('strong', {'itemprop': 'name'})
            if not title_elem:
                title_elem = soup.find('h1', class_='d-flex')
            title = title_elem.text.strip() if title_elem else url.split('/')[-1]
            print(f"{Colors.OKBLUE}📚 Found repository: {title}{Colors.ENDC}")
            
            content = []
            description = soup.find('p', {'class': 'f4'})
            if description:
                content.append(description.text.strip())
            
            readme_content = extract_readme_content(soup)
            if readme_content:
                content.extend(readme_content)
        else:
            # Handle general webpages
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('h1').text.strip() if soup.find('h1') else "No Title Found"
            print(f"{Colors.OKBLUE}📄 Page title: {title}{Colors.ENDC}")
            
            content = []
            article = soup.find('article') or soup.find(class_='entry-content')
            if article:
                content = extract_content_from_element(article)

        result = {
            "title": title,
            "text": "\n\n".join(content),
            "metadata": {
                "url": url,
                "crawled_at": datetime.now().isoformat()
            }
        }

        print(f"{Colors.OKGREEN}✨ Successfully scraped content ({len(result['text'])} characters){Colors.ENDC}")
        return result

    except Exception as e:
        print(f"{Colors.FAIL}❌ Error scraping content: {str(e)}{Colors.ENDC}")
        return None

def summarize_content(text, max_sentences=5):
    """Simple text summarization using sentence scoring"""
    print(f"\n{Colors.HEADER}📝 Starting content summarization...{Colors.ENDC}")
    try:
        sentences = sent_tokenize(text)
        
        if len(sentences) <= max_sentences:
            return text
            
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = 0
            words = len(sentence.split())
            
            if 10 <= words <= 30:
                score += 3
            elif 5 <= words <= 40:
                score += 2
            
            if i < len(sentences) * 0.3:
                score += 3
            elif i < len(sentences) * 0.6:
                score += 1
            
            important_words = ['important', 'significant', 'key', 'main', 'critical', 'essential']
            for word in important_words:
                if word.lower() in sentence.lower():
                    score += 2
            
            scored_sentences.append((sentence, score))
        
        sorted_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)
        summary_sentences = [sent[0] for sent in sorted_sentences[:max_sentences]]
        summary_sentences.sort(key=lambda x: sentences.index(x))
        
        summary = ' '.join(summary_sentences)
        print(f"{Colors.OKGREEN}✨ Generated summary ({len(summary)} characters){Colors.ENDC}")
        return summary
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error during summarization: {str(e)}{Colors.ENDC}")
        return "Failed to generate summary."

def save_content_json(content, output_file):
    """Save content to JSON file"""
    print(f"\n{Colors.OKBLUE}💾 Saving JSON: {output_file}{Colors.ENDC}")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    print(f"{Colors.OKGREEN}✓ JSON saved{Colors.ENDC}")

def save_content_markdown(content, output_file):
    """Save content to Markdown file"""
    print(f"\n{Colors.OKBLUE}📝 Saving Markdown: {output_file}{Colors.ENDC}")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# {content['title']}\n\n")
        f.write(f"URL: {content['metadata']['url']}\n\n")
        f.write(f"Crawled at: {content['metadata']['crawled_at']}\n\n")
        if 'summary' in content:
            f.write(f"## Summary\n\n{content['summary']}\n\n")
        f.write(content['text'])
    print(f"{Colors.OKGREEN}✓ Markdown saved{Colors.ENDC}")

def main():
    print_dark_ascii()
    print(f"{Colors.CYAN}🌙 Dark Mode Web Scraping Tool{Colors.ENDC}")
    print_disclaimer()
    
    print(f"\n{Colors.OKBLUE}📌 Enter URL (or press Enter for default):{Colors.ENDC}")
    user_input = input(f"{Colors.DIM}➡️ {Colors.ENDC}").strip()
    
    url = user_input if user_input else "https://example.com"
    print(f"\n{Colors.CYAN}🔗 URL: {url}{Colors.ENDC}")
    
    content = scrape_content(url)

    if content:
        print(f"\n{Colors.OKBLUE}⚡ Processing content...{Colors.ENDC}")
        summary = summarize_content(content['text'])
        content['summary'] = summary

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("scraped_output", exist_ok=True)
        
        json_file = f"scraped_output/scraped_{timestamp}.json"
        md_file = f"scraped_output/scraped_{timestamp}.md"
        
        save_content_json(content, json_file)
        save_content_markdown(content, md_file)
        
        print(f"\n{Colors.OKGREEN}🎉 Operation complete:{Colors.ENDC}")
        print(f"{Colors.DIM}    📄 JSON: {json_file}")
        print(f"    📝 Markdown: {md_file}{Colors.ENDC}")
    else:
        print(f"\n{Colors.FAIL}❌ Failed to crawl content{Colors.ENDC}")

if __name__ == "__main__":
    main()
