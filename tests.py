import unittest

from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from dateutil.parser import parse

from crawler import (
    extract_dates_from_url,
    get_og_tag,
    get_og_image_url,
    get_published_time,
    check_is_article,
    check_is_recent,
    get_content,
)

class TestHelpers(unittest.TestCase):
    def test_extract_dates_from_url(self):
        # Test with a valid date in the URL
        url = 'https://example.com/2023/09/15/article-title'
        dates = extract_dates_from_url(url)
        self.assertEqual(len(dates), 1)
        self.assertEqual(dates[0], datetime(2023, 9, 15))

        # Test with multiple valid dates in the URL
        url = 'https://example.com/2023/09/15/article-title'
        dates = extract_dates_from_url(url)
        self.assertEqual(len(dates), 1)
        self.assertEqual(dates[0], datetime(2023, 9, 15)) 

        # Test with an invalid date in the URL
        url = 'https://example.com/2023/02/30/article-title'
        dates = extract_dates_from_url(url)
        self.assertEqual(len(dates), 0)

        # Test with no date in the URL
        url = 'https://example.com/article-title'
        dates = extract_dates_from_url(url)
        self.assertEqual(len(dates), 0)

    def test_get_og_tag(self):
        html = '''
        <html>
            <head>
                <meta property="og:title" content="Test Title">
                <meta property="og:type" content="article">
            </head>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        self.assertEqual(get_og_tag(soup, 'title'), 'Test Title')
        self.assertEqual(get_og_tag(soup, 'type'), 'article')
        self.assertIsNone(get_og_tag(soup, 'description'))

    def test_get_og_image_url(self):
        # Test with 'og:image' meta tag present
        html = '''
        <html>
            <head>
                <meta property="og:image" content="https://example.com/image.jpg">
            </head>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        self.assertEqual(get_og_image_url(soup), 'https://example.com/image.jpg')

        # Test with fallback to image with class 'main-image'
        html = '''
        <html>
            <body>
                <img class="main-image" src="https://example.com/main-image.jpg">
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        self.assertEqual(get_og_image_url(soup), 'https://example.com/main-image.jpg')

        # Test with no image available
        html = '<html></html>'
        soup = BeautifulSoup(html, 'html.parser')
        self.assertIsNone(get_og_image_url(soup))

    def test_get_published_time(self):
        # Test with 'og:article:published_time' meta tag
        html = '''
        <html>
            <head>
                <meta property="og:article:published_time" content="2023-09-15T12:34:56Z">
            </head>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        url = 'https://example.com/article'
        published_time = get_published_time(soup, url)
        expected_time = parse('2023-09-15T12:34:56Z', fuzzy=True)
        self.assertEqual(published_time, expected_time)

        # Test with date extracted from URL
        html = '<html></html>'
        soup = BeautifulSoup(html, 'html.parser')
        url = 'https://example.com/2023/09/15/article'
        published_time = get_published_time(soup, url)
        expected_time = datetime(2023, 9, 15)
        self.assertEqual(published_time.date(), expected_time.date())

        # Test with <time datetime=""> tag
        html = '''
        <html>
            <body>
                <time datetime="2023-09-15T12:34:56Z"></time>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        url = 'https://example.com/article'
        published_time = get_published_time(soup, url)
        expected_time = parse('2023-09-15T12:34:56Z', fuzzy=True)
        self.assertEqual(published_time, expected_time)

        # Test with text inside <time> tag
        html = '''
        <html>
            <body>
                <time>September 15, 2023</time>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        published_time = get_published_time(soup, url)
        expected_time = parse('September 15, 2023', fuzzy=True)
        self.assertEqual(published_time.date(), expected_time.date())

        # Test with class 'post-date'
        html = '''
        <html>
            <body>
                <div class="post-date">September 15, 2023</div>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        published_time = get_published_time(soup, url)
        expected_time = parse('September 15, 2023', fuzzy=True)
        self.assertEqual(published_time.date(), expected_time.date())

        # Test with no date available
        html = '<html></html>'
        soup = BeautifulSoup(html, 'html.parser')
        published_time = get_published_time(soup, url)
        self.assertIsNone(published_time)

    def test_check_is_article(self):
        # Test when 'og:type' is 'article'
        html = '''
        <html>
            <head>
                <meta property="og:type" content="article">
            </head>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        self.assertTrue(check_is_article(soup))

        # Test when 'og:type' is not 'article'
        html = '''
        <html>
            <head>
                <meta property="og:type" content="website">
            </head>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        self.assertFalse(check_is_article(soup))

        # Test when 'og:type' is missing
        html = '<html></html>'
        soup = BeautifulSoup(html, 'html.parser')
        self.assertFalse(check_is_article(soup))

    def test_check_is_recent(self):
        # Test with a recent date
        published_at = datetime.now(timezone.utc) - timedelta(days=5)
        self.assertTrue(check_is_recent(published_at, days=14))

        # Test with an old date
        published_at = datetime.now(timezone.utc) - timedelta(days=30)
        self.assertFalse(check_is_recent(published_at, days=14))

        # Test with no date provided
        self.assertFalse(check_is_recent(None))

    def test_get_content(self):
        # Test with <article> tag present
        html = '''
        <html>
            <body>
                <article>
                    <p>This is the content.</p>
                </article>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        content = get_content(soup)
        self.assertEqual(content, 'This is the content.')

        # Test with element having id 'article-content'
        html = '''
        <html>
            <body>
                <div id="article-content">
                    <p>This is the content.</p>
                </div>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        content = get_content(soup)
        self.assertEqual(content, 'This is the content.')

        # Test with no content available
        html = '<html></html>'
        soup = BeautifulSoup(html, 'html.parser')
        content = get_content(soup)
        self.assertIsNone(content)

if __name__ == '__main__':
    unittest.main()
