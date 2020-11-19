import pytest
from jinja2 import nodes

from jinja2schema import config, parse, UnexpectedExpression, InvalidExpression
from jinja2schema.visitors.expr import visit_filter, Context
from jinja2schema.model import Dictionary, Scalar, List, Unknown, String, Number


def get_scalar_context(ast):
    return Context(return_struct_cls=Scalar, predicted_struct=Scalar.from_ast(ast))


def test_string_filters():
    for filter in ('capitalize', 'lower', 'striptags', 'title', 'upper', 'urlize'):
        template = '{{ x|' + filter + ' }}'
        ast = parse(template).find(nodes.Filter)

        ctx = Context(return_struct_cls=Scalar, predicted_struct=Scalar.from_ast(ast))
        rtype, struct = visit_filter(ast, ctx)

        expected_rtype = String(label='x', linenos=[1])
        expected_struct = Dictionary({
            'x': String(label='x', linenos=[1]),
        })
        assert rtype == expected_rtype
        assert struct == expected_struct


def test_batch_and_slice_filters():
    for filter in ('batch', 'slice'):
        template = '{{ items|' + filter + '(3, "&nbsp;") }}'
        ast = parse(template).find(nodes.Filter)

        unknown_ctx = Context(predicted_struct=Unknown.from_ast(ast))
        rtype, struct = visit_filter(ast, unknown_ctx)

        expected_rtype = List(List(Unknown(), linenos=[1]), linenos=[1])
        assert rtype == expected_rtype

        expected_struct = Dictionary({
            'items': List(Unknown(), label='items', linenos=[1]),
        })
        assert struct == expected_struct

        scalar_ctx = Context(predicted_struct=Scalar.from_ast(ast))
        with pytest.raises(UnexpectedExpression) as e:
            visit_filter(ast, scalar_ctx)
        assert str(e.value) == ('conflict on the line 1\n'
                                'got: AST node jinja2.nodes.Filter of structure [[<unknown>]]\n'
                                'expected structure: <scalar>')


def test_default_filter():
    for filter in ('d', 'default'):
        template = '''{{ x|''' + filter + '''('g') }}'''

        ast = parse(template).find(nodes.Filter)
        rtype, struct = visit_filter(ast, get_scalar_context(ast))

        expected_struct = Dictionary({
            'x': String(label='x', linenos=[1], used_with_default=True, value='g'),
        })
        assert struct == expected_struct


def test_filter_chaining():
    template = '''{{ (xs|first|last).gsom|sort|length }}'''
    ast = parse(template).find(nodes.Filter)
    rtype, struct = visit_filter(ast, get_scalar_context(ast))

    expected_struct = Dictionary({
        'xs': List(List(Dictionary({
            'gsom': List(Unknown(), label='gsom', linenos=[1]),
        }, linenos=[1]), linenos=[1]), label='xs', linenos=[1]),
    })
    assert struct == expected_struct

    template = '''{{ x|list|sort|first }}'''
    ast = parse(template).find(nodes.Filter)
    rtype, struct = visit_filter(ast, get_scalar_context(ast))

    expected_struct = Dictionary({
        'x': Scalar(label='x', linenos=[1]),
    })
    assert struct == expected_struct

    template = '''{{ x|first|list }}'''
    ast = parse(template).find(nodes.Filter)
    with pytest.raises(UnexpectedExpression) as e:
        visit_filter(ast, get_scalar_context(ast))
    expected = "conflict on the line 1\n\
got: AST node jinja2.nodes.Filter of structure [<scalar>]\n\
expected structure: <scalar>"
    assert expected == str(e.value)


def test_raise_on_unknown_filter():
    template = '''{{ x|unknownfilter }}'''
    ast = parse(template).find(nodes.Filter)
    with pytest.raises(InvalidExpression) as e:
        visit_filter(ast, get_scalar_context(ast))
    assert 'line 1: unknown filter "unknownfilter"' == str(e.value)

    template = '''{{ x|attr('attr') }}'''
    ast = parse(template).find(nodes.Filter)
    with pytest.raises(InvalidExpression) as e:
        visit_filter(ast, get_scalar_context(ast))
    assert 'line 1: "attr" filter is not supported' == str(e.value)


def test_abs_filter():
    ast = parse('{{ x|abs }}').find(nodes.Filter)
    rtype, struct = visit_filter(ast, get_scalar_context(ast))
    assert rtype == Number(label='x', linenos=[1])
    assert struct == Dictionary({
        'x': Number(label='x', linenos=[1])
    })


def test_int_filter():
    ast = parse('{{ x|int }}').find(nodes.Filter)
    rtype, struct = visit_filter(ast, get_scalar_context(ast))
    assert rtype == Number(label='x', linenos=[1])
    assert struct == Dictionary({
        'x': Scalar(label='x', linenos=[1]),
    })


def test_wordcount_filter():
    ast = parse('{{ x|wordcount }}').find(nodes.Filter)
    rtype, struct = visit_filter(ast, get_scalar_context(ast))
    assert rtype == Number(label='x', linenos=[1])
    assert struct == Dictionary({
        'x': String(label='x', linenos=[1])
    })


def test_join_filter():
    ast = parse('{{ xs|join(separator|default("|")) }}').find(nodes.Filter)
    rtype, struct = visit_filter(ast, get_scalar_context(ast))
    assert rtype == String(label='xs', linenos=[1])
    assert struct == Dictionary({
        'xs': List(String(), label='xs', linenos=[1]),
        'separator': String(label='separator', linenos=[1], used_with_default=True, value='|'),
    })


def test_length_filter():
    for filter in ('count', 'length'):
        template = '{{ xs|' + filter + ' }}'

        ast = parse(template).find(nodes.Filter)
        rtype, struct = visit_filter(ast, get_scalar_context(ast))
        assert rtype == Number(label='xs', linenos=[1])
        assert struct == Dictionary({
            'xs': List(Unknown(), label='xs', linenos=[1]),
        })

def test_max_min_filter():
    for filter in ('max', 'min'):
        template = '{{ values|' + filter + ' }}'
        ast = parse(template).find(nodes.Filter)

        rtype, struct = visit_filter(ast, get_scalar_context(ast))
        assert rtype == Scalar(label='values', linenos=[1])
        assert struct == Dictionary({
            'values': List(Scalar(linenos=[1]), label='values', linenos=[1]),
        })

def test_unique_filter():
    template = '{{ values|unique }}'
    ast = parse(template).find(nodes.Filter)

    unknown_ctx = Context(predicted_struct=Unknown.from_ast(ast))
    rtype, struct = visit_filter(ast, unknown_ctx)
    assert rtype == Unknown(label='values', linenos=[1])
    assert struct == Dictionary({
        'values': List(Unknown(), label='values', linenos=[1]),
    })

def test_reverse_filter():
    template = '{{ x|reverse }}'

    ast = parse(template).find(nodes.Filter)
    rtype, struct = visit_filter(ast, get_scalar_context(ast))

    assert rtype == Unknown(label='x', linenos=[1])
    expected_struct = Dictionary({
        'x': Unknown(label='x', linenos=[1]),
    })
    assert struct == expected_struct

def test_tojson_filter():
    template = '{{ x|tojson }}'

    ast = parse(template).find(nodes.Filter)
    rtype, struct = visit_filter(ast, get_scalar_context(ast))

    assert rtype == String(label='x', linenos=[1])
    expected_struct = Dictionary({
        'x': Unknown(label='x', linenos=[1]),
    })
    assert struct == expected_struct

def test_filesizeformat_filter():
    template = '{{ x|filesizeformat }}'

    ast = parse(template).find(nodes.Filter)
    rtype, struct = visit_filter(ast, get_scalar_context(ast))

    assert rtype == String(label='x', linenos=[1])
    expected_struct = Dictionary({
        'x': Number(label='x', linenos=[1]),
    })
    assert struct == expected_struct

def test_string_filter():
    template = '{{ x|string }}'

    ast = parse(template).find(nodes.Filter)
    rtype, struct = visit_filter(ast, get_scalar_context(ast))

    assert rtype == String(label='x', linenos=[1])
    expected_struct = Dictionary({
        'x': Scalar(label='x', linenos=[1]),
    })
    assert struct == expected_struct

def test_sum_filter():
    template = '{{ x|sum }}'

    ast = parse(template).find(nodes.Filter)
    rtype, struct = visit_filter(ast, get_scalar_context(ast))

    assert rtype == Scalar(label='x', linenos=[1])
    expected_struct = Dictionary({
        'x': List(Scalar(), label='x', linenos=[1]),
    })
    assert struct == expected_struct

def test_pprint_filter():
    template = '{{ x|pprint }}'

    ast = parse(template).find(nodes.Filter)
    rtype, struct = visit_filter(ast, get_scalar_context(ast))

    assert rtype == Scalar(label='x', linenos=[1])
    expected_struct = Dictionary({
        'x': Scalar(label='x', linenos=[1]),
    })
    assert struct == expected_struct

def test_ignore_all_unknown_filter():
    template = '{{ x|foo|bar|baz }}'

    cfg = config.default_config
    cfg.IGNORE_UNKNOWN_FILTERS = True

    ast = parse(template).find(nodes.Filter)
    rtype, struct = visit_filter(ast, get_scalar_context(ast), None, cfg)

    assert rtype == Unknown(label='x', linenos=[1])
    expected_struct = Dictionary({
        'x': Unknown(label='x', linenos=[1]),
    })
    assert struct == expected_struct

def test_ignore_some_unknown_filter():
    cfg = config.default_config
    cfg.IGNORE_UNKNOWN_FILTERS = ('foo', 'bar', 'baz')

    # 1. Check that it works when all the filter names are given
    template = '{{ x|foo|bar|baz }}'
    ast = parse(template).find(nodes.Filter)
    rtype, struct = visit_filter(ast, get_scalar_context(ast), None, cfg)

    assert rtype == Unknown(label='x', linenos=[1])
    expected_struct = Dictionary({
        'x': Unknown(label='x', linenos=[1]),
    })
    assert struct == expected_struct

    # 2. Check that an exception is raised for a filter whose name is not in the list
    template = '{{ x|foo|bar|baz|boz }}'
    ast = parse(template).find(nodes.Filter)
    with pytest.raises(InvalidExpression) as e:
        visit_filter(ast, get_scalar_context(ast), None, cfg)
    assert 'line 1: unknown filter "boz"' == str(e.value)
