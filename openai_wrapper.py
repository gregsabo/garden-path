import os
from dotenv import load_dotenv
import lxml.etree as etree
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def gpt4(system_prompt, user_prompt=None):
    """
    Hits GPT-4, parameteres intended for
    creativity.
    """
    print("-" * 80)
    print("-- system --")
    print(system_prompt)
    if user_prompt:
        print("-- user --")
        print(user_prompt)
    print("." * 80)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt or ""
            }
        ],
        temperature=1,
        max_tokens=6000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=2
    )
    text = response.choices[0].message.content
    print(text)
    return etree.fromstring(text, etree.XMLParser(remove_blank_text=True))
