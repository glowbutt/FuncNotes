# Functions & Recursion (Lectures 1–5, 8)

The two engines of F#: **higher-order functions** (functions that take or return
functions - `map`/`filter`/`fold`) replace most loops, and **recursion** is how
functions repeat. Then how to make recursion safe with **tail recursion**.

> Covered elsewhere: function declaration, currying, partial application,
> pipes (`|>`) & composition (`>>`) → `00-foundations`; the data types you
> recurse over (DUs, trees) → `01-data-types`; collection-specific helpers →
> `04-collections`.

---

## 1. Higher-order functions

A **higher-order function (HOF)** takes a function as an argument and/or returns
one. Because functions are values in F#, this is ordinary. HOFs let you write
short, declarative code and **replace loops** - done well, programs become
concise and easy to read.

```fsharp
let twice f x = f (f x)          // ('a -> 'a) -> 'a -> 'a
twice (fun x -> x + 3) 10        // 16

let adder n = fun x -> x + n     // returns a function
let add5 = adder 5               // add5 7 = 12
```

---

## 2. map, filter, fold

Three HOFs cover most list processing. (They exist for every collection, e.g.
`List.map`, `Array.map`, `Seq.map`.)

| Function | Does | Signature (`List`) |
|----------|------|--------------------|
| `map`    | transform every element | `('a -> 'b) -> 'a list -> 'b list` |
| `filter` | keep elements matching a predicate | `('a -> bool) -> 'a list -> 'a list` |
| `fold`   | collapse a list to one value | `('s -> 'a -> 's) -> 's -> 'a list -> 's` |

```fsharp
List.map    (fun x -> x * 2)      [1;2;3]   // [2; 4; 6]
List.filter (fun x -> x % 2 = 1)  [1;2;3;4] // [1; 3]
List.fold   (fun acc x -> acc + x) 0 [1;2;3]// 6
```

**`fold` is the general loop.** It threads an accumulator left-to-right:

```text
fold f acc [x1; x2; …; xn]  =  f (… (f (f acc x1) x2) …) xn
```

Evaluation of `List.fold (-) 0 [1; 2; 3]` (note: left-associative):

```text
fold (-) 0 [1;2;3] ⤳ fold (-) (0-1) [2;3] ⤳ fold (-) (-1-2) [3]
                   ⤳ fold (-) (-3-3) []   ⤳ -6
```

`foldBack` is the right-to-left twin (list first, state last):
`('a -> 's -> 's) -> 'a list -> 's -> 's`.

```fsharp
List.foldBack (fun x acc -> x :: acc) [1;2;3] []   // [1; 2; 3] (rebuilds)
```

### Chaining them

Compose a pipeline with `|>`. "Last digit of every odd number, as a string":

```fsharp
let mergeLastDigits lst =
    lst
    |> List.filter (fun x -> x % 2 = 1)     // drop even numbers
    |> List.map    (fun x -> x % 10)        // keep the last digit
    |> List.fold   (fun acc x -> acc + string x) ""

mergeLastDigits [123; 124; 5; 1233]         // "353"
```

The same thing point-free with composition (`>>`) reads worse - prefer the
piped form. **Become good friends with `|>`, `>>`, `map`, `filter`, `fold`.**

---

## 3. Recursion

A function is **recursive** when it calls itself. F# requires the `rec` keyword,
and you usually branch with pattern matching: a **base case** stops, a
**recursive case** shrinks the problem toward it.

```fsharp
let rec fact (x: int) : int =
    match x with
    | 0 -> 1                 // base case
    | x -> x * fact (x - 1)  // recursive case
```

### Evaluation = reduction (HR §1.4)

Substitute the definition repeatedly (`⤳` = "reduces to"):

```text
fact 3 ⤳ 3 * fact 2
       ⤳ 3 * (2 * fact 1)
       ⤳ 3 * (2 * (1 * fact 0))
       ⤳ 3 * (2 * (1 * 1))
       ⤳ 6
```

### What happens in the stack and heap

Each call pushes a **stack frame** holding its parameters and the *work still
pending after the recursive call returns* - here the multiplication `x * _`.
The frames pile up to a depth equal to the recursion depth, then the base case
fires and they **unwind**, doing the deferred work on the way out:

```text
push fact 3 → push fact 2 → push fact 1 → push fact 0   (stack grows)
return 1 → 1*1 → 2*1 → 3*2 = 6                          (stack unwinds)
```

The **stack** holds these frames; immutable values like list cells and closures
live on the **heap**. Frames are finite, so recursion that is too deep (e.g.
`fact 1_000_000`) overflows the stack with a `StackOverflowException`. The fix
is tail recursion (§6).

---

## 4. Mutual recursion

Two functions that call each other are defined together with `let rec … and …`,
so each is in scope for the other.

```fsharp
let rec isEven n = if n = 0 then true  else isOdd  (n - 1)
and     isOdd  n = if n = 0 then false else isEven (n - 1)

isEven 10   // true
```

---

## 5. Recursion over recursive types

Recursive *types* (`01-data-types`) are consumed by recursive *functions* with
the same shape - one match case per constructor:

```fsharp
type Tree = Leaf | Node of Tree * int * Tree

let rec sum t =
    match t with
    | Leaf         -> 0                  // base case
    | Node (l,n,r) -> sum l + n + sum r  // recurse into both subtrees
```

---

## 6. Tail recursion

A call is in **tail position** if nothing is left to do after it returns. A
function is **tail recursive** when its recursive call is in tail position - the
result of the recursive call *is* the result. The compiler then reuses one stack
frame instead of pushing new ones, so it **cannot overflow the stack** and runs
like a loop.

> A function is **not** tail recursive if, after the recursive call returns, the
> function still has work to do (e.g. `x * fact (x-1)` - the `*` is pending).

Two techniques turn a non-tail function into a tail-recursive one. The core
difference is **what is carried along**: an accumulator stores *data*, a
continuation stores *instructions*.

### Accumulators - carry the result so far

Pass the partial result down as an extra argument; at the base case it's already
complete, so there's nothing pending.

```fsharp
let sum xs =
    let rec loop acc = function
        | []      -> acc                 // answer already built
        | x :: xs -> loop (acc + x) xs   // tail call - add as we go
    loop 0 xs

let reverse xs =
    let rec loop acc = function
        | []      -> acc
        | x :: xs -> loop (x :: acc) xs  // builds the reversed list directly
    loop [] xs
```

### Continuations - carry the work to do later

Pass a function representing "what to do with the result." You don't compute now;
you describe what should happen later, and the call stays in tail position.

```fsharp
let fact n =
    let rec loop n cont =
        match n with
        | 0 -> cont 1                          // run the accumulated plan
        | n -> loop (n - 1) (fun r -> cont (n * r))
    loop n id
```

`cont` = "what to do with the result later"; each step extends the plan and the
recursive call is the last thing done.

> Tail recursion, accumulators, and continuations: slides **Lecture 8**
> (optimisation), or HR chapters **8.1–8.6** and **9**.


### MATCH WITH vs FUNCTION
function is shorthand for an anonymous function that immediately pattern matches on its single argument.
```
let f =
    function
    | [] -> 0
    | x::xs -> x
```
is equivalent to:
```
let f xs =
    match xs with
    | [] -> 0
    | x::xs -> x
```
key constraint: function only works when you are defining a function with exactly one implicit argument. it introduces that argument automatically.

once you already have named parameters, function becomes wrong:
```
let g xs cont =
    function
    | [] -> cont 0
    | x::xs -> cont x
```
this is actually:
```
let g xs cont =
    fun arg ->
        match arg with
        | [] -> cont 0
        | x::xs -> cont x
```
so g now takes 3 arguments, not 2.

correct version:
```
let g xs cont =
    match xs with
    | [] -> cont 0
    | x::xs -> cont x
```