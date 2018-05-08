# -*- coding: utf-8 -*-
from lark.lexer import Token

from .version import version


class Compiler:

    """
    Compiles Storyscript abstract syntax tree to JSON.
    """

    @staticmethod
    def path(tree):
        return {'$OBJECT': 'path', 'paths': [tree.child(0).value]}

    @staticmethod
    def string(tree):
        return {'$OBJECT': 'string', 'string': tree.child(0).value[1:-1]}

    @classmethod
    def line(cls, tree):
        """
        Finds the line number of a tree, by finding the first token in the tree
        and returning its line
        """
        for item in tree.children:
            if isinstance(item, Token):
                return str(item.line)
            return cls.line(item)

    @staticmethod
    def assignment(tree):
        return {
            'method': 'set',
            'ln': Compiler.line(tree),
            'container': None,
            'args': [
                Compiler.path(tree.node('path')),
                Compiler.string(tree.child(2).node('string'))
            ],
            'output': None,
            'enter': None,
            'exit': None
        }

    @staticmethod
    def command(tree):
        dictionary = {
            'method': 'run',
            'ln': tree.children[0].line,
            'container': tree.children[0].value,
            'args': None,
            'output': None,
            'enter': None,
            'exit': None
        }
        return dictionary

    @classmethod
    def parse_tree(cls, tree):
        return {}

    @staticmethod
    def compile(tree):
        dictionary = {'script': Compiler.parse_tree(tree), 'version': version}
        return dictionary
