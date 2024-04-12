
BOT_NAME = "recipe"
SPIDER_MODULES = ["recipe.spiders"]
USER_AGENT = "RecipeSpider"

# Pagination links only appear during browsing through the pages, needs depth.
DEPTH_LIMIT = 1000
# Be nice and don't go too fast.
DOWNLOAD_DELAY = 1.4

# No cookies necessary.
COOKIES_ENABLED = False
# Useful for development, and we want to keep the raw sources too.
HTTPCACHE_ENABLED = True
