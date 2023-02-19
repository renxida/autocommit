import os
import sys

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
    commit message and not a single word more, no introduction text 
    such as "Commit: ". Also there is no need to include filenames.
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


def main():
    # Prompt for OpenAI API key if it's not set
    if OPENAI_KEY:
        openai_api_key = OPENAI_KEY
    else:
        print("No API key provided")
        exit(-1)

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
