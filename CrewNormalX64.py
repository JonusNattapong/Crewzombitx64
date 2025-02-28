import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import urllib.parse
import os
from nltk.tokenize import sent_tokenize
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def print_ascii_art():
    ascii_art = """
███████╗ ██████╗ ███╗   ███╗██████╗ ██╗████████╗██╗  ██╗ ██████╗ ██╗  ██╗
╚══███╔╝██╔═══██╗████╗ ████║██╔══██╗██║╚══██╔══╝╚██╗██╔╝██╔════╝ ██║  ██║
  ███╔╝ ██║   ██║██╔████╔██║██████╔╝██║   ██║    ╚███╔╝ ███████╗ ███████║
 ███╔╝  ██║   ██║██║╚██╔╝██║██╔══██╗██║   ██║    ██╔██╗ ██╔═══██╗╚════██║
███████╗╚██████╔╝██║ ╚═╝ ██║██████╔╝██║   ██║   ██╔╝ ██╗╚██████╔╝     ██║
╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝      ╚═╝
    """
    print(ascii_art)

def check_robots_txt(url):
    try:
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.netloc:
            # Handle URLs without scheme (e.g., "example.com/page.html")
            parsed_url = urllib.parse.urlparse("http://" + url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        print(f"Parsed URL: {parsed_url}")  # Debug print
        print(f"Robots URL: {robots_url}")  # Debug print
        response = requests.get(robots_url)
        response.raise_for_status()

        # More robust parsing for Disallow directives with wildcards
        for line in response.text.splitlines():
            if line.lower().startswith('user-agent:') and not re.match(r'user-agent:\s*\*.*', line.lower()):
                continue # Skip lines not for our user-agent
            if line.startswith('Disallow:'):
                parts = line.split(': ')
                if len(parts) > 1:
                    disallowed_path = parts[1].strip()
                    # Handle wildcards
                    if '*' in disallowed_path:
                        regex_pattern = disallowed_path.replace('*', '.*')
                        if re.match(regex_pattern, parsed_url.path):
                            return False
                    elif disallowed_path == '/':
                        return False
                    elif parsed_url.path.startswith(disallowed_path):
                        return False
        return True
    except Exception as e:
        print(f"Error checking robots.txt: {str(e)}")
        return True  # Assume allowed if error

def scrape_content(url):
    print(f"\n🔍 Starting to scrape: {url}")
    
    if not check_robots_txt(url):
        print("❌ Crawling disallowed by robots.txt")
        return None

    try:
        print("📡 Fetching page content...")
        response = requests.get(url)
        response.raise_for_status()

        # Check if it's a raw markdown file
        if url.endswith('.md'):
            print("📝 Processing raw markdown content...")
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

        soup = BeautifulSoup(response.text, 'html.parser')

        # Handle GitHub repository pages
        if 'github.com' in url and '/raw/' not in url:
            print("🔍 Detected GitHub repository, parsing specific elements...")
            
            title_elem = soup.find('strong', {'itemprop': 'name'})
            if not title_elem:
                title_elem = soup.find('h1', class_='d-flex')
            title = title_elem.text.strip() if title_elem else "No Title Found"
            print(f"📚 Found repository title: {title}")

            content = []
            
            description = soup.find('p', {'class': 'f4'})
            if description:
                desc_text = description.text.strip()
                content.append(desc_text)
                print(f"📋 Found repository description: {desc_text}")

            readme = soup.find('article', class_='markdown-body')
            
            if readme:
                print("📖 Extracting README content...")
                for unwanted in readme.find_all(['nav', 'footer', 'script', 'style']):
                    unwanted.decompose()
                
                for element in readme.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol']):
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
            else:
                print("[-] No README content found. Trying alternative method...")
                readme_box = soup.find('div', class_='Box-body')
                if readme_box:
                    print("[*] Found README in Box-body")
                    for unwanted in readme_box.find_all(['nav', 'footer', 'script', 'style']):
                        unwanted.decompose()
                    
                    for element in readme_box.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol']):
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

        else:
            print("[*] Processing non-GitHub webpage...")
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
        
        print(f"[+] Successfully scraped content:")
        print(f"    - Title: {title}")
        print(f"    - Content length: {len(result['text'])} characters")
        return result

    except Exception as e:
        print(f"[-] Error scraping content: {str(e)}")
        return None

def extract_content_from_element(element):
    content = []
    for child in element.children:
        if child.name == 'p':
            content.append(extract_text_and_links(child))
        elif child.name in ['h2', 'h3', 'h4', 'h5', 'h6']:
            content.append(f"{'#' * int(child.name[1])} {extract_text_and_links(child)}")
        elif child.name == 'ul':
            content.append(extract_list(child, ordered=False))
        elif child.name == 'ol':
            content.append(extract_list(child, ordered=True))
        elif child.name == 'div':
            content.extend(extract_content_from_element(child))  # Recursively handle divs
        elif child.name == 'pre':
            content.append(f"```\n{child.text.strip()}\n```") # Markdown code block
        elif child.string and child.string.strip():
            content.append(child.string.strip())
    return content

def extract_text_and_links(element):
    text = ''
    for a_tag in element.find_all('a'):
        href = a_tag.get('href')
        link_text = a_tag.text.strip()
        if href:
            a_tag.replace_with(f"[{link_text}]({href})")
        else:
            a_tag.replace_with(link_text)
    text = element.text.strip()
    return text

def extract_list(list_element, ordered=False):
    items = []
    for i, li in enumerate(list_element.find_all('li')):
        list_prefix = f"{i+1}. " if ordered else "* "
        items.append(list_prefix + extract_text_and_links(li))
    return "\n".join(items)

def summarize_content(text, max_sentences=5):
    """Simple text summarization using sentence scoring"""
    print("\n📝 Starting content summarization...")
    try:
        # Split text into sentences
        sentences = sent_tokenize(text)
        
        if len(sentences) <= max_sentences:
            return text
        
        # Score sentences based on their position and length
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = 0
            words = len(sentence.split())
            
            # Favor sentences of moderate length
            if 10 <= words <= 30:
                score += 3
            elif 5 <= words <= 40:
                score += 2
                
            # Favor sentences at the beginning
            if i < len(sentences) * 0.3:
                score += 3
            elif i < len(sentences) * 0.6:
                score += 1
            
            # Favor sentences with important keywords
            important_words = ['important', 'significant', 'key', 'main', 'critical', 'essential']
            for word in important_words:
                if word.lower() in sentence.lower():
                    score += 2
            
            scored_sentences.append((sentence, score))
        
        # Sort sentences by score and select top ones
        sorted_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)
        summary_sentences = [sent[0] for sent in sorted_sentences[:max_sentences]]
        
        # Reorder sentences to maintain original flow
        summary_sentences.sort(key=lambda x: sentences.index(x))
        
        summary = ' '.join(summary_sentences)
        print(f"✅ Generated summary ({len(summary)} characters)")
        return summary
        
    except Exception as e:
        print(f"❌ Error during summarization: {str(e)}")
        return "Failed to generate summary."

def save_content_json(content, output_file):
    print(f"\n💾 Saving content to JSON file: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    print(f"✅ Successfully saved JSON file")

def save_content_markdown(content, output_file):
    print(f"\n📝 Saving content to Markdown file: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# {content['title']}\n\n")
        f.write(f"URL: {content['metadata']['url']}\n\n")
        f.write(f"Crawled at: {content['metadata']['crawled_at']}\n\n")
        if 'summary' in content:
            f.write(f"## Summary\n\n{content['summary']}\n\n")
        f.write(content['text'])
    print(f"✅ Successfully saved Markdown file")

def main():
    print_ascii_art()
    print("\n🚀 === Web Scraping and Summarization Tool === 🚀")
    
    print("\n📌 Enter GitHub repository URL (or press Enter for default):")
    user_input = input("➡️ ").strip()
    
    repo_url = user_input if user_input else "https://example.com"
    
    raw_url = f"{repo_url}/raw/master/README.md"
    print(f"\n🔗 Repository URL: {repo_url}")
    print(f"[*] Fetching README from: {raw_url}")
    
    # First try the raw README URL
    content = scrape_content(raw_url)
    if not content or not content.get('text'):
        print("[-] Raw README not found, trying main branch...")
        raw_url = f"{repo_url}/raw/main/README.md"
        content = scrape_content(raw_url)
        
    # If still no content, fall back to repository page
    if not content or not content.get('text'):
        print("[-] Failed to fetch raw README, falling back to repository page...")
        content = scrape_content(repo_url)

    if content:
        print("\n[*] Processing scraped content...")
        # Create basic summary without API
        summary = summarize_content(content['text'])
        content['summary'] = summary

        # Save content with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure output directory exists
        os.makedirs("scraped_output", exist_ok=True)
        
        json_file = f"scraped_output/scraped_{timestamp}.json"
        md_file = f"scraped_output/scraped_{timestamp}.md"
        
        save_content_json(content, json_file)
        save_content_markdown(content, md_file)
        
        print("\n🎉 Operation completed successfully:")
        print(f"    📄 JSON output: {json_file}")
        print(f"    📝 Markdown output: {md_file}")
    else:
        print("\n❌ Failed to crawl content")

if __name__ == "__main__":
    main()
