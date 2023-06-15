# %%
import json
import os
import sys

import openai
import pandas as pd

# %%
# load question
df = pd.read_csv("data/l1.csv", sep=";;", engine="python")
line = 238  # pg 104 q118
q = df.iloc[line - 2]

print(q.question)

# %%
# load model
model = "gpt-3.5-turbo"
temperature = 0.2
with open(os.path.expanduser("~/.cache/oai"), "r") as f:
    openai.api_key = f.read().strip()

sys_prompt = f"""
You are a CFA (chartered financial analyst) taking a test to evaluate your knowledge of finance. 
You will be given a question along with three possible answers. 
Before answering, you should think through the question step-by-step.
Explain your reasoning at each step towards answering the question.
You must then choose the correct answer, indicating it at the end of your response with:
[[Answer: X]]
Where X is either A, B, or C. Be sure to answer in exactly this format. 
Do not include any additional text in the answer line.
"""

messages = [
    {
        "role": "system",
        "content": sys_prompt,
    },
    {
        "role": "user",
        "content": q.question,
    },
]

# %%
res = openai.ChatCompletion.create(
    model=model, messages=messages, temperature=temperature, stream=True
)
res_msg = ""

for completion_tokens, chunk in enumerate(res):
    delta = chunk.choices[0].delta  # type: ignore
    if "content" in delta.__dict__["_previous"]:
        res_msg += delta.content
        sys.stdout.write(delta.content)
        sys.stdout.flush()
print()

messages.append({"role": "assistant", "content": res_msg})


# %%
if res_msg.splitlines()[-1] != q.answer:
    msg = f"Expected: {q.answer}\nGot: {res_msg.splitlines()[-1]}\nExplanation: {q.explanation}"
    print("-" * 80)
    print("CORRECTION")
    print(msg)
    print("-" * 80)

    messages.append({"role": "user", "content": msg})

    res = openai.ChatCompletion.create(
        model=model, messages=messages, temperature=temperature, stream=True
    )
    res_msg = ""

    for completion_tokens, chunk in enumerate(res):
        delta = chunk.choices[0].delta  # type: ignore
        if "content" in delta.__dict__["_previous"]:
            res_msg += delta.content
            sys.stdout.write(delta.content)
            sys.stdout.flush()

# %%
print(sys_prompt)
print(q.question)

# %%
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=[
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": q.question},
    ],
    functions=[
        {
            "name": "answer",
            "description": "Think through and answer a multiple choice question on finance",
            "parameters": {
                "type": "object",
                "properties": {
                    "thinking": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "Thought and/or calculation for a step in the process of answering the question",
                        },
                        "description": "Step by step thought process and calculations towards answering the question",
                    },
                    "answer": {
                        "type": "string",
                        "description": "The answer to the question",
                        "enum": ["A", "B", "C"],
                    },
                },
                "required": ["thinking", "answer"],
            },
        }
    ],
    function_call={"name": "answer"},
)
reply = completion.choices[0].message  # type: ignore
reply

# %%
ans = reply.to_dict()["function_call"]["arguments"]
ans = json.loads(ans)

for line in ans["thinking"]:
    print("-", line)
print()
print("Answer:", ans["answer"])

# %%
pd.read_csv("chatgpt.csv").head()
