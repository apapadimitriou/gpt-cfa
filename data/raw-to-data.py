import re

with open("raw.txt", "r") as f:
    data = f.readlines()

f = open("l1.csv", "a")


def get_next():
    try:
        cur = data.pop(0).strip()
        if cur.startswith("© Wiley 2017"):
            return get_next()
        if cur.startswith("Mock Exam"):
            return get_next()
        if re.match(r"^\d{1,3}\. ", cur):
            cur = re.sub(r"^\d{1,3}\. ", "", cur)
            return cur, True
        return cur, False
    except IndexError:
        exit()


def write_section(until):
    cur, _ = get_next()
    while not re.match(rf"^{until}", cur):
        f.write(" " + cur)
        cur, _ = get_next()
    f.write(";;" + cur)


col = "question"
while len(data) > 0:
    if col == "question":
        write_section(until=r"A\. ")
        col = "A"
    elif col == "A":
        write_section(until=r"B\. ")
        col = "B"
    elif col == "B":
        write_section(until=r"C\. ")
        col = "C"
    elif col == "C":
        write_section(until="Answer: ")
        f.write(";;")
        col = "explanation"
    elif col == "explanation":
        cur, isq = get_next()
        while not isq:
            f.write(" " + cur)
            cur, isq = get_next()
        col = "question"
        f.write("\n")
        f.write(cur)

f.close()
