import builtins

import pytest

from xonsh.ast import pdump, pprint_ast

from coral.formatter import reformat

from tools import nodes_equal


@pytest.mark.parametrize("inp, exp", [
("#a bad comment\n", "# a bad comment\n"),
("'single quotes'", '"single quotes"'),
("True", "True"),
("None\n", "None\n"),
("42\n", "42\n"),
("42.84\n", "42.84\n"),
("42E+84\n", "4.2e+85\n"),
("[]\n", "[]\n"),
("()\n", "()\n"),
("{}\n", "{}\n"),
])
def test_formatting(inp, exp):
    execer =  builtins.__xonsh__.execer
    # first check that we get what we expect
    try:
        obs = reformat(inp)
    except TypeError:
        print("Formatter failed!")
        pprint_ast(execer.parse(inp, {}))
        raise
    assert exp == obs, "Bad Tree:\n" + pdump(execer.parse(inp, {}))
    # next check that the transformation is stable
    obs2 = reformat(obs)
    assert obs == obs2
    # last, check that the initial AST is the same as the AST we produced
    # using the normal xonsh parser, barring line & column numbers
    exp_tree = execer.parse(exp, {})
    obs_tree = execer.parse(obs, {})
    assert nodes_equal(exp_tree, obs_tree, check_attributes=False)



