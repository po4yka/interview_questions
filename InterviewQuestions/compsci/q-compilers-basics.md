---
id: cs-comp-basics
title: Compilers - Basics and Type Systems
topic: compilers
difficulty: hard
tags:
- cs_compilers
- type_systems
anki_cards:
- slug: cs-comp-0-en
  language: en
  anki_id: 1769160677774
  synced_at: '2026-01-23T13:31:19.030190'
- slug: cs-comp-0-ru
  language: ru
  anki_id: 1769160677799
  synced_at: '2026-01-23T13:31:19.031710'
- slug: cs-comp-1-en
  language: en
  anki_id: 1769160677826
  synced_at: '2026-01-23T13:31:19.032858'
- slug: cs-comp-1-ru
  language: ru
  anki_id: 1769160677849
  synced_at: '2026-01-23T13:31:19.033993'
- slug: cs-comp-2-en
  language: en
  anki_id: 1769160677874
  synced_at: '2026-01-23T13:31:19.035099'
- slug: cs-comp-2-ru
  language: ru
  anki_id: 1769160677899
  synced_at: '2026-01-23T13:31:19.036387'
---
# Compilers and Type Systems

## Compilation Phases

```
Source Code
    |
    v
[Lexical Analysis] -> Tokens
    |
    v
[Syntax Analysis] -> AST
    |
    v
[Semantic Analysis] -> Annotated AST
    |
    v
[Intermediate Code] -> IR
    |
    v
[Optimization]
    |
    v
[Code Generation] -> Machine Code
```

## Lexical Analysis (Scanning)

Convert source text to tokens.

```
Input:  "if (x > 5) { return x; }"

Tokens:
  IF
  LPAREN
  IDENTIFIER("x")
  GT
  NUMBER(5)
  RPAREN
  LBRACE
  RETURN
  IDENTIFIER("x")
  SEMICOLON
  RBRACE
```

**Tools**: Regular expressions, finite automata.

```python
import re

TOKEN_PATTERNS = [
    ('NUMBER', r'\d+'),
    ('IDENTIFIER', r'[a-zA-Z_]\w*'),
    ('PLUS', r'\+'),
    ('EQUALS', r'='),
    ('WHITESPACE', r'\s+'),
]

def tokenize(code):
    tokens = []
    while code:
        for name, pattern in TOKEN_PATTERNS:
            match = re.match(pattern, code)
            if match:
                if name != 'WHITESPACE':
                    tokens.append((name, match.group()))
                code = code[match.end():]
                break
    return tokens
```

## Syntax Analysis (Parsing)

Build Abstract Syntax Tree (AST) from tokens.

### Context-Free Grammars

```
expr   -> term (('+' | '-') term)*
term   -> factor (('*' | '/') factor)*
factor -> NUMBER | '(' expr ')'
```

### Parsing Techniques

**Top-down (LL)**:
- Start from grammar start symbol
- Recursive descent
- LL(k): k tokens lookahead

**Bottom-up (LR)**:
- Start from input, reduce to start symbol
- Shift-reduce parsing
- More powerful than LL

### Recursive Descent Parser

```python
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse_expr(self):
        left = self.parse_term()
        while self.current() in ['+', '-']:
            op = self.current()
            self.advance()
            right = self.parse_term()
            left = BinaryExpr(op, left, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.current() in ['*', '/']:
            op = self.current()
            self.advance()
            right = self.parse_factor()
            left = BinaryExpr(op, left, right)
        return left

    def parse_factor(self):
        if self.current_type() == 'NUMBER':
            value = int(self.current())
            self.advance()
            return NumberExpr(value)
        elif self.current() == '(':
            self.advance()  # Skip '('
            expr = self.parse_expr()
            self.advance()  # Skip ')'
            return expr
```

### Abstract Syntax Tree

```
Expression: 2 + 3 * 4

AST:
        +
       / \
      2   *
         / \
        3   4
```

## Semantic Analysis

Type checking, scope resolution, binding.

### Symbol Table

Track declarations and their attributes.

```python
class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def define(self, name, type):
        self.symbols[name] = type

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        raise NameError(f"Undefined: {name}")
```

### Type Checking

```python
def check_type(node, symbol_table):
    if isinstance(node, NumberExpr):
        return 'int'
    elif isinstance(node, BinaryExpr):
        left_type = check_type(node.left, symbol_table)
        right_type = check_type(node.right, symbol_table)
        if left_type != right_type:
            raise TypeError(f"Type mismatch: {left_type} vs {right_type}")
        return left_type
    elif isinstance(node, Identifier):
        return symbol_table.lookup(node.name)
```

## Type Systems

### Static vs Dynamic Typing

| Static | Dynamic |
|--------|---------|
| Types checked at compile time | Types checked at runtime |
| Faster execution | More flexible |
| Earlier error detection | Easier prototyping |
| Java, C++, Rust | Python, JavaScript |

### Strong vs Weak Typing

| Strong | Weak |
|--------|------|
| Strict type rules | Implicit conversions |
| Fewer bugs | More convenient |
| Python, Java | C, JavaScript |

### Type Inference

Deduce types without explicit annotations.

```haskell
-- Haskell: types inferred
add x y = x + y  -- inferred: Num a => a -> a -> a
```

```rust
// Rust: local type inference
let x = 5;        // inferred: i32
let y = vec![1, 2, 3];  // inferred: Vec<i32>
```

### Generics (Parametric Polymorphism)

```java
// Java generics
public <T> T identity(T value) {
    return value;
}

List<String> strings = new ArrayList<>();
List<Integer> numbers = new ArrayList<>();
```

### Variance

**Covariance**: If A < B, then Container<A> < Container<B>.
**Contravariance**: If A < B, then Container<B> < Container<A>.
**Invariance**: No subtyping relationship.

```kotlin
// Kotlin
class Producer<out T>  // Covariant (can return T)
class Consumer<in T>   // Contravariant (can accept T)
class Both<T>          // Invariant
```

## Intermediate Representation (IR)

### Three-Address Code

```
Source: a = b + c * d

IR:
  t1 = c * d
  t2 = b + t1
  a = t2
```

### Static Single Assignment (SSA)

Each variable assigned exactly once.

```
// Original
x = 1
x = 2
y = x

// SSA
x1 = 1
x2 = 2
y = x2
```

## Code Optimization

### Common Optimizations

**Constant folding**:
```
x = 2 + 3  ->  x = 5
```

**Dead code elimination**:
```
x = 5
// x never used
-> remove assignment
```

**Loop unrolling**:
```
for i in range(4):    for i in range(2):
    f(i)          ->      f(i*2)
                          f(i*2 + 1)
```

**Inlining**:
```
def square(x):        a = x * x  // inline
    return x * x
a = square(x)
```

## Garbage Collection

### Reference Counting

Count references to object, free when zero.

```python
# Increment on reference
a = Object()  # refcount = 1
b = a         # refcount = 2

# Decrement when out of scope
del b         # refcount = 1
del a         # refcount = 0 -> free
```

**Problem**: Circular references.

### Mark-and-Sweep

1. Mark all reachable objects from roots
2. Sweep (free) unmarked objects

```
Roots: [stack, globals]
    |
Mark: Trace all reachable objects
Sweep: Free unreachable objects
```

### Generational GC

Young objects collected more frequently.

```
Generation 0: New objects (collect often)
Generation 1: Survived some collections
Generation 2: Long-lived (collect rarely)
```

**Hypothesis**: Most objects die young.

### GC Strategies Comparison

| Strategy | Pause | Throughput | Memory |
|----------|-------|------------|--------|
| Reference counting | None | Good | Overhead per object |
| Mark-and-sweep | Stop-the-world | Good | None |
| Generational | Short pauses | Best | Extra for generations |
| Concurrent | Minimal | Lower | Barriers needed |

## Interview Questions

1. **What are compilation phases?**
   - Lexical analysis (tokens)
   - Syntax analysis (AST)
   - Semantic analysis (types)
   - Code generation

2. **Static vs dynamic typing?**
   - Static: Checked at compile time, faster, safer
   - Dynamic: Checked at runtime, flexible

3. **How does garbage collection work?**
   - Reference counting: Track references
   - Mark-and-sweep: Trace reachable, free rest
   - Generational: Young objects collected more

4. **What is type inference?**
   - Compiler deduces types without annotations
   - Based on usage and constraints
   - Hindley-Milner algorithm for functional languages
