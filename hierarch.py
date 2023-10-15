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
from openai_wrapper import gpt4

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
    if not novel.xpath(".//title") or not novel.xpath(".//summary"):
        title, summary = generate_concept()
        novel.append(title)
        novel.append(summary)
        return False
    if not novel.xpath(".//characters"):
        novel.append(generate_characters(novel))
        return False
    return True


def work_and_save(tree):
    schema = etree.XMLSchema(load_schema_xml())
    schema.assertValid(tree)
    is_done = False
    while not is_done:
        is_done = work(tree)
        schema.assertValid(tree)
        title = tree.xpath(".//title")[0].text.strip()
        # lowercase and replace whitespace with underscores
        title = title.lower().replace(" ", "_")
        timestamp = tree.xpath(".//timestamp")[0].text.strip()
        path = os.path.join("output", f"{title}_{timestamp}.xml")
        with open(path, "w") as file:
            file.write(encode_xml(tree))


generate_concept_prompt = """
You are a renowned, award-winning novelist.
Generate ten <ideas>.

You MUST Structure your response as XML.
Do NOT use apersands (&) anywhere in your response.
Do NOT add any commentary before or after the XML.
Your output MUST validate against the following schema:

<xs:element name="ideas">
<xs:complexType>
  <xs:sequence>
    <xs:element name="idea" minOccurs="10" maxOccurs="10">
        <xs:complexType>
        <xs:sequence>
            <xs:element name="critique" type="xs:string"/>
            <xs:element name="title" type="xs:string"/>
            <xs:element name="summary" type="xs:string"/>
        </xs:sequence>
        </xs:complexType>
    </xs:element>
  </xs:sequence>
</xs:complexType>
</xs:element>

Each <idea> should attempt to improve on the previous one.

The <critique> is a 1-sentence rejection of the previous
idea by the Nobel committee.

The committee HATES cliches."""


def generate_concept():
    tree = gpt4(generate_concept_prompt)
    last_idea = tree.xpath(".//idea[last()]")[0]
    return last_idea.xpath(".//title")[0], last_idea.xpath(".//summary")[0]


generate_characters_prompt = Template("""
You are a renowned, award-winning novelist.
Given a summary of the book, write a list of characters.

What we know about the novel thus far:
$novel

You MUST Structure your response as XML.
Do NOT use apersands (&) anywhere in your response.
Do NOT add any commentary before or after the XML.
Your output MUST validate against the following schema:
$schema
""")


def generate_characters(novel):
    # extract the title and summary fields from the novel with xpath
    summary = novel.xpath(".//summary")[0]
    schema = render_subschema("characters")
    prompt = generate_characters_prompt.substitute(
        novel=encode_xml(summary),
        schema=schema
    )
    return gpt4(prompt)


def render_subschema(name):
    schema = load_schema_xml()
    # Find the "characters" element
    found_subschema = schema.find(
        f".//xsd:element[@name='{name}']",
        namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"},
    )[0]

    if found_subschema is not None:
        out_str = encode_xml(found_subschema)
        return out_str
    else:
        return "Element not found"


SCHEMA = None


def load_schema_xml():
    global SCHEMA
    if SCHEMA:
        return SCHEMA

    with open("hierarch_schema.xsd", "r") as file:
        return etree.XML(file.read())


def parse_xml(xml):
    """
    xml string -> etree element, according to my preferences.
    """
    return etree.fromstring(xml, etree.XMLParser(remove_blank_text=True))


def encode_xml(xml):
    """
    etree element -> xml string, pretty printed.
    """
    return etree.tostring(xml, pretty_print=True).decode("utf-8")

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
