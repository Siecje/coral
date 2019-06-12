"""Tests coral parser"""
import ast
from textwrap import dedent
from itertools import zip_longest

import pytest

from xonsh.ast import pdump, pprint_ast, Module, Expr, Expression, NameConstant

from coral.parser import Comment, NodeWithComment, parse, add_comments


def nodes_equal(x, y):
    __tracebackhide__ = True
    assert type(x) == type(y), "Ast nodes do not have the same type: '%s' != '%s'" % (
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
    for xchild, ychild in zip_longest(ast.iter_child_nodes(x), ast.iter_child_nodes(y)):
        assert xchild is not None, "AST node has fewer childern"
        assert ychild is not None, "AST node has more childern"
        assert nodes_equal(xchild, ychild), "Ast node children differs"
    return True


#
# parse tests
#


def test_parse_only_comment():
    tree, comments = parse("# I'm a comment\n")
    assert tree is None
    assert comments == [Comment(s="# I'm a comment", lineno=1, col_offset=0)]


def test_parse_twoline_comment():
    tree, comments = parse("True  \n# I'm a comment\n", debug_level=0)
    exp = Module(body=[Expr(value=NameConstant(value=True), lineno=1, col_offset=0)])
    assert nodes_equal(tree, exp)
    assert comments == [Comment(s="# I'm a comment", lineno=2, col_offset=0)]


def test_parse_inline_comment():
    tree, comments = parse("True  # I'm a comment\n", debug_level=0)
    exp = Module(body=[Expr(value=NameConstant(value=True), lineno=1, col_offset=0)])
    assert nodes_equal(tree, exp)
    assert comments == [Comment(s="# I'm a comment", lineno=1, col_offset=6)]


#
# add_comments() tests
#

def check_add_comments(code, exp_tree, debug_level=0):
    code = dedent(code).lstrip()
    tree, comments = parse(code, debug_level=debug_level)
    tree = add_comments(tree, comments)
    try:
        assert nodes_equal(tree, exp_tree)
    except AssertionError:
        pprint_ast(tree)
        raise
    return tree


def test_add_only_comment():
    code = "# I'm a comment\n"
    exp = Module(body=[Comment(s="# I'm a comment", lineno=1, col_offset=0)])
    check_add_comments(code, exp)


def test_add_twoline_comment():
    code = "True  \n# I'm a comment\n"
    exp = Module(body=[Expr(value=NameConstant(value=True), lineno=1, col_offset=0), Comment(s="# I'm a comment", lineno=2, col_offset=0)])
    check_add_comments(code, exp)


def test_add_inline_comment():
    code = "True  # I'm a comment\n"
    exp = Module(
        body=[
            NodeWithComment(
                node=Expr(value=NameConstant(value=True), lineno=1, col_offset=0),
                comment=Comment(s="# I'm a comment", lineno=1, col_offset=6),
                lineno=1,
                col_offset=0,
            )
        ]
    )
    check_add_comments(code, exp)


def test_add_inline_comment_func():
    code = """
    # comment 1
    def func():  # comment 2
        # comment 3
        True  # comment 4
        # comment 5
    # comment 6
    """
    exp = Module(
        body=[
            Comment(s="# comment 1", lineno=1, col_offset=0),
            NodeWithComment(
                node=Expr(value=NameConstant(value=True), lineno=1, col_offset=0),
                comment=Comment(s="# I'm a comment", lineno=1, col_offset=6),
                lineno=1,
                col_offset=0,
            ),
            Comment(s="# comment 6", lineno=7, col_offset=0),
        ]
    )
    check_add_comments(code, exp)

