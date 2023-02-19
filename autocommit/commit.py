from __future__ import print_function, unicode_literals
from PyInquirer import prompt as py_inquirer_prompt, style_from_dict, Token
import subprocess

import keyring

import os
import re
import markdown
import sys

from pydantic import BaseModel
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_KEY")


prompt = PromptTemplate(
    input_variables=["diff", "repo_info"],
    template="""
    What follows "-------" is a git diff for a potential commit.
    Reply with what you think is the best possible Git commit message 
    (a Git commit message should be concise but also try to describe 
    the important changes in the commit). Print exactly the proposed 
    commit message and not a single word more, no introduction text. 
    The git repository is described as: 
    {repo_info}
    ------- 
    {diff}
""",
)


def generate_suggestion(diff, repo_info, openai_api_key=OPENAI_KEY):

    llm = OpenAI(
        temperature=0.2,
        openai_api_key=openai_api_key,
        max_tokens=100,
        model_name="text-davinci-003",
    )  # type: ignore

    # query OpenAI
    formattedPrompt = prompt.format(diff=diff, repo_info=repo_info)
    response = llm(formattedPrompt)

    return response


SERVICE_ID = "auto-commit-cli"


def prompt_for_openai_api_key():
    questions = [
        {
            "type": "input",
            "name": "openai_api_key",
            "message": "Please enter your OpenAI API key:",
        }
    ]
    answers = py_inquirer_prompt(questions)
    openai_api_key = answers["openai_api_key"]
    keyring.set_password(SERVICE_ID, "user", openai_api_key)
    return openai_api_key


def main():
    # Prompt for OpenAI API key if it's not set
    if OPENAI_KEY:
        openai_api_key = OPENAI_KEY
    else:
        openai_api_key = keyring.get_password(SERVICE_ID, "user")
        if openai_api_key is None:
            openai_api_key = prompt_for_openai_api_key()
    diff = sys.stdin.read()

    if len(diff) == 0:
        print("There was an error retrieving the current diff")
        exit(-1)

    # Trim the diff
    diff = diff.strip()

    if len(diff) == 0:
        print("Diff is empty. Nothing to commit.")
        exit(0)

    repo_info = sys.argv[1]

    suggestion = None

    try:
        suggestion = generate_suggestion(diff[:7000], repo_info, openai_api_key=openai_api_key)
    except Exception as e:
        print("There was an error generating suggestions from OpenAI: ")
        # Prompt for OpenAI API key if it's incorrect
        if "Incorrect API key provided" in str(e):
            openai_api_key = prompt_for_openai_api_key()
            print("Please re-run the command now.")
        else:
            print(e)
        exit(-1)
    print(suggestion)

if __name__ == "__main__":
    main()
