Array to string\
```System.String(arr)```

String to array\
```s.ToCharArray()```

List to string (char list)\
```System.String(List.toArray lst)```

String to list\
```s |> Seq.toList```

Set to list\
```Set.toList s```

List to set\
```Set.ofList lst```

Seq to list\
```Seq.toList s```

List to seq\
```Seq.ofList lst```

Array to list\
```Array.toList arr```

List to array\
```List.toArray lst```

Array to seq\
```Array.toSeq arr```

Seq to array\
```Seq.toArray s```

String split to list\
```s.Split(' ') |> Array.toList```

Split by multiple chars\
```s.Split([|',';';'|]) |> Array.toList```

Chunk string into list\
```[ for i in 0 .. n .. s.Length - 1 -> s.Substring(i, min n (s.Length - i)) ]```