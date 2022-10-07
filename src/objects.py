from typing import Any
from dataclasses import dataclass
from tokenizer import Token

@dataclass
class DefaultVariable:
    pass

@dataclass
class Variable:
    type: str
    name: str
    value: Any

@dataclass
class FunctionCall:
    name: str
    args: list[Token]
    tokens: list[Token]
    line: int

@dataclass
class Function:
    name: str
    return_type: str
    args: str

@dataclass
class Expression:
    tokens: list[Token]
    line: int

@dataclass
class Comprasion:
    what: Expression
    sign: str
    with_: Expression

@dataclass
class Block:
    tokens: list[Token, ...]
    line: int

@dataclass
class MathOperationVariable:
    on: Variable
    operation: str
    value: Any
