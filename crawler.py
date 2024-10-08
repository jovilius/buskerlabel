import asyncio, re, io, json
from datetime import datetime, timezone
from urllib.parse import urlparse

from crawlee import EnqueueStrategy, Glob
from crawlee.beautifulsoup_crawler import BeautifulSoupCrawler, BeautifulSoupCrawlingContext
from crawlee.storages import RequestQueue
from crawlee.storages._dataset import Dataset
from crawlee.configuration import Configuration
from dateutil.parser import parse

def extract_dates_from_url(url):
    """
    Extract valid dates from a URL path using the pattern '/yyyy/mm/dd'.

    Args:
        url (str): The URL to extract dates from.

    Returns:
        list: A list of datetime objects found in the URL.
    """
    path = urlparse(url).path
    pattern = r"/(\d{4})/(\d{2})/(\d{2})(?:/|$)"
    dates = []
    for year, month, day in re.findall(pattern, path):
        try:
            dates.append(datetime(int(year), int(month), int(day)))
        except ValueError:
            continue
    return dates

def get_og_tag(soup, tag_name):
    """
    Retrieve the content of an Open Graph meta tag.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object of the page.
        tag_name (str): The Open Graph tag name to retrieve.

    Returns:
        str or None: The content of the Open Graph tag, or None if not found.
    """
    og_tag = soup.find('meta', property=f'og:{tag_name}')
    return og_tag.get('content') if og_tag else None

def get_og_image_url(soup):
    """
    Get the URL of the main image from Open Graph tags or fallback methods.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object of the page.

    Returns:
        str or None: The URL of the main image, or None if not found.
    """
    main_image_url = get_og_tag(soup, 'image')
    if main_image_url:
        return main_image_url
    # Fallback to finding an image with class 'main-image'
    main_image = soup.find('img', class_='main-image')
    if main_image and main_image.get('src'):
        return main_image['src']
    return None

def get_published_time(soup, url):
    """
    Extract the published time of an article from various sources.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object of the page.
        url (str): The URL of the page.

    Returns:
        datetime or None: The published datetime, or None if not found.
    """
    methods = [
        # Method 1: Open Graph 'article:published_time' meta tag
        lambda: get_og_tag(soup, 'article:published_time'),
        # Method 2: Date extracted from URL
        lambda: extract_dates_from_url(url)[0].isoformat() if extract_dates_from_url(url) else None,
        # Method 3: 'datetime' attribute of <time> tag
        lambda: soup.find('time')['datetime'] if soup.find('time') and soup.find('time').has_attr('datetime') else None,
        # Method 4: Text content of <time> tag
        lambda: soup.find('time').get_text(strip=True) if soup.find('time') else None,
        # Method 5: Text content of element with class 'post-date'
        lambda: soup.find(class_='post-date').get_text(strip=True) if soup.find(class_='post-date') else None,
        # Method 6: Text content of element with class 'date'
        lambda: soup.find(class_='date').get_text(strip=True) if soup.find(class_='date') else None,
    ]
    for method in methods:
        timestamp = method()
        if timestamp:
            try:
                return parse(timestamp, fuzzy=True)
            except ValueError:
                continue
    return None

def check_is_article(soup):
    """
    Check if the page is identified as an article based on Open Graph tags.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object of the page.

    Returns:
        bool: True if the page is an article, False otherwise.
    """
    return get_og_tag(soup, 'type') == 'article'

def check_is_recent(published_at, days):
    """
    Determine if the article was published within a certain number of days.

    Args:
        published_at (datetime): The published datetime of the article.
        days (int): The number of days to consider as recent.

    Returns:
        bool: True if the article is recent, False otherwise.
    """
    if published_at:
        now = datetime.now(timezone.utc)
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)
        return (now - published_at).days < days
    return False

def get_content(soup):
    """
    Extract the main content text from the article.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object of the page.

    Returns:
        str or None: The text content of the article, or None if not found.
    """
    # Try to find the <article> tag
    content = soup.find('article')
    if content:
        return content.get_text(strip=True)
    # Fallback to element with id 'article-content'
    content_element = soup.find(id='article-content')
    if content_element:
        return content_element.get_text(strip=True)
    # Fallback to the main <div> with class 'entry-content'
    entry_content = soup.find('div', class_='entry-content')
    if entry_content:
        return entry_content.get_text(strip=True)
    return None

def get_title(soup):
    """
    Extract the title of the article.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object of the page.

    Returns:
        str or None: The title of the article, or None if not found.
    """
    title = soup.title
    return title.string.split('|')[0].strip() if title else None

async def init_crawler(
        request_queue,         
        max_requests_per_crawl, 
        max_days_old,
        store,
        already_crawled_urls : set[str]
):
    """
    Initialize and configure the BeautifulSoupCrawler.

    Args:
        request_queue (RequestQueue): The request queue to use.
        include_url_glob (str): The glob pattern for URLs to include.
        max_requests_per_crawl (int): Maximum number of requests to process.
        store (Dataset): The dataset to store the results.

    Returns:
        BeautifulSoupCrawler: The configured crawler instance.
    """
    crawler = BeautifulSoupCrawler(
        request_provider=request_queue,
        max_requests_per_crawl=max_requests_per_crawl,
    )

    exclude_urls = [Glob(url) for url in already_crawled_urls]

    @crawler.router.default_handler
    async def request_handler(context: BeautifulSoupCrawlingContext):
        """
        Handle each crawled page: extract data, enqueue new links, and store results.

        Args:
            context (BeautifulSoupCrawlingContext): The crawling context.
        """
        url = context.request.url
        context.log.info(f'Crawling: {url}')

        # Extract data from the page
        title = get_title(context.soup)
        content = get_content(context.soup)
        published_at = get_published_time(context.soup, url)
        og_image = get_og_image_url(context.soup)
        is_article = check_is_article(context.soup)
        is_recent = check_is_recent(published_at, max_days_old) 

        # Enqueue new links from the same domain that match the glob pattern
        await context.enqueue_links(
            strategy=EnqueueStrategy.SAME_DOMAIN,
            # include=[Glob(include_url_glob)],                        
            exclude=exclude_urls
        )

        # Store data if it's a recent article
        if is_article and is_recent and title and content and og_image:
            data = {
                'fetched_at': datetime.now(timezone.utc).isoformat(),
                'published_at': published_at.isoformat() if published_at else None,
                'url': url,
                'title': title,
                'image_url': og_image,
                'content': content,
            }
            await store.push_data(data)

    return crawler


async def crawl(already_crawled_urls: set[str]):
    """ 
    Set up and run the crawlers for multiple sources, then export the data.
    """
    sources = [
        {
            'name': 'digitalmusicnews',
            'base_url': 'https://www.digitalmusicnews.com/category/music-industry/music-tech-news/',
            'include_url_glob': 'https://**/????/??/??/**',
        },
        {
            'name': 'hypebot',
            'base_url': 'https://www.hypebot.com/hypebot/category/music-tech',
            'include_url_glob': 'https://www.hypebot.com/**/????/??/**',
        },
        {
            'name': 'techcrunch',
            'base_url': 'https://techcrunch.com/?s=ai+music',
            'include_url_glob': 'https://techcrunch.com/????/??/??/**',
        }
    ]

    #print('Already crawled URLs:')
    #for url in already_crawled_urls:
    #    print(url)
    #print()

    # Get the global configuration
    config = Configuration.get_global_configuration()

    # Disable storage and metadata writing 
    # (because on Vercel we don't have write access)
    config.persist_storage = False   
    config.write_metadata = False 
    
    store = await Dataset.open()

    for source in sources:
        source_name = source['name']
        print(f'Crawling: {source_name} ...')

        # Initialize request queue and add the base URL
        rq = await RequestQueue.open(name=source_name)
        await rq.add_request(source['base_url'])

        # Initialize and run the crawler for the source
        crawler = await init_crawler(
            request_queue = rq,              
            max_requests_per_crawl = 32, 
            max_days_old = 7,
            store = store,
            already_crawled_urls = already_crawled_urls
        )
        await crawler.run()

    fetched_stories_io = io.StringIO()
    await store.write_to(content_type="json", destination=fetched_stories_io)

    fetched_stories_io.seek(0)
    fetched_stories = json.loads(fetched_stories_io.getvalue())
    fetched_stories_io.close()
    return fetched_stories

if __name__ == '__main__':
    asyncio.run(crawl())
