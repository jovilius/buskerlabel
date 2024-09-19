import asyncio

from datetime import datetime, timezone
from dateutil.parser import parse

import re
from urllib.parse import urlparse
from pathlib import Path

from crawlee.beautifulsoup_crawler import BeautifulSoupCrawler, BeautifulSoupCrawlingContext
from crawlee.storages import RequestQueue
from crawlee import EnqueueStrategy
from crawlee import Glob
from crawlee.storages._dataset import Dataset

def extract_dates_from_url(url):
    # Parse the URL to extract the path
    path = urlparse(url).path
    # Regular expression pattern to match /yyyy/mm/dd
    pattern = r"/(\d{4})/(\d{2})/(\d{2})(?:/|$)"
    # Search for all occurrences that match the date pattern
    matches = re.findall(pattern, path)
    valid_dates = []
    # Iterate over all matches to validate the dates
    for year, month, day in matches:
        try:
            # Attempt to create a datetime object to validate the date
            date_obj = datetime(int(year), int(month), int(day))
            valid_dates.append(date_obj)
        except ValueError:
            continue  # Invalid date, proceed to check the next match

    return valid_dates

def get_og_tag(soup, tag_name):
    property = "og:{}".format(tag_name)
    og_tag = soup.find('meta', property=property)
    og_tag = og_tag['content'] if og_tag else None
    return og_tag 

def get_og_image_url(soup) -> str | None:
    main_image_url = get_og_tag(soup, 'image')
    if not main_image_url:
        # Fallback methods
        main_image = soup.find('img', class_='main-image')
        if main_image and main_image['src']:
            main_image_url = main_image['src']
        else:
            # Additional methods...
            pass
    return main_image_url

def get_published_time(soup, url):   
    timestamp = None
    # Extract the published time from the Open Graph meta tag    
    published_time = get_og_tag(soup,'article:published_time')
    if published_time:
        timestamp = published_time
    else:
        # Extract the date from the URL
        url_dates = extract_dates_from_url(url) 
        url_date = url_dates[0].isoformat() if url_dates else None
        if url_date:
            timestamp = url_date
        else:
            # Find the time tag in the page
            time_tag = soup.find('time')
            if time_tag:
                # Check if datetime attribute exists
                if time_tag.has_attr('datetime'):
                    timestamp = time_tag['datetime']
                else:
                    timestamp = time_tag.get_text(strip=True)
            else:
                # Find an element with class 'post-date' or 'date'
                date_element = soup.find(class_='post-date') or soup.find(class_='date')
                if date_element:
                    timestamp = date_element.get_text(strip=True)            

    if timestamp:
        timestamp = parse(timestamp, fuzzy=True)        
    return timestamp

def check_is_article(soup):
    # Check if the page is an article
    type = get_og_tag(soup, 'type')    
    if type == 'article':
        return True
    return False

def check_is_recent(published_at, days=14):
    # Check if the article was published within the last 30 days
    if published_at:
        now = datetime.now(timezone.utc)
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)
        delta = now - published_at
        return delta.days < days
    return False

def get_content(soup):
    # Find the main content of the article
    content = soup.find('article')
    if content:
        # Extract the text from the content
        content = content.get_text(strip=True)
    else:
        # find the main div with class 'content' or 'main-content'
        content_element = \
            soup.find(id='article-content')
        if content_element:
            content = content_element.get_text(strip=True)

    return content


async def init_crawler(
        request_queue,
        include_ulr_glob, 
        max_requests_per_crawl, 
        store 
) -> None:
    
    crawler = BeautifulSoupCrawler(request_provider=request_queue, max_requests_per_crawl=max_requests_per_crawl)
    
    # Define a request handler and attach it to the crawler using the decorator.
    @crawler.router.default_handler
    async def request_handler(context: BeautifulSoupCrawlingContext) -> None:

        url = context.request.url
        context.log.info(f'Fetching : {url}')

        # Extract the title, content, published time, and main image URL
        title = context.soup.title.string if context.soup.title else None
        content = get_content(context.soup)                
        published_at = get_published_time(context.soup, url)
        og_image = get_og_image_url(context.soup)
        is_article = check_is_article(context.soup)
        is_recent = check_is_recent(published_at)
 
        # Enqueue links from the same domain
        await context.enqueue_links(
            strategy=EnqueueStrategy.SAME_DOMAIN,
            include=[Glob(include_ulr_glob)]          
        ) 

        # Store the fetched data
        fetched_at = datetime.now(timezone.utc).isoformat()

        # Check if the article is valid
        ok = is_article and is_recent

        if ok:
            # Store the data in the dataset
            data = {    
                'fetched_at': fetched_at,                        
                'published_at': published_at,               
                'url': url,
                'title': title,
                'og_image': og_image,
                'content': content
            }
            await store.push_data(data)

    return crawler

async def main():

    sources = [
        { 'name': 'digitalmusicnews', 'base_url': 'https://www.digitalmusicnews.com/category/music-industry/music-tech-news/',  'include_ulr_glob': 'https://**/????/??/??/**' },
        { 'name': 'hypebot', 'base_url': 'https://www.hypebot.com/hypebot/category/music-tech', 'include_ulr_glob': 'https://www.hypebot.com/**/????/??/**' },
        { 'name': 'fortune', 'base_url': 'https://fortune.com/section/tech', 'include_ulr_glob': 'https://fortune.com/**/????/??/??/**' }
    ]
   
    store = await Dataset.open()

    for source in sources:        
        rq = await RequestQueue.open(name=source['name'])
        await rq.add_request(source['base_url'])
        crawler = await init_crawler(
            rq,        
            source['include_ulr_glob'],
            64,
            store       
        )
        await crawler.run()

    with open("fetched.csv", "a") as output:
        await store.write_to(content_type = "csv", destination=output)

if __name__ == '__main__':
    asyncio.run(main())