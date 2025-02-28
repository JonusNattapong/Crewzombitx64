import json
import csv
import logging
from typing import Dict
from datetime import datetime
from urllib.parse import urlparse

class DataExporter:
    @staticmethod
    async def export_to_json(data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filename

    @staticmethod
    async def export_to_csv(data, filename):
        flattened_data = DataExporter._flatten_data(data)

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if flattened_data:
                writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                writer.writeheader()
                writer.writerows(flattened_data)
        return filename

    @staticmethod
    async def export_to_markdown(data, filename):
        """Export data to Markdown format."""
        md_content = []
        
        # Handle single page or multiple pages
        if isinstance(data, list):
            for page in data:
                md_content.extend(DataExporter._page_to_markdown(page))
                md_content.append("\n---\n")  # Page separator
        else:
            md_content.extend(DataExporter._page_to_markdown(data))

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))
        return filename

    @staticmethod
    def _page_to_markdown(page):
        md = []
        
        # Header & Meta Information
        title = page.get('content', {}).get('title', urlparse(page.get('url', '')).path.split('/')[-1] or 'Untitled Page')
        md.append(f"# {title}")
        md.append(f"URL: {page.get('url', 'N/A')}")
        timestamp = page.get('timestamp')
        if timestamp:
            crawl_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            md.append(f"Crawled: {crawl_time}")
        md.append("")

        # Summary section
        md.append("## 📊 Summary")
        links_count = len(page.get('links', []))
        internal_links = sum(1 for link in page.get('links', []) if link.get('type') == 'internal')
        external_links = links_count - internal_links
        images_count = len(page.get('media', {}).get('images', []))
        videos_count = len(page.get('media', {}).get('videos', []))
        docs_count = len(page.get('media', {}).get('documents', []))
        
        md.append(f"- Total Links: {links_count}")
        md.append(f"  - Internal Links: {internal_links}")
        md.append(f"  - External Links: {external_links}")
        md.append(f"- Images: {images_count}")
        md.append(f"- Videos: {videos_count}")
        md.append(f"- Documents: {docs_count}")
        md.append("")

        # Content Section
        if 'content' in page:
            md.append("## 📝 Content")
            content = page['content']
            if isinstance(content, dict):
                for key, value in content.items():
                    if key != 'title':  # Skip title as it's already used
                        md.append(f"### {key.replace('_', ' ').title()}")
                        md.append("```json")
                        md.append(json.dumps(value, indent=2, ensure_ascii=False))
                        md.append("```")
                        md.append("")
            else:
                md.append(str(content))
            md.append("")

        # Links Section
        if page.get('links'):
            md.append("## 🔗 Links")
            
            # Internal Links
            internal_links = [link for link in page['links'] if link.get('type') == 'internal']
            if internal_links:
                md.append("### Internal Links")
                for link in internal_links:
                    text = link.get('text', 'No text')
                    url = link.get('url', '#')
                    md.append(f"- [{text}]({url})")
                md.append("")

            # External Links
            external_links = [link for link in page['links'] if link.get('type') == 'external']
            if external_links:
                md.append("### External Links")
                for link in external_links:
                    text = link.get('text', 'No text')
                    url = link.get('url', '#')
                    md.append(f"- [{text}]({url})")
                md.append("")

        # Media Section
        if 'media' in page:
            media = page['media']
            
            # Images
            if media.get('images'):
                md.append("## 🖼️ Images")
                for img in media['images']:
                    alt = img.get('alt', 'No description')
                    url = img.get('url', '')
                    if url:
                        md.append(f"![{alt}]({url})")
                        if img.get('title'):
                            md.append(f"*{img['title']}*")
                md.append("")

            # Videos
            if media.get('videos'):
                md.append("## 🎥 Videos")
                for video in media['videos']:
                    if video.get('type') == 'youtube':
                        md.append(f"- 📺 YouTube: [{video.get('title', 'Video')}]({video.get('url', '')})")
                    elif video.get('type') == 'vimeo':
                        md.append(f"- 🎬 Vimeo: [{video.get('title', 'Video')}]({video.get('url', '')})")
                    else:
                        md.append(f"- 🎥 Video: {video.get('url', '')}")
                md.append("")

            # Documents
            if media.get('documents'):
                md.append("## 📄 Documents")
                for doc in media['documents']:
                    text = doc.get('text', 'Document')
                    url = doc.get('url', '')
                    doc_type = doc.get('type', 'unknown').upper()
                    md.append(f"- [{text}]({url}) ({doc_type})")
                md.append("")

        return md

    @staticmethod
    def _flatten_data(data):
        if isinstance(data, list):
            return [DataExporter._flatten_dict(item) for item in data]
        else:
            return [DataExporter._flatten_dict(data)]

    @staticmethod
    def _flatten_dict(d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k

            if isinstance(v, dict):
                items.extend(DataExporter._flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list):
                if all(isinstance(x, dict) for x in v):
                    for i, item in enumerate(v):
                        items.extend(DataExporter._flatten_dict(item, f"{new_key}{sep}{i}", sep).items())
                else:
                    items.append((new_key, ', '.join(str(x) for x in v)))
            else:
                items.append((new_key, v))
        return dict(items)
