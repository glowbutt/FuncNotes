# F# Data Types — Complete Exam Cheat Sheet

---

## Immutability by Default

F# values are **immutable** by default. Use `mutable` + `<-` to opt in:

```fsharp
let x = 5           // immutable
let mutable y = 5   // mutable
y <- 10             // ok
x <- 10             // ❌ compiler error
```

Prefer immutability — it avoids side effects and makes reasoning easier.

---

## Primitive Types

```fsharp
let i : int    = 42
let f : float  = 3.14
let b : bool   = true
let s : string = "hello"
let c : char   = 'a'
let u : unit   = ()   // "nothing" — like void, but a real value
```

Type annotations are optional — F# **infers types** automatically:

```fsharp
let square x = x * x          // inferred: int -> int
let square (x:float) = x * x  // forced:   float -> float
```

---

## Tuples

Quick, anonymous grouping. No field names. Components accessed by position or destructuring.

```fsharp
let point  = (3, 4)               // int * int
let triple = ("Alice", 30, true)  // string * int * bool

// Destructuring
let (x, y) = point      // x = 3, y = 4
let (_, b, _) = triple  // b = 30 (wildcard _ ignores)

// Built-in helpers for pairs
fst (1, "a")  // 1
snd (1, "a")  // "a"

// In function patterns
let add (a, b) = a + b   // add : int * int -> int
add (3, 4)               // 7
```

**Use when:** quick, throwaway grouping — no semantic weight needed.

---

## Records

Named fields. Like a struct or named tuple. Must declare type first.

```fsharp
// Declare
type Person = { Name: string; Age: int; Birthday: int * int }

// Create
let alice = { Name = "Alice"; Age = 30; Birthday = (3, 7) }

// Access fields
let n = alice.Name          // "Alice"
let a = alice.Age           // 30

// "Update" — creates a copy, original is unchanged
let older = { alice with Age = 31 }

// Pattern matching on records
let greet { Name = n; Age = a } =
    printfn "%s is %d years old" n a

// Equality is structural (field-by-field)
alice = { Name = "Alice"; Age = 30; Birthday = (3, 7) }  // true
```

**Note:** Field order doesn't matter when creating or comparing records.

**Use when:** a fixed set of named fields all belong together (a `Person`, `Config`, `Point`).

---

## Discriminated Unions (DU) — Tagged Values / Algebraic Data Types

A value that is **exactly one** of several distinct cases, each optionally carrying data.
Also called: tagged values, sum types, or algebraic data types in HR.

```fsharp
// Declare
type Shape =
    | Circle   of float
    | Square   of float
    | Triangle of float * float * float

// Create — constructors are functions
let c = Circle 1.2                  // Shape
let s = Square 3.4                  // Shape
let t = Triangle (3.0, 4.0, 5.0)   // Shape

// Pattern match — compiler forces ALL cases
let area shape =
    match shape with
    | Circle r          -> System.Math.PI * r * r
    | Square a          -> a * a
    | Triangle (a,b,c)  ->
        let s = (a + b + c) / 2.0
        sqrt (s*(s-a)*(s-b)*(s-c))

area (Circle 1.2)            // 4.52...
area (Triangle(3.0,4.0,5.0)) // 6.0
```

**Key rule:** A constructor only matches itself — not other constructors.

**Cases without data** (enumerations):

```fsharp
type Direction = | North | South | East | West

let move dir =
    match dir with
    | North -> "going north"
    | South -> "going south"
    | East  -> "going east"
    | West  -> "going west"
```

**Use when:** a value can be one of several mutually exclusive alternatives.

---

## Option — The Canonical DU

Replaces `null`. Either there is a value, or there isn't.

```fsharp
// Built-in definition:
// type 'a option = | Some of 'a | None

let safeDivide a b =
    if b = 0 then None
    else Some (a / b)

match safeDivide 10 2 with
| Some v -> printfn "Result: %d" v
| None   -> printfn "Division by zero"
```

---

## Result — Errors Without Exceptions

```fsharp
// type Result<'a,'e> = | Ok of 'a | Error of 'e

let parseInt (s: string) : Result<int, string> =
    match System.Int32.TryParse(s) with
    | true,  v -> Ok v
    | false, _ -> Error $"'{s}' is not a number"
```

---

## Recursive Types

Types that refer to themselves. Used to build trees, expressions, linked structures, etc.

```fsharp
// Binary tree
type 'a Tree =
    | Leaf
    | Node of 'a * 'a Tree * 'a Tree

// Create
let myTree = Node(1, Node(2, Leaf, Leaf), Node(3, Leaf, Leaf))

// Recurse over it
let rec size = function
    | Leaf           -> 0
    | Node(_, l, r)  -> 1 + size l + size r

size myTree  // 3
```

Another classic — arithmetic expressions:

```fsharp
type Expr =
    | Num of int
    | Add of Expr * Expr
    | Mul of Expr * Expr

let rec eval = function
    | Num n         -> n
    | Add (e1, e2)  -> eval e1 + eval e2
    | Mul (e1, e2)  -> eval e1 * eval e2

// Represents: (2 + 3) * 4
eval (Mul(Add(Num 2, Num 3), Num 4))  // 20
```

**Use when:** data is inherently hierarchical or self-referential (trees, expressions, parsers).

---

## Lists

Immutable, singly-linked. All elements must be the same type.

```fsharp
let xs = [1; 2; 3]
let ys = 0 :: xs       // prepend → [0; 1; 2; 3]
let zs = xs @ [4; 5]   // append  → [1; 2; 3; 4; 5]

// Pattern matching
match xs with
| []       -> "empty"
| [x]      -> "singleton"
| x :: rest -> $"head={x}, tail has {List.length rest} elements"

// Common operations
List.map    (fun x -> x * 2) [1;2;3]   // [2; 4; 6]
List.filter (fun x -> x > 1) [1;2;3]   // [2; 3]
List.fold   (fun acc x -> acc + x) 0 [1;2;3]  // 6
```

---

## Exceptions

Signal errors. Can be raised and caught.

```fsharp
// Declare a named exception
exception MyError of string

// Raise
raise (MyError "something went wrong")
failwith "quick error message"    // built-in shorthand

// Catch
try
    let result = someRiskyOperation()
    printfn "OK: %d" result
with
| MyError msg -> printfn "Error: %s" msg
| :? System.DivideByZeroException -> printfn "Division by zero"
```

---

## Generic Types

Both records and DUs can be parameterized with type variables:

```fsharp
// Generic record
type 'a Store = { Data: 'a; Owner: int option }

let s : int Store = { Data = 42; Owner = Some 1 }

// Generic DU
type 'a MyOption =
    | MySome of 'a
    | MyNone

// Generic tree (from above)
type 'a Tree = | Leaf | Node of 'a * 'a Tree * 'a Tree
```

---

## DU vs Record — When to Use Which?

| Situation | Use |
|-----------|-----|
| Fixed set of named fields that always coexist | **Record** |
| Value can be *one of several distinct things* | **DU** |
| Modelling a state machine or game state | **DU** |
| Success/failure/absence | **DU** (`Result`, `Option`) |
| Hierarchical or recursive data | **DU** |
| Config, entity, data transfer object | **Record** |

```fsharp
// ✅ Record: a player always has BOTH a name AND a score
type Player = { Name: string; Score: int }

// ✅ DU: a game state is exactly ONE of these at a time
type GameState =
    | Running of Player
    | Won     of Player
    | Draw
```

A record says **"all of these things together"**.
A DU says **"exactly one of these alternatives"**.

---

## Quick Comparison Table

| Type | Named fields | Multiple cases | Pattern match | Recursive | Immutable |
|------|:-:|:-:|:-:|:-:|:-:|
| Tuple  | ❌ | ❌ | ✅ | ❌ | ✅ |
| Record | ✅ | ❌ | ✅ | ❌ | ✅ (default) |
| DU     | per-case | ✅ | ✅ exhaustive | ✅ | ✅ |
| List   | ❌ | ❌ | ✅ | ✅ | ✅ |

