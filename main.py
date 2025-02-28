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
    print(f"\n[*] Starting to scrape: {url}")
    
    if not check_robots_txt(url):
        print("[-] Crawling disallowed by robots.txt")
        return None

    try:
        print("[*] Fetching page content...")
        response = requests.get(url)
        response.raise_for_status()

        # Check if it's a raw markdown file
        if url.endswith('.md'):
            print("[*] Processing raw markdown content...")
            content = []
            
            # Split the content into lines and process
            lines = response.text.split('\n')
            for line in lines:
                line = line.strip()
                if line:  # Skip empty lines
                    # Handle headers
                    if line.startswith('#'):
                        content.append(line)
                    # Handle lists
                    elif line.startswith('- ') or line.startswith('* '):
                        content.append(line)
                    # Handle everything else
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

        # Handle HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Handle GitHub repository pages
        if 'github.com' in url and '/raw/' not in url:
            print("[*] Detected GitHub repository, parsing specific elements...")
            
            # Get repository title
            title_elem = soup.find('strong', {'itemprop': 'name'})
            if not title_elem:
                title_elem = soup.find('h1', class_='d-flex')
            title = title_elem.text.strip() if title_elem else "No Title Found"
            print(f"[+] Found repository title: {title}")

            # Get repository content
            content = []
            
            # Get repository description
            description = soup.find('p', {'class': 'f4'})
            if description:
                desc_text = description.text.strip()
                content.append(desc_text)
                print(f"[+] Found repository description: {desc_text}")

            # Get README content from the article directly
            readme = soup.find('article', class_='markdown-body')
            
            if readme:
                print("[*] Extracting README content...")
                
                # Remove unwanted elements
                for unwanted in readme.find_all(['nav', 'footer', 'script', 'style']):
                    unwanted.decompose()
                
                # Extract content sequentially maintaining structure
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
                
                print(f"[+] Successfully extracted {len(content)} content blocks from README")
            else:
                print("[-] No README content found. Trying alternative method...")
                
                # Try finding the README content in the Box-body
                readme_box = soup.find('div', class_='Box-body')
                if readme_box:
                    print("[*] Found README in Box-body")
                    
                    # Remove unwanted elements
                    for unwanted in readme_box.find_all(['nav', 'footer', 'script', 'style']):
                        unwanted.decompose()
                    
                    # Extract meaningful content
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
                    
                    print(f"[+] Successfully extracted {len(content)} content blocks from Box-body")

        else:
            print("[*] Processing non-GitHub webpage...")
            # Handle other websites as before
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
def split_content(content, max_chars=20000):
    """Split content into chunks of max_chars, breaking at newlines when possible."""
    chunks = []
    current_chunk = []
    current_length = 0
    
    for line in content.split('\n'):
        line_length = len(line)
        
        if current_length + line_length + 1 <= max_chars:  # +1 for newline
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
    print("\n[*] Starting content summarization with Mistral AI...")
    try:
        print(f"[*] Total content length: {len(content)} characters")
        
        # Split content into chunks if it's too large
        if len(content) > 20000:
            print("[*] Content too large, splitting into chunks...")
            chunks = split_content(content)
            print(f"[*] Split content into {len(chunks)} chunks")
            
            # Summarize each chunk
            summaries = []
            for i, chunk in enumerate(chunks, 1):
                print(f"\n[*] Processing chunk {i}/{len(chunks)} ({len(chunk)} characters)")
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
            
            # If we have multiple summaries, combine them
            if len(summaries) > 1:
                print("\n[*] Combining chunk summaries...")
                final_summary_prompt = "Please provide a concise overall summary of these summaries:\n\n"
                final_summary_prompt += "\n\n".join([f"Summary {i+1}:\n{s}" for i, s in enumerate(summaries)])
                
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
            else:
                summary = summaries[0]
        else:
            # For smaller content, summarize directly
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
        print(f"[-] Error with Mistral summarization: {str(e)}")
        return "AI Summarization failed."

# ฟังก์ชันในการบันทึกข้อมูลในรูปแบบ JSON
def save_content_json(content, output_file):
    print(f"\n[*] Saving content to JSON file: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    print(f"[+] Successfully saved JSON file")

# ฟังก์ชันในการบันทึกข้อมูลในรูปแบบ Markdown
def save_content_markdown(content, output_file):
    print(f"\n[*] Saving content to Markdown file: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# {content['title']}\n\n")
        f.write(f"URL: {content['metadata']['url']}\n\n")
        f.write(f"Crawled at: {content['metadata']['crawled_at']}\n\n")
        f.write(f"## Summary\n\n{content['summary']}\n\n")
        f.write(content['text'])
    print(f"[+] Successfully saved Markdown file")

# ฟังก์ชันหลัก
def main():
    print("\n=== Web Scraping and Summarization Tool ===")
    repo_url = "https://github.com/amrzv/awesome-colab-notebooks"
    raw_url = f"{repo_url}/raw/master/README.md"
    print(f"\n[*] Repository URL: {repo_url}")
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
        # Summarize content using Mistral API
        summary = summarize_with_mistral(content['text'])

        # Add summary to content
        content['summary'] = summary

        # Save content in JSON and Markdown formats
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = f"scraped_output/scraped_{timestamp}.json"
        md_file = f"scraped_output/scraped_{timestamp}.md"
        
        # Ensure output directory exists
        os.makedirs("scraped_output", exist_ok=True)
        
        save_content_json(content, json_file)
        save_content_markdown(content, md_file)
        
        print("\n[+] Operation completed successfully:")
        print(f"    - JSON output: {json_file}")
        print(f"    - Markdown output: {md_file}")
    else:
        print("\n[-] Failed to crawl content")

if __name__ == "__main__":
    main()
