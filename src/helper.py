def make_str_two_digits(s):
    s = str(s)
    while len(s) < 2:
        s = " " + s
    return s

def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]
