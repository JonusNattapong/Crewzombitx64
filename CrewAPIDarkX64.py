import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
from mistralai import Mistral
from dotenv import load_dotenv

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

# Load API Key from .env
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

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

if not api_key:
    print(f"{Colors.FAIL}❌ MISTRAL_API_KEY not found in .env file{Colors.ENDC}")
    print(f"{Colors.WARNING}📝 Please add your Mistral API key to .env file:{Colors.ENDC}")
    print("MISTRAL_API_KEY=your_api_key_here")
    exit(1)

try:
    client = Mistral(api_key=api_key)
except Exception as e:
    print(f"{Colors.FAIL}❌ Error initializing Mistral client: {str(e)}{Colors.ENDC}")
    print(f"{Colors.WARNING}⚠️ Please check if your API key is valid{Colors.ENDC}")
    exit(1)

def extract_repository_data(soup):
    """Extract metadata about the repository"""
    data = {}
    
    # Languages
    lang_stats = soup.find_all(class_='Progress-item')
    if lang_stats:
        data['languages'] = {}
        for lang in lang_stats:
            name = lang.get('aria-label', '').split()[0]
            percentage = lang.get('style', '').replace('width:', '').replace('%;', '')
            if name and percentage:
                data['languages'][name] = float(percentage)

    # Stats & metadata
    stats = {}
    for link in soup.find_all('a', class_='Link--muted'):
        text = link.text.strip()
        for metric in ['star', 'fork', 'watch']:
            if metric in text.lower():
                stats[metric] = text.split()[0]
    if stats:
        data['stats'] = stats

    # Topics
    topics = soup.find_all('a', {'data-ga-click': 'Topic, repository page'})
    if topics:
        data['topics'] = [topic.text.strip() for topic in topics]

    # Last update
    last_update = soup.find('relative-time')
    if last_update:
        data['last_updated'] = last_update.get('datetime')

    return data

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

def extract_directory_content(soup):
    """Extract directory listing content"""
    content = []
    
    file_tree = soup.find('[role="grid"][aria-labelledby="files"]')
    if file_tree:
        content.append("# Directory Contents\n")
        for row in file_tree.find_all('[role="row"]'):
            link = row.find('a')
            if link:
                name = link.text.strip()
                path = link.get('href', '').strip()
                item_type = "📁 " if row.find('.octicon-file-directory') else "📄 "
                content.append(f"{item_type} {name}")
    
    return '\n'.join(content)

def extract_file_content(soup):
    """Extract file content"""
    code_element = soup.find('table', class_='highlight')
    if code_element:
        return code_element.get_text('\n', strip=True)
    return ""

def scrape_content(url):
    """Main function for scraping content from URLs"""
    print(f"\n{Colors.HEADER}🔍 Starting to scrape: {url}{Colors.ENDC}")

    try:
        print(f"{Colors.OKBLUE}📡 Fetching page content...{Colors.ENDC}")
        response = requests.get(url)
        response.raise_for_status()

        # Handle different content types
        if 'github.com' in url:
            return handle_github_content(url, response)
        
        # Handle raw markdown
        if url.endswith('.md'):
            print(f"{Colors.OKBLUE}📝 Processing markdown content...{Colors.ENDC}")
            content = []
            
            lines = response.text.split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    if line.startswith('#'):
                        content.append(line)
                    elif line.startswith('- ') or line.startswith('* '):
                        content.append(line)
                    else:
                        content.append(line)
            
            return {
                "title": "README.md",
                "text": "\n\n".join(content),
                "metadata": {
                    "url": url,
                    "crawled_at": datetime.now().isoformat()
                }
            }
        
        # Handle general content
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1').text.strip() if soup.find('h1') else "No Title Found"
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
        
        print(f"{Colors.OKGREEN}✨ Successfully scraped content:{Colors.ENDC}")
        print(f"    📑 Title: {title}")
        print(f"    📊 Content length: {len(result['text'])} characters")
        return result

    except Exception as e:
        print(f"{Colors.FAIL}❌ Error scraping content: {str(e)}{Colors.ENDC}")
        return None

def handle_github_content(url, response):
    """Handle content scraping specifically for GitHub repositories"""
    soup = BeautifulSoup(response.text, 'html.parser')
    content = {
        'type': 'github',
        'title': '',
        'text': '',
        'metadata': {
            'url': url,
            'crawled_at': datetime.now().isoformat()
        }
    }

    # Parse repository structure
    path_parts = url.replace('https://github.com/', '').split('/')
    if len(path_parts) >= 2:
        content['metadata'].update({
            'owner': path_parts[0],
            'repo': path_parts[1],
            'path_type': path_parts[2] if len(path_parts) > 2 else 'root'
        })

    # Get title
    title_elem = soup.find('strong', {'itemprop': 'name'}) or soup.find('h1', class_='d-flex')
    content['title'] = title_elem.text.strip() if title_elem else path_parts[1]
    print(f"{Colors.OKBLUE}📚 Found repository: {content['title']}{Colors.ENDC}")

    # Extract metadata
    repo_data = extract_repository_data(soup)
    content['metadata'].update(repo_data)
    
    # Get description
    description = soup.find('p', {'class': 'f4'})
    if description:
        desc_text = description.text.strip()
        content['metadata']['description'] = desc_text
        print(f"{Colors.OKBLUE}📋 Description: {desc_text}{Colors.ENDC}")

    # Extract content based on path type
    if content['metadata']['path_type'] == 'root':
        readme_content = extract_readme_content(soup)
        if readme_content:
            content['text'] = '\n\n'.join(readme_content)
    elif content['metadata']['path_type'] == 'tree':
        content['text'] = extract_directory_content(soup)
    elif content['metadata']['path_type'] == 'blob':
        content['text'] = extract_file_content(soup)
    
    return content

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

def summarize_with_mistral(content):
    """Generate content summary using Mistral AI"""
    print(f"\n{Colors.HEADER}🤖 Starting Mistral AI summarization...{Colors.ENDC}")
    try:
        print(f"{Colors.OKBLUE}📊 Content length: {len(content)} characters{Colors.ENDC}")
        
        if len(content) > 20000:
            print(f"{Colors.OKBLUE}📎 Splitting large content into chunks...{Colors.ENDC}")
            chunks = split_content(content)
            print(f"{Colors.DIM}🔄 Processing {len(chunks)} chunks{Colors.ENDC}")
            
            summaries = []
            for i, chunk in enumerate(chunks, 1):
                print(f"\n{Colors.OKBLUE}⏳ Processing chunk {i}/{len(chunks)}{Colors.ENDC}")
                try:
                    response = client.chat.complete(
                        model="mistral-large-latest",
                        messages=[{"role": "user", "content": f"Please summarize:\n\n{chunk}"}]
                    )
                    chunk_summary = response.choices[0].message.content
                    summaries.append(chunk_summary)
                    print(f"{Colors.OKGREEN}✓ Chunk {i} complete{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.FAIL}❌ Error on chunk {i}: {str(e)}{Colors.ENDC}")
                    summaries.append(f"[Summary failed for chunk {i}]")
            
            if len(summaries) > 1:
                print(f"\n{Colors.OKBLUE}🔄 Combining summaries...{Colors.ENDC}")
                final_prompt = "Please provide a concise overall summary:\n\n"
                final_prompt += "\n\n".join([f"Part {i+1}:\n{s}" for i, s in enumerate(summaries)])
                
                response = client.chat.complete(
                    model="mistral-large-latest",
                    messages=[{"role": "user", "content": final_prompt}]
                )
                summary = response.choices[0].message.content
            else:
                summary = summaries[0]
        else:
            response = client.chat.complete(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": f"Please summarize:\n\n{content}"}]
            )
            summary = response.choices[0].message.content
        
        print(f"{Colors.OKGREEN}✨ Summary generated successfully!{Colors.ENDC}")
        return summary

    except Exception as e:
        error_msg = str(e)
        print(f"{Colors.FAIL}❌ Summarization error: {error_msg}{Colors.ENDC}")
        
        if "api_key" in error_msg.lower():
            return "❌ Invalid API key. Check your MISTRAL_API_KEY in .env file."
        elif "timeout" in error_msg.lower():
            return "❌ Request timed out. Please try again."
        elif "too many requests" in error_msg.lower():
            return "❌ Rate limit exceeded. Please wait and try again."
        else:
            return f"❌ Error: {error_msg}"

def split_content(content, max_chars=20000):
    """Split content into chunks"""
    chunks = []
    current_chunk = []
    current_length = 0
    
    for line in content.split('\n'):
        line_length = len(line)
        if current_length + line_length + 1 <= max_chars:
            current_chunk.append(line)
            current_length += line_length + 1
        else:
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_length = line_length
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

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
    
    raw_url = f"{url}/raw/master/README.md"
    print(f"\n{Colors.CYAN}🔗 URL: {url}{Colors.ENDC}")
    
    # Try different README paths
    content = scrape_content(raw_url)
    if not content or not content.get('text'):
        print(f"{Colors.DIM}↻ Trying main branch...{Colors.ENDC}")
        raw_url = f"{url}/raw/main/README.md"
        content = scrape_content(raw_url)
        
    if not content or not content.get('text'):
        print(f"{Colors.DIM}↻ Trying repository page...{Colors.ENDC}")
        content = scrape_content(url)

    if content:
        print(f"\n{Colors.OKBLUE}⚡ Processing content...{Colors.ENDC}")
        summary = summarize_with_mistral(content['text'])
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
