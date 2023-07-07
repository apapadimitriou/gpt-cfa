import argparse
import json
import os
import requests
import time

import openai
import pandas as pd
from tqdm import tqdm

# ------------------------------------------------------------------------------
#                                 Parseargs
# ------------------------------------------------------------------------------
argparser = argparse.ArgumentParser()
argparser.add_argument("-f", "--file", type=str, required=True)
argparser.add_argument("-m", "--model", type=str, default="gpt-4-0613")
argparser.add_argument("-t", "--temp", type=float, default=0.0)
args = argparser.parse_args()
model = args.model
temp = args.temp

# ------------------------------------------------------------------------------
#                                  Get key
# ------------------------------------------------------------------------------
try:
    openai.api_key = os.environ["OPENAI_API_KEY"]
except:
    print("Open AI API key not found")
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


# ------------------------------------------------------------------------------
#                                Functions
# ------------------------------------------------------------------------------
FUNCTIONS=[
    {
        "name": "ask_investopedia",
        "description": "Use this function to find further information on financial concepts you are not familiar with or need help with",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The financial term or concept you wish to find more information about"
                }
            },
            "required": ["query"],
        },
    },
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
]


def ask_investopedia(query: str) -> str:
    """Function to query Investopedia API service"""
    try:
        url = f"https://m4fnh5lv0b.execute-api.us-east-1.amazonaws.com/dev/search?query={query}"
        response = requests.get(url)
        content = response.json()
        information = content["content"]
    except Exception as e:
        information = f"query failed with error: {e}"
    return information


def ask_gpt(question):
    out = None
    for _ in range(3):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                temperature=temp,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": question},
                ],
                functions=FUNCTIONS,
                function_call={"name": "ask_investopedia"},
            )
            message = response["choices"][0]["message"]
            arguments = json.loads(message["function_call"]["arguments"])
            function_response = ask_investopedia(query=arguments.get("query"))
            
            res = openai.ChatCompletion.create(
                model=model,
                temperature=temp,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": question},
                    message,
                    {"role": "function", "name": "ask_investopedia", "content": function_response},
                ],
                functions=FUNCTIONS,
                function_call={"name": "answer_question"},
            )
            ans = res.choices[0].message.to_dict()["function_call"]["arguments"]  # type: ignore
            out = json.loads(ans)
            return out
        except Exception as e:
            print(e)
            time.sleep(3)
            continue

    return {"thinking": ["failed to get response"], "answer": "N"}


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

exam.to_csv("gpt_investopedia.csv", index=False)
