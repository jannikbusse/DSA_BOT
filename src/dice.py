import random
import re

def simulate_dice(st):
    r = parse_dice(st)
    res = parse_eq(r)
    return res

def replace_stats(st:str, statList) -> str:
    stats = ["mu","kl","in","ch","ff","ge", "ko", "kk"]
    return st

def roll_dice(sides):
    return random.randint(0, max(0, sides))

def parse_atomic(s):
    try: 
        int(s)
        return int(s)
    except ValueError:
        print("error in parsing: " +s)
        return 0

def parse_dice(s):
    p = re.compile("[0-9]*w[0-9]*")
    for m in p.finditer(s):
        left = s[:m.start()]
        right = s[m.start() + len(m.group()):]
        mid = str(m.group())
        pre, post = re.compile(r'w').split(mid)
        if pre == "":
            pre = 1
        if post == "":
            post = 20
        total = 0
        for i in range(int(pre)):
            total += roll_dice(int(post))
        s = left + str(total) + right
    return s

def parse_eq(s): 
    comps = []    
    if '+' in s or '-' in s:
        comps = re.compile(r'[\-\+]').split(s)
    elif '*' in s:
        comps = re.compile(r'[\*]').split(s)    
    else:
        return parse_atomic(s)
    
    pos = len(comps[0])
    left = s[:pos]
    right = s[pos+1:]
    operator = s[pos]

    if operator == '*' :
        return parse_eq(left) * parse_eq(right)
    elif operator == '+' :
        return parse_eq(left) + parse_eq(right)
    elif operator == '-' :
        return parse_eq(left) - parse_eq(right)





