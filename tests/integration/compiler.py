# -*- coding: utf-8 -*-
from lark.lexer import Token

from pytest import fixture

from storyscript.compiler import Compiler
from storyscript.parser import Parser


@fixture
def parser():
    return Parser()


def test_compiler_expression_sum(parser):
    """
    Ensures that numbers are compiled correctly
    """
    tree = parser.parse('3 + 2')
    result = Compiler.compile(tree)
    args = [
        {'$OBJECT': 'expression', 'expression': '{} + {}', 'values': [3, 2]}
    ]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_expression_mutation(parser):
    """
    Ensures that mutation expressions are compiled correctly
    """
    tree = parser.parse("'hello' length")
    result = Compiler.compile(tree)
    args = [
        {'$OBJECT': 'string', 'string': 'hello'},
        {'$OBJECT': 'mutation', 'mutation': 'length', 'arguments': []}
    ]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_if(parser):
    tree = parser.parse('if colour == "red"\n\tx = 0')
    result = Compiler.compile(tree)
    args = [
        {'$OBJECT': 'expression', 'expression': '{} == {}',
         'values': [{'$OBJECT': 'path', 'paths': ['colour']},
                    {'$OBJECT': 'string', 'string': 'red'}]}
    ]
    assert result['tree']['1']['method'] == 'if'
    assert result['tree']['1']['args'] == args
    assert result['tree']['1']['enter'] == '2'
    assert result['tree']['2']['parent'] == '1'


def test_compiler_if_elseif(parser):
    source = 'if colour == "red"\n\tx = 0\nelse if colour == "blue"\n\tx = 1'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    args = [
        {'$OBJECT': 'expression', 'expression': '{} == {}',
         'values': [{'$OBJECT': 'path', 'paths': ['colour']},
                    {'$OBJECT': 'string', 'string': 'blue'}]}]
    assert result['tree']['1']['exit'] == '3'
    assert result['tree']['3']['method'] == 'elif'
    assert result['tree']['3']['args'] == args
    assert result['tree']['4']['parent'] == '3'


def test_compiler_foreach(parser):
    tree = parser.parse('foreach items as item\n\tx = 0')
    result = Compiler.compile(tree)
    args = [{'$OBJECT': 'path', 'paths': ['items']}]
    assert result['tree']['1']['method'] == 'for'
    assert result['tree']['1']['output'] == ['item']
    assert result['tree']['1']['args'] == args
    assert result['tree']['1']['enter'] == '2'
    assert result['tree']['2']['parent'] == '1'


def test_compiler_foreach_key_value(parser):
    tree = parser.parse('foreach items as key, value\n\tx = 0')
    result = Compiler.compile(tree)
    assert result['tree']['1']['output'] == ['key', 'value']


def test_compiler_set(parser):
    """
    Ensures that assignments are compiled correctly
    """
    tree = parser.parse('a = 0')
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'set'
    assert result['tree']['1']['args'] == [0]


def test_compiler_set_service(parser):
    """
    Ensures that service assignments are compiled correctly
    """
    tree = parser.parse('a = alpine echo')
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'execute'
    assert result['tree']['1']['name'] == ['a']


def test_compiler_service(parser):
    """
    Ensures that services are compiled correctly
    """
    tree = parser.parse("alpine echo message:'hello'")
    result = Compiler.compile(tree)
    args = [
        {'$OBJECT': 'argument', 'name': 'message', 'argument':
         {'$OBJECT': 'string', 'string': 'hello'}}
    ]
    assert result['tree']['1']['method'] == 'execute'
    assert result['tree']['1']['service'] == 'alpine'
    assert result['tree']['1']['command'] == 'echo'
    assert result['tree']['1']['args'] == args


def test_compiler_function(parser):
    tree = parser.parse('function sum a:int returns int\n\treturn 0')
    result = Compiler.compile(tree)
    args = [{
        '$OBJECT': 'argument',
        'argument': {'$OBJECT': 'type', 'type': 'int'}, 'name': 'a'
    }]
    assert result['tree']['1']['method'] == 'function'
    assert result['tree']['1']['function'] == 'sum'
    assert result['tree']['1']['args'] == args
    assert result['tree']['1']['output'] == ['int']
    assert result['tree']['1']['next'] == '2'
    assert result['tree']['2']['method'] == 'return'
    assert result['tree']['2']['args'] == [0]
    assert result['tree']['2']['parent'] == '1'


def test_compiler_function_call(parser):
    source = 'function sum a:int returns int\n\treturn 0\nsum a:1'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    args = [{'$OBJECT': 'argument', 'name': 'a', 'argument': 1}]
    assert result['tree']['3']['method'] == 'call'
    assert result['tree']['3']['service'] == 'sum'
    assert result['tree']['3']['args'] == args