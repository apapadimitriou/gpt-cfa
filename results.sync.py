# %%
import pandas as pd

# %%
chatgpt = pd.read_csv(f"chatgpt.csv")
gpt4 = pd.read_csv(f"gpt4.csv")

# %%
print(sum(chatgpt["correct"] == "yes") / len(chatgpt) * 100)
print(sum(gpt4["correct"] == "yes") / len(gpt4) * 100)

# %%
chatgptwrong = chatgpt[chatgpt["correct"] == "no"][
    ["answer", "guess", "thinking", "explanation"]
]
gpt4wrong = gpt4[gpt4["correct"] == "no"][
    ["answer", "guess", "thinking", "explanation"]
]

# %%
i = 2

# %%
print(chatgpt.iloc[i]["answer"])
print(chatgptwrong.iloc[i]["guess"])
print()
print(chatgptwrong.iloc[i]["thinking"])
print()
print(chatgptwrong.iloc[i]["explanation"])

# %%
print(gpt4wrong.iloc[i]["answer"])
print(gpt4wrong.iloc[i]["guess"])
print()
print(gpt4wrong.iloc[i]["thinking"])
print()
print(gpt4wrong.iloc[i]["explanation"])

# %%
math = pd.read_csv(f"is_math.csv")
chatgpt["is_math"] = math["is_math"]
gpt4["is_math"] = math["is_math"]

print(
    sum(chatgpt[chatgpt["is_math"] == 1]["correct"] == "yes")
    / len(chatgpt[chatgpt["is_math"] == 1])
    * 100
)
print(
    sum(gpt4[gpt4["is_math"] == 1]["correct"] == "yes")
    / len(gpt4[gpt4["is_math"] == 1])
    * 100
)
