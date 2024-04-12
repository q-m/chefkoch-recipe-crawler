# Spider for recipes from chefkoch.de

A spider to crawl recipe data from [chefkoch.de](https://www.chefkoch.de).

Note that PLUS recipes, for which an account is needed, are not included.

## Setup

Requires: [Python 3](https://www.python.org/) (tested with Python 3.12.3).

```
pip install -r requirements.txt
```

## Develop

You can look at the output of a single recipe with the help of `scrapy parse`:

```
scrapy parse -c parse_recipe https://www.chefkoch.de/rezepte/4291431709202820/Spargel-Walnuss-Pesto.html
```

To view what pages would be traversed, you can use the `_parse` callback
(though this could change when [CrawlSpider](https://docs.scrapy.org/en/latest/topics/spiders.html#crawlspider)
internals are changed):

```
scrapy parse -c _parse https://www.chefkoch.de/rezepte/
```


## Run

```
scrapy crawl chefkoch -o recipes.jsonl 2>&1 | \
  grep --line-buffered -v "^{'url'" | \
  tee recipes.log
```

Note that this will take a bit more than a week to run.
Data is saved in the [JSON Lines](https://jsonlines.org/) file `recipes.jsonl`, and the logs
are saved to `recipes.log` (relevant for checking errors).

All requests and responses are cached in `.scrapy/httpcache/`. If you want to work on fresh
data, which is then fetched all anew from the website again, remove that directory.


## Transform

To obtain data in CSV format instead of JSON Lines, the processing script can be ran:

```
python process.py -s -n recipes.jsonl
```

This results three CSV files `recipes.csv`, `recipes-ingredients.csv` and `recipes-preparation.csv`.

The `-s` option enables the transformation of ingredient amounts into value and unit.
To get an idea of all occuring amounts, the following command can be useful:

```
cat recipes.jsonl | jq -r -s '.[].ingredients[].amount' | sort | uniq -c | sort -nr
```

### Lookup source HTML

If you want to lookup the source HTML for a specific recipe, take its `url_fingerprint`
and locate its file in `.scrapy/httpcache/chefkoch` like this:

```bash
# assumes the bash shell
fingerprint=0123456789abcdef0123456789abcdef01234567
cat .scrapy/httpcache/chefkoch/${fp:0:2}/${fp}/response_body | gunzip
```


## Notes

* On the [all recipes page](https://www.chefkoch.de/rs/s0/Rezepte.html) you can find a total number of recipes.
* As this spider omits the PLUS recipes, the collected number will be lower.
* The number of pages per search filter is limited, so we cannot just crawl the unfiltered index.


## License

This software is distributed under the [MIT license](LICENSE).
Note that this applies to the software only, not to the data gathered from the recipe website.
