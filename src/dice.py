import random
import re
import logging


no_errors = True

def simulate_dice(st):
    global no_errors
    no_errors = True
    if not is_sanitized_input(st):
        return "numbers are too big!"
    r, r_print = parse_dice(st)
    res = parse_eq(r)
    if not no_errors:
        return "Error in string! Could not parse.."
    return "Results:" + r_print + " =\n **" + str(res)+"**"

def is_sanitized_input(st):
    x = re.findall('[0-9]{6}', st)
    return (len(x) <= 0)

def replace_stats(st:str, statList) -> str:
    stats = ["mu","kl","in","ch","ff","ge", "ko", "kk"]
    return st

def roll_dice(sides):
    return random.randint(0, max(0, sides))

def parse_atomic(s):
    global no_errors
    try: 
        int(s)
        return int(s)
    except ValueError:
        logging.info("error in parsing: " +s + "<")
        no_errors = False
        return 0

def parse_dice(s):
    global no_errors
    s_print = s
    p = re.compile("[0-9]*w[0-9]*")
    for m in p.finditer(s):
        left = s[:m.start()]
        right = s[m.start() + len(m.group()):]
        mid = str(m.group())
        pre, post = re.compile(r'w').split(mid)
        if pre == "":
            pre = 1
        if int(pre) > 999: #dont let ppl roll too often!
            pre = 0
            no_errors = False
        if post == "":
            post = 20
        total = 0
        total_print = ""
        for i in range(int(pre)):
            d_res = roll_dice(int(post))
            total += d_res
            total_print = total_print +  "**" + str(d_res) + "**"
            if not i == int(pre)-1:
                total_print += " + "
        s = left + "( " + str(total) + " ) " + right
        s_print = left + " [ " + str(total_print) + " ] " + right

    return (s,s_print)

def parse_eq(s): 
    global no_errors
    if not no_errors:
        return 0

    comps = []    
    if ')' in s:
        comps = re.compile(r'[\)]').split(s)    
    elif '+' in s or '-' in s:
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
    elif operator ==')':
        if not '(' in left:
            no_errors = False

        last_idx = left.rfind('(')
        inner_bracket = left[last_idx+1:]
       

        bracket = str(parse_eq(inner_bracket))
        return parse_eq(str(left[:last_idx])+str(bracket)+str(right))





