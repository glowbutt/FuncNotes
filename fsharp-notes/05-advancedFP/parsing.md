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

### OR
<|>

try left parser, if it fails try right parser

Example:\
pchar '+' <|> pchar '-'

### REPETITION

many p\
parse 0 or more occurrences

many1 p\
parse 1 or more occurrences

Example:
- many (satisfy isLetter)\
Result:
- list of chars

### OPTIONAL PARSING

opt p
- optional parser

Returns:\
Some value if found\
None if not found

### COMMON HELPERS

between pOpen pClose pContent\
parses content inside delimiters

Example:
between (pchar '(') (pchar ')') pint32

Result:
number inside parentheses

### LIST PARSERS

sepBy p sep\
parse list of p separated by sep

Example:\
sepBy pint32 (pchar ',')

Input:
1,2,3

Result:
[1;2;3]

### RECURSIVE PARSERS

Sometimes grammar is recursive:

Example:\
expression -> expression + term | term

To define this you use:\
createParserForwardedToRef

This allows:
- defining parser before it exists
- filling it later