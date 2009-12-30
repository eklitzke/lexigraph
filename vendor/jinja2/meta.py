# -*- coding: utf-8 -*-
"""
    jinja2.meta
    ~~~~~~~~~~~

    This module implements various functions that exposes information about
    templates that might be interesting for various kinds of applications.

    :copyright: (c) 2009 by the Jinja Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from vendor.jinja2 import nodes
from vendor.jinja2.compiler import CodeGenerator


class TrackingCodeGenerator(CodeGenerator):
    """We abuse the code generator for introspection."""

    def __init__(self, environment):
        CodeGenerator.__init__(self, environment, '<introspection>',
                               '<introspection>')
        self.undeclared_identifiers = set()

    def write(self, x):
        """Don't write."""

    def pull_locals(self, frame):
        """Remember all undeclared identifiers."""
        self.undeclared_identifiers.update(frame.identifiers.undeclared)


def find_undeclared_variables(ast):
    """Returns a set of all variables in the AST that will be looked up from
    the context at runtime.  Because at compile time it's not known which
    variables will be used depending on the path the execution takes at
    runtime, all variables are returned.

    >>> from vendor.jinja2 import Environment, meta
    >>> env = Environment()
    >>> ast = env.parse('{% set foo = 42 %}{{ bar + foo }}')
    >>> meta.find_undeclared_variables(ast)
    set(['bar'])

    .. admonition:: Implementation

       Internally the code generator is used for finding undeclared variables.
       This is good to know because the code generator might raise a
       :exc:`TemplateAssertionError` during compilation and as a matter of
       fact this function can currently raise that exception as well.
    """
    codegen = TrackingCodeGenerator(ast.environment)
    codegen.visit(ast)
    return codegen.undeclared_identifiers


def find_referenced_templates(ast):
    """Finds all the referenced templates from the AST.  This will return an
    iterator over all the hardcoded template extensions, inclusions and
    imports.  If dynamic inheritance or inclusion is used, `None` will be
    yielded.

    >>> from vendor.jinja2 import Environment, meta
    >>> env = Environment()
    >>> ast = env.parse('{% extends "layout.html" %}{% include helper %}')
    >>> list(meta.find_referenced_templates(ast))
    ['layout.html', None]

    This function is useful for dependency tracking.  For example if you want
    to rebuild parts of the website after a layout template has changed.
    """
    for node in ast.find_all((nodes.Extends, nodes.FromImport, nodes.Import,
                              nodes.Include)):
        if isinstance(node.template, nodes.Const) and \
           isinstance(node.template.value, basestring):
            yield node.template.value
        else:
            yield None
