"""Formatting tools for xonsh."""
from ast import NodeVisitor

from coral.parser import parse, add_comments


class Formatter(NodeVisitor):
    """Converts a node into a coral-formatted string."""

    # indent helpers

    base_indent = "    "
    indent = ""
    indent_level = 0

    def inc_indent(self):
        self.indent_level += 1
        self.indent = self.base_indent * self.indent_level

    def dec_indent(self):
        self.indent_level -= 1
        self.indent = self.base_indent * self.indent_level

    # other helpers

    def _func_args(self, args):
        """converts function arguments to a str"""
        rendered = []
        npositional = len(args.args) - len(args.defaults)
        positional_args = args.args[:npositional]
        keyword_args = args.args[npositional:]
        keywordonly_args = args.kwonlyargs
        for arg in positional_args:
            rendered.append(arg.arg)
        for arg, default in zip(keyword_args, args.defaults):
            rendered.append(arg.arg + "=" + self.visit(default))
        if args.vararg is not None:
            rendered.append("*" + args.vararg.arg)
        if keywordonly_args:
            if args.vararg is None:
                rendered.append("*")
            for arg, default in zip(keywordonly_args, args.kw_defaults):
                rendered.append(arg.arg + "=" + self.visit(default))
        return ", ".join(rendered)

    # visitors

    def visit_Module(self, node):
        parts = []
        for n in node.body:
            parts.append(self.visit(n))
        return "\n".join(parts) + "\n"

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_Comment(self, node):
        _, _, comment = node.s.partition('#')
        return '# ' + comment.strip()

    def visit_Str(self, node):
        return '"' + node.s  + '"'

    def visit_Num(self, node):
        return str(node.n)

    def visit_NameConstant(self, node):
        return str(node.value)

    def visit_List(self, node):
        s = "["
        new_elts = []
        for elt in node.elts:
            new_elts.append(self.visit(elt))
        s += ", ".join(new_elts)
        s += "]"
        return s

    def visit_Tuple(self, node):
        if len(node.elts) == 0:
            return "()"
        elif len(node.elts) == 1:
            return "(" + self.visit(node.elts[0]) + ",)"
        s = "("
        new_elts = []
        for elt in node.elts:
            new_elts.append(self.visit(elt))
        s += ", ".join(new_elts)
        s += ")"
        return s

    def visit_Dict(self, node):
        s = "{"
        new_elts = []
        for key, value in zip(node.keys, node.values):
            k = self.visit(key)
            v = self.visit(value)
            new_elts.append(k + ": " + v)
        s += ", ".join(new_elts)
        s += "}"
        return s

    def visit_Set(self, node):
        s = "{"
        new_elts = []
        for elt in node.elts:
            new_elts.append(self.visit(elt))
        s += ", ".join(new_elts)
        s += "}"
        return s

    def visit_Lambda(self, node):
        s = "lambda"
        args = self._func_args(node.args)
        if args:
            s += " " + args
        s += ": " + self.visit(node.body)
        return s


def format(tree):
    """Formats an AST of xonsh code into a nice string"""
    formatter = Formatter()
    s = formatter.visit(tree)
    return s


def reformat(inp, debug_level=0):
    """Reformats xonsh code (str) into a nice string"""
    tree, comments, lines = parse(inp, debug_level=debug_level)
    tree = add_comments(tree, comments, lines)
    return format(tree)
