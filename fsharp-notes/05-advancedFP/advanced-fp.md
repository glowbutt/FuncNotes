# Advanced FP (Lectures 10–12)

Three advanced topics: **monads** (chaining computations that carry context),
**parser combinators** (building big parsers from small ones), and **async /
concurrency / parallelism**.

> Covered elsewhere: `bind`, `Option`/`Result`, expression trees → `01-data-types`;
> combinators are higher-order functions → `02-functions-and-recursion`.

---

## 1. Monads

What is a Monad?\
A monad is a wrapper around a value that also carries some extra context (like state, errors, lists, etc.). The wrapper lets you chain computations together without manually threading that context everywhere.

A State Monad specifically carries:

- A computation (a function)
- That computation takes a state as input and returns a (result, new state) pair

So a state monad wraps a function **state → (value, state)**

### The core idea

A monad is something that has:

- a way to wrap a value
- a way to chain computations

In F# terms:

**ret — wrapping** (return / unit)

- Wraps a plain value into the monad, doing nothing to the state

```fsharp
let ret x = SM (fun s -> Some (x, s))
//                   ↑     ↑
//               result  state unchanged
```

`ret 5` gives you a state computation that, given any state `s`, returns `(5, s)`. It doesn't touch the state.

**fail**

```fsharp
let fail = SM (fun _ -> None)
```

just a computation that always fails. use it in bind.

**bind**

```fsharp
let bind f (SM a) : StateMonad<'b> =
    SM (fun s ->
        match a s with
        | Some (x, s') -> let (SM g) = f x
                          g s'
        | None -> None)
```

This chains two computations together. Step by step:

- runs the first computation `a` on the current state `s`
- If that succeeds with `(x, s')`, it calls `f x`. This gives back a new monadic computation (let's call it `g`)
- It then runs `g` on the updated state `s'`
- If step 1 fails, the whole thing returns `None`. short-circuit, no further computation runs

This is how state is threaded through a seq of steps without having to pass it manually.

`>>=` is just bind with arguments flipped:

```fsharp
let (>>=) x f = bind f x
```

So `computation >>= f` means "run this computation, then pass the result to f". It lets you write pipelines left-to-right:

```fsharp
getChar >>= (fun c -> checkLetter c >>= (fun _ -> ret c))
```

`>>>=` is "sequence" — run two computations in order, but throw away the result of the first:

```fsharp
let (>>>=) x y = x >>= (fun _ -> y)
```

Useful when you only care about the side effect (state update) of the first computation.

**Monad laws:**

- Law 1: `ret a >>= f = f a` ("left identity")

  Wrapping `a` in `ret` and then binding `f` is the same as just calling `f a` directly. `ret` does nothing interesting.

- Law 2: `m >>= ret = m` ("right identity")

  Binding `ret` onto a computation does nothing. `ret` just re-wraps the value without touching state, so `m >>= ret` gives back the same result as `m`.

- Law 3: `(m >>= f) >>= g = m >>= (fun x -> f x >>= g)` ("associativity")

  Chaining doesn't care about parenthesisation. Whether you go (m then f) then g or m then (f then g), you get the same result. This is what lets you build long pipelines without worrying about grouping.

---

## 2. Parsers

### Parsers — basics

Parsing is the process of taking raw input (usually a string) and converting it into a structured form.

Examples:

```text
"123"              -> integer 123
"a + b * c"        -> expression tree
"if x then y else z" -> AST node
```

A parser is basically a function:

- input string -> parsed value + remaining input (or failure)

Combinator parsers:\
Instead of writing one big parser, you build small parsers and combine them.
small parsers + combinators = big parser

### Transformation (mapping)

`|>>` (map) — transforms parsed result

```fsharp
pint32 |>> (fun x -> x + 1)
```

Meaning: parse int, then add 1

### Sequencing

`.>>.` — (AND THEN, keep both results)

run parser A then parser B, return tuple `(A result, B result)`

```fsharp
pchar '(' .>>. pint32      // Result: ('(', 123)
```

`.>>` keeps only left side, `>>.` keeps only right side.

### OR

`<|>` — try left parser, if it fails try right parser

```fsharp
pchar '+' <|> pchar '-'
```

### REPETITION

`many p` — parse 0 or more occurrences\
`many1 p` — parse 1 or more occurrences

```fsharp
many (satisfy isLetter)    // Result: list of chars
```

### OPTIONAL PARSING

`opt p` — optional parser

Returns: `Some value` if found, `None` if not found

### COMMON HELPERS

`between pOpen pClose pContent` — parses content inside delimiters

```fsharp
between (pchar '(') (pchar ')') pint32   // number inside parentheses
```

### LIST PARSERS

`sepBy p sep` — parse list of `p` separated by `sep`

```fsharp
sepBy pint32 (pchar ',')   // "1,2,3"  ->  [1; 2; 3]
```

### RECURSIVE PARSERS

Sometimes grammar is recursive:

```text
expression -> expression + term | term
```

To define this you use `createParserForwardedToRef`. This allows:

- defining parser before it exists
- filling it later

---

## 3. Async, Concurrency & Parallelism

### 3.1 Intro

three related but different ideas:

- **Synchronous execution**: one thing happens at a time
- **Concurrency**: multiple tasks are *in progress* (interleaved)
- **Parallelism**: multiple tasks run *at the same time*

In F#, `async {}` is mainly about **concurrency**, not automatic parallelism.

### 3.2 What is `Async<'T>`?

An `Async<'T>` is:

> a *description* of a computation that will eventually produce a value of type `'T`

It does NOT run immediately.

```fsharp
let work =
    async {
        return 1 + 1
    }
```

At this point: nothing has executed — it's just a recipe.

### 3.3 How to RUN async code

**`Async.RunSynchronously`**

```fsharp
let result = Async.RunSynchronously work
```

- runs the async computation
- blocks the current thread
- returns `'T`

Think: "run async code like normal blocking code".

**`Async.Start`**

```fsharp
Async.Start work
```

- runs in background
- does NOT block
- returns `unit`

You don't get the result directly.

### 3.4 Async workflows (`async {}`)

```fsharp
async {
    let! x = asyncComputation
    return x + 1
}
```

Key ideas:

- `let!` = wait for async result
- `return` = wrap result
- `return!` = chain async computations

### 3.5 Concurrency vs Parallelism

**Concurrency (Async)** — F# switches between tasks during waits.

```text
Task A: ----wait----
Task B: ----wait----
```

**Parallelism (CPU cores)** — actually simultaneous execution.

```text
Core 1: Task A running
Core 2: Task B running
```

### 3.6 `Async.Parallel`

```fsharp
Async.Parallel : Async<'T> list -> Async<'T[]>
```

It means: run multiple async computations at the same time and collect results.

```fsharp
let tasks =
    [
        async { return 1 }
        async { return 2 }
        async { return 3 }
    ]

Async.Parallel tasks
|> Async.RunSynchronously
// [|1; 2; 3|]
```

### 3.7 Common mistake (VERY IMPORTANT)

**WRONG** — inputs are NOT `Async<'T>`, they are plain values:

```fsharp
[1;2;3]
|> List.map (fun x -> x + 1)
|> Async.Parallel
```

**RIGHT**:

```fsharp
[1;2;3]
|> List.map (fun x -> async { return x + 1 })
|> Async.Parallel
```

### 3.8 Why `Async.Parallel` often "does nothing"

If your work is tiny (like string operations), CPU cheap, or has no waiting (I/O),
then overhead > benefit — it may feel like nothing changed.

### 3.9 `Async.RunSynchronously` danger

```fsharp
Async.RunSynchronously (Async.Parallel tasks)
```

This blocks the main thread, waits for all tasks, and removes the async benefit
at top level. Use mainly in scripts or the main entry point.

### 3.10 `let!` vs `let`

```fsharp
let  x = asyncComputation   // x is Async<'T>  (no wait)
let! x = asyncComputation   // x is 'T         (waits)
```

### 3.11 `return` vs `return!`

```fsharp
return 5            // wrap value → Async<int>
return! otherAsync  // flatten async
```

### 3.12 Why a Caesar example fails

```fsharp
text.Split(' ')
|> Array.map (fun str -> encrypt str offset)
```

Problem: `encrypt` returns `string`, not `Async<string>`, so `Async.Parallel` cannot be used. Fix:

```fsharp
text.Split(' ')
|> Array.map (fun str -> async { return encrypt str offset })
|> Async.Parallel
```

### 3.13 When should you use Async?

Use Async when: file IO, network calls, waiting (sleep, delays), independent tasks that can overlap.

DON'T use it when: simple loops, small CPU work, pure transformations.

### 3.14 When should you use Parallel?

Use parallel when: CPU-heavy work, independent computations, large datasets.

```fsharp
Array.Parallel.map expensiveFunction data
```

### 3.15 Simple mental model

- **Async** = "I will wait for something later"
- **Parallel** = "I want multiple CPU cores now"

### 3.16 Summary

- `Async<'T>` = description of work
- `Async.RunSynchronously` = run and block
- `Async.Start` = run in background
- `Async.Parallel` = run multiple async tasks together
- async does NOT mean parallel automatically
