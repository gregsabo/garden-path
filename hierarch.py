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
from openai_wrapper import gpt4

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def work(tree):
    """
    Does one step of work on the novel then returns
    True if the novel is complete, False otherwise.
    """
    novel = tree.getroot()
    # check if there is no title
    if not tree.xpath(".//timestamp"):
        e = etree.Element("timestamp")
        e.text = str(datetime.now().isoformat())
        novel.append(e)
    if not tree.xpath(".//title") or not tree.xpath(".//summary"):
        title, summary = generate_concept()
        novel.append(title)
        novel.append(summary)
        return False
    # if not tree.xpath(".//characters"):
    #     novel.append(generate_characters(novel))
    #     return False
    return True


def work_and_save(tree):
    schema = load_schema()
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
        with open(path, "wb") as file:
            file.write(etree.tostring(tree, pretty_print=True))


generate_concept_prompt = """
You are a renowned, award-winning novelist.
Generate ten <ideas>.

You MUST Structure your response as XML.
You MUST escape any XML special characters.
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


def generate_characters(novel):
    pass


def load_schema():
    with open("hierarch_schema.xsd", "r") as file:
        xsd_tree = etree.XML(file.read())
        return etree.XMLSchema(xsd_tree)


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
            novel = etree.fromstring(file.read())
            work_and_save(novel)
    else:
        root = etree.Element("novel")
        tree = etree.ElementTree(root)
        work_and_save(tree)
