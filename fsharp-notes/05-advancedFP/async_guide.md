please polish this file about async programming. make it more readable and concise.

# F# Async, Concurrency, and Parallelism

## 1. Intro

three related but different ideas:

-   **Synchronous execution**: one thing happens at a time
-   **Concurrency**: multiple tasks are *in progress* (interleaved)
-   **Parallelism**: multiple tasks run *at the same time*

In F#, `async {}` is mainly about **concurrency**, not automatic parallelism

------------------------------------------------------------------------

## 2. What is `Async<'T>`?

An `Async<'T>` is:

> a *description* of a computation that will eventually produce a value
> of type `'T`

It does NOT run immediately.

### Example

``` fsharp
let work =
    async {
        return 1 + 1
    }
```

At this point: - nothing has executed - it's just a recipe

------------------------------------------------------------------------

## 3. How to RUN async code

### 3.1 `Async.RunSynchronously`

``` fsharp
let result =
    Async.RunSynchronously work
```

-   runs the async computation
-   blocks the current thread
-   returns `'T`

Think:

> "run async code like normal blocking code"

------------------------------------------------------------------------

### 3.2 `Async.Start`

``` fsharp
Async.Start work
```

-   runs in background
-   does NOT block
-   returns `unit`

You don't get the result directly.

------------------------------------------------------------------------

## 4. Async workflows (`async {}`)

Inside:

``` fsharp
async {
    let! x = asyncComputation
    return x + 1
}
```

Key ideas:

-   `let!` = wait for async result
-   `return` = wrap result
-   `return!` = chain async computations

------------------------------------------------------------------------

## 5. Concurrency vs Parallelism

### Concurrency (Async)

``` text
Task A: ----wait----
Task B: ----wait----
```

F# switches between tasks during waits.

------------------------------------------------------------------------

### Parallelism (CPU cores)

``` text
Core 1: Task A running
Core 2: Task B running
```

Actually simultaneous execution.

------------------------------------------------------------------------

## 6. `Async.Parallel`

### Type

``` fsharp
Async.Parallel : Async<'T> list -> Async<'T[]>
```

It means:

> run multiple async computations at the same time and collect results

------------------------------------------------------------------------

### Example

``` fsharp
let tasks =
    [
        async { return 1 }
        async { return 2 }
        async { return 3 }
    ]

Async.Parallel tasks
|> Async.RunSynchronously
```

Result:

``` fsharp
[|1;2;3|]
```

------------------------------------------------------------------------

## 7. Common mistake (VERY IMPORTANT)

### WRONG

``` fsharp
[1;2;3]
|> List.map (fun x -> x + 1)
|> Async.Parallel
```

Why wrong? - inputs are NOT `Async<'T>` - they are plain values

------------------------------------------------------------------------

### RIGHT

``` fsharp
[1;2;3]
|> List.map (fun x -> async { return x + 1 })
|> Async.Parallel
```

------------------------------------------------------------------------

## 8. Why `Async.Parallel` often "does nothing"

If your work is:

-   tiny (like string operations)
-   CPU cheap
-   no waiting (I/O)

Then: - overhead \> benefit - it may feel like nothing changed

------------------------------------------------------------------------

## 9. `Async.RunSynchronously` danger

``` fsharp
Async.RunSynchronously (Async.Parallel tasks)
```

This: - blocks main thread - waits for all tasks - removes async benefit
at top level

Use mainly in: - scripts - main entry point

------------------------------------------------------------------------

## 10. `let!` vs `let`

### let (no wait)

``` fsharp
let x = asyncComputation
```

x is `Async<'T>`

------------------------------------------------------------------------

### let! (wait)

``` fsharp
let! x = asyncComputation
```

x is `'T`

------------------------------------------------------------------------

## 11. `return` vs `return!`

### return

Wrap value:

``` fsharp
return 5
```

becomes `Async<int>`

------------------------------------------------------------------------

### return!

Flatten async:

``` fsharp
return! otherAsync
```

------------------------------------------------------------------------

## 12. Why your Caesar example failed

You had:

``` fsharp
text.Split(' ')
|> Array.map (fun str -> encrypt str offset)
```

Problem: - `encrypt` returns string - not Async`<string>`{=html}

So `Async.Parallel` cannot be used.

Fix:

``` fsharp
text.Split(' ')
|> Array.map (fun str -> async { return encrypt str offset })
|> Async.Parallel
```

------------------------------------------------------------------------

## 13. When should you use Async?

Use Async when:

-   file IO
-   network calls
-   waiting (sleep, delays)
-   independent tasks that can overlap

DON'T use it when:

-   simple loops
-   small CPU work
-   pure transformations

------------------------------------------------------------------------

## 14. When should you use Parallel?

Use parallel when:

-   CPU-heavy work
-   independent computations
-   large datasets

Example:

``` fsharp
Array.Parallel.map expensiveFunction data
```

------------------------------------------------------------------------

## 15. Simple mental model

Think:

### Async = "I will wait for something later"

### Parallel = "I want multiple CPU cores now"

------------------------------------------------------------------------

## 16. Summary

-   `Async<'T>` = description of work
-   `Async.RunSynchronously` = run and block
-   `Async.Start` = run in background
-   `Async.Parallel` = run multiple async tasks together
-   async does NOT mean parallel automatically
