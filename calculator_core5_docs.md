# Architecture Decision Record
## App 32 — Calculator
**Roadmap CLI Apps | Document 1 of 5**
**Status: Accepted**

---

## Context

Calculator is a command-line calculator that intentionally implements its own expression language instead of delegating evaluation to Python's `eval()`. The app supports arithmetic, precedence, parentheses, unary operators, exponentiation, integer division, modulo, multiple number literal formats, variables, built-in constants, result memory through `ans`, user-defined functions, built-in math functions, Decimal precision control, trigonometry angle modes, output formatting, script execution, stdin piping, persistent REPL history, and JSON configuration.

The central architectural problem was that the app needed to behave like a small language interpreter while remaining understandable as an academic CLI project. A calculator that simply called `eval()` would be smaller, but it would not demonstrate lexical analysis, grammar design, AST modeling, scoped evaluation, domain-specific errors, or safe execution. The decision was therefore to build a complete but bounded interpreter pipeline: source text becomes tokens, tokens become an AST, the AST is evaluated against a mutable calculator environment, and the result is formatted for the active CLI mode.

---

## Decisions

### Decision 1 — Hand-written lexer instead of `eval()` or regex-only parsing

**Chosen:** A character-by-character lexer in `calc/lexer.py` that emits `Token` objects from raw source text.

**Rejected:** Python `eval()`, direct string splitting, or a single regex-based parser.

**Reason:** The purpose of the app is not only to calculate answers, but to prove understanding of how expression languages are built. A hand-written lexer makes token boundaries explicit and lets the app report precise positions for unexpected characters, malformed scientific notation, and invalid base literals. It also keeps the supported language intentionally smaller than Python, which improves safety and makes behavior predictable.

---

### Decision 2 — Recursive-descent parser with explicit precedence layers

**Chosen:** A recursive-descent parser in `calc/parser.py` with separate methods for assignment, function definition, addition, multiplication, unary, power, and primary expressions.

**Rejected:** A shunting-yard parser or parser generator.

**Reason:** Recursive descent made the grammar readable and teachable. Each precedence level has a corresponding method, so the code structure mirrors the grammar. This was a better academic fit than a parser generator because it required implementing parsing decisions directly. It was also easier to extend than an ad hoc evaluator because new syntax can be introduced by adding tokens, AST nodes, and parser branches.

---

### Decision 3 — Frozen AST dataclasses with visitor-style evaluation

**Chosen:** AST node classes such as `NumberNode`, `BinaryOpNode`, `UnaryOpNode`, `VariableNode`, `FunctionCallNode`, `AssignmentNode`, and `FunctionDefinitionNode`, each implemented as a dataclass with an `accept()` method.

**Rejected:** Evaluating directly during parsing or representing expressions as nested dictionaries.

**Reason:** Separating parsing from evaluation gives the app a clean internal representation of user input. The parser only answers “what does this source mean structurally?” while the evaluator answers “what value does this structure produce in the current environment?” Frozen dataclasses reduce accidental mutation and make AST nodes easier to inspect in tests.

---

### Decision 4 — `decimal.Decimal` as the numeric core

**Chosen:** All parsed numeric values are converted to `Decimal`, with session precision controlled through configuration and runtime commands.

**Rejected:** Native `float` arithmetic only.

**Reason:** A calculator should not surprise users with classic floating-point artifacts such as `0.1 + 0.2` becoming `0.30000000000000004`. `Decimal` provides predictable display behavior, configurable precision, and cleaner results for common CLI calculator use. The trade-off is that some transcendental functions require extra care because not every math operation is naturally Decimal-native.

---

### Decision 5 — Stateful `CalculatorSession` as the shared runtime boundary

**Chosen:** `CalculatorSession` owns configuration, environment, evaluator, formatter, and history. CLI modes and the REPL all call `session.execute()`.

**Rejected:** Separate evaluator setup for one-shot CLI mode, script mode, pipe mode, and REPL mode.

**Reason:** A calculator has session state: variables, `ans`, user-defined functions, precision, angle mode, output format, and history. Centralizing this in `CalculatorSession` prevents duplicated orchestration logic and keeps every front end consistent. The same expression should behave the same whether it comes from a command-line argument, script file, pipe, or REPL input.

---

### Decision 6 — Environment object for variables, constants, and user functions

**Chosen:** A mutable `Environment` stores user variables, constants, user-defined functions, precision, and angle mode.

**Rejected:** Global module-level dictionaries or passing variable maps through every evaluator method.

**Reason:** State needs a clear owner. The environment separates language state from parser mechanics and CLI handling. It also enforces rules such as “constants cannot be overwritten” and keeps built-in constants separate from user variables. This makes it easier to reset user state without losing constants.

---

### Decision 7 — User-defined functions store AST bodies, not strings

**Chosen:** A user-defined function is stored as a `UserFunction(parameters, body)` where `body` is already parsed AST.

**Rejected:** Storing function definitions as raw source strings and reparsing on every call.

**Reason:** Parsing once at definition time avoids repeated parser work and ensures syntax errors are caught immediately. Function calls only need to bind argument values into a local scope and evaluate the saved AST body. This also reinforces the language-interpreter structure of the project.

---

### Decision 8 — Local scope stack for function calls

**Chosen:** The evaluator keeps `_local_scopes: list[dict[str, Decimal]]` and checks local scopes before the environment.

**Rejected:** Mutating the global environment with function parameters during calls.

**Reason:** Function parameters should not permanently overwrite user variables. A scope stack gives each call temporary bindings and guarantees cleanup through a `finally` block. This is the minimum viable version of lexical scoping for this app’s size.

---

### Decision 9 — Custom error hierarchy with source positions

**Chosen:** `CalcError`, `LexerError`, `ParseError`, `EvaluationError`, `DivisionByZeroError`, and `UndefinedVariableError`, each capable of rendering user-facing messages with caret pointers when a source position is known.

**Rejected:** Letting raw Python exceptions reach the user.

**Reason:** A CLI language tool needs errors that explain the user’s expression, not the implementation’s stack trace. Position-aware errors support better debugging in one-shot CLI mode, script mode, and the REPL. They also allow script mode to report a bad line and continue processing later lines.

---

### Decision 10 — Multi-mode CLI with one execution engine

**Chosen:** `calc.cli` supports one-shot expression mode, script-file mode, piped stdin mode, and REPL mode, all backed by `CalculatorSession`.

**Rejected:** Building only a REPL or only a one-shot calculator.

**Reason:** The project is a command-line app, not only a math library. Supporting all four modes makes it useful for interactive learning, shell scripting, quick command evaluation, and file-based calculation batches. Keeping all modes on the same engine prevents behavior drift.

---

## Consequences

**Positive:**
- The app demonstrates real interpreter architecture: lexer → parser → AST → evaluator → formatter.
- The absence of `eval()` keeps the language constrained and safer than executing arbitrary Python.
- The parser is readable because precedence is represented directly in method structure.
- Decimal arithmetic gives cleaner user-facing calculator results and configurable precision.
- `CalculatorSession` creates a reusable runtime boundary for CLI, REPL, script, and pipe modes.
- Custom errors improve user experience and make recovery possible after invalid input.
- User-defined functions provide meaningful scope and environment design practice.

**Negative / Trade-offs:**
- The project is larger than a simple CLI calculator and approaches medium-project scope.
- Decimal-based trigonometry requires custom sine/cosine series logic and convergence safeguards.
- The parser currently handles one statement at a time rather than a full multi-statement program grammar.
- Error messages are human-readable, not machine-readable JSON.
- The language does not support comments inside expressions, multiline function definitions, arrays, booleans, or symbolic math.

---

## Alternatives Not Explored

- **Parser generators** such as Lark or ANTLR: rejected because the learning goal was to manually implement tokenization and parsing.
- **Python `ast` module**: rejected because it would still inherit Python grammar rather than a calculator-specific grammar.
- **Float-only evaluation**: rejected because Decimal better fits calculator expectations.
- **Bytecode or compiled AST execution**: unnecessary for this scope; tree walking is simpler and fast enough for CLI usage.
- **Persistent variables/functions across REPL sessions**: omitted to keep persistence limited to history and config.

---

*Constitution reference: Article 1 (Python fundamentals and architectural thinking), Article 3.4 (larger project classification), Article 4 (engineering quality), Article 6 (verification). No authorship flags identified from the inspected repository material.*

---


# Technical Design Document
## App 32 — Calculator
**Roadmap CLI Apps | Document 2 of 5**

---

## Overview

Calculator is a Python package named `calc` that implements a small expression language and exposes it through `python -m calc` and the `calc` console script. The implementation is organized around a classic interpreter pipeline:

```
source text
   │
   ▼
Lexer.tokenize()
   │  list[Token]
   ▼
Parser.parse()
   │  ASTNode
   ▼
Evaluator.evaluate()
   │  Decimal or FunctionDefinitionResult
   ▼
CalculatorSession.execute()
   │  CalculationResult
   ▼
Formatter.format()
   │
   ▼
stdout / REPL display / script output
```

**Package:** `calc`
**Primary CLI entry points:** `python -m calc`, `calc`
**Core runtime object:** `CalculatorSession`
**Primary implementation style:** hand-written lexer, recursive-descent parser, frozen AST nodes, tree-walking evaluator
**Runtime dependencies:** Python standard library only
**Development dependency:** `pytest`

---

## System Context

Calculator runs entirely as a local command-line application. It reads input from one of four sources:

- command-line expression arguments,
- a script file supplied with `-f` / `--file`,
- stdin when piped input is detected,
- interactive REPL input when stdin is a TTY.

It writes successful calculation results to stdout. User-facing errors are written to stderr in one-shot, script, and pipe modes. In REPL mode, errors are printed and the session continues.

The app has two optional filesystem side effects:

- reading JSON config from `~/.calcrc`,
- loading/saving plain-text history at `~/.calc_history` when history saving is enabled.

It does not make network calls, spawn subprocesses, or require external services.

---

## Component Breakdown

### `calc/__init__.py`
Exports `CalculatorSession` and defines `__version__ = "1.0.0"`.

### `calc/__main__.py`
Module entry point for `python -m calc`. Delegates to `calc.cli.main()`.

### `calc/tokens.py`
Defines `TokenType` and frozen `Token` objects. Token types include numbers, identifiers, arithmetic operators, parentheses, comma, assignment, and EOF.

### `calc/lexer.py`
Converts raw source text into tokens. It scans character by character, supports decimal/scientific/base-specific number literals, identifiers, arithmetic operators, and position-aware lexer errors.

### `calc/ast_nodes.py`
Defines the AST node hierarchy and `ASTVisitor` protocol. Nodes include numbers, binary operations, unary operations, variables, function calls, assignments, and function definitions.

### `calc/parser.py`
Recursive-descent parser that consumes tokens and produces one AST node representing either an expression, assignment, or function definition.

### `calc/evaluator.py`
Tree-walking evaluator that visits AST nodes, resolves variables/functions, performs Decimal arithmetic, applies built-in functions, manages function-call local scopes, and raises evaluation errors.

### `calc/environment.py`
Owns mutable calculator state: variables, constants, user-defined functions, precision, and angle mode. Also defines the `UserFunction` dataclass.

### `calc/engine.py`
High-level session orchestration. `CalculatorSession.execute()` runs lexing, parsing, evaluation, answer updating, formatting, and history recording for one source line.

### `calc/formatter.py`
Formats Decimal values using `auto`, `fixed`, or `scientific` output strategies.

### `calc/config.py`
Loads and validates JSON config from `~/.calcrc`. Invalid or missing config falls back to defaults.

### `calc/history.py`
Tracks in-memory calculation history and optionally persists the most recent 500 entries to `~/.calc_history`.

### `calc/errors.py`
Defines the custom exception hierarchy and caret-style error rendering.

### `calc/repl.py`
Interactive REPL with commands such as `help`, `history`, `vars`, `clear`, `set precision`, `set angle`, `set format`, `quit`, and `exit`.

### `calc/cli.py`
Command-line argument parsing and execution-mode selection. Handles one-shot, file, pipe, and REPL modes.

### `tests/`
Unit and integration tests covering lexer behavior, parser behavior, evaluator behavior, built-ins, variables, functions, custom error recovery, and CLI script/single-expression modes.

---

## Module Dependency Graph

```
calc.__main__
    └── calc.cli

calc.cli
    ├── calc.__version__
    ├── calc.config
    ├── calc.engine
    ├── calc.errors
    └── calc.repl

calc.repl
    ├── calc.__version__
    ├── calc.engine
    └── calc.errors

calc.engine
    ├── calc.config
    ├── calc.environment
    ├── calc.evaluator
    ├── calc.formatter
    ├── calc.history
    ├── calc.lexer
    └── calc.parser

calc.parser
    ├── calc.ast_nodes
    ├── calc.errors
    └── calc.tokens

calc.lexer
    ├── calc.errors
    └── calc.tokens

calc.evaluator
    ├── decimal / math
    ├── calc.ast_nodes
    ├── calc.environment
    ├── calc.errors
    └── calc.tokens

calc.environment
    ├── decimal
    ├── calc.ast_nodes
    └── calc.errors

calc.formatter
    ├── decimal
    └── calc.config
```

The dependency direction is intentionally one-way: CLI and REPL depend on the session engine, the session engine depends on language internals, and language internals do not depend on CLI presentation.

---

## Grammar Summary

The parser accepts one complete statement or expression per call.

```text
statement             → function_definition | assignment | expression EOF
function_definition   → IDENTIFIER "(" parameters? ")" "=" expression
parameters            → IDENTIFIER ("," IDENTIFIER)*
assignment            → IDENTIFIER "=" expression
expression            → addition
addition              → multiplication (("+" | "-") multiplication)*
multiplication        → unary (("*" | "/" | "//" | "%") unary)*
unary                 → ("+" | "-") unary | power
power                 → primary (("^" | "**") unary)?
primary               → NUMBER | IDENTIFIER | function_call | "(" expression ")"
function_call         → IDENTIFIER "(" arguments? ")"
arguments             → expression ("," expression)*
```

Notable behavior:

- `^` and `**` are normalized to the same power token.
- Unary binds so that `-2^2` evaluates as `-(2^2)`, producing `-4`.
- Function definitions are distinguished from function calls by scanning ahead for `name(parameters) = expression`.
- Duplicate function parameters are rejected during parsing.

---

## Core Algorithms & Logic

### 1. Lexing

`Lexer.tokenize()` loops over the source string until EOF. Each scan records a token start position, consumes one character, and dispatches to one of the scanner branches:

1. ignore whitespace and BOM characters,
2. scan number literals,
3. scan identifiers,
4. scan single-character or two-character operators,
5. raise `LexerError` for unknown characters.

Number handling includes:

- integer and decimal numbers,
- scientific notation such as `3.14e-2`,
- hexadecimal literals such as `0xFF`,
- binary literals such as `0b1010`,
- octal literals such as `0o77`.

The lexer appends an EOF token at the end so the parser can validate that the entire input was consumed.

---

### 2. Parsing

`Parser.parse()` decides whether the input is a function definition, assignment, or expression. It then calls the corresponding grammar method and requires EOF afterward. This prevents partially valid expressions such as `2 + 2 garbage` from being silently accepted.

The parser builds nested AST objects. For example:

```text
2 + 2 * 3
```

becomes structurally equivalent to:

```text
BinaryOpNode(
  left=NumberNode(2),
  operator=PLUS,
  right=BinaryOpNode(NumberNode(2), STAR, NumberNode(3))
)
```

This structure preserves precedence for the evaluator without needing to know about source-level parsing rules.

---

### 3. Evaluation

`Evaluator.evaluate()` calls `node.accept(self)`, causing each AST node to dispatch to a matching visitor method.

- `visit_number()` returns the literal Decimal.
- `visit_binary()` evaluates left and right operands, checks operator type, and performs Decimal arithmetic.
- `visit_unary()` handles unary plus and minus.
- `visit_variable()` checks local function scopes first, then environment variables/constants.
- `visit_function_call()` dispatches either to a built-in function or a stored user-defined function.
- `visit_assignment()` stores a variable in the environment and returns its value.
- `visit_function_definition()` stores a parsed function body in the environment and returns a definition message result.

Division-like operations guard against zero and raise `DivisionByZeroError`. Domain-sensitive functions such as `sqrt`, `log`, and trigonometry validate input and raise `EvaluationError` when needed.

---

### 4. User-defined function calls

When a user-defined function is called:

1. all call arguments are evaluated to Decimal values,
2. argument count is checked against the function parameter list,
3. parameters are zipped with argument values into a local scope dictionary,
4. the scope is pushed onto `_local_scopes`,
5. the stored AST body is evaluated,
6. the scope is popped in a `finally` block.

This prevents function parameters from leaking into global variables.

---

### 5. Session execution

`CalculatorSession.execute()` is the main application pipeline for one line:

1. strip whitespace,
2. return `None` for empty input,
3. tokenize source,
4. parse tokens into an AST,
5. evaluate AST,
6. update `ans` for numeric results,
7. format the result,
8. record history when enabled,
9. return a `CalculationResult`.

Function definitions return a message such as `Defined function f(x).` rather than a numeric value.

---

## Data Structures

### `Token`
```python
Token(type: TokenType, lexeme: str, position: int)
```
Immutable lexical token with source position.

### `TokenType`
Enum containing all supported token categories: number, identifier, operators, parentheses, comma, assignment, EOF.

### AST nodes
All AST nodes include `position: int` and implement `accept(visitor)`.

Important node shapes:

```python
NumberNode(value: Decimal)
BinaryOpNode(left: ASTNode, operator: Token, right: ASTNode)
UnaryOpNode(operator: Token, operand: ASTNode)
VariableNode(name: str)
FunctionCallNode(name: str, arguments: list[ASTNode])
AssignmentNode(name: str, expression: ASTNode)
FunctionDefinitionNode(name: str, parameters: list[str], body: ASTNode)
```

### `Environment`
```python
variables: dict[str, Decimal]
functions: dict[str, UserFunction]
precision: int
angle_mode: str
constants: dict[str, Decimal]
```

### `UserFunction`
```python
UserFunction(parameters: list[str], body: ASTNode)
```

### `CalculatorSession`
```python
config: CalcConfig
environment: Environment
evaluator: Evaluator
formatter: Formatter
history: HistoryManager
```

### `CalculationResult`
```python
CalculationResult(source: str, value: Decimal | None, message: str | None)
```

`display` returns `message` when present, otherwise stringifies the numeric value.

### `HistoryEntry`
```python
HistoryEntry(source: str, outcome: str)
```

---

## State Management

Calculator state is session-based.

**In memory:**
- variables, including `ans`,
- user-defined functions,
- precision,
- angle mode,
- output format,
- REPL history entries.

**On disk:**
- config is read from `~/.calcrc`,
- history is read from and saved to `~/.calc_history` when enabled.

**Per function call:**
- evaluator local scopes are pushed and popped around user-defined function calls.

**Per command invocation:**
- one-shot CLI mode creates a session, evaluates once, and exits,
- script and pipe modes reuse a session across lines so assignments and functions persist within the file/stream,
- REPL mode reuses one session until exit.

---

## Error Handling Strategy

Errors are classified by stage:

| Stage | Error Type | Example |
|---|---|---|
| Lexing | `LexerError` | unexpected character, malformed scientific notation, invalid base digit |
| Parsing | `ParseError` | missing parenthesis, duplicate parameter, invalid syntax |
| Evaluation | `EvaluationError` | invalid domain, undefined function, wrong arity |
| Division | `DivisionByZeroError` | `/`, `//`, `%`, or `tan` division by zero |
| Variable lookup | `UndefinedVariableError` | reference to missing variable |

Each `CalcError` can render itself as:

```text
ParseError: Expected an expression, found '*'.
3 + * 5
    ^
```

CLI behavior:

- one-shot expression errors return exit code `1`,
- file and pipe mode errors include line numbers, continue processing later lines, and return exit code `1` if any line failed,
- REPL errors are printed and the session continues,
- invalid config does not stop startup; defaults are used instead.

---

## External Dependencies

Runtime dependencies: none outside the Python standard library.

Development/testing dependencies:

| Dependency | Purpose |
|---|---|
| `pytest` | test runner |

Packaging metadata requires Python `>=3.10` and uses `setuptools` as the build backend.

---

## Concurrency Model

The calculator is fully synchronous and single-threaded. There is no async I/O, threading, multiprocessing, background worker, or network concurrency. This is appropriate because each expression is evaluated locally and quickly. A synchronous model also keeps REPL state, history saving, and error recovery easy to reason about.

---

## Design Patterns Used

| Pattern | Where | Justification |
|---|---|---|
| Interpreter pipeline | lexer → parser → AST → evaluator | Natural structure for a custom expression language |
| Visitor-style dispatch | AST `accept()` and evaluator methods | Separates AST structure from evaluation behavior |
| Session facade | `CalculatorSession` | Provides one API for CLI, script, pipe, and REPL modes |
| Strategy-like formatting | `Formatter` modes | Keeps output formatting separate from evaluation |
| Scoped environment | evaluator local scope stack | Prevents user-function parameters from mutating global state |
| Custom exception hierarchy | `calc.errors` | Gives predictable user-facing failures |

---

## Known Limitations

- The parser handles one statement per line, not full multi-line programs.
- User-defined functions cannot contain statement bodies, conditionals, or recursion safeguards beyond Python’s own call stack behavior.
- Decimal trigonometry is implemented with series expansion for sine/cosine; extremely high precision or pathological inputs may expose convergence/performance limits.
- History is plain text, not structured JSON.
- Config is JSON but has no schema file.
- Errors are optimized for human readability, not machine consumption.
- The app does not persist user-defined variables/functions across sessions.
- There is no plugin system for adding custom built-in functions.

---

*Constitution reference: This design satisfies Article 1 through explicit interpreter architecture, Article 4 through modular separation, and Article 6 through testable pipeline boundaries.*

---


# Interface Design Specification
## App 32 — Calculator
**Roadmap CLI Apps | Document 3 of 5**

---

## Invocation Syntax

### Installed console script

```bash
calc [OPTIONS] [EXPRESSION ...]
```

### Module execution

```bash
python -m calc [OPTIONS] [EXPRESSION ...]
```

### Common forms

```bash
python -m calc "2 + 2"
python -m calc --precision 50 "1 / 7"
python -m calc --angle deg "sin(90)"
python -m calc --format scientific "123456789"
python -m calc -f script.calc
"sqrt(81) + max(2, 7)" | python -m calc
python -m calc
```

---

## Argument Reference Table

| Name | Type | Required | Default | Accepted Values | Description |
|---|---:|---:|---|---|---|
| `EXPRESSION` | `list[str]` | No | none | Any calculator expression tokens | Expression to evaluate. Multiple shell arguments are joined with spaces. |
| `-f`, `--file` | `path` | No | none | Readable UTF-8 text file | Evaluates one expression per non-empty, non-comment line. |
| `--precision` | `int` | No | config/default `28` | `1` through `200` after validation | Decimal precision for evaluation and display. |
| `--angle` | `choice` | No | config/default `rad` | `rad`, `deg` | Trigonometry angle mode. |
| `--format` | `choice` | No | config/default `auto` | `auto`, `fixed`, `scientific` | Output formatting strategy. |
| `--version` | flag | No | false | — | Prints `calc 1.0.0` and exits. |
| `--help` | flag | No | false | — | Prints argparse help and exits. |

---

## Execution Mode Selection

The CLI chooses mode in this order:

1. `--file PATH` → script mode,
2. expression arguments present → one-shot expression mode,
3. stdin is not a TTY → pipe mode,
4. otherwise → interactive REPL mode.

---

## Expression Input Contract

### Accepted source forms

- arithmetic expressions: `2 + 2 * 3`
- grouped expressions: `(2 + 2) * 3`
- unary expressions: `-5`, `+(2)`, `-(2 + 3)`
- exponentiation: `2^8`, `2**8`
- assignment: `x = 5`
- variable use: `x * 3`
- function definition: `f(x) = x^2 + 1`
- function call: `f(10)`
- built-in function call: `sqrt(81)`, `gcd(54, 24)`

### Number literal forms

| Form | Example |
|---|---|
| integer | `42` |
| decimal | `3.1415` |
| scientific notation | `2.5e-3` |
| hexadecimal | `0xFF` |
| binary | `0b1010` |
| octal | `0o77` |

### Identifier rules

Identifiers begin with a letter or underscore and may continue with letters, digits, or underscores.

### Script and pipe rules

- Input is read line by line.
- Empty lines are skipped.
- Lines beginning with `#` after stripping whitespace are skipped.
- Each non-skipped line is parsed as one complete expression or statement.
- A failed line reports an error and processing continues.

---

## Supported Operators

| Operator | Meaning | Notes |
|---|---|---|
| `+` | addition / unary plus | Binary and unary |
| `-` | subtraction / unary minus | Binary and unary |
| `*` | multiplication | — |
| `/` | Decimal division | zero divisor rejected |
| `//` | integer/floor-style division | zero divisor rejected |
| `%` | modulo | zero divisor rejected |
| `^` | exponentiation | same as `**` |
| `**` | exponentiation | same as `^` |
| `()` | grouping / calls | grouping or function arguments |
| `=` | assignment / function definition | only valid at statement level |
| `,` | argument separator | function parameters and calls |

---

## Built-In Constants

| Name | Meaning |
|---|---|
| `pi` | π |
| `e` | Euler’s number |
| `tau` | 2π |
| `inf` | Decimal infinity |
| `ans` | Most recent numeric result; starts as `0` |

Constants cannot be assigned over. `ans` is a variable and updates after each numeric result.

---

## Built-In Functions

| Function | Arity | Description |
|---|---:|---|
| `abs(x)` | 1 | absolute value |
| `round(x)` | 1 | rounded integer value |
| `round(x, places)` | 2 | rounded to decimal places |
| `floor(x)` | 1 | floor |
| `ceil(x)` | 1 | ceiling |
| `sqrt(x)` | 1 | square root, `x >= 0` |
| `pow(x, y)` | 2 | exponentiation |
| `min(...)` | 1+ | minimum |
| `max(...)` | 1+ | maximum |
| `factorial(n)` | 1 | non-negative integer factorial |
| `gcd(a, b, ...)` | 2+ | greatest common divisor for integers |
| `log(x)` | 1 | natural log, `x > 0` |
| `log(x, base)` | 2 | logarithm with positive base not equal to `1` |
| `log10(x)` | 1 | base-10 log, `x > 0` |
| `log2(x)` | 1 | base-2 log, `x > 0` |
| `sin(x)` | 1 | sine, obeys angle mode |
| `cos(x)` | 1 | cosine, obeys angle mode |
| `tan(x)` | 1 | tangent, obeys angle mode |

---

## REPL Commands

| Command | Description |
|---|---|
| `help` | Show command help and examples |
| `history` | Show calculation history |
| `clear history` / `history clear` | Clear in-memory and saved history |
| `vars` | List current variables |
| `clear` | Clear user-defined variables and functions |
| `set precision N` | Set Decimal precision, 1 to 200 |
| `set angle deg|rad` | Set trigonometry angle mode |
| `set format auto|fixed|scientific` | Set output formatting mode |
| `quit` / `exit` | Leave the REPL |

REPL control behavior:

- Empty input is ignored.
- Ctrl+C cancels the current input and keeps the REPL open.
- Ctrl+D exits cleanly.

---

## Output Contract

### Successful one-shot expression

stdout contains exactly one formatted result line:

```text
4
```

### Successful assignment

stdout contains the assigned value:

```text
5
```

### Successful function definition

stdout contains a definition message:

```text
Defined function f(x).
```

### Script or pipe mode

stdout contains one output line per successful non-skipped input line. Failed lines write errors to stderr and do not produce a normal result line.

### REPL mode

The REPL prints prompts, command responses, results, and errors interactively.

---

## Output Formatting Modes

| Mode | Behavior |
|---|---|
| `auto` | Compact display; strips unnecessary zeros; switches to scientific notation for very large/small magnitudes |
| `fixed` | Fixed number of digits after the decimal point based on precision |
| `scientific` | Scientific notation with precision-controlled mantissa |

---

## Exit Code Reference

| Exit Code | Condition |
|---:|---|
| `0` | Successful one-shot evaluation, successful script/pipe run with no failed lines, normal REPL exit, `--help`, or `--version` |
| `1` | One-shot evaluation error, unreadable script file, or at least one failed script/pipe line |
| `2` | Argument parsing failure produced by `argparse`, such as invalid choices for `--angle` or `--format` |

---

## Error Output Behavior

### One-shot expression error

stderr receives a rendered custom error:

```text
DivisionByZeroError: Division by zero.
10 / 0
   ^
```

### Script/pipe line error

stderr includes the line number first:

```text
Line 3:
ParseError: Expected an expression, found '*'.
3 + * 5
    ^
```

Errors are human-readable and caret-oriented. They are not JSON or guaranteed machine-readable records.

---

## Environment Variables

The app does not define or read any calculator-specific environment variables.

Standard OS behavior still affects path expansion and home directory resolution because config/history paths are based on `Path.home()`.

---

## Configuration Files

### Default path

```text
~/.calcrc
```

### Format

JSON object.

### Supported keys

| Key | Type | Default | Validation |
|---|---|---|---|
| `precision` | int-like | `28` | clamped to `1..200` |
| `angle_mode` | str | `rad` | invalid values reset to `rad` |
| `output_format` | str | `auto` | invalid values reset to `auto` |
| `save_history` | bool-like | `true` | converted with `bool()` |

### Example

```json
{
  "precision": 50,
  "angle_mode": "deg",
  "output_format": "auto",
  "save_history": true
}
```

### Precedence

1. CLI flags,
2. config file,
3. hardcoded defaults.

Invalid JSON or unreadable config files do not stop startup; defaults are used.

---

## Side Effects

| Side Effect | Trigger |
|---|---|
| Reads `~/.calcrc` | session startup |
| Reads `~/.calc_history` | history manager startup when enabled |
| Writes `~/.calc_history` | normal REPL exit when history saving is enabled |
| Deletes `~/.calc_history` | `clear history` / `history clear` command |
| Reads script file | `-f` / `--file` |

No network calls are made.

---

## Usage Examples

### Basic use

```bash
python -m calc "2 + 2 * 3"
```

Expected stdout:

```text
8
```

### Precision control

```bash
python -m calc --precision 50 "1 / 7"
```

Expected stdout is a Decimal-formatted value with higher precision than the default.

### Degree-mode trigonometry

```bash
python -m calc --angle deg "sin(90)"
```

Expected stdout:

```text
1
```

### User-defined function in script mode

`script.calc`:

```text
x = 10
f(n) = n^2 + 1
f(x)
```

Run:

```bash
python -m calc -f script.calc
```

Expected stdout:

```text
10
Defined function f(n).
101
```

### Piped input

```bash
printf "sqrt(81)\ngcd(54, 24)\n" | python -m calc
```

Expected stdout:

```text
9
6
```

### Intentional failure

```bash
python -m calc "10 / 0"
```

Expected stderr includes:

```text
DivisionByZeroError: Division by zero.
```

Expected exit code: `1`.

---

*Constitution reference: This interface specification supports Article 6 by making invocation, inputs, outputs, errors, and exit codes verifiable.*

---


# Runbook
## App 32 — Calculator
**Roadmap CLI Apps | Document 4 of 5**

---

## Prerequisites

- Python 3.10 or later
- A terminal or shell capable of running Python modules
- `pip` for installing development dependencies
- No runtime third-party dependencies
- `pytest` for running the test suite

---

## Installation Procedure

### From a fresh clone

```bash
git clone https://github.com/PrincetonAfeez/Calculator_v2.git
cd Calculator_v2
python -m venv .venv
```

Activate the virtual environment.

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

Or install the package in editable mode:

```bash
python -m pip install -e .
```

---

## Configuration Steps

Configuration is optional. The calculator works with defaults if no config exists.

Default config path:

```text
~/.calcrc
```

Example config:

```json
{
  "precision": 50,
  "angle_mode": "deg",
  "output_format": "auto",
  "save_history": true
}
```

If config is missing, invalid, or unreadable, the app falls back to defaults:

```text
precision = 28
angle_mode = rad
output_format = auto
save_history = true
```

CLI flags override config values for that run.

---

## Standard Operating Procedures

### Evaluate one expression

```bash
python -m calc "2 + 2"
```

### Use installed console script

```bash
calc "2 + 2"
```

### Start REPL

```bash
python -m calc
```

### Run a script file

```bash
python -m calc -f script.calc
```

Script files should contain one expression or statement per line. Blank lines and `#` comment lines are skipped.

### Use stdin pipe mode

```bash
printf "x = 5\nx * 3\n" | python -m calc
```

### Set precision from CLI

```bash
python -m calc --precision 50 "1 / 7"
```

### Use degree mode

```bash
python -m calc --angle deg "sin(90)"
```

### Use scientific formatting

```bash
python -m calc --format scientific "123456789"
```

### Define and call a function in REPL

```text
calc> f(x) = x^2 + 1
Defined function f(x).
calc> f(10)
101
```

---

## Health Checks

Run these commands after installation.

### Basic arithmetic

```bash
python -m calc "2 + 2 * 3"
```

Expected:

```text
8
```

### Decimal behavior

```bash
python -m calc "0.1 + 0.2"
```

Expected:

```text
0.3
```

### Built-in function

```bash
python -m calc "sqrt(81)"
```

Expected:

```text
9
```

### Degree-mode trig

```bash
python -m calc --angle deg "sin(90)"
```

Expected:

```text
1
```

### CLI error handling

```bash
python -m calc "10 / 0"
```

Expected:

- stderr includes `DivisionByZeroError`,
- exit code is `1`,
- no Python traceback is shown.

---

## Running Tests

```bash
pytest
```

Expected result: all tests pass.

Test coverage includes:

- tokenization of numbers, identifiers, and operators,
- lexer errors for invalid characters and malformed literals,
- parser AST construction for assignments and function definitions,
- parser errors for invalid syntax,
- arithmetic precedence and Decimal behavior,
- variables, `ans`, and user-defined functions,
- built-in functions,
- trigonometry in degree mode,
- custom error recovery,
- CLI one-shot and script modes.

---

## Expected Output Samples

### Expression

```bash
python -m calc "(2 + 2) * 3"
```

```text
12
```

### Assignment in script mode

Input file:

```text
x = 10
x * 3
```

Output:

```text
10
30
```

### Function definition

```text
Defined function f(n).
```

### Variable listing in REPL

```text
ans = 18
x = 5
```

---

## Known Failure Modes

| Failure Mode | Trigger | Output / Behavior | Resolution |
|---|---|---|---|
| Lexer error | Unknown character such as `@` | `LexerError` with caret | Remove or replace unsupported character |
| Bad scientific notation | `3e` | `LexerError` | Add exponent digits, e.g. `3e2` |
| Invalid base literal | `0b102` | `LexerError` | Use valid digits for the base |
| Parse error | `3 + * 5` | `ParseError` with caret | Correct expression syntax |
| Missing parenthesis | `(2 + 3` | `ParseError` | Add closing parenthesis |
| Duplicate function parameter | `f(x, x) = x` | `ParseError` | Use unique parameter names |
| Division by zero | `10 / 0` | `DivisionByZeroError` | Change divisor or guard input |
| Undefined variable | `missing + 1` | `UndefinedVariableError` | Define variable first |
| Domain error | `sqrt(-1)`, `log(0)` | `EvaluationError` | Use values inside function domain |
| Script file unreadable | bad path or permission error | stderr message and exit `1` | Fix path or permissions |
| Invalid CLI choice | `--angle degrees` | argparse error and exit `2` | Use `deg` or `rad` |

---

## Troubleshooting Decision Tree

### Symptom: command says module not found

Probable cause: package was not installed or command was run outside the repo.

Diagnostic:

```bash
python -m calc "2 + 2"
```

Resolution:

```bash
pip install -r requirements.txt
# or
python -m pip install -e .
```

---

### Symptom: `calc` command is not recognized

Probable cause: console script is not installed or virtual environment is not active.

Diagnostic:

```bash
python -m calc "2 + 2"
```

Resolution:

```bash
python -m pip install -e .
```

Then reactivate the virtual environment if needed.

---

### Symptom: expression works in REPL but not in shell

Probable cause: shell quoting or operator expansion.

Diagnostic:

```bash
python -m calc "2 * (3 + 4)"
```

Resolution: wrap expressions in quotes, especially those containing `*`, parentheses, or spaces.

---

### Symptom: script continues after errors

Probable cause: this is intentional script-mode behavior.

Diagnostic: check stderr for `Line N:` messages.

Resolution: fix the failed lines. The final exit code remains `1` if any line failed.

---

### Symptom: history is not saved

Probable cause: `save_history` is disabled, history path is not writable, or session did not exit normally.

Diagnostic:

```bash
cat ~/.calcrc
ls -la ~/.calc_history
```

Resolution: set `"save_history": true`, ensure home directory is writable, and exit REPL with `quit`, `exit`, or Ctrl+D.

---

### Symptom: config seems ignored

Probable cause: invalid JSON, unsupported key, or CLI flag overriding the setting.

Diagnostic:

```bash
cat ~/.calcrc
python -m calc --precision 10 "1 / 7"
```

Resolution: validate JSON and use supported keys only: `precision`, `angle_mode`, `output_format`, `save_history`.

---

## Dependency Failure Handling

### Missing `pytest`

Runtime calculator usage does not require pytest. Tests require it.

Resolution:

```bash
pip install -r requirements.txt
```

### Unreadable script file

The CLI catches `OSError` and returns exit code `1`.

Resolution: check the path, encoding, and permissions.

### Broken config file

Invalid config is ignored and defaults are used.

Resolution: repair `~/.calcrc` if custom settings are needed.

---

## Recovery Procedures

### Clear calculator state in REPL

```text
calc> clear
Environment cleared.
```

This clears variables and user-defined functions while preserving built-in constants.

### Clear history

```text
calc> clear history
History cleared.
```

or:

```text
calc> history clear
History cleared.
```

### Reset bad config

Delete or rename the config file:

```bash
mv ~/.calcrc ~/.calcrc.bak
```

The next run uses defaults.

### Remove saved history manually

```bash
rm ~/.calc_history
```

The next session starts with empty history.

---

## Logging Reference

The app does not implement a logging subsystem. User-facing errors are printed directly to stderr in non-REPL modes and stdout-like REPL output in interactive mode.

There are no log files, verbosity levels, or debug flags.

---

## Maintenance Notes

- Keep parser grammar and README examples synchronized.
- Add tests whenever adding a token, AST node, operator, or built-in function.
- Be careful when modifying operator precedence; small parser changes can alter mathematical meaning.
- Decimal precision changes should be tested with arithmetic, power, log, and trig functions.
- History file format is plain text; changing it may require a migration or backward-compatible parser.
- Config is forgiving by design; invalid values silently normalize, so tests should cover defaults and overrides.
- Any future machine-readable error mode should be added as an explicit flag rather than changing current human-readable output.

---

*Constitution reference: This runbook supports Article 6 through repeatable health checks, expected outputs, failure modes, and recovery procedures.*

---


# Lessons Learned
## App 32 — Calculator
**Roadmap CLI Apps | Document 5 of 5**

---

## Project Summary

Calculator is a command-line expression evaluator built as a small interpreter rather than a wrapper around Python evaluation. It tokenizes raw input, parses tokens into an AST, evaluates the AST against a session environment, formats Decimal results, and supports one-shot CLI use, script mode, pipe mode, and an interactive REPL. The project achieved more than basic arithmetic: it demonstrates language-design fundamentals, state management, custom errors, user-defined functions, and CLI operations.

---

## Original Goals vs. Actual Outcome

**Original goal:** Build a safer, more educational calculator that avoids `eval()` and demonstrates real parsing and evaluation.

**Actual outcome:** The app became a full mini-language runtime. It supports precedence, grouping, number literal variants, variables, `ans`, constants, user functions, built-in functions, Decimal precision, trig mode, configurable formatting, config files, persistent history, script mode, pipe mode, and REPL commands.

**Gap:** The feature set grew beyond a small 24-hour utility. That is not automatically a failure because this app belongs more naturally in the medium-project category, but the scope should be acknowledged. The app is still disciplined because the complexity is organized around a coherent interpreter architecture rather than scattered feature additions.

---

## Technical Decisions That Paid Off

### Hand-built lexer/parser

This was the most important learning decision. It forced the project to define the calculator language directly instead of borrowing Python’s grammar. It also made position-aware errors possible.

### AST separation

The AST layer kept parsing and evaluation separate. This made it easier to test parser behavior without executing results and easier to reason about evaluator behavior without parsing source every time.

### `CalculatorSession`

The session object became the app’s strongest boundary. It allowed CLI, REPL, script mode, and pipe mode to share the same execution path.

### Decimal arithmetic

Using Decimal made calculator outputs match user expectations for common decimal arithmetic. The test for `0.1 + 0.2` confirms why this choice matters.

### Custom error classes

The custom error hierarchy improved the user experience and prevented raw stack traces from leaking into normal CLI usage.

---

## Technical Decisions That Created Debt

### Custom Decimal trigonometry

Implementing sine and cosine with Decimal series expansion was educational but created complexity. It required normalization, precision padding, epsilon thresholds, and convergence guards. This is a reasonable academic implementation, but it is more maintenance-heavy than delegating to `math` with float conversion.

### REPL commands are string-dispatched

The REPL command handler is simple and readable, but as commands grow, a dictionary-based command registry would scale better than a chain of `if` statements.

### History format is plain text

Plain text is easy to inspect but not robust. If expressions or outputs contain the separator string ` => `, parsing can become ambiguous. JSON Lines would be safer for long-term use.

### Config validation silently normalizes invalid values

This makes startup forgiving, but it can hide user mistakes. A warning mode or config diagnostics command would make bad config easier to discover.

---

## What Was Harder Than Expected

**Operator precedence:** Correctly handling unary minus and exponentiation is subtle. The test case `-2^2 == -4` shows that parser structure matters, not just token order.

**Function definitions vs. function calls:** The parser needed lookahead logic to distinguish `f(x) = x + 1` from `f(x)`. That is a real grammar-design problem.

**Scoped user-defined functions:** Function parameters required temporary local bindings without corrupting global variables. The local scope stack solved this cleanly but added evaluator complexity.

**Decimal math beyond arithmetic:** Addition, multiplication, and division are straightforward with Decimal. Logs, non-integer powers, and trigonometry require extra domain handling and precision management.

**Multi-mode CLI consistency:** One-shot mode, file mode, pipe mode, and REPL mode all have different UX expectations. Sharing the session engine helped keep behavior consistent.

---

## What Was Easier Than Expected

**Basic tokenization:** Once token types were defined, walking the input character by character was clearer than expected.

**AST node modeling:** Dataclasses made the AST concise and readable. Each node type naturally matched a grammar concept.

**Script mode:** Reusing `CalculatorSession.execute()` made script mode almost a loop over lines with error handling.

**Formatter isolation:** Keeping output formatting separate from evaluation prevented display concerns from leaking into the evaluator.

---

## Python-Specific Learnings

- `dataclass(frozen=True, slots=True)` is useful for small immutable model objects.
- `Enum` makes token categories explicit and safer than raw strings.
- `decimal.Decimal` is powerful but requires careful context management.
- `localcontext()` is the right tool for temporary precision changes.
- `argparse` can support a polished CLI without third-party dependencies.
- `Path.home()` and `pathlib.Path` simplify config/history file handling.
- Custom exception classes can carry both messages and source positions.
- Pattern matching with `match` improves readability for operator dispatch.

---

## Architecture Insights

The biggest architectural lesson is that even a calculator becomes manageable when treated as a language pipeline. Trying to parse and evaluate in one pass would have created tangled code. The lexer/parser/AST/evaluator split created natural places for tests, errors, and future features.

Another important insight is that state deserves an explicit owner. Variables, constants, functions, precision, angle mode, and `ans` all belong in the environment/session layer, not scattered across CLI functions or globals.

The app also shows a useful pattern for CLI projects: build a core engine first, then make each interface mode a thin adapter around that engine.

---

## Testing Gaps

The inspected tests cover major behavior, including lexing, parsing, evaluator math, user-defined functions, built-ins, custom errors, and CLI script mode. Remaining gaps include:

- config loading edge cases,
- history persistence edge cases,
- REPL command behavior under interactive input,
- formatter behavior across all precision and format modes,
- log/log10/log2 domain and precision cases,
- tangent near undefined angles,
- non-integer powers and exponent limit errors,
- script mode with mixed successful and failed lines,
- function arity errors and attempts to redefine built-ins/constants,
- invalid config normalization.

These gaps do not invalidate the project, but they identify the next layer of verification needed if this app were treated as production software.

---

## Reusable Patterns Identified

- Lexer → parser → AST → evaluator pipeline for small DSLs.
- Frozen dataclasses for syntax tree nodes and token objects.
- Session facade for sharing logic across CLI modes.
- Environment object for mutable runtime state.
- Error classes with source-position rendering.
- Script mode that continues after line-level failures but returns a nonzero final exit code.
- Formatter object for separating computation from presentation.
- Local scope stack for user-defined function calls.

---

## If I Built This Again

The highest-impact change would be to introduce a formal grammar document and keep it next to the parser tests. The parser is readable, but a grammar reference would make future syntax changes safer.

The second change would be to add a structured command registry for the REPL. The current command chain is fine at this size, but a registry would make help text, command dispatch, and future commands easier to maintain.

The third change would be to move history persistence to JSON Lines so entries remain unambiguous and easier to migrate later.

---

## Open Questions

- Should variables and user-defined functions persist across sessions, or should only history persist?
- Should the app add a machine-readable `--json` error/result mode?
- Should Decimal trig remain custom, or should the project explicitly trade precision for simplicity by using `math` float functions?
- Should the language eventually support comments after expressions in script mode?
- Should the parser support multiple statements in one input string?
- Should recursive user-defined functions be allowed, limited, or explicitly rejected?
- Should config validation warn users instead of silently normalizing invalid values?

---

*Constitution v2.0 checklist: This document satisfies Article 5 by identifying design rationale, intentional omissions, weaknesses, scaling concerns, testing gaps, and the next likely refactors. The project also supports Article 7 because it demonstrates progression from simple CLI scripting into language implementation and stateful runtime design.*
