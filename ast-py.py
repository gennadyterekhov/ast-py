#!/usr/bin/env python3
import ast
import json
import math
import os
from pathlib import Path
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


def parse_file(path):
    with tokenize.open(path) as source:
        return json_value(ast.parse(source.read(), filename=path))


def raise_walk_error(error):
    raise error


def parse_directory(path):
    root = Path(path)
    trees = {}
    for directory, dirs, files in os.walk(root, onerror=raise_walk_error):
        dirs.sort()
        for name in sorted(files):
            file = Path(directory) / name
            if file.suffix == ".py" and not file.is_symlink() and file.is_file():
                trees[file.relative_to(root).as_posix()] = parse_file(str(file))
    return trees


def main(args):
    if len(args) != 1:
        print("usage: ast-py FILE|DIR", file=sys.stderr)
        return 2

    path = args[0]
    try:
        tree = parse_directory(path) if os.path.isdir(path) else parse_file(path)
        print(json.dumps(tree, allow_nan=False))
    except SyntaxError as error:
        print(f"{error.filename or path}: {error}", file=sys.stderr)
        return 2
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
