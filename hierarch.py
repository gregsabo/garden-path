"""
Hierarch
Writes a novel hierarchically.
Structure:
Novel
    title
    summary
    coverArt
    characters
    compressedCharacters
    blurb
    chapters
        moments
            prose
"""

import os
import lxml.etree as etree
import argparse
from datetime import datetime
from dotenv import load_dotenv
import openai
from string import Template

from openai_wrapper import gpt4_xml
from pretty_xml import parse_xml, encode_xml

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def work(novel):
    """
    Does one step of work on the novel then returns
    True if the novel is complete, False otherwise.
    """
    # check if there is no title
    if not novel.xpath(".//timestamp"):
        e = etree.Element("timestamp")
        e.text = str(datetime.now().isoformat())
        novel.append(e)
    if not novel.xpath(".//summary"):
        novel.append(generate_summary())
        return False
    # if not novel.xpath(".//characters"):
    #     novel.append(generate_characters(novel))
    #     return False
    # if not novel.xpath(".//compressedCharacters"):
    #     novel.append(compress_characters(novel))
    #     return False
    return True


def work_and_save(tree):
    schema = etree.XMLSchema(load_schema_xml())
    schema.assertValid(tree)
    is_done = False
    while not is_done:
        is_done = work(tree)
        schema.assertValid(tree)

        title_elements = tree.xpath(".//title")
        if len(title_elements) == 0:
            print("Skipping saving, no title yet.")
            print(encode_xml(tree))
            return

        title = title_elements[0].text.strip()
        # lowercase and replace whitespace with underscores
        title = title.lower().replace(" ", "_")
        timestamp = tree.xpath(".//timestamp")[0].text.strip()
        path = os.path.join("output", f"{title}_{timestamp}.xml")
        with open(path, "w") as file:
            file.write(encode_xml(tree))


generate_summary_prompt = """
You are a renowned, award-winning novelist.
Generate ten <ideas> for your next novel.
Each idea should have a one-sentence summary.
"""


def generate_summary():
    schema = add_chain_of_critique_to_schema(get_subschema("summary"))
    response = gpt4_xml(xml_schema=schema, system_prompt=generate_summary_prompt)

    last_idea = response.xpath(".//idea")[-1]
    # get the summary from the last idea
    summary = last_idea.xpath(".//summary")[0]
    return summary


def add_chain_of_critique_to_schema(xml_schema):
    """
    Adds a chain of critique to the schema.
    """
    # load the hierarch_ideas_schema.xml
    ideas_schema = etree.parse("hierarch_ideas_schema.xml")

    # insert the xml_schema element in place of the first element where name=content
    content_element = ideas_schema.find(
        ".//xsd:element[@name='content']",
        namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"},
    )
    content_element.getparent().replace(content_element, xml_schema)
    return ideas_schema


generate_characters_prompt = Template(
    """
You are a renowned, award-winning novelist.
Given a summary of the book, write a list of characters.

What we know about the novel thus far:
$novel

You MUST Structure your response as XML.
Do NOT use apersands (&) anywhere in your response.
Do NOT add any commentary before or after the XML.
Your output MUST validate against the following schema:
$schema
"""
)


def generate_characters(novel):
    summary = novel.xpath(".//summary")[0]
    schema = get_subschema("characters")
    prompt = generate_characters_prompt.substitute(
        novel=encode_xml(summary), schema=schema
    )
    return gpt4_xml(prompt)


compress_characters_prompt = Template(
    """
"""
)


def compress_characters(novel):
    characters = novel.xpath(".//characters")[0]
    schema = get_subschema("compressedCharacters")
    prompt = compress_characters_prompt.substitute(
        novel=encode_xml(characters), schema=schema
    )
    return gpt4_xml(prompt)


def get_subschema(name):
    schema = load_schema_xml()
    found_subschema = schema.find(
        f".//xsd:element[@name='{name}']",
        namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"},
    )
    return found_subschema


SCHEMA = None


def load_schema_xml():
    global SCHEMA
    if SCHEMA:
        return SCHEMA

    with open("hierarch_schema.xsd", "r") as file:
        return parse_xml(file.read())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate or resume a novel.")
    parser.add_argument(
        "--resume_path",
        type=str,
        help="Path to directory of existing concept and novel to resume",
    )

    args = parser.parse_args()
    if args.resume_path:
        with open(args.resume_path, "r") as file:
            root = parse_xml(file.read())
            work_and_save(root)
    else:
        root = etree.Element("novel")
        work_and_save(root)
