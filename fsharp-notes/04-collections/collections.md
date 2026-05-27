# Collections (Lectures 5, 6, 9)

F#'s five workhorse collections - **lists, arrays, sets, maps, sequences** -
plus **comprehensions** and the conversions between them. All except arrays are
immutable by default.

> Covered elsewhere: the list type as a recursive DU → `01-data-types`;
> the higher-order functions (`map`/`filter`/`fold`) these all share →
> `02-functions-and-recursion`.

| Collection | Literal | Mutable? | Ordered? | Lookup | Best at |
|------------|---------|:--------:|:--------:|--------|---------|
| **List**  | `[1; 2; 3]`        | no  | yes | O(n) | head/tail recursion, prepend |
| **Array** | `[\| 1; 2; 3 \|]`  | yes | yes | O(1) index | random access, in-place update |
| **Set**   | `set [1; 2; 3]`    | no  | sorted | O(log n) | membership, uniqueness |
| **Map**   | `Map.ofList [(1,"a")]` | no | sorted by key | O(log n) | key → value lookup |
| **Seq**   | `seq { 1; 2; 3 }`  | no  | yes | lazy | huge/infinite/streamed data |

---

## 1. Lists - immutable, singly-linked

All elements one type. Cheap to prepend (`::`), O(n) to index or append.

```fsharp
let xs = [1; 2; 3]
let ys = 0 :: xs        // prepend → [0; 1; 2; 3]   (O(1))
let zs = xs @ [4; 5]    // append  → [1; 2; 3; 4; 5] (O(n))
xs.[1]                  // 2   (indexing is O(n) - avoid in loops)
[1 .. 5]                // [1; 2; 3; 4; 5]   range
[1 .. 2 .. 9]           // [1; 3; 5; 7; 9]   range with step

match xs with
| []        -> "empty"
| x :: rest -> $"head {x}, {List.length rest} more"
```

**Use when:** you process front-to-back / recursively - the default FP collection.

---

## 2. Arrays - mutable, fixed-size, O(1) indexed

Written `[| … |]`. The one **mutable** built-in collection: update in place.

```fsharp
let arr = [| 10; 20; 30 |]
arr.[0]                       // 10        - get  (O(1))
arr.[0] <- 99                 // mutate index 0 in place
arr.Length                    // 3

// creating arrays
Array.create 3 0              // [| 0; 0; 0 |]
Array.init 4 (fun i -> i * i) // [| 0; 1; 4; 9 |]
Array.zeroCreate 3            // [| 0; 0; 0 |]
[| 1 .. 5 |]                  // [| 1; 2; 3; 4; 5 |]
```

**Use when:** you need fast random access or genuine in-place mutation
(e.g. performance-sensitive numeric code).

---

## 3. Sets - immutable, unique, sorted

An unordered collection of **distinct** values (kept sorted internally).
Adding a duplicate is a no-op. Operations return a *new* set.

```fsharp
let s  = set [3; 1; 2; 2]     // {1; 2; 3} - duplicate dropped
let s2 = Set.add 4 s          // {1; 2; 3; 4}
Set.contains 2 s              // true       (O(log n))
Set.union  (set [1;2]) (set [2;3])   // {1; 2; 3}
Set.intersect (set [1;2]) (set [2;3])// {2}
Set.difference (set [1;2;3]) (set [2])  // {1; 3}
```

**Use when:** you care about membership and uniqueness, not order or position.

---

## 4. Maps - immutable key → value

An immutable dictionary, sorted by key. Keys are unique.

```fsharp
let m  = Map.ofList [(1, "one"); (2, "two")]
let m2 = Map.add 3 "three" m        // returns a new map
m.[1]                               // "one"   (throws if missing)
Map.tryFind 2 m                     // Some "two"   (safe - returns option)
Map.tryFind 9 m                     // None
Map.containsKey 2 m                 // true
Map.remove 1 m                      // map without key 1
```

```fsharp
// Idiomatic safe lookup with a default
match Map.tryFind k m with
| Some v -> v
| None   -> "missing"
```

**Use when:** you look things up by key - counts, lookups, caches.

---

## 5. Sequences - lazy, possibly infinite

`seq` is F#'s lazy collection (`IEnumerable<'T>`): elements are **computed on
demand**, so a sequence can be infinite as long as you only take a finite prefix.

```fsharp
let nums = seq { 1; 2; 3 }
let sq   = seq { for i in 1 .. 5 -> i * i }   // lazy - nothing computed yet

Seq.take 3 sq |> Seq.toList                   // [1; 4; 9]   forces 3 elements

// infinite sequence - fine because it's lazy
let naturals = Seq.initInfinite (fun i -> i)  // 0, 1, 2, 3, …
naturals |> Seq.take 5 |> Seq.toList          // [0; 1; 2; 3; 4]
```

**Use when:** data is large, streamed, generated, or infinite, and you only need
part of it. (Lists/arrays are *eager* - fully built immediately.)

---

## 6. Comprehensions

A **comprehension** builds a collection by describing its elements with a `for`
loop - `-> expr` yields one element per item, `do … yield` gives full control.
The bracket type chooses the collection: `[ ]` list, `[| |]` array, `seq { }`
sequence (wrap in `set`/`Map.ofList` for those).

```fsharp
[ for x in 1 .. 5 -> x * x ]              // [1; 4; 9; 16; 25]   (list)
[| for x in 1 .. 5 -> x * x |]            // array version
seq { for x in 1 .. 5 -> x * x }          // lazy version

// filter with `do … if … then yield`
[ for x in 1 .. 10 do if x % 2 = 0 then yield x ]   // [2; 4; 6; 8; 10]

// multiple generators (nested loops)
[ for x in 1 .. 2 do for y in 1 .. 2 -> (x, y) ]    // [(1,1);(1,2);(2,1);(2,2)]

set  [ for x in [1;2;2;3] -> x ]          // {1; 2; 3}
```

---

## 7. Common operations (work on every collection)

The same higher-order functions exist per module - `List.`, `Array.`, `Set.`,
`Map.`, `Seq.`:

```fsharp
List.map     (fun x -> x * 2) [1;2;3]          // [2; 4; 6]
List.filter  (fun x -> x > 1) [1;2;3]          // [2; 3]
List.fold    (fun acc x -> acc + x) 0 [1;2;3]  // 6
List.sum     [1;2;3]                           // 6
List.length  [1;2;3]                           // 3
List.rev     [1;2;3]                           // [3; 2; 1]
List.sortBy  abs [-3; 1; -2]                   // [1; -2; -3]
List.contains 2 [1;2;3]                        // true

[1;2;3;4]
|> List.filter (fun x -> x % 2 = 0)
|> List.map (fun x -> x * 10)
|> List.sum                                    // 60
```

---

## 8. Conversions cheat sheet

```fsharp
// between collections
List.toArray  lst        Array.toList  arr
List.toSeq    lst        Seq.toList    s
Array.toSeq   arr        Seq.toArray   s
Set.ofList    lst        Set.toList    s
Map.ofList    pairs      Map.toList    m

// strings ↔ collections
s.ToCharArray ()                 // string  → char[]
System.String arr                // char[]  → string
System.String (List.toArray lst) // char list → string   (or String.Concat)
s |> Seq.toList                  // string  → char list

// splitting strings
s.Split(' ')        |> Array.toList          // by one char
s.Split([| ','; ';' |]) |> Array.toList      // by several chars

// chunk a string into pieces of length n
[ for i in 0 .. n .. s.Length - 1 -> s.Substring(i, min n (s.Length - i)) ]
```

```fsharp
// build a string from an int list via a pipeline
let lastDigitsString lst =
    lst |> List.map (fun x -> x % 10) |> List.map string |> String.concat ""
```

---

## 9. List of `T` → set / seq / array of something *else*

A very common task: given a `list`, produce a `Set` (or seq/array) of some
**derived** element type. Always two steps - **(1) map** each element to its
piece(s), then **(2) collect** the pieces into the target collection.

### Each element → one value

`map`, then convert with the target module:

```fsharp
[1;2;3] |> List.map (fun x -> x * x) |> Set.ofList    // set {1; 4; 9}
[1;2;3] |> List.map string            |> List.toArray // [| "1"; "2"; "3" |]
```

### Each element → a *collection*, then merge

When `f x` itself returns a set/list, you must **combine** the results:

```fsharp
// list of sets → ONE set   (e.g. rectangles → their union of coordinates)
rects |> List.map coordsAcc |> Set.unionMany          // unions every set
//   Set.unionMany : seq<Set<'a>> -> Set<'a>

xs |> List.collect f                  // map + flatten = List.map f >> List.concat
xs |> List.map f |> Array.concat      // list of arrays → one array
xs |> List.map f |> Seq.concat        // list of seqs   → one seq
```

> This is the fix for a "list → set" merge: each element already gives a `Set`,
> so combine with `Set.unionMany` (or `List.fold Set.union Set.empty`) - **not**
> `Set.add`, which adds a single *element*, not a whole set.

### …and back again (reverse) - pick the *target* module

Conversions are pure and work in any direction:

| from ↓ / to → | List | Array | Set | Seq |
|---|---|---|---|---|
| **List**  | - | `List.toArray` | `Set.ofList` | `List.toSeq` |
| **Array** | `Array.toList` | - | `Set.ofArray` | `Array.toSeq` |
| **Set**   | `Set.toList` | `Set.toArray` | - | `Set.toSeq` |
| **Seq**   | `Seq.toList` | `Seq.toArray` | `Set.ofSeq` | - |

### Async / parallel version

When producing each piece is *async* work you want to overlap, map to
`Async<_>`, run with `Async.Parallel` (which yields an **array**), then collect:

```fsharp
items
|> List.map (fun x -> async { return expensive x })   // Async<'b> list
|> Async.Parallel                                      // Async<'b[]>
|> Async.RunSynchronously                              // 'b[]
|> Set.ofArray                                         // collect → set (or Array.toList, …)
```

Only the **work** is async - the conversion itself is always pure/synchronous,
so the "reverse" is just the normal `Array.toList` / `Set.ofArray` step at the
end. (`async` / `Async.Parallel` details → `05-advancedFP`.)
