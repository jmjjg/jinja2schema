from jinja2 import Template

types = {
    'bools': [True, False],
    'dicts': [{'a': 123, 'b': 'foo'}],
    'lists': [[1, 2, 3], ['a', 'b', 'c']],
    'nones': [None],
    'numbers': [123456, 456.78],
    'strings': ["910", "foo bar baz qux"],
    'tuples': [(1, 2, 3), ('a', 'b', 'c')],
}

# https://github.com/pallets/jinja/blob/2.11.x/src/jinja2/filters.py
filters = [
    'abs',
    # 'attr("a")',
    # 'batch(3)',
    # 'capitalize',
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

for filter in filters:
    print("=" * 80)
    print("Filter: %s" % filter)
    print("=" * 80)
    for type, values in types.items():
        print("\t" + "-" * 72)
        print("\ttype: %s" % type)
        print("\t" + "-" * 72)
        for value in values:
            try:
                template = Template('''{{value|'''+ filter +'''}}''')
                rendered = template.render({'value':value})
                print("\t\t{} -> {}".format(value, rendered))
            except Exception as exc:
                print("\t\tError: %s (%s)" % (str(exc), value))