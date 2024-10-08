from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from bs4 import BeautifulSoup as bs
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import (
    StreamingStdOutCallbackHandler,
)

# ----------------------------- Model set up ----------------------------- #

with open('prompt_template.txt', 'r') as file:
    template = file.read()

callback_man = CallbackManager([StreamingStdOutCallbackHandler()])
model = OllamaLLM(model="llama3.2",
                  callback_manager=callback_man, temperature=0.4, num_ctx=1024)
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Hardcoded HTML source code of the privacy policy page
with open('test_policy1.html', 'r') as file:
    html_as_string = file.read()

# ----------------------------- Summarization process ----------------------------- #


def extract_policy_text(html):
    """
    Extracts the visible text content from the provided HTML code of a privacy policy page.

    Args:
        html (str): The HTML content as a string from which the policy text will be extracted.

    Returns:
        str: A string containing the visible text content from the HTML, separated by new lines.
    """
    soup = bs(html, 'html.parser')

    policy_text = soup.get_text(separator="\n").strip()
    return policy_text


policy_text = extract_policy_text(html_as_string)


def handle_conversation():
    """
    Handles the process of summarizing a privacy policy using a local language model (LocalLLM).

    This function prints a message indicating the start of the summarization process and invokes
    the language model to generate a summary of the provided policy text.

    Args:
        None

    Returns:
        None
    """
    print("Summarizing the privacy policy...")
    result = chain.invoke({"policy_text": policy_text})


if __name__ == "__main__":
    handle_conversation()
