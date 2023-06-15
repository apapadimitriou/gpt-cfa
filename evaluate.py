import argparse
import json
import os
import sys
import time

import openai
import pandas as pd
from tqdm import tqdm

# ------------------------------------------------------------------------------
#                                 Parseargs
# ------------------------------------------------------------------------------
argparser = argparse.ArgumentParser()
argparser.add_argument("-f", "--file", type=str, required=True)
argparser.add_argument("-m", "--model", type=str, default="gpt-3.5-turbo-0613")
argparser.add_argument("-t", "--temp", type=float, default=0.0)
args = argparser.parse_args()
model = args.model
temp = args.temp

# ------------------------------------------------------------------------------
#                                  Get key
# ------------------------------------------------------------------------------
try:
    with open(os.path.expanduser("~/.cache/oai"), "r") as f:
        openai.api_key = f.read().strip()
except:
    print("Error reading openai api key from ~/.cache/oai")
    exit(1)


# ------------------------------------------------------------------------------
#                               System prompt
# ------------------------------------------------------------------------------
sys_prompt = """You are a CFA (chartered financial analyst) taking a test to evaluate your knowledge of finance.
You will be given a question along with three possible answers (A, B, and C).
Before answering, you should think through the question step-by-step.
Explain your reasoning at each step towards answering the question.
If calculation is required, do each step of the calculation as a step in your reasoning.
Finally, indicate the correct answer
"""


def ask_gpt(question):
    while True:
        try:
            res = openai.ChatCompletion.create(
                model=model,
                temperature=temp,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": question},
                ],
                functions=[
                    {
                        "name": "answer_question",
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
                function_call={"name": "answer_question"},
            )
        except:
            time.sleep(3)
            continue
        ans = res.choices[0].message.to_dict()["function_call"]["arguments"]  # type: ignore
        out = json.loads(ans)
        return out


exam = pd.read_csv(args.file, sep=";;", engine="python")
exam["guess"] = ""
exam["thinking"] = ""
exam["correct"] = ""

correct = 0
for i, row in tqdm(exam.iterrows(), total=len(exam)):
    ans = ask_gpt(row.question)
    exam.loc[i, "guess"] = ans["answer"]
    exam.loc[i, "thinking"] = " - ".join(ans["thinking"])
    if ans["answer"] == row.answer:
        correct += 1
        exam.loc[i, "correct"] = "yes"
    else:
        exam.loc[i, "correct"] = "no"

print(f"Score: {correct}/{len(exam)} {correct/len(exam)}%")

exam.to_csv("chatgpt.csv", index=False)
