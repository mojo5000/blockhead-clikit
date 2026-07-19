"""Composable validators. Return True if valid, else an error message string."""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

Validator = Callable[[str], "bool | str"]


def nonempty(value: str) -> bool | str:
    return True if value.strip() else "cannot be empty"


def port_range(value: str) -> bool | str:
    try:
        port = int(value)
    except ValueError:
        return "must be a number"
    return True if 1 <= port <= 65535 else "must be between 1 and 65535"


def path_exists(value: str) -> bool | str:
    return True if Path(value).exists() else "path does not exist"


def regex(pattern: str, message: str) -> Validator:
    compiled = re.compile(pattern)

    def _validate(value: str) -> bool | str:
        return True if compiled.match(value) else message

    return _validate


def one_of(options: list[str]) -> Validator:
    def _validate(value: str) -> bool | str:
        return True if value in options else f"must be one of: {', '.join(options)}"

    return _validate


def chain(*validators: Validator) -> Validator:
    def _validate(value: str) -> bool | str:
        for validator in validators:
            result = validator(value)
            if result is not True:
                return result
        return True

    return _validate
