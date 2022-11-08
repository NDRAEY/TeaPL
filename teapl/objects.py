from typing import Any
from dataclasses import dataclass

try:
    from .tokenizer import Token
except:
    from tokenizer import Token

ver = "1.1"

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
    args: list[Token, ...]
    tokens: list[Token, ...]
    line: int

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
    start: int
    end: int
    line: int

@dataclass
class MathOperationVariable:
    on: Variable
    operation: str
    value: Any

@dataclass
class Loop:
    condition: Comprasion
    body: list[Token, ...]

@dataclass
class Group:
    tokens: list[Token, ...]

@dataclass
class Array:
    tokens: list[Token, ...]

@dataclass
class IndexedValue:
    value: Any
    index: Token

@dataclass
class Return:
    value: Any
