# Data Types (Lectures 1–2, 4)

How to model data in F#: primitives, tuples, records, discriminated unions
(algebraic data types), `Option`/`Result`, and recursive types — plus pattern
matching, the tool that takes them apart.

> Covered elsewhere: immutability, type inference & polymorphism → `00-foundations`;
> list/collection *operations* (`map`/`filter`/`fold`) → `02-functions-and-recursion`
> and `04-collections`.

---

## 1. Primitive & unit types

```fsharp
let i : int    = 42
let f : float  = 3.14
let b : bool   = true
let s : string = "hello"
let c : char   = 'a'
let u : unit   = ()    // "nothing" — like void, but a real value
```

Annotations are optional — F# **infers** types. `int` and `float` never mix
implicitly; convert with `float x` / `int x`.

---

## 2. Tuples — anonymous grouping

Fixed-size, ordered, **no field names**. Type is written with `*`.

```fsharp
let point  = (3, 4)               // int * int
let triple = ("Alice", 30, true)  // string * int * bool

let (x, y)    = point             // destructure: x = 3, y = 4
let (_, b, _) = triple            // wildcard _ ignores a component
fst (1, "a")                      // 1     (pairs only)
snd (1, "a")                      // "a"
```

**Use when:** a quick, throwaway grouping with no semantic weight.

---

## 3. Records — named fields

A fixed set of named fields that always coexist. Declare the type first.

```fsharp
type Person = { Name: string; Age: int }

let alice = { Name = "Alice"; Age = 30 }   // field order doesn't matter
let n     = alice.Name                     // "Alice"
let older = { alice with Age = 31 }        // copy-and-update; alice unchanged

// pattern match on fields
let greet { Name = n; Age = a } = printfn "%s is %d" n a

alice = { Age = 30; Name = "Alice" }       // true — equality is structural
```

**Use when:** an entity has a fixed set of fields all present at once
(`Person`, `Config`, `Point`). A record says *"all of these together."*

---

## 4. Discriminated Unions (algebraic data types)

A value that is **exactly one** of several cases, each optionally carrying data.
Also called *inductively defined types*, *tagged values*, *sum types*, or
*disjoint unions*. Declared with `type` (not `let`); a DU concisely says **how
the members of a type are created**.

```fsharp
type Shape =
    | Circle   of float
    | Square   of float
    | Triangle of float * float * float

let c = Circle 1.2                 // constructors are functions: Shape
let t = Triangle (3.0, 4.0, 5.0)
```

Cases **without data** behave like an enum (Java `enum`):

```fsharp
type Direction = North | South | East | West
```

### Pattern matching

The way you consume a DU. The compiler **checks all cases are covered**
(incomplete matches warn). A constructor only matches itself.

```fsharp
let area shape =
    match shape with
    | Circle r         -> System.Math.PI * r * r
    | Square a         -> a * a
    | Triangle (a,b,c) -> let s = (a + b + c) / 2.0
                          sqrt (s*(s-a)*(s-b)*(s-c))
```

**Use when:** a value is one of several mutually exclusive alternatives — a
state machine, a command, success/failure. A DU says *"exactly one of these."*

### Unwrapping: binding through a pattern

A `let` doesn't only bind names — it can bind through a **pattern**. For a
**single-case** DU (a wrapper), that lets you pull the contents out in one line:

```fsharp
type Board = T of int[]          // a single-case DU wrapping an array
let t = T [| 1; 2; 3 |]

let (T arr) = t                  // arr : int[]  — unwrapped in the binding
let area (T arr) = Array.sum arr // same trick in a function parameter
```

This is safe because the pattern is **irrefutable** — there's only one case, so
it always matches. (It's exactly the `let (SM a) = …` idiom in the monads
section of `05-advancedFP`.) The same works for any irrefutable pattern —
tuples and records:

```fsharp
let (x, y)        = (3, 4)            // tuple
let { Name = n }  = { Name = "A"; Age = 1 }   // record field
```

> ⚠️ A **refutable** (multi-case) pattern compiles but warns and may crash at
> runtime if it doesn't match: `let (Some x) = o` or `let x :: rest = xs`. For
> those, use `match` instead.

**…and "wrapper" types that aren't single-case DUs?** The analog differs:
- `Async<'T>` — unwrap with `let! x = …` inside an `async { }` workflow (→ `05-advancedFP`).
- `seq` / `Set` / `Map` — *abstract* types with no visible constructor, so there's
  nothing to pattern-match; read them with module functions (`Seq.head`,
  `Set.minElement`, `Map.tryFind`) or convert (→ `04-collections`).

---

## 5. Option & Result — the canonical DUs

`Option` replaces `null`: there either is a value or there isn't.

```fsharp
// type 'a option = Some of 'a | None
let safeDivide a b = if b = 0 then None else Some (a / b)

match safeDivide 10 2 with
| Some v -> printfn "Result: %d" v
| None   -> printfn "Division by zero"
```

`Result` carries an error instead of just absence — errors without exceptions.

```fsharp
// type Result<'a,'e> = Ok of 'a | Error of 'e
let parseInt (s: string) : Result<int, string> =
    match System.Int32.TryParse s with
    | true,  v -> Ok v
    | false, _ -> Error $"'{s}' is not a number"
```

---

## 6. Recursive types — trees & expressions

A type whose cases refer to itself: how you model hierarchical data.

```fsharp
type Tree =
    | Leaf
    | Node of Tree * int * Tree

let rec sum t =
    match t with
    | Leaf          -> 0
    | Node (l,n,r)  -> sum l + n + sum r
```

The classic **expression tree** (a tiny calculator) — data *represents* a program:

```fsharp
type Expr =
    | Num of int
    | Add of Expr * Expr
    | Mul of Expr * Expr

let rec eval = function
    | Num n        -> n
    | Add (e1, e2) -> eval e1 + eval e2
    | Mul (e1, e2) -> eval e1 * eval e2

eval (Mul (Add (Num 2, Num 3), Num 4))   // (2 + 3) * 4 = 20
```

**Use when:** data is inherently hierarchical or self-referential — trees,
expressions, parsers. (Recursing over these → `02-functions-and-recursion`.)

---

## 7. Lists — built-in recursive DU

Immutable, singly-linked, all elements the same type. Conceptually
`[] | head :: tail`, so they pattern-match like any DU.

```fsharp
let xs = [1; 2; 3]
let ys = 0 :: xs        // prepend  → [0; 1; 2; 3]   (cheap)
let zs = xs @ [4; 5]    // append   → [1; 2; 3; 4; 5]

match xs with
| []        -> "empty"
| [x]       -> "one element"
| x :: rest -> $"head={x}, {List.length rest} more"
```

> Operations (`map`/`filter`/`fold`) and other collections (arrays, sets, maps,
> sequences) live in `04-collections`.

---

## 8. Generic types

Records and DUs can take type parameters (`'a`, `'b`, …):

```fsharp
type 'a Store = { Data: 'a; Owner: int option }
type 'a Tree  = Leaf | Node of 'a * 'a Tree * 'a Tree   // tree of any element type
```

---

## 9. Exceptions (when a value can't express the error)

```fsharp
exception MyError of string
raise (MyError "went wrong")
failwith "quick error"            // shorthand

try someRiskyOp ()
with
| MyError msg -> printfn "Error: %s" msg
| :? System.DivideByZeroException -> printfn "div by zero"
```

Prefer `Option`/`Result` for *expected* failures; reserve exceptions for the
truly exceptional.

---

## 10. Record vs DU — which one?

| Situation | Use |
|-----------|-----|
| Fixed set of fields that always coexist | **Record** |
| Value is *one of* several distinct things | **DU** |
| State machine / game state | **DU** |
| Success / failure / absence | **DU** (`Result`, `Option`) |
| Hierarchical or recursive data | **DU** (recursive) |
| Config, entity, DTO | **Record** |

```fsharp
type Player = { Name: string; Score: int }      // ✅ always BOTH fields
type GameState =                                 // ✅ exactly ONE at a time
    | Running of Player
    | Won     of Player
    | Draw
```

### Quick comparison

| Type | Named fields | Multiple cases | Recursive | Immutable |
|------|:-:|:-:|:-:|:-:|
| Tuple  | ❌ | ❌ | ❌ | ✅ |
| Record | ✅ | ❌ | ❌ | ✅ (default) |
| DU     | per-case | ✅ | ✅ | ✅ |
| List   | ❌ | ❌ | ✅ | ✅ |
