import argparse

import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument(
    "-m", "--model", type=str, required=True, help="Model name (gpt4, chatgpt)"
)
parser.add_argument(
    "-i", "--investopedia", action="store_true"
)

args = parser.parse_args()

if args.model not in ("gpt4", "chatgpt"):
    print("Models: gpt4, chatgpt")
    exit()

if args.investopedia:
    df = pd.read_csv(f"{args.model}_investopedia.csv")
else:
    df = pd.read_csv(f"{args.model}.csv")

print(f'{sum(df["correct"] == "yes") / len(df) * 100:.2f}%')
