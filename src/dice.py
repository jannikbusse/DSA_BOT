import random

def simulate_dice(st):
    print(st)


def replace_stats(st:str) -> str:
    inte = 10
    ch = 40
    kk = 30

    st = st.replace("in", str(inte))
    st = st.replace("ch", str(ch))
    st = st.replace("kk", str(kk))
    return st


res = replace_stats("/r in ch kk")

print(res)