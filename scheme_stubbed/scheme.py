"""A Scheme interpreter and its read-eval-print loop."""
from __future__ import print_function  # Python 2 compatibility

import sys
import os

from scheme_builtins import *
from scheme_reader import *
from ucb import main, trace


SPECIAL_FORMS = dict()

##############
# Eval/Apply #
##############

def scheme_eval(expr, env, show_info=True): # Optional third argument is ignored
    """Evaluate Scheme expression EXPR in environment ENV.

    >>> expr = read_line('(+ 2 2)')
    >>> expr
    Pair('+', Pair(2, Pair(2, nil)))
    >>> scheme_eval(expr, create_global_frame())
    4
    """
    if not isinstance(expr, Pair):
        return env.lookup(expr)
    return scheme_apply(scheme_eval(expr.first, env), expr.rest, env)


def scheme_apply(procedure, args, env):
    """Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    environment ENV."""
    if not isinstance(procedure, SpecialForm):
        args = args.map(lambda expr:scheme_eval(expr, env))
    stack = [[procedure, args, env]]
    result = None

    while len(stack) != 0:
        procedure, args, env = stack[-1]
        stack = stack[:-1]
        try:
            result = procedure.apply(args, env, stack)
        except AttributeError as err:
            raise SchemeError(err)
    return result

def insert_pair(body, env, stack):
    procedure, args = scheme_eval(body.first, env), body.rest
    if not isinstance(procedure, SpecialForm):
        args = args.map(lambda expr:scheme_eval(expr, env))
    stack.append([procedure, args, env])



################
# Environments #
################

class Frame(object):
    """An environment frame binds Scheme symbols to Scheme values."""
    def __init__(self, parent):
        """An empty frame with parent frame PARENT (which may be None)."""
        self.parent = parent
        self.bindings = dict()

    def __repr__(self):
        if self.parent is None:
            return '<Global Frame>'
        s = sorted(['{0}: {1}'.format(k, v) for k, v in self.bindings.items()])
        return '<{{{0}}} -> {1}>'.format(', '.join(s), repr(self.parent))

    def define(self, symbol, value):
        """Define Scheme SYMBOL to have VALUE."""
        if not isinstance(symbol, str):
            raise SchemeError('illegal name.')
        self.bindings[symbol] = value
        return symbol

    # BEGIN PROBLEM 2/3
    "*** YOUR CODE HERE ***"
    def lookup(self, name):
        try:
            if name in SPECIAL_FORMS:
                return SPECIAL_FORMS[name]
        except TypeError:
            pass
        if not isinstance(name, str):
            return name
        if name in self.bindings:
            return self.bindings[name]
        if self.parent is None:
            raise SchemeError('name "{}" was not defined'.format(name))
        else:
            return self.parent.lookup(name)
    # END PROBLEM 2/3

##############
# Procedures #
##############

class Procedure(object):
    """The supertype of all Scheme procedures."""

def scheme_procedurep(x):
    return isinstance(x, Procedure)

class BuiltinProcedure(Procedure):
    """A Scheme procedure defined as a Python function."""

    def __init__(self, fn, use_env=False, name='builtin'):
        self.name = name
        self.fn = fn
        self.use_env = use_env

    def __str__(self):
        return '#[{0}]'.format(self.name)

    def apply(self, args, env, stack = None):
        """Apply SELF to ARGS in ENV, where ARGS is a Scheme list.

        >>> env = create_global_frame()
        >>> plus = env.bindings['+']
        >>> twos = Pair(2, Pair(2, nil))
        >>> plus.apply(twos, env)
        4
        """
        # BEGIN PROBLEM 2
        "*** YOUR CODE HERE ***"
        lst = []
        while args != nil:
            lst.append(args.first)
            args = args.rest
        try:
            if self.use_env:
                lst.append(env)
            return self.fn(*lst)
        except TypeError:
            raise SchemeError('type error')
        # END PROBLEM 2


class LambdaProcedure(Procedure):
    """A procedure defined by a lambda expression or a define form."""

    def __init__(self, formals, body, env):
        """A procedure with formal parameter list FORMALS (a Scheme list),
        whose body is the Scheme list BODY, and whose parent environment
        starts with Frame ENV."""
        self.formals = formals
        self.body = body
        self.env = env

    def __str__(self):
        return str(Pair('lambda', Pair(self.formals, self.body)))

    def __repr__(self):
        return 'LambdaProcedure({0}, {1}, {2})'.format(
            repr(self.formals), repr(self.body), repr(self.env))
    
    def apply(self, args, env, stack = None, use_current_env = False):
        if len(args) != len(self.formals):
            raise SchemeError('requires {0} argument(s) but gets {1}'.format(len(self.formals), len(self.args)))
        if use_current_env:
            env = Frame(env)
        else:
            env = Frame(self.env)
        
        para, arg = self.formals, args
        while para != nil:
            env.define(para.first, arg.first)
            para, arg = para.rest, arg.rest
        
        body = self.body
        while body.rest != nil:
            scheme_eval(body.first, env)
            body = body.rest
        
        # tail recursion
        if True:
            if isinstance(body.first, Pair):
                return insert_pair(body.first, env, stack)
        return scheme_eval(body.first, env)

def add_builtins(frame, funcs_and_names):
    """Enter bindings in FUNCS_AND_NAMES into FRAME, an environment frame,
    as built-in procedures. Each item in FUNCS_AND_NAMES has the form
    (NAME, PYTHON-FUNCTION, INTERNAL-NAME)."""
    for name, fn, proc_name in funcs_and_names:
        frame.define(name, BuiltinProcedure(fn, name=proc_name))

#################
# Special Forms #
#################

"""
How you implement special forms is up to you. We recommend you encapsulate the
logic for each special form separately somehow, which you can do here.
"""

class SpecialForm(Procedure):

    def __init__(self, fn, name='special form'):
        self.name = name
        self.fn = fn

    def __str__(self):
        return '#[{0}]'.format(self.name)

    def apply(self, args, env, stack = None):
        return self.fn(args, env, stack)

class MacroProcedure(SpecialForm):

    def __init__(self, formals, body, env, name = 'macro'):
        self.formals = formals
        self.body = body
        self.env = env
        self.name = name

    def apply(self, args, env, stack = None):
        if len(args) != len(self.formals):
            raise SchemeError('arguments number error')
        
        bindings = dict()
        formals = self.formals
        while args != nil:
            bindings[formals.first] = args.first
            formals, args = formals.rest, args.rest
        
        def replace(pair):
            if pair == nil:
                return nil
            elif not isinstance(pair, Pair):
                if pair in bindings:
                    return Pair('quote', Pair(bindings[pair], nil))
                else:
                    return pair
            return Pair(replace(pair.first), replace(pair.rest))
        
        body = replace(self.body).map(lambda expr:scheme_eval(expr, env))
        return scheme_begin(body, env, stack)

def special_form(name):
    def add(fn):
        SPECIAL_FORMS[name] = SpecialForm(fn, name)
        return fn
    return add

def check_argument(args, req):
    if not req(len(args)):
        raise SchemeError('get {} arguments'.format(len(args)))

@special_form("define")
def scheme_define(args, env, stack):
    check_argument(args, lambda x:x>=2)

    symbol = args.first
    if isinstance(symbol, Pair):
        fn = scheme_lambda(Pair(args.first.rest, args.rest), env, stack)
        return env.define(args.first.first, fn)
    value = scheme_eval(args.rest.first, env)
    return env.define(symbol, value)

@special_form("define-macro")
def scheme_define_macro(args, env, stack):
    check_argument(args, lambda x:x>=2)
    
    symbol = args.first
    fn = MacroProcedure(args.first.rest, args.rest, env, args.first.first)
    return env.define(args.first.first, fn)

@special_form("quote")
def scheme_quote(args, env, stack):
    check_argument(args, lambda x:x==1)

    symbol = args.first
    return symbol

@special_form("quasiquote")
def scheme_quasiquote(args, env, stack):
    check_argument(args, lambda x:x==1)
    
    symbol = args.first
    if isinstance(symbol, Pair):
        if symbol.first == 'unquote':
            return scheme_unquote(symbol.rest, env, stack, True)
        return symbol.map(lambda expr:scheme_quasiquote(Pair(expr, nil), env, stack))
    return symbol

@special_form("unquote")
def scheme_unquote(args, env, stack, inside_quasiquote = False):
    check_argument(args, lambda x:x==1)
    
    if not inside_quasiquote:
        raise SchemeError('unquote outside of a quasiquote')
    symbol = args.first
    return scheme_eval(symbol, env)

@special_form("begin")
def scheme_begin(args, env, stack):
    while args.rest != nil:
        scheme_eval(args.first, env)
        args = args.rest
    
    if isinstance(args.first, Pair):
        return insert_pair(args.first, env, stack)
    return scheme_eval(args.first, env)

@special_form("lambda")
def scheme_lambda(args, env, stack):
    check_argument(args, lambda x:x>=2)
    
    formals, body = args.first, args.rest
    return LambdaProcedure(formals, body, env)

@special_form("mu")
def scheme_mu(args, env, stack):
    check_argument(args, lambda x:x>=2)
    
    formals, body = args.first, args.rest
    return MuProcedure(formals, body)

@special_form("if")
def scheme_if(args, env, stack):
    check_argument(args, lambda x:x==3)
    
    cond, suite, alter = args.first, args.rest.first, args.rest.rest.first
    if is_true_primitive(scheme_eval(cond, env)):
        if isinstance(suite, Pair):
            return insert_pair(suite, env, stack)
        else:
            return scheme_eval(suite, env)
    else:
        if isinstance(alter, Pair):
            return insert_pair(alter, env, stack)
        else:
            return scheme_eval(alter, env)

@special_form("cond")
def scheme_cond(args, env, stack):
    if len(args) == 0:
        return None
    
    term = args.first
    check_argument(term, lambda x:x>=1)
    
    if term.first == 'else':
        return scheme_begin(Pair(True, term.rest), env, stack)

    val = scheme_eval(term.first, env)
    if is_true_primitive(val):
        if len(term.rest) == 0:
            return val
        return scheme_begin(term.rest, env, stack)
    else:
        return scheme_cond(args.rest, env, stack)

@special_form("and")
def scheme_and(args, env, stack):
    if args == nil:
        return True
    while args.rest != nil:
        val = scheme_eval(args.first, env)
        if is_false_primitive(val):
            return val
        args = args.rest
    if isinstance(args.first, Pair):
        return insert_pair(args.first, env, stack)
    else:
        return scheme_eval(args.first, env)

@special_form("or")
def scheme_or(args, env, stack):
    if args == nil:
        return False
    while args.rest != nil:
        val = scheme_eval(args.first, env)
        if is_true_primitive(val):
            return val
        args = args.rest
    if isinstance(args.first, Pair):
        return insert_pair(args.first, env, stack)
    else:
        return scheme_eval(args.first, env)

@special_form("let")
def scheme_let(args, env, stack):
    check_argument(args, lambda x:x>=2)
    bindings, body = args.first, args.rest
    my_frame = Frame(env)

    while len(bindings) != 0:
        binding = bindings.first
        bindings = bindings.rest
        check_argument(binding, lambda x:x==2)
        name, value = binding.first, scheme_eval(binding.rest.first, env)
        my_frame.define(name, value)
    
    return scheme_begin(body, my_frame, stack)


# Utility methods for checking the structure of Scheme programs

def validate_form(expr, min, max=float('inf')):
    """Check EXPR is a proper list whose length is at least MIN and no more
    than MAX (default: no maximum). Raises a SchemeError if this is not the
    case.

    >>> validate_form(read_line('(a b)'), 2)
    """
    if not scheme_listp(expr):
        raise SchemeError('badly formed expression: ' + repl_str(expr))
    length = len(expr)
    if length < min:
        raise SchemeError('too few operands in form')
    elif length > max:
        raise SchemeError('too many operands in form')

def validate_formals(formals):
    """Check that FORMALS is a valid parameter list, a Scheme list of symbols
    in which each symbol is distinct. Raise a SchemeError if the list of
    formals is not a list of symbols or if any symbol is repeated.

    >>> validate_formals(read_line('(a b c)'))
    """
    symbols = set()
    def validate_and_add(symbol, is_last):
        if not scheme_symbolp(symbol):
            raise SchemeError('non-symbol: {0}'.format(symbol))
        if symbol in symbols:
            raise SchemeError('duplicate symbol: {0}'.format(symbol))
        symbols.add(symbol)

    while isinstance(formals, Pair):
        validate_and_add(formals.first, formals.rest is nil)
        formals = formals.rest

    # here for compatibility with DOTS_ARE_CONS
    if formals != nil:
        validate_and_add(formals, True)

def validate_procedure(procedure):
    """Check that PROCEDURE is a valid Scheme procedure."""
    if not scheme_procedurep(procedure):
        raise SchemeError('{0} is not callable: {1}'.format(
            type(procedure).__name__.lower(), repl_str(procedure)))

#################
# Dynamic Scope #
#################

class MuProcedure(LambdaProcedure):
    """A procedure defined by a mu expression, which has dynamic scope.
     _________________
    < Scheme is cool! >
     -----------------
            \   ^__^
             \  (oo)\_______
                (__)\       )\/\
                    ||----w |
                    ||     ||
    """

    def __init__(self, formals, body):
        """A procedure with formal parameter list FORMALS (a Scheme list) and
        Scheme list BODY as its definition."""
        self.formals = formals
        self.body = body


    def __str__(self):
        return str(Pair('mu', Pair(self.formals, self.body)))

    def __repr__(self):
        return 'MuProcedure({0}, {1})'.format(
            repr(self.formals), repr(self.body))
    
    def apply(self, args, env, stack, use_current_env = True):
        return LambdaProcedure.apply(self, args, env, stack, use_current_env)


##################
# Tail Recursion #
##################

# Make classes/functions for creating tail recursive programs here?

def complete_apply(procedure, args, env):
    """Apply procedure to args in env; ensure the result is not a Thunk.
    Right now it just calls scheme_apply, but you will need to change this
    if you attempt the extra credit."""
    val = scheme_apply(procedure, args.map(lambda expr: Pair('quote', Pair(expr, nil))), env)
    # Add stuff here?
    return val



####################
# Extra Procedures #
####################

def scheme_map(fn, s, env):
    validate_type(fn, scheme_procedurep, 0, 'map')
    validate_type(s, scheme_listp, 1, 'map')
    return s.map(lambda x: complete_apply(fn, Pair(x, nil), env))

def scheme_filter(fn, s, env):
    validate_type(fn, scheme_procedurep, 0, 'filter')
    validate_type(s, scheme_listp, 1, 'filter')
    head, current = nil, nil
    while s is not nil:
        item, s = s.first, s.rest
        if complete_apply(fn, Pair(item, nil), env):
            if head is nil:
                head = Pair(item, nil)
                current = head
            else:
                current.rest = Pair(item, nil)
                current = current.rest
    return head

def scheme_reduce(fn, s, env):
    validate_type(fn, scheme_procedurep, 0, 'reduce')
    validate_type(s, lambda x: x is not nil, 1, 'reduce')
    validate_type(s, scheme_listp, 1, 'reduce')
    value, s = s.first, s.rest
    while s is not nil:
        value = complete_apply(fn, scheme_list(value, s.first), env)
        s = s.rest
    return value

################
# Input/Output #
################

def read_eval_print_loop(next_line, env, interactive=False, quiet=False,
                         startup=False, load_files=()):
    """Read and evaluate input until an end of file or keyboard interrupt."""
    if startup:
        for filename in load_files:
            scheme_load(filename, True, env)
    while True:
        try:
            src = next_line()
            while src.more_on_line:
                expression = scheme_read(src)
                result = scheme_eval(expression, env)
                if not quiet and result is not None:
                    print(repl_str(result))
        except (SchemeError, SyntaxError, ValueError, RuntimeError) as err:
            if (isinstance(err, RuntimeError) and
                'maximum recursion depth exceeded' not in getattr(err, 'args')[0]):
                raise
            elif isinstance(err, RuntimeError):
                print('Error: maximum recursion depth exceeded')
            else:
                print('Error:', err)
        except KeyboardInterrupt:  # <Control>-C
            if not startup:
                raise
            print()
            print('KeyboardInterrupt')
            if not interactive:
                return
        except EOFError:  # <Control>-D, etc.
            print()
            return

def scheme_load(*args):
    """Load a Scheme source file. ARGS should be of the form (SYM, ENV) or
    (SYM, QUIET, ENV). The file named SYM is loaded into environment ENV,
    with verbosity determined by QUIET (default true)."""
    if not (2 <= len(args) <= 3):
        expressions = args[:-1]
        raise SchemeError('"load" given incorrect number of arguments: '
                          '{0}'.format(len(expressions)))
    sym = args[0]
    quiet = args[1] if len(args) > 2 else True
    env = args[-1]
    if (scheme_stringp(sym)):
        sym = eval(sym)
    validate_type(sym, scheme_symbolp, 0, 'load')
    with scheme_open(sym) as infile:
        lines = infile.readlines()
    args = (lines, None) if quiet else (lines,)
    def next_line():
        return buffer_lines(*args)

    read_eval_print_loop(next_line, env, quiet=quiet)

def scheme_open(filename):
    """If either FILENAME or FILENAME.scm is the name of a valid file,
    return a Python file opened to it. Otherwise, raise an error."""
    try:
        return open(filename)
    except IOError as exc:
        if filename.endswith('.scm'):
            raise SchemeError(str(exc))
    try:
        return open(filename + '.scm')
    except IOError as exc:
        raise SchemeError(str(exc))

def create_global_frame():
    """Initialize and return a single-frame environment with built-in names."""
    env = Frame(None)
    env.define('eval',
               BuiltinProcedure(scheme_eval, True, 'eval'))
    env.define('apply',
               BuiltinProcedure(complete_apply, True, 'apply'))
    env.define('load',
               BuiltinProcedure(scheme_load, True, 'load'))
    env.define('procedure?',
               BuiltinProcedure(scheme_procedurep, False, 'procedure?'))
    env.define('map',
               BuiltinProcedure(scheme_map, True, 'map'))
    env.define('filter',
               BuiltinProcedure(scheme_filter, True, 'filter'))
    env.define('reduce',
               BuiltinProcedure(scheme_reduce, True, 'reduce'))
    env.define('undefined', None)
    add_builtins(env, BUILTINS)
    return env

@main
def run(*argv):
    import argparse
    parser = argparse.ArgumentParser(description='CS 61A Scheme Interpreter')
    parser.add_argument('--pillow-turtle', action='store_true',
                        help='run with pillow-based turtle. This is much faster for rendering but there is no GUI')
    parser.add_argument('--turtle-save-path', default=None,
                        help='save the image to this location when done')
    parser.add_argument('-load', '-i', action='store_true',
                       help='run file interactively')
    parser.add_argument('file', nargs='?',
                        type=argparse.FileType('r'), default=None,
                        help='Scheme file to run')
    args = parser.parse_args()

    import scheme
    scheme.TK_TURTLE = not args.pillow_turtle
    scheme.TURTLE_SAVE_PATH = args.turtle_save_path
    sys.path.insert(0, '')
    sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(scheme.__file__))))

    next_line = buffer_input
    interactive = True
    load_files = []

    if args.file is not None:
        if args.load:
            load_files.append(getattr(args.file, 'name'))
        else:
            lines = args.file.readlines()
            def next_line():
                return buffer_lines(lines)
            interactive = False

    read_eval_print_loop(next_line, create_global_frame(), startup=True,
                         interactive=interactive, load_files=load_files)
    tscheme_exitonclick()