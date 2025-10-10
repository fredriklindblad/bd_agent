# type hints
# useful functions are id(), dir(), help(), type(), isinstance()
# hur funkar sessions?

import analyze_agent

# print(analyze_agent.__version__)
# print(analyze_agent.__all__)
# print(analyze_agent.__doc__)
# help(analyze_agent)


"""packa upp dictionary som keyword arguments"""


def greet(name, age):
    print(f"Hej {name}, du är {age} år gammal!")


# vanlig anropning
greet("Fredrik", 32)

# samma sak med dictionary (packa upp nycklarna)
person = {"name": "Fredrik", "age": 32}
greet(**person)  # ← OBS ** här!
