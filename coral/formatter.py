"""Formatting tools for xonsh."""
import ast

from coral.parser import parse, add_comments


OP_STRINGS = {
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.Div: "/",
    ast.FloorDiv: "//",
    ast.Pow: "**",
    ast.MatMult: "@",
    ast.LShift: "<<",
    ast.RShift: ">>",
    ast.BitAnd: "&",
    ast.BitOr: "|",
    ast.BitXor: "^",
    ast.Or: "or",
    ast.And: "and",
    ast.USub: "-",
    ast.UAdd: "+",
    ast.Invert: "~",
    ast.Not: "not",
}


def op_to_str(op):
    return OP_STRINGS[type(op)]


class Formatter(ast.NodeVisitor):
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
        if args.kwarg is not None:
            rendered.append("**" + args.kwarg.arg)
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

    def visit_Name(self, node):
        return node.id

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

    def visit_BinOp(self, node):
        s = self.visit(node.left) + " "
        s += op_to_str(node.op)
        s += " " + self.visit(node.right)
        return s

    def visit_BoolOp(self, node):
        op = " " + op_to_str(node.op) + " "
        s = op.join(map(self.visit, node.values))
        return s

    def visit_UnaryOp(self, node):
        space = ""
        if isinstance(node.op, ast.Not):
            space = " "
        s = op_to_str(node.op) + space + self.visit(node.operand)
        return s

    def visit_IfExp(self, node):
        s = self.visit(node.body) + " if " + self.visit(node.test)
        s += " else " + self.visit(node.orelse)
        return s

    def _generators(self, node):
        s = ""
        for generator in node.generators:
            s += " for " + self.visit(generator.target)
            s += " in " + self.visit(generator.iter)
            for clause in generator.ifs:
                s += " if " + self.visit(clause)
        return s

    def visit_ListComp(self, node):
        return "[" + self.visit(node.elt) + self._generators(node) + "]"

    def visit_DictComp(self, node):
        s = "{" + self.visit(node.key) + ": " + self.visit(node.value)
        s += self._generators(node) + "}"
        return s

    def visit_SetComp(self, node):
        return "{" + self.visit(node.elt) + self._generators(node) + "}"

    def visit_GeneratorExp(self, node):
        return "(" + self.visit(node.elt) + self._generators(node) + ")"


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
