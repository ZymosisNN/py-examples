# Before / - only positional args, after * - only keywords
def func(a, /):
    print(a)


# Works
func(111)

# Error:
# func(a=111)
