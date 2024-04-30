import re
import w3lib.html

def text(s):
    """Clean up text from page"""
    if not s: return None
    s = w3lib.html.remove_tags(s)
    s = re.sub(r'\s+', ' ', s) # squash whitespace
    return s.strip()

def html(s):
    """Clean up HTML from page"""
    if not s: return None
    # omit outer element
    s = re.sub(r'^\s*<[^>]+>(.*)<\/[^>]+>\s*$', r'\1', s, flags=re.DOTALL)
    return s.strip()

def strip_hash(url):
    """Strip any hash from the URL given"""
    if not url: return None
    url = re.sub(r'#.*$', '', url)
    return url

def strip_qs(url):
    """Strip any hash from the URL given"""
    if not url: return None
    url = re.sub(r'\?.*$', '', url)
    return url

def strip_hash_qs(url):
    """Strip any hash and querystring from the URL given"""
    if not url: return None
    return strip_qs(strip_hash(url))

# based on https://github.com/scrapy/scrapy/issues/3613#issuecomment-473443247
def apply_priority(priority):
    """Return a function to apply a priority to existing request, useful for CrawlSpider rules"""
    def process_request(request, spider):
        return request.replace(priority=priority)
    return process_request
