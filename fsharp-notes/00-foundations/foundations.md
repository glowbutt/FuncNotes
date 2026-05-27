# Foundations (Lectures 1–2)

Cheat sheet for F# basics: the FP mindset, the REPL, expressions, immutability,
operators, type inference, functions, and pipelines/composition.

> Covered elsewhere: lists/records/tuples/DUs → `01-data-types`;
> recursion + higher-order functions (`map`/`filter`/`fold`) → `02-functions-and-recursion`.

---

## 1. FP mindset

- **Declarative**: describe *what* a result is, not *how* to compute it.
  Imperative/OO describe *how* (state + state-changing steps).
- A program is a **mathematical function**; running it = **evaluating** it.
- Built on the **λ-calculus** (Church, ~1930): `f(x) = x + 2` is `λx. x + 2`.
- Core ideas: first-class & higher-order functions, type inference &
  polymorphism, recursion, algebraic data types, immutability.

---

## 2. The REPL

Input ends with `;;`. F# replies with `val <name> : <type> = <value>`.

```fsharp
> 2 * 3 + 4;;
val it : int = 10        // `it` always names the last unnamed result
```

- A **binding** maps a name to a value: `price ↦ 125`.
- An **environment** is a collection of bindings.

```fsharp
> let price = 25 * 5;;        // val price : int = 125
> let newPrice = price * 2;;  // val newPrice : int = 250
// environment: [price ↦ 125; newPrice ↦ 250]
```

**Primitive types:** `int` (`42`), `float` (`1.0`), `bool` (`true`),
`string` (`"hi"`), `char` (`'a'`).

---

## 3. Expressions

In F# (almost) **everything is an expression** — it evaluates to a value.
This replaces imperative *statements*, which only produce side effects.

**If-expression** — both branches required and must have the *same type*:

```fsharp
if b then e1 else e2
1 + (if 1 > 1 then 1 else 2)   // = 3
```

**`let ... in`** (nested/local bindings): the local name is only in scope
in the body.

```fsharp
let area =
    let pi = 3.14159
    let r  = 2.0
    pi * r * r
```

**Evaluation = reduction** by substitution (`⤳` = "reduces to"):

```text
fact 3 ⤳ 3 * fact 2 ⤳ 3 * 2 * fact 1 ⤳ ... ⤳ 3 * 2 * 1 * 1 ⤳ 6
```

---

## 4. Immutability

- Bindings are **immutable by default**: `let x = 5` cannot be reassigned.
- A second `let x = ...` **shadows** the old one (new binding, no mutation).
- Opt into mutation explicitly (used *sparingly*):

```fsharp
let mutable x = 0
x <- x + 1          // `<-` assigns to a mutable binding
```

Why it matters: easier to reason about, no hidden side effects, safe to
parallelise.

### Side effects & sequencing (`;`)

A **side effect** is anything a function does besides return a value — printing,
or mutating (`<-`, `arr.[i] <- x`). Such expressions return **`unit`** (`()`).

The semicolon **sequences** two expressions: `e1 ; e2` evaluates `e1` (for its
effect, discarding its result), then evaluates `e2` and returns *its* value. The
left side **must be `unit`**, else you get a warning.

```fsharp
let eat t p =
    getLeftFork t p ; getRightFork t p   // run left (unit), then right; result = right
```

A **newline at the same indentation does the same thing** — usually preferred:

```fsharp
let eat t p =
    getLeftFork t p        // unit
    getRightFork t p       // value of the block = this last expression
```

- To discard a non-`unit` result so it can sit on the left, pipe it to
  `ignore`: `expensive () |> ignore`.
- Don't confuse this `;` with the **separator** `;` in `[1; 2; 3]` or
  `{ A = 1; B = 2 }` — same symbol, different role.

---

## 5. Operators

| Kind | Operators |
|------|-----------|
| Arithmetic | `+  -  *  /  %`  (`/` is integer division on `int`) |
| Comparison | `=` (equal), `<>` (not equal), `<  >  <=  >=` |
| Boolean | `&&`  `\|\|`  `not` |
| String | `+` (concatenation) |

- **No implicit numeric conversion**: can't mix `int` and `float`; convert with
  `float x` / `int x`.
- **Operators are functions.** Wrap in parentheses to use prefix:

```fsharp
(+) 2 3        // = 5
List.reduce (+) [1;2;3]
```

---

## 6. Type inference & polymorphism

F# **infers** types automatically (no annotations needed):

```fsharp
let rec pow = function
    | (x, 0) -> 1.0
    | (x, n) -> x * pow (x, n - 1)
// 1.0 is float ⇒ result float ⇒ x float ⇒ pow : float * int -> float
```

- When a type isn't constrained, F# **generalises** it to a **polymorphic**
  type using type variables `'a`, `'b`, …

```fsharp
let id x = x        // id : 'a -> 'a
List.length         // 'a list -> int
```

- Annotate when you want to fix a type: `let f (x: int) : int = x + 1`.

---

## 7. Functions

**Declaration** mirrors value bindings; type is `<arg> -> <return>`:

```fsharp
let circleArea r = System.Math.PI * r * r   // float -> float
```

**Anonymous functions** (`fun`) and **pattern functions** (`function`):

```fsharp
fun r -> System.Math.PI * r * r             // float -> float
function | 0 -> true | _ -> false           // int -> bool  (`_` = wildcard)
```

> Incomplete patterns compile but warn — cover all cases (use `_`).

**Recursion** needs the `rec` keyword:

```fsharp
let rec fact = function
    | 0 -> 1
    | x -> x * fact (x - 1)
```

### Currying & partial application

`let f x y = ...` takes args **one at a time**; `let f (x, y) = ...` takes
**one tuple**:

```fsharp
let f x y = x + y         // int -> int -> int   (curried)
let g (x, y) = x + y      // int * int -> int    (one pair)

f 5                       // ⤳ fun y -> 5 + y    (partial application)
let add5 = f 5            // specialise for later use
```

Prefer curried functions — partial application + first-class functions is the
power combo.

---

## 8. Pipelines & composition

**Pipe** feeds a *value* into a function (reads left→right, fewer parens):

```fsharp
x |> f          // = f x
[1;2;3] |> List.map (fun x -> x * 2) |> List.sum   // = 12
f <| x          // = f x   (reverse pipe, occasionally useful)
```

**Composition** combines *functions* into a new function:

```fsharp
let double x = x * 2
let inc    x = x + 1
let f = double >> inc      // (f >> g) x = g (f x): double first, then inc
let h = double << inc      // (f << g) x = f (g x): inc first, then double
```

**Pipes work on values, composition works on functions.**
Both encourage step-by-step, transformation-based code.
