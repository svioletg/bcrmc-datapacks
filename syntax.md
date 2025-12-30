# Custom MCFunction Comment Macro/Expression Syntax

## Single-line

### Macro

**Prefix:** `#>`

**Example:** `#>calc_disc_total`

Calls a function defined in `parser.py` and prefixed with `macro_`, replacing this lines by the
returned lines of the function. The `macro_` can be omitted when calling, as shown above. Macro
functions are passed the `Context` object for the current pack, but receive no other arguments.

## Multi-line
