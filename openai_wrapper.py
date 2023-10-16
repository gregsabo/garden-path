import os
from dotenv import load_dotenv
import lxml.etree as etree
import openai
import time

from pretty_xml import parse_xml, encode_xml

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def gpt4(system_prompt, user_prompt=None, retries=5):
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
    try:
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
    except openai.error.RateLimitError as e:
        print(e)
        print("Rate limit error, sleeping for 60 seconds.")
        time.sleep(60)
        return gpt4(system_prompt, user_prompt, retries=retries - 1)
    text = response.choices[0].message.content
    print(text)
    return text


xml_schema_prompt_suffix = """
You MUST Structure your response as XML.
Do NOT use apersands (&) anywhere in your response.
Do NOT add any commentary before or after the XML.
Your output MUST validate against the following schema:
"""


def gpt4_xml(xml_schema, system_prompt, user_prompt=None):
    """
    Given an xml_schema, hits GPT-4 and requires the response
    to be valid against the xml schema. Returns parsed XML.

    xml_schema: etree element representing a schema (not a schema object)
    """
    schema_string = encode_xml(xml_schema)
    prompt_with_xml = system_prompt + xml_schema_prompt_suffix + schema_string

    text = gpt4(prompt_with_xml, user_prompt)

    parsed = parse_xml(text)
    # TODO: figure out how to validate this against xml_schema

    return parsed
