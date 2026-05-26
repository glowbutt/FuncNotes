What is a Monad?\
A monad is a wrapper around a value that also carries some extra context (like state, errors, lists, etc.). The wrapper lets you chain computations together without manually threading that context everywhere.

A State Monad specifically carries:

- A computation (a function)
-  That computation takes a state as input and returns a (result, new state) pair

So a state monad wraps a function **state → (value, state)**


### The core idea 

A monad is something that has:

- a way to wrap a value
- a way to chain computations

In F# terms:

**return - wrapping**

ret (return / unit)

- Wraps a plain value into the monad, doing nothing to the state

``` fsharp
    let ret x = SM (fun s -> Some (x, s))
    //                   ↑     ↑
    //               result  state unchanged
    ret 5 gives you a state computation that, given any state s, returns (5, s). It doesn't touch the state.
```
**fail**

```let fail = SM (fun _ -> None)```

just a computation that always fails. use it in bind

**bind**\

``` fsharp
let bind f (SM a) : StateMonad<'b> =
    SM (fun s ->
        match a s with
        | Some (x, s') -> let (SM g) = f x
                          g s'
        | None -> None)

```
This chains two computations together. Step by step:

- runs the first computation a on the current state s
- If that succeeds with (x, s'), it calls f x. This gives back a new monadic computation (let's call it g)
- It then runs g on the updated state s'
- If step 1 fails, the whole thing returns None. short-circuit, no further computation runs

This is how state is threaded through a seq of steps without having to pass it manually.

'>>=' is just bind with arguments flipped:

``` fsharp
let (>>=) x f = bind f x
```
So computation >>= f means "run this computation, then pass the result to f". It lets you write pipelines left-to-right:

```getChar >>= (fun c -> checkLetter c >>= (fun _ -> ret c))```

'>>>=' is "sequence" - run two computations in order, but throw away the result of the first:

``` fsharplet 
(>>>=) x y = x >>= (fun _ -> y)
```

Useful when you only care about the side effect (state update) of the first computation.

**Monad laws**:

- Law 1: ret a >>= f = f a ("left identity")

Wrapping a in ret and then binding f is the same as just calling f a directly. ret does nothing interesting.

- Law 2: m >>= ret = m ("right identity")

Binding ret onto a computation does nothing. 
ret just re-wraps the value without touching state, so m >>= ret gives back the same result as m.

- Law 3: (m >>= f) >>= g = m >>= (fun x -> f x >>= g) ("associativity")\

Chaining doesn't care about parenthesisation. 
Whether you go (m then f) then g or m then (f then g), you get the same result. This is what lets you build long pipelines without worrying about grouping.