import asyncio

from datetime import datetime, timezone
from dateutil.parser import parse

from pathlib import Path

from crawlee.beautifulsoup_crawler import BeautifulSoupCrawler, BeautifulSoupCrawlingContext
from crawlee.storages import RequestQueue
from crawlee import EnqueueStrategy
from crawlee import Glob
from crawlee.storages._dataset import Dataset

async def get_og_image_url(soup):
    og_image = soup.find('meta', property='og:image')
    main_image_url = None
    if og_image and og_image['content']:
        main_image_url = og_image['content']
    else:
        # Fallback methods
        main_image = soup.find('img', class_='main-image')
        if main_image and main_image['src']:
            main_image_url = main_image['src']
        else:
            # Additional methods...
            pass
    return main_image_url

async def get_publishing_time(soup):
    date_str = None
    timestamp = None
    meta_tag = soup.find('meta', property='article:published_time')
    if meta_tag and meta_tag.get('content'):
        date_str = meta_tag['content']
    else:
        time_tag = soup.find('time')
        if time_tag:
            # Check if datetime attribute exists
            if time_tag.has_attr('datetime'):
                date_str = time_tag['datetime']
            else:
                date_str = time_tag.get_text(strip=True)
        else:
            # Example: Find an element with class 'post-date' or 'date'
            date_element = soup.find(class_='post-date') or soup.find(class_='date')
            if date_element:
                date_str = date_element.get_text(strip=True)
    if date_str:
        timestamp = parse(date_str, fuzzy=True)        
    return timestamp

async def check_is_article(soup):
    # Check if the page is an article
    og_type = soup.find('meta', property='og:type')
    if og_type and og_type['content'] == 'article':
        return True
    return False

async def check_is_recent(published_at, days=30):
    # Check if the article was published within the last 30 days
    if published_at:
        now = datetime.now(timezone.utc)
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)
        
        delta = now - published_at
        return delta.days < days
    return False

async def init_crawler(
        request_queue,
        include_ulr_glob, 
        max_requests_per_crawl, 
        store,        
        previously_fetched_url        
) -> None:
    
    crawler = BeautifulSoupCrawler(request_provider=request_queue, max_requests_per_crawl=max_requests_per_crawl)
    
    # Define a request handler and attach it to the crawler using the decorator.
    @crawler.router.default_handler
    async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
    
        url = context.request.url
        previously_fetched_fetched = await previously_fetched_url(url)

        if not previously_fetched_fetched:

            context.log.info(f'Fetching : {url}')

            title = context.soup.title.string if context.soup.title else None
            content = context.soup.find('article')
            content = content.get_text(strip=True) if content else None        
            published_at = await get_publishing_time(context.soup)
            og_image = await get_og_image_url(context.soup)
            is_article = await check_is_article(context.soup)
            is_recent = await check_is_recent(published_at)
            
            # Enqueue links from the same domain
            await context.enqueue_links(
                strategy=EnqueueStrategy.SAME_DOMAIN,
                include=[Glob(include_ulr_glob)]
            ) 

            fetched_at = datetime.now(timezone.utc).isoformat()

            ok = is_article and og_image and published_at and is_recent 
            data = {    
                'fetched_at': fetched_at,                           
                'url': url,
                'ok': ok,
                'title': title if ok else None,
                'published_at': published_at if ok else None,
                'og_image': og_image if ok else None,
                'content': content if ok else None
            }
            await store.push_data(data)

    return crawler

async def main():

    sources = [
        { 'name': 'digitalmusicnews', 'base_url': 'https://www.digitalmusicnews.com/category/music-industry/music-tech-news/',  'include_ulr_glob': 'https://**/????/??/??/**' },
        { 'name': 'hypebot', 'base_url': 'https://www.hypebot.com/hypebot/category/music-tech', 'include_ulr_glob': 'https://**/????/??/**' }
    ]
    
    async def previously_fetched_url(url: str) -> bool:
        # Check if the URL was already fetched
        return False

    store = await Dataset.open()

    for source in sources:
        rq = await RequestQueue.open(name=source['name'])
        await rq.add_request(source['base_url'])
        crawler = await init_crawler(
            rq,        
            source['include_ulr_glob'],
            10,
            store,        
            previously_fetched_url        
        )
        await crawler.run()
        #await crawler.export_data(path = 'fetched.csv', content_type = "csv")

    with open("fetched.csv", "a") as output:
        await store.write_to(content_type = "csv", destination=output)

    


if __name__ == '__main__':
    asyncio.run(main())