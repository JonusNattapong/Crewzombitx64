import json
import csv
import os
from typing import Dict, List, Any, Optional
import time
from security_manager import SecurityManager
from urllib.parse import urlparse
import aiohttp
import asyncio
import re
import logging

class DataExporter:
    def __init__(self):
        self.session = None
        self.security_manager = SecurityManager()

    async def _get_file_size(self, url: str) -> str:
        """Get file size in human readable format"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            async with self.session.head(url, allow_redirects=True, timeout=5) as response:
                size = int(response.headers.get('content-length', 0))
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024:
                        return f"{size:.1f} {unit}"
                    size /= 1024
                return f"{size:.1f} TB"
        except:
            return "Unknown size"

    def _extract_metadata(self, data: Dict) -> Dict:
        """Extract metadata from JSON-LD"""
        metadata = {}
        json_ld = data.get('content', {}).get('json_ld', [])
        if isinstance(json_ld, list) and json_ld:
            for item in json_ld:
                if '@graph' in item:
                    for node in item['@graph']:
                        if node.get('@type') == 'Article':
                            metadata.update({
                                'title': node.get('headline', ''),
                                'author': node.get('author', {}).get('name', ''),
                                'date_published': node.get('datePublished', ''),
                                'date_modified': node.get('dateModified', ''),
                                'word_count': node.get('wordCount', ''),
                                'section': node.get('articleSection', []),
                                'language': node.get('inLanguage', '')
                            })
                        elif node.get('@type') == 'Organization':
                            metadata['publisher'] = node.get('name', '')
                            
        return metadata

    def _filter_tracking_pixels(self, images: List[Dict]) -> List[Dict]:
        """Filter out tracking pixels and small images"""
        def is_tracking_pixel(img: Dict) -> bool:
            url = img.get('url', '').lower()
            return any(x in url for x in ['facebook.com/tr', 'tracking', 'pixel', 'analytics', 'beacon'])
            
        return [img for img in images if not is_tracking_pixel(img)]

    def _check_export_warnings(self, data: Optional[Dict] = None) -> None:
        """Show GDPR and copyright warnings before exporting data"""
        self.security_manager.show_warning('gdpr')
        self.security_manager.show_warning('copyright')
        
        # Additional checks on data content
        if data:
            # Check if data contains personal information
            if any(key in str(data).lower() for key in ['email', 'phone', 'address', 'name']):
                logging.warning("\n⚠️ This data may contain personal information. Ensure GDPR compliance.")
            
            # Check for potential copyrighted content
            if any(key in str(data).lower() for key in ['copyright', '©', 'all rights reserved']):
                logging.warning("\n⚠️ This content may be copyrighted. Verify usage rights.")

    async def export_to_markdown(self, data: Dict, filename: str) -> str:
        """Export data to Markdown file with improved formatting"""
        self._check_export_warnings(data)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        metadata = self._extract_metadata(data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            # Title
            title = metadata.get('title') or data.get('content', {}).get('title', 'Untitled Page')
            f.write(f"# {title}\n\n")
            
            # Table of Contents
            f.write("## 📑 Table of Contents\n")
            f.write("1. [Meta Information](#meta-information)\n")
            f.write("2. [Summary](#summary)\n")
            if metadata.get('section'): f.write("3. [Tags](#tags)\n")
            f.write("4. [Content](#content)\n")
            f.write("5. [Links](#links)\n")
            if data.get('media', {}).get('images'): f.write("6. [Images](#images)\n")
            if data.get('media', {}).get('videos'): f.write("7. [Videos](#videos)\n")
            if data.get('media', {}).get('documents'): f.write("8. [Documents](#documents)\n")
            f.write("\n")

            # Meta Information
            f.write("## 🔍 Meta Information\n")
            f.write(f"- **URL**: {data.get('url', 'N/A')}\n")
            f.write(f"- **Crawled**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- **Load Time**: {data.get('load_time', 0):.1f} seconds\n")
            f.write(f"- **Word Count**: {metadata.get('word_count', 'N/A')}\n")
            if metadata.get('author'): f.write(f"- **Author**: {metadata['author']}\n")
            if metadata.get('publisher'): f.write(f"- **Publisher**: {metadata['publisher']}\n")
            if metadata.get('date_published'): f.write(f"- **Published**: {metadata['date_published']}\n")
            if metadata.get('date_modified'): f.write(f"- **Last Modified**: {metadata['date_modified']}\n")
            if metadata.get('language'): f.write(f"- **Language**: {metadata['language']}\n")
            f.write("\n")

            # Tags Section
            if metadata.get('section'):
                f.write("## 🏷️ Tags\n")
                for tag in metadata['section']:
                    f.write(f"- {tag}\n")
                f.write("\n")

            # Summary Section
            f.write("## 📊 Summary\n")
            internal_links = [link for link in data.get('links', []) if link.get('type') == 'internal']
            external_links = [link for link in data.get('links', []) if link.get('type') == 'external']
            f.write(f"- **Total Links**: {len(data.get('links', []))}\n")
            f.write(f"  - Internal Links: {len(internal_links)}\n")
            f.write(f"  - External Links: {len(external_links)}\n")
            f.write(f"- **Media**:\n")
            
            # Filter tracking pixels from images
            images = self._filter_tracking_pixels(data.get('media', {}).get('images', []))
            f.write(f"  - Images: {len(images)}\n")
            
            videos = data.get('media', {}).get('videos', [])
            content_videos = [v for v in videos if not any(x in v.get('url', '') for x in ['gtm', 'analytics', 'tracking'])]
            f.write(f"  - Videos: {len(content_videos)}\n")
            
            if 'documents' in data.get('media', {}):
                f.write(f"  - Documents: {len(data.get('media', {}).get('documents', []))}\n")
            f.write("\n")

            # Content Section
            f.write("## 📝 Content\n")
            for content_type, content in data.get('content', {}).items():
                if content and content_type not in ['title', 'author', 'date_published', 'date_modified', 'word_count']:
                    f.write(f"### {content_type.replace('_', ' ').title()}\n")
                    if isinstance(content, (dict, list)):
                        f.write("```json\n")
                        f.write(json.dumps(content, indent=2, ensure_ascii=False))
                        f.write("\n```\n\n")
                    else:
                        f.write(f"{content}\n\n")

            # Links Section
            f.write("## 🔗 Links\n")
            if internal_links:
                f.write("### Internal Links\n")
                sorted_internal = sorted(internal_links, 
                                      key=lambda x: x.get('text', '').strip() or x.get('title', ''))
                for link in sorted_internal:
                    text = link.get('text', '').strip() or link.get('title', '')
                    url = link.get('url', '')
                    f.write(f"- [{text}]({url})\n")
                f.write("\n")
            
            if external_links:
                f.write("### External Links\n")
                for link in sorted(external_links, 
                                 key=lambda x: x.get('text', '').strip() or x.get('title', '')):
                    text = link.get('text', '').strip() or link.get('title', '')
                    url = link.get('url', '')
                    domain = urlparse(url).netloc
                    f.write(f"- [{text}]({url}) `{domain}`\n")
                f.write("\n")

            # Images Section with sizes
            if images:
                f.write("## 🖼️ Images\n")
                for img in images:
                    alt = img.get('alt', '') or img.get('title', '')
                    size = await self._get_file_size(img['url'])
                    f.write(f"![{alt}]({img['url']}) _{size}_\n")
                f.write("\n")

            # Videos Section with types
            if content_videos:
                f.write("## 🎥 Videos\n")
                for video in content_videos:
                    title = video.get('title', '')
                    video_type = video.get('type', 'default')
                    if video_type in ('youtube', 'vimeo'):
                        f.write(f"- 🎬 [{title or 'Video'}]({video['url']}) `{video_type}`\n")
                    else:
                        size = await self._get_file_size(video['url'])
                        f.write(f"- 🎥 [{title or 'Video'}]({video['url']}) _{size}_\n")
                f.write("\n")

            # Documents Section with sizes
            if data.get('media', {}).get('documents'):
                f.write("## 📄 Documents\n")
                for doc in data['media']['documents']:
                    doc_type = doc.get('type', '').upper()
                    text = doc.get('text', '') or 'Document'
                    size = await self._get_file_size(doc['url'])
                    f.write(f"- [{text}]({doc['url']}) `{doc_type}` _{size}_\n")

            # Footer
            crawl_time = data.get('load_time', 0)
            f.write("\n---\n")
            f.write(f"Generated by CrewColabX64 Crawler (Crawl time: {crawl_time:.1f}s)\n")

        if self.session:
            await self.session.close()
            self.session = None

        return filename

    async def export_to_json(self, data: Dict, filename: str, pretty: bool = True) -> str:
        """Export data to JSON file"""
        self._check_export_warnings(data)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
        return filename

    async def export_to_csv(self, data: Dict, filename: str) -> str:
        """Export data to CSV file"""
        self._check_export_warnings(data)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Flatten the data structure
        flattened_data = []
        if isinstance(data, dict):
            flattened_data.append(self._flatten_dict(data))
        elif isinstance(data, list):
            for item in data:
                flattened_data.append(self._flatten_dict(item))

        if flattened_data:
            fieldnames = flattened_data[0].keys()
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flattened_data)
        return filename

    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list):
                if v and isinstance(v[0], dict):
                    # Handle list of dictionaries
                    items.append((new_key, json.dumps(v)))
                else:
                    items.append((new_key, ', '.join(map(str, v))))
            else:
                items.append((new_key, v))
        return dict(items)
