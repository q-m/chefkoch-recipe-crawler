
BOT_NAME = "recipe"
SPIDER_MODULES = ["recipe.spiders"]
USER_AGENT = "RecipeSpider"

# Pagination links only appear during browsing through the pages, needs depth.
DEPTH_LIMIT = 200
# Be nice and don't go too fast.
DOWNLOAD_DELAY = 1.2

# No cookies necessary.
COOKIES_ENABLED = False
# Useful for development, and we want to keep the raw sources too.
HTTPCACHE_ENABLED = True
# Speedup when crawling from cache (at the expense of memory use)
CONCURRENT_ITEMS = 1500
REACTOR_THREADPOOL_MAXSIZE = 50
