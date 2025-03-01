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

if not api_key:
    print("❌ MISTRAL_API_KEY not found in .env file")
    print("📝 Please add your Mistral API key to .env file:")
    print("MISTRAL_API_KEY=your_api_key_here")
    exit(1)

try:
    client = Mistral(api_key=api_key)
except Exception as e:
    print(f"❌ Error initializing Mistral client: {str(e)}")
    print("⚠️ Please check if your API key is valid")
    exit(1)

def check_robots_txt(url):
    """Check if crawling is allowed by robots.txt"""
    try:
        response = requests.get(url + "/robots.txt")
        response.raise_for_status()
        return "Disallow" not in response.text
    except Exception as e:
        print(f"Error checking robots.txt: {e}")
        return True  # Assume allowed if error

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

    # Stars, forks, watchers
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
    
    # Try article.markdown-body first
    readme = soup.find('article', class_='markdown-body')
    if not readme:
        readme = soup.find('div', class_='Box-body')
    
    if readme:
        print("📖 Extracting README content...")
        
        # Remove unwanted elements
        for unwanted in readme.find_all(['nav', 'footer', 'script', 'style']):
            unwanted.decompose()
        
        # Extract content sequentially maintaining structure
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
        
        print(f"[+] Successfully extracted {len(content)} content blocks from README")
    
    return content

def extract_directory_content(soup):
    """Extract directory listing content"""
    content = []
    
    # Get the file tree
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

    # Parse repository structure from URL
    path_parts = url.replace('https://github.com/', '').split('/')
    if len(path_parts) >= 2:
        content['metadata']['owner'] = path_parts[0]
        content['metadata']['repo'] = path_parts[1]
        content['metadata']['path_type'] = path_parts[2] if len(path_parts) > 2 else 'root'

    # Get repository title
    title_elem = soup.find('strong', {'itemprop': 'name'})
    if not title_elem:
        title_elem = soup.find('h1', class_='d-flex')
    content['title'] = title_elem.text.strip() if title_elem else path_parts[1]
    print(f"📚 Found repository title: {content['title']}")

    # Extract repository data
    repo_data = extract_repository_data(soup)
    content['metadata'].update(repo_data)
    
    # Get repository description
    description = soup.find('p', {'class': 'f4'})
    if description:
        desc_text = description.text.strip()
        content['metadata']['description'] = desc_text
        print(f"📋 Found repository description: {desc_text}")

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

def scrape_content(url):
    """Main function for scraping content from URLs"""
    print(f"\n🔍 Starting to scrape: {url}")
    
    if not check_robots_txt(url):
        print("❌ Crawling disallowed by robots.txt")
        return None

    try:
        print("📡 Fetching page content...")
        response = requests.get(url)
        response.raise_for_status()

        # Handle different content types
        if 'github.com' in url:
            return handle_github_content(url, response)
        
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
        
        # Handle general HTML content
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
        
        print(f"[+] Successfully scraped content:")
        print(f"    - Title: {title}")
        print(f"    - Content length: {len(result['text'])} characters")
        return result

    except Exception as e:
        print(f"[-] Error scraping content: {str(e)}")
        return None

def extract_content_from_element(element):
    """Extract formatted content from HTML elements"""
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

def split_content(content, max_chars=20000):
    """Split content into chunks for summarization"""
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

def summarize_with_mistral(content):
    """Generate content summary using Mistral AI"""
    print("\n🤖 Starting content summarization with Mistral AI...")
    try:
        print(f"📊 Total content length: {len(content)} characters")
        
        if len(content) > 20000:
            print("📎 Content too large, splitting into chunks...")
            chunks = split_content(content)
            print(f"🔄 Split content into {len(chunks)} chunks")
            
            summaries = []
            for i, chunk in enumerate(chunks, 1):
                print(f"\n🔄 Processing chunk {i}/{len(chunks)} ({len(chunk)} characters)")
                try:
                    print(f"⏳ Generating summary for chunk {i}...")
                    response = client.chat.complete(
                        model="mistral-large-latest",
                        messages=[
                            {
                                "role": "user",
                                "content": f"Please summarize the following content concisely:\n\n{chunk}"
                            }
                        ]
                    )
                    chunk_summary = response.choices[0].message.content
                    summaries.append(chunk_summary)
                    print(f"✅ Successfully summarized chunk {i}")
                except Exception as e:
                    print(f"❌ Error summarizing chunk {i}: {str(e)}")
                    summaries.append(f"[Summary failed for chunk {i}]")
            
            if len(summaries) > 1:
                print("\n🔄 Combining chunk summaries...")
                try:
                    failed_chunks = [i+1 for i, s in enumerate(summaries) if "[Summary failed for chunk" in s]
                    if failed_chunks:
                        print(f"⚠️ Note: Chunks {', '.join(map(str, failed_chunks))} failed to summarize")
                    
                    final_summary_prompt = "Please provide a concise overall summary of these summaries:\n\n"
                    final_summary_prompt += "\n\n".join([f"Summary {i+1}:\n{s}" for i, s in enumerate(summaries)])
                    
                    print("⏳ Generating final summary...")
                    response = client.chat.complete(
                        model="mistral-large-latest",
                        messages=[
                            {
                                "role": "user",
                                "content": final_summary_prompt
                            }
                        ]
                    )
                    summary = response.choices[0].message.content
                    print("✨ Final summary generated successfully!")
                except Exception as e:
                    print(f"❌ Error generating final summary: {str(e)}")
                    summary = "⚠️ Failed to generate final summary. Individual chunk summaries:\n\n" + "\n\n".join(summaries)
            else:
                summary = summaries[0]
                if "[Summary failed for chunk" in summary:
                    summary = "⚠️ " + summary
        else:
            response = client.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {
                        "role": "user",
                        "content": f"Please summarize the following content concisely:\n\n{content}"
                    }
                ]
            )
            summary = response.choices[0].message.content
        
        print("[+] Successfully generated summary")
        print(f"[*] Final summary length: {len(summary)} characters")
        return summary
    except Exception as e:
        error_message = str(e)
        print(f"❌ Error with Mistral summarization: {error_message}")
        
        if "api_key" in error_message.lower():
            return "⚠️ AI Summarization failed: Missing or invalid API key. Please check your MISTRAL_API_KEY in .env file."
        elif "timeout" in error_message.lower():
            return "⚠️ AI Summarization failed: Request timed out. Please try again."
        elif "too many requests" in error_message.lower():
            return "⚠️ AI Summarization failed: Rate limit exceeded. Please wait a moment and try again."
        else:
            return f"⚠️ AI Summarization failed: {error_message}"

def save_content_json(content, output_file):
    """Save content to JSON file"""
    print(f"\n💾 Saving content to JSON file: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    print(f"✅ Successfully saved JSON file")

def save_content_markdown(content, output_file):
    """Save content to Markdown file"""
    print(f"\n📝 Saving content to Markdown file: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# {content['title']}\n\n")
        f.write(f"URL: {content['metadata']['url']}\n\n")
        f.write(f"Crawled at: {content['metadata']['crawled_at']}\n\n")
        f.write(f"## Summary\n\n{content['summary']}\n\n")
        f.write(content['text'])
    print(f"✅ Successfully saved Markdown file")

def print_ascii_art():
    """Print ASCII art banner"""
    ascii_art = """
███████╗ ██████╗ ███╗   ███╗██████╗ ██╗████████╗██╗  ██╗ ██████╗ ██╗  ██╗
╚══███╔╝██╔═══██╗████╗ ████║██╔══██╗██║╚══██╔══╝╚██╗██╔╝██╔════╝ ██║  ██║
  ███╔╝ ██║   ██║██╔████╔██║██████╔╝██║   ██║    ╚███╔╝ ███████╗ ███████║
 ███╔╝  ██║   ██║██║╚██╔╝██║██╔══██╗██║   ██║    ██╔██╗ ██╔═══██╗╚════██║
███████╗╚██████╔╝██║ ╚═╝ ██║██████╔╝██║   ██║   ██╔╝ ██╗╚██████╔╝     ██║
╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝      ╚═╝
    """
    print(ascii_art)

def main():
    """Main program entry point"""
    print_ascii_art()
    print("\n🚀 === Web Scraping and Summarization Tool === 🚀")
    
    print("\n📌 Enter GitHub repository URL (or press Enter for default):")
    user_input = input("➡️ ").strip()
    
    repo_url = user_input if user_input else "https://example.com"
    
    raw_url = f"{repo_url}/raw/master/README.md"
    print(f"\n🔗 Repository URL: {repo_url}")
    print(f"[*] Fetching README from: {raw_url}")
    
    content = scrape_content(raw_url)
    if not content or not content.get('text'):
        print("[-] Raw README not found, trying main branch...")
        raw_url = f"{repo_url}/raw/main/README.md"
        content = scrape_content(raw_url)
        
    if not content or not content.get('text'):
        print("[-] Failed to fetch raw README, falling back to repository page...")
        content = scrape_content(repo_url)

    if content:
        print("\n[*] Processing scraped content...")
        summary = summarize_with_mistral(content['text'])
        content['summary'] = summary

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = f"scraped_output/scraped_{timestamp}.json"
        md_file = f"scraped_output/scraped_{timestamp}.md"
        
        os.makedirs("scraped_output", exist_ok=True)
        
        save_content_json(content, json_file)
        save_content_markdown(content, md_file)
        
        print("\n🎉 Operation completed successfully:")
        print(f"    📄 JSON output: {json_file}")
        print(f"    📝 Markdown output: {md_file}")
    else:
        print("\n❌ Failed to crawl content")

if __name__ == "__main__":
    main()
