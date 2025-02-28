import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import urllib.parse

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
    if not check_robots_txt(url):
        print("Crawling disallowed by robots.txt")
        return None

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

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
        print(f"Error scraping content: {str(e)}")
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

def save_content_json(content, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)

def save_content_markdown(content, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# {content['title']}\n\n")
        f.write(f"URL: {content['metadata']['url']}\n\n")
        f.write(f"Crawled at: {content['metadata']['crawled_at']}\n\n")
        f.write(content['text'])

def main():
    url = "https://github.com/amrzv/awesome-colab-notebooks/blob/main/data/tutorials.json"
    content = scrape_content(url)

    if content:
        save_content_json(content, "crawled_content1.json")
        save_content_markdown(content, "crawled_content1.md")
        print("Content has been successfully crawled and saved to crawled_content.json and crawled_content.md")
    else:
        print("No content was crawled")

if __name__ == "__main__":
    main()
