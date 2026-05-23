# Pipelines and Composition

## Pipelines

The pipeline operator passes a value into a function.

```fsharp
value |> functionName
```

Example:

```fsharp
[1;2;3]
|> List.map (fun x -> x * 2)
|> List.sum
```

## Why pipelines are useful

Pipelines:

- improve readability
- express transformations step-by-step
- reduce nested parentheses

Without pipelines:

```fsharp
List.sum (List.map (fun x -> x * 2) [1;2;3])
```

## Function composition

Composition combines functions into a new function. 

Operator:

```fsharp
>>
```

Example:

```fsharp
let double x = x * 2
let increment x = x + 1

let doubleThenIncrement =
    double >> increment
```

## Reading composition

```text
f >> g
```

means:

```text
apply f first, then g
```

## Pipelines vs composition

Pipelines work with values.

```fsharp
value |> f |> g
```

Composition works with functions.

```fsharp
f >> g
```

## Functional style

Pipelines and composition encourage declarative programming and transformation-based thinking.

## Related concepts

- higher-order functions
- lists
- map/filter/fold