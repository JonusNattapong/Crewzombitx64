import asyncio
from Crew4lX64.web_crawler import WebCrawler

async def test_urls():
    # Initialize crawler
    crawler = WebCrawler()
    await crawler.setup(
        use_browser=True,  # Using browser for JavaScript rendering
        headless=True,     # Run browser in headless mode
        rate_limit=1.0,    # 1 request per second
        respect_robots=True
    )

    try:
        # URLs to test
        urls = [
            "https://originshq.com/blog/top-ai-llm-learning-resource-in-2025/#ib-toc-anchor-0",
            "https://github.com/amrzv/awesome-colab-notebooks"
        ]

        # Test each URL
        for url in urls:
            print(f"\nTesting URL: {url}")
            result = await crawler.crawl(url, depth=1)
            
            if result:
                print("✅ Successfully crawled")
                print("Content extracted:")
                if 'content' in result:
                    if 'title' in result['content']:
                        print(f"Title: {result['content']['title']}")
                    if 'text' in result['content']:
                        print(f"Text length: {len(result['content']['text'])} characters")
                    if 'meta' in result['content']:
                        print(f"Meta tags found: {len(result['content']['meta'])}")
                
                if 'links' in result:
                    print(f"Links found: {len(result['links'])}")
                
                if 'media' in result:
                    print("Media found:")
                    for media_type, items in result['media'].items():
                        print(f"- {media_type}: {len(items)} items")
            else:
                print("❌ Failed to crawl")
            
            print("-" * 50)

    finally:
        await crawler.close()

if __name__ == "__main__":
    asyncio.run(test_urls())
