import re

# 7-bit C1 ANSI sequences
ansi_escape = re.compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)
result = ansi_escape.sub('', sometext)
# or, without the VERBOSE flag, in condensed form:

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
result = ansi_escape.sub('', sometext)
# Demo:

# >>> import re
# >>> ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
# >>> sometext = 'ls\r\n\x1b[00m\x1b[01;31mexamplefile.zip\x1b[00m\r\n\x1b[01;31m'
# >>> ansi_escape.sub('', sometext)

# The above regular expression covers all 7-bit ANSI C1 escape sequences, but not the 8-bit C1 escape sequence openers. The latter are never used in today's UTF-8 world where the same range of bytes have a different meaning.

# If you do need to cover the 8-bit codes too (and are then, presumably, working with bytes values) then the regular expression becomes a bytes pattern like this:

# 7-bit and 8-bit C1 ANSI sequences
ansi_escape_8bit = re.compile(br'''
    (?: # either 7-bit C1, two bytes, ESC Fe (omitting CSI)
        \x1B
        [@-Z\\-_]
    |   # or a single 8-bit byte Fe (omitting CSI)
        [\x80-\x9A\x9C-\x9F]
    |   # or CSI + control codes
        (?: # 7-bit CSI, ESC [ 
            \x1B\[
        |   # 8-bit CSI, 9B
            \x9B
        )
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)
result = ansi_escape_8bit.sub(b'', somebytesvalue)
# which can be condensed down to

# 7-bit and 8-bit C1 ANSI sequences
ansi_escape_8bit = re.compile(
    br'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])'
)
result = ansi_escape_8bit.sub(b'', somebytesvalue)