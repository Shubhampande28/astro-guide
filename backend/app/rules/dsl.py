"""Safe condition DSL for rules (CLAUDE.md 5.2). No `eval`/`exec`.

Conditions are parsed with Python's own `ast.parse(mode="eval")` -- this
only builds a syntax tree, it does not execute anything -- and then that
tree is validated against a strict whitelist of node types and function/
attribute names before being walked by our own interpreter. Anything
outside the whitelist (imports, lambdas, subscripts, arbitrary function
calls, etc.) is rejected at parse time.

Supported syntax: lord(n), house(n), planet(X).sign/.dignity/.retro/
.nakshatra/.navamsa_sign, aspects(X, n), conj(X, Y), dasha.maha,
dasha.antar, transit(X).house, bare planet names (Sun, Moon, ...), string/
int/bool literals, `and`/`or`/`not`, `==`/`!=`/`in`, parentheses.
"""

import ast

from app.rules.context import ChartContext

_PLANET_NAMES = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
_PLANET_ATTRS = {"sign", "dignity", "retro", "nakshatra", "navamsa_sign"}
_DASHA_ATTRS = {"maha", "antar"}
_TRANSIT_ATTRS = {"house"}
_FUNC_NAMES = {"lord", "house", "planet", "aspects", "conj", "transit"}


class DslError(Exception):
    """Raised for both parse-time validation failures and eval-time errors."""


class _HouseRef:
    def __init__(self, house_num: int):
        self.house_num = house_num


class _PlanetRef:
    def __init__(self, planet: str):
        self.planet = planet


class _TransitRef:
    def __init__(self, planet: str):
        self.planet = planet


class _DashaRef:
    pass


def parse(condition: str) -> ast.Expression:
    """Parses and validates a condition string. Raises DslError if unsafe."""
    try:
        tree = ast.parse(condition, mode="eval")
    except SyntaxError as e:
        raise DslError(f"Invalid syntax: {e}") from e
    _validate(tree.body)
    return tree


def _validate(node: ast.AST) -> None:
    if isinstance(node, ast.BoolOp):
        for v in node.values:
            _validate(v)
    elif isinstance(node, ast.UnaryOp):
        if not isinstance(node.op, ast.Not):
            raise DslError("Only 'not' unary operator is allowed")
        _validate(node.operand)
    elif isinstance(node, ast.Compare):
        if len(node.ops) != 1 or len(node.comparators) != 1:
            raise DslError("Chained comparisons are not allowed")
        if not isinstance(node.ops[0], (ast.Eq, ast.NotEq, ast.In)):
            raise DslError("Only ==, !=, and 'in' comparisons are allowed")
        _validate(node.left)
        _validate(node.comparators[0])
    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _FUNC_NAMES:
            raise DslError(f"Unknown function call: {ast.dump(node.func)}")
        if node.keywords:
            raise DslError("Keyword arguments are not allowed")
        for arg in node.args:
            _validate(arg)
    elif isinstance(node, ast.Attribute):
        allowed_attrs = _PLANET_ATTRS | _DASHA_ATTRS | _TRANSIT_ATTRS
        if node.attr not in allowed_attrs:
            raise DslError(f"Unknown attribute: {node.attr}")
        _validate(node.value)
    elif isinstance(node, ast.Name):
        if node.id not in _PLANET_NAMES and node.id != "dasha":
            raise DslError(f"Unknown identifier: {node.id}")
    elif isinstance(node, ast.Constant):
        if not isinstance(node.value, (str, int, bool)):
            raise DslError("Only string, int, and bool literals are allowed")
    else:
        raise DslError(f"Disallowed syntax: {type(node).__name__}")


def evaluate(tree: ast.Expression, ctx: ChartContext) -> bool:
    result = _eval_node(tree.body, ctx)
    if not isinstance(result, bool):
        raise DslError("Condition must evaluate to a boolean")
    return result


def _eval_node(node: ast.AST, ctx: ChartContext):
    if isinstance(node, ast.BoolOp):
        values = [_eval_node(v, ctx) for v in node.values]
        return all(values) if isinstance(node.op, ast.And) else any(values)
    if isinstance(node, ast.UnaryOp):
        return not _eval_node(node.operand, ctx)
    if isinstance(node, ast.Compare):
        left = _eval_node(node.left, ctx)
        right = _eval_node(node.comparators[0], ctx)
        op = node.ops[0]
        if isinstance(op, ast.Eq):
            return left == right
        if isinstance(op, ast.NotEq):
            return left != right
        return _eval_in(left, right, ctx)
    if isinstance(node, ast.Call):
        return _eval_call(node, ctx)
    if isinstance(node, ast.Attribute):
        return _eval_attribute(node, ctx)
    if isinstance(node, ast.Name):
        if node.id == "dasha":
            return _DashaRef()
        return node.id  # bare planet name literal
    if isinstance(node, ast.Constant):
        return node.value
    raise DslError(f"Cannot evaluate: {type(node).__name__}")


def _eval_in(left, right, ctx: ChartContext) -> bool:
    if isinstance(right, _HouseRef):
        if not isinstance(left, str) or left not in _PLANET_NAMES:
            raise DslError("'in house(n)' requires a planet name on the left")
        return ctx.house_of(left) == right.house_num
    raise DslError("'in' is only supported with house(n) on the right")


def _eval_call(node: ast.Call, ctx: ChartContext):
    name = node.func.id
    args = [_eval_node(a, ctx) for a in node.args]

    if name == "lord":
        return ctx.lord_of(_require_int(args[0]))
    if name == "house":
        return _HouseRef(_require_int(args[0]))
    if name == "planet":
        return _PlanetRef(_require_planet(args[0]))
    if name == "transit":
        return _TransitRef(_require_planet(args[0]))
    if name == "aspects":
        return ctx.aspects(_require_planet(args[0]), _require_int(args[1]))
    if name == "conj":
        return ctx.conjunct(_require_planet(args[0]), _require_planet(args[1]))
    raise DslError(f"Unhandled function: {name}")


def _eval_attribute(node: ast.Attribute, ctx: ChartContext):
    target = _eval_node(node.value, ctx)
    attr = node.attr

    if isinstance(target, _PlanetRef):
        if attr not in _PLANET_ATTRS:
            raise DslError(f"Unknown planet attribute: {attr}")
        if attr == "sign":
            return ctx.sign_of(target.planet)
        if attr == "dignity":
            return ctx.dignity_of(target.planet)
        if attr == "retro":
            return ctx.is_retrograde(target.planet)
        if attr == "nakshatra":
            return ctx.nakshatra_of(target.planet)
        return ctx.navamsa_sign_of(target.planet)

    if isinstance(target, _DashaRef):
        if attr not in _DASHA_ATTRS:
            raise DslError(f"Unknown dasha attribute: {attr}")
        return ctx.dasha_maha if attr == "maha" else ctx.dasha_antar

    if isinstance(target, _TransitRef):
        if attr not in _TRANSIT_ATTRS:
            raise DslError(f"Unknown transit attribute: {attr}")
        return ctx.transit_house_of(target.planet)

    raise DslError(f"Cannot access attribute '{attr}' on {type(target).__name__}")


def _require_int(value) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise DslError("Expected an integer argument")
    return value


def _require_planet(value) -> str:
    if not isinstance(value, str) or value not in _PLANET_NAMES:
        raise DslError(f"Expected a planet name, got: {value!r}")
    return value
