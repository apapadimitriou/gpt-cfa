import argparse

import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument(
    "-m", "--model", type=str, required=True, help="Model name (gpt4, chatgpt)"
)

args = parser.parse_args()

if args.model not in ("gpt4", "chatgpt"):
    print("Models: gpt4, chatgpt")
    exit()

df = pd.read_csv(f"{args.model}.csv")
# df = pd.read_csv("chatgpt.csv")
print(f'{sum(df["correct"] == "yes") / len(df) * 100:.2f}%')
