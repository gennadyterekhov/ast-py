#!/usr/bin/env python3
import ast
import json
import math
import sys
import tokenize


def json_value(value):
    if isinstance(value, ast.AST):
        return {
            "_type": type(value).__name__,
            **{name: json_value(item) for name, item in vars(value).items()},
        }
    if isinstance(value, list):
        return [json_value(item) for item in value]
    if isinstance(value, bytes):
        return {"_type": "bytes", "hex": value.hex()}
    if isinstance(value, complex):
        return {
            "_type": "complex",
            "real": json_value(value.real),
            "imag": json_value(value.imag),
        }
    if isinstance(value, float) and not math.isfinite(value):
        return {"_type": "float", "value": repr(value)}
    if value is Ellipsis:
        return {"_type": "ellipsis"}
    return value


def main(args):
    if len(args) != 1:
        print("usage: ast-py FILE", file=sys.stderr)
        return 2

    path = args[0]
    try:
        with tokenize.open(path) as source:
            tree = ast.parse(source.read(), filename=path)
        print(json.dumps(json_value(tree), allow_nan=False))
    except (OSError, SyntaxError, UnicodeError, ValueError) as error:
        print(error, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
