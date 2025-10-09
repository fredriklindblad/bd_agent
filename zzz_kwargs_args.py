def demo(a, b, *args, c=0, **kwargs):
    print(f"a: {a}")
    print(f"b: {b}")
    print(f"args: {args}")
    print(f"c: {c}")
    print(f"kwargs: {kwargs}")


demo(1, 4, x=20, y=30, c=10)


"""
Takeaway:
- *args captures additional positional arguments as a tuple.
- **kwargs captures additional keyword arguments as a dictionary.
- * and ** is the syntax, words args and kwargs are just conventions.

"""


""" ÖVNING *args och **kwargs - avancerad hantering av argument i Python"""


# # --- Steg 1: Se hur *args och **kwargs fångas upp ---------------------------
# def echo(a, b, *args, c=0, **kwargs):
#     """
#     Returnera precis det vi fick så vi kan inspektera det.
#     - a, b är vanliga positionella
#     - *args = extra positionella -> tuple
#     - c är keyword-only pga placeringen efter *
#     - **kwargs = extra keyword -> dict
#     """
#     return {
#         "a": a,
#         "b": b,
#         "args": args,
#         "c": c,
#         "kwargs": kwargs,
#     }


# # Testa: vad hamnar var?
# out = echo(1, 2, 3, 4, c=5, x=10, y=20)
# assert out["a"] == 1
# assert out["b"] == 2
# assert out["args"] == (3, 4)  # tuple!
# assert out["c"] == 5
# assert out["kwargs"] == {"x": 10, "y": 20}  # dict!
# print("Steg 1 klart ✅", out)


# # --- Steg 2: Packa upp och anropa en funktion -------------------------------
# def apply(fn, args_tuple, kwargs_dict):
#     """
#     Anropa godtycklig funktion med redan packade argument.
#     Här använder vi * och ** för att packa upp.
#     """
#     print(f"Calling {fn.__name__} with args={args_tuple} kwargs={kwargs_dict}")
#     print("type args", type(args_tuple), "type kwargs dict", type(kwargs_dict))
#     return fn(*args_tuple, **kwargs_dict)


# def add(*args: float, **kwargs: float) -> float:
#     if not all(isinstance(x, (int, float)) for x in args):
#         raise TypeError("All positional arguments must be numbers")
#     for v in kwargs.values():
#         if not isinstance(v, (int, float)):
#             raise TypeError("All keyword arguments must be numbers")
#     print("sum arggs", sum(args), "sum kwargs", sum(kwargs.values()))
#     return sum(args) + sum(kwargs.values())


# def greet(first, last, *, title=""):
#     return f"Hello {title + ' ' if title else ''}{first} {last}"


# # Test: packa & packa upp
# args = (2, 3, 4.9, 5.2)
# kwargs = {"a": 4352, "b": 3.1}
# print(apply(add, args, kwargs))
# # assert apply(add, args, kwargs) == 10  # 2 + 3 +4 + 5

# args = ("Ada", "Lovelace")
# kwargs = {"title": "Dr"}
# assert apply(greet, args, kwargs) == "Hello Dr Ada Lovelace"
# print("Steg 2 klart ✅")


# # --- Steg 3: Wrapper/dekorator som vidarebefordrar exakt allt ---------------
# def log_calls(fn):
#     def wrapper(*args, **kwargs):
#         print(f"[log] {fn.__name__} args={args} kwargs={kwargs}")
#         return fn(*args, **kwargs)  # kritiskt: packa upp vidare

#     return wrapper


# @log_calls
# def power(base, exp=2):
#     return base**exp


# p = power(3)
# print("power", p)


# assert power(3) == 9  # loggar och returnerar 9
# assert power(2, exp=5) == 32
# print("Steg 3 klart ✅")


# # --- Steg 4: Kombinera flera källor av argument -----------------------------
# def connect(host, port, *, ssl=False, timeout=5):
#     return {"host": host, "port": port, "ssl": ssl, "timeout": timeout}


# base_cfg = {"host": "db.local", "port": 5432}
# overrides = {"timeout": 10, "ssl": True}
# # Dict-unpack (**): senare nycklar vinner
# final_cfg = {**base_cfg, **overrides}
# print("final_cfg", final_cfg)
# # Tuple/list-unpack (*) för positionella
# pos = (final_cfg["host"], final_cfg["port"])
# print("pos", pos)
# kw = {"ssl": final_cfg["ssl"], "timeout": final_cfg["timeout"]}
# print("kw", kw)

# res = connect(*pos, **kw)
# assert res == {"host": "db.local", "port": 5432, "ssl": True, "timeout": 10}
# print("Steg 4 klart ✅", res)


# # --- Steg 5 (valfritt): Star assignment (packa upp från sekvens) ------------
# head, *mid, tail = [10, 20, 30, 40, 50]
# print("head", head)
# print("mid", mid)
# print("tail", tail)

# assert head == 10 and mid == [20, 30, 40] and tail == 50

# # Bygg nya listor med *
# xs = [2, 3]
# ys = [4, 5]
# merged = [1, *xs, *ys, 6]
# print(merged)
# # assert merged == [1, 2, 3, 4, 5, 6]
# print("Steg 5 klart ✅")


# --- Steg 6 (bonus): Test-hake – samla anrop --------------------------------
calls = []


def recorder(*args, **kwargs):
    calls.append(args)
    calls.append(kwargs)


recorder(1, 2, mode="fast")
print(calls)
recorder("a", key=123)
print(calls)
print(type(calls[2]))
assert calls[0] == (1, 2)
assert calls[1] == {"mode": "fast"}
assert calls[2] == ("a",)
assert calls[3] == {"key": 123}
print("Steg 6 klart ✅", calls)

print("\nAllt klart! 🎉")
