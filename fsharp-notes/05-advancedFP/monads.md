A monad is a pattern for sequencing computations where each step can carry extra “context” along with it.

A more precise but still simple way to say it:

"A monad is a way to chain computations where each step produces a value and some extra structure, and that structure is automatically passed to the next step."

That “extra structure” could be:

- failure (Option)
- multiple results (List)
- state (State)
- async computation (Async)

### The core idea 

A monad is something that has:

- a way to wrap a value
- a way to chain computations

In F# terms:

**wrap**\
```return x```

- take a plain value
- put it into the monad context

**chain**\
```bind : M<'a> -> ('a -> M<'b>) -> M<'b>```

Meaning:

- run first computation
- take its result
- feed it into the next computation
- keep the context going