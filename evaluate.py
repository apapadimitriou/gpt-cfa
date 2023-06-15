import os
import sys

import openai
import pandas as pd

if __name__ == "__main__":
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("-m", "--model", type=str, default="gpt-3.5-turbo")
    argparser.add_argument("-t", "--temp", type=float, default=0.2)

    args = argparser.parse_args()
