#!/usr/bin/env python3
#
# Split the Scrapy cache files into recipes and category pages.
#
import pickle
import re
from pathlib import Path

recipes_file = open('cache_paths_recipes', 'w')
categories_file = open('cache_paths_categories', 'w')

cache = Path('.scrapy/httpcache')
for metapath in cache.glob('**/pickled_meta'):
    meta = pickle.load(metapath.open('rb'))
    url = meta['url']

    if re.search(r'/rs/s\d+/|/rezepte/?$', url):
        categories_file.write(str(metapath.parent) + '\n')
    elif re.search(r'/rezepte/', url):
        recipes_file.write(str(metapath.parent) + '\n')
    else:
        print('Unrecognized cache entry: %s' % url)

print('Created the files cache_paths_recipes and cache_paths_categories.')
print('To create archives with the corresponding cache files, run:')
print('  tar -c -z -f cache_recipes.tar.gz -T cache_paths_recipes')
print('  tar -c -z -f cache_categories.tar.gz -T cache_paths_categories')
