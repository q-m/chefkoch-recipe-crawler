#!/usr/bin/env python3
import csv
import json
import os
import re
import sys
from optparse import OptionParser


class Item:
    """Base class for items containing the relevant data we're working with"""
    def __init__(self, data):
        self.data = data

    def to_dict(self):
        return self.data

class Ingredient(Item):
    """A recipe ingredient"""
    def __init__(self, data):
        super().__init__(data)

    def split_amount(self):
        """Split the amount into value and unit"""
        amount = self.data.pop('amount') # pop and re-add to keep the fields together
        value, unit = split_ingredient_amount(amount)
        self.data['amount'] = amount
        self.data['value'] = value
        self.data['unit'] = unit

    def normalize_value(self):
        """Normalize the ingredient value (when present)"""
        if self.data.get('value') is None: return
        self.data['value'] = normalize_value(self.data['value'])

class Preparation(Item):
    """A recipe preparation step"""
    pass

class Recipe(Item):
    """A recipe, the central element here"""
    def __init__(self, data):
        id = re.search(r'/rezepte/(\d+)/', data['url']).group(1)
        super().__init__({ 'id': id, **data })
        # ingredients and preparations have their own model
        self.ingredients = [Ingredient({ 'recipe_id': id, 'index': n+1, **i }) for n,i in enumerate(self.data.pop('ingredients'))]
        self.preparation = [Preparation({ 'recipe_id': id, 'index': n+1, 'text': p }) for n,p in enumerate(self.data.pop('preparation'))]
        # durations and tags are lists we want to squash to a single value
        if self.data.get('durations') is not None:
            self.data['durations'] = ' | '.join([k + ': ' + v for k,v in self.data['durations'].items()])
        if self.data.get('tags') is not None:
            self.data['tags'] = ' | '.join(self.data['tags'])

class CSVWriter:
    """A generic CSV writer for dicts, emitting headers based on the first item seen"""
    def __init__(self, filename):
        self.file = open(filename, 'w', newline='')
        self.writer = None

    def write(self, data):
        if self.writer is None:
            self.writer = csv.DictWriter(self.file, data.keys())
            self.writer.writeheader()
        self.writer.writerow(data)

class RecipeWriter:
    """Writes a recipe to three different CSV files"""
    def __init__(self, output_prefix):
        self.recipes = CSVWriter(output_prefix + '.csv')
        self.ingredients = CSVWriter(output_prefix + '.ingredients.csv')
        self.preparation = CSVWriter(output_prefix + '.preparation.csv')

    def write(self, recipe):
        self.recipes.write(recipe.to_dict())
        for ingredient in recipe.ingredients:
            self.ingredients.write(ingredient.to_dict())
        for preparation in recipe.preparation:
            self.preparation.write(preparation.to_dict())

def process_file(input, output, split_ingredients=False, normalize_values=False):
    """Convert the JSON lines input file to the various CSV files"""
    with open(input, 'r') as infile:
        recipe_writer = RecipeWriter(output)
        for line in infile.readlines():
            recipe = Recipe(json.loads(line))
            for i in recipe.ingredients:
                if split_ingredients: i.split_amount()
                if normalize_values: i.normalize_value()
            recipe_writer.write(recipe)

def main():
    parser = OptionParser(
        usage='usage: %prog [options] inputfile.jsonl',
        description='Convert the JSON Lines file returned from the recipe spider '
                    'into separate CSV files, with additional post-processing.'
    )
    parser.add_option('-o', '--output', dest='output',
                      help='Prefix CSV filenames with PREFIX (default derived from input file)', metavar='PREFIX')
    parser.add_option('-s', '--split-ingredient-amount', dest='split', action='store_true',
                      help='Split ingredient amounts into value and unit')
    parser.add_option('-n', '--normalize-ingredient-value', dest='normalize', action='store_true',
                      help='Normalize ingredient value (only makes sense with --split-ingredient-amount)')
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_usage()
        sys.exit(1)

    input = args[0]
    output = options.output or os.path.splitext(input)[0]

    process_file(input, output, split_ingredients=options.split, normalize_values=options.normalize)


FRACTIONS ={
  '½': 1/2, '⅓': 1/3, '⅕': 1/5, '⅙': 1/6, '⅛': 1/8,
  '⅔': 2/3, '⅖': 2/5, '⅚': 5/6, '⅜': 3/8, '¾': 3/4, '⅗': 3/5,
  '⅝': 5/8, '⅞': 7/8, '⅘': 4/5, '¼': 1/4, '⅐': 1/7, '⅑': 1/9, '⅒': 1/10
}
INGREDIENT_AMOUNT_RE = re.compile('\\s*([0-9]*\\s*[' + ''.join(FRACTIONS.keys()) + ']|[0-9,.]+)\\s*(\\w.*)?$')
VALUE_WITH_FRACTION_RE = re.compile('^([0-9]*)\\s*([' + ''.join(FRACTIONS.keys()) + '])$')

def split_ingredient_amount(s):
    """Return the value and unit for an ingredient amount like '500g' or '½ Stiel/e' etc."""
    # number and optional unit
    m = re.match(INGREDIENT_AMOUNT_RE, s)
    if m: return m.group(1), m.group(2)
    return None, s

def normalize_value(s):
    """Normalize a numerical ingredient amount value"""
    if s is None: return
    s = s.strip()
    s = re.sub(r'^([0-9]+),([0-9]+)$', r'\1.\2', s) # use point as decimal separator - can break with thousand separators (!)
    m = re.match(VALUE_WITH_FRACTION_RE, s)
    if m:
        whole = int(m.group(1)) if m.group(1) != '' else 0
        return whole + FRACTIONS[m.group(2)]
    elif re.match(r'^[0-9]+$', s):
        return int(s)
    elif re.match(r'^[0-9]+\.[0-9]+', s):
        return float(s)
    else:
        return s


if __name__ == '__main__':
    main()