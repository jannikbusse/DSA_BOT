def make_str_two_digits(s):
    s = str(s)
    while len(s) < 2:
        s = " " + s
    return s

def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]

def attribute_value_from_list(attributes, attribute):
    res = 0
    for a in attributes:
        if a[0] == attribute:
            res = a[1]
            break
    return res
