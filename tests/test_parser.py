"""Tests coral parser"""
import ast

import pytest

from xonsh.ast import pprint_ast, Module, Expr, Expression

from coral.parser import Parser, Comment


@pytest.fixture(scope="module")
def parser():
    return Parser()


def nodes_equal(x, y):
    __tracebackhide__ = True
    assert type(x) == type(y), "Ast nodes do not have the same type: '%s' != '%s' " % (
        type(x),
        type(y),
    )
    if isinstance(x, (ast.Expr, ast.FunctionDef, ast.ClassDef)):
        assert (
            x.lineno == y.lineno
        ), "Ast nodes do not have the same line number : %s != %s" % (
            x.lineno,
            y.lineno,
        )
        assert x.col_offset == y.col_offset, (
            "Ast nodes do not have the same column offset number : %s != %s"
            % (x.col_offset, y.col_offset)
        )
    for (xname, xval), (yname, yval) in zip(ast.iter_fields(x), ast.iter_fields(y)):
        assert xname == yname, (
            "Ast nodes fields differ : %s (of type %s) != %s (of type %s)"
            % (xname, type(xval), yname, type(yval))
        )
        assert type(xval) == type(yval), (
            "Ast nodes fields differ : %s (of type %s) != %s (of type %s)"
            % (xname, type(xval), yname, type(yval))
        )
    for xchild, ychild in zip(ast.iter_child_nodes(x), ast.iter_child_nodes(y)):
        assert nodes_equal(xchild, ychild), "Ast node children differs"
    return True


def test_comment(parser):
    obs = parser.parse("# I'm a comment\n")
    exp = Module(
        body=[
            Expr(
                value=Comment(s="# I'm a comment", lineno=1, col_offset=0),
                lineno=1,
                col_offset=0,
            )
        ]
    )
    assert nodes_equal(obs, exp)


def test_inline_comment(parser):
    obs = parser.parse("True  \n# I'm a comment\n", debug_level=0)
    exp = Module(
        body=[
            Expr(
                value=Comment(s="# I'm a comment", lineno=1, col_offset=0),
                lineno=1,
                col_offset=0,
            )
        ]
    )
    assert nodes_equal(obs, exp)
