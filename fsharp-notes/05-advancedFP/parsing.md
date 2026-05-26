### Parsers - basics
Parsing is the process of taking raw input (usually a string)
and converting it into a structured form.

Examples:

"123" -> integer 123
"a + b * c" -> expression tree
"if x then y else z" -> AST node

A parser is basically a function:
- input string -> parsed value + remaining input (or failure)

Combinator parsers:\
Instead of writing one big parser, you build small parsers
and combine them.
small parsers + combinators = big parser

### Transformation (mapping)

|>> (map)

transforms parsed result

Example:
pint32 |>> (fun x -> x + 1)

Meaning:
parse int, then add 1

### Sequencing
.>>. 
- (AND THEN, keep both results)

run parser A then parser B
return tuple (A result, B result)

Example:
pchar '(' .>>. pint32
Result:
('(', 123)

.>> keeps only left side, >>. keeps only right side.