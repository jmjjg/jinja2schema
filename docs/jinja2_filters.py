# -*- coding: utf-8 -*-
"""
Use this file to test what really works and doesn't work using jinja2 builtin
filters with different data types.
"""
import inspect

from jinja2 import Template

class Foo:
    attribute = 'value of attribute'

test_types = {
    'bools': [True, False],
    'dicts': [{'attribute': 123, 'other': 'foo'}],
    'lists': [[1, 2, 3], ['a', 'b', 'c']],
    'nones': [None],
    'objects': [Foo()],
    'numbers': [123456, 456.78],
    'strings': ['910', 'foo bar baz qux'],
    'tuples': [(1, 2, 3), ('a', 'b', 'c')],
}

# https://github.com/pallets/jinja/blob/2.11.x/src/jinja2/filters.py
test_filters = [
    # 'abs', # @info: doesn't error on bools
    # 'attr("attribute")', # @info: only wroks for objects
    'batch(3)',
    # 'capitalize',
    #-------------------------------------------------------------------------------------------------------------------
    # 'center(80)',
    # 'count',
    # 'default("")',
    # 'dictsort',
    # 'escape',
    # 'filesizeformat',
    # 'first',
    # 'float(0.0)',
    # 'forceescape',
    # 'format("foo", "bar")',
    # 'groupby("a")',
    # 'indent(width=4, first=False, blank=False, indentfirst=None)',
    # 'int(default=0, base=10)',
    # 'join(d=u"", attribute=None)',
    # 'last',
    # 'length',
    # 'list',
    # 'lower',
    # 'map',
    # 'max',
    # 'min',
    # 'pprint',
    # 'random',
    # 'reject',
    # 'rejectattr',
    # 'replace("foo", "bar", count=None)',
    # 'reverse',
    # 'round(precision=0, method="common")',
    # 'safe',
    # 'select',
    # 'selectattr',
    # 'slice',
    # 'sort',
    # 'string',
    # 'striptags',
    # 'sum',
    # 'title',
    # 'tojson',
    # 'trim',
    # 'truncate(length=255, killwords=False, end="...", leeway=None)',
    # 'unique(case_sensitive=False, attribute=None)',
    # 'upper',
    # 'urlencode',
    # 'urlize(trim_url_limit=None, nofollow=False, target=None, rel=None)',
    # 'wordcount',
    # 'wordwrap(width=79, break_long_words=True, wrapstring=None, break_on_hyphens=True)',
    # 'xmlattr(autospace=True)',
]

for test_filter in test_filters:
    print("=" * 80)
    print("Filter: %s" % test_filter)
    print("=" * 80)
    for test_type, test_values in test_types.items():
        print("\t" + "-" * 72)
        print("\ttype: %s" % test_type)
        print("\t" + "-" * 72)
        for test_value in test_values:
            try:
                template = Template('''{{value|'''+ test_filter +'''}}''')
                rendered = template.render({'value': test_value})
                if str(rendered).startswith('<generator object '):
                    template = Template('''{{value|''' + test_filter + '''|list}}''')
                    rendered = template.render({'value': test_value})
                print("\t\t{} -> {}".format(test_value, rendered))
            except Exception as exc:
                print("\t\tError: %s (%s)" % (str(exc), test_value))