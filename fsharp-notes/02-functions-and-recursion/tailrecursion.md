# Tail Recursion
See also slides 'Lecture 8' or HR chapters  8.1 - 8.6 and 9

Tail recursion is...

- Accumulators and Continuations are used to transform non-tail-recursive functions into tail-recursive ones.
- Good because they don't overflow the call stack.
- Core difference is what is stored during recursion: an accumulator **stores data**, while a continuation **stores instructions**

A function is not tail recursive if:
**after the recursive call returns, the function still has work to do.**

## Accumulators

An accumulator passes intermediate data (the result so far) as an extra argument down into recursive calls.
A running result. Answer is built up as you go.

Example:
``` F#
let sum xs =
    let rec loop xs acc =
        match xs with
        | [] -> acc
        | x::xs -> loop xs (acc + x)
    loop xs 0
```
- acc stores the running total
- we add each element as we go
- final answer is already in acc

Example 2:
``` F#
let reverse xs =
    let rec loop xs acc =
        match xs with
        | [] -> acc
        | x::xs -> loop xs (x::acc)
    loop xs []
```
- acc slowly builds the reversed list
- we build it directly, so no waiting for recursive calls to return before completing the work

## Continuations

- Store instructions for what to do later.
- A continuation passes a function (representing the "work left to do") as an extra argument down into recursive calls.
- Think “I don’t compute the answer now, just describe what should happen later.”

Example (factorial)
``` F#
let rec fact n cont =
    if n = 0 then cont 1
    else fact (n - 1) (fun result -> cont (n * result))
```
- cont = “what to do with the result later”
- we pass a function forward that delays work

Example 2 - sum of list:
``` F#
let rec sum xs cont =
    match xs with
    | [] -> cont 0
    | x::xs ->
        sum xs (fun result -> cont (x + result))
```

- dont add immediately
- we build a “plan” for adding later