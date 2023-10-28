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
from copy import deepcopy

from openai_wrapper import gpt4_xml, gpt4
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
    if not novel.xpath(".//title"):
        novel.append(generate_title(novel))
        return False
    if not novel.xpath(".//setting"):
        novel.append(generate_setting(novel))
        return False
    if not novel.xpath(".//characters"):
        novel.append(generate_characters(novel))
        return False
    if not novel.xpath(".//compressedCharacters"):
        novel.append(compress_characters(novel))
        return False
    if not novel.xpath(".//chapters"):
        novel.append(generate_chapters(novel))
        return False
    # Iterate over each <chapter> element
    for chapter in novel.xpath(".//chapter"):
        # check if there is no <moments> element
        if not chapter.xpath(".//moments"):
            chapter.append(generate_moments(novel, chapter))
            return False
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
        else:
            title = title_elements[0].text.strip()
            timestamp = tree.xpath(".//timestamp")[0].text.strip()
            # replace any non alphanumeric characters with _
            filename = f"{title}_{timestamp}"
            filename = "".join([c if c.isalnum() else "_" for c in filename])
            path = os.path.join("output", f"{filename}.xml")
            # handle the case where the directory doesn't exist yet
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as file:
                file.write(encode_xml(tree))


generate_summary_prompt = """
You are a renowned, award-winning novelist.
Generate ten <ideas>.

The <critique> is a 1-sentence rejection of the previous idea by the Nobel committee.
The committee HATES cliches.
Take each critique, and use it to form a better <idea>.
"""


def generate_summary():
    schema = add_chain_of_critique_to_schema(get_subschema("summary"))
    response = gpt4_xml(xml_schema=schema, system_prompt=generate_summary_prompt)

    last_idea = response.xpath(".//idea")[-1]
    summary = last_idea.xpath(".//summary")[0]
    return summary


generate_title_prompt = Template(
    """
You are a renowned, award-winning novelist.
Generate ten <ideas> for the title of your next novel.
Keep your titles SHORT - no more than 5 words.

The <critique> is a 1-sentence rejection of the title by a publisher.
The publisher LOVES marketable titles.
Take each <critique> and use it to form a better <idea>.

What we know about the novel thus far:
$novel
"""
)


def generate_title(novel):
    schema = add_chain_of_critique_to_schema(get_subschema("title"))
    prompt = generate_title_prompt.substitute(novel=encode_xml(novel))
    response = gpt4_xml(xml_schema=schema, system_prompt=prompt)

    last_idea = response.xpath(".//idea")[-1]
    title = last_idea.xpath(".//title")[0]
    return title


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


generate_setting_prompt = Template(
    """
You are a renowned, award-winning novelist.
Write the setting of the novel as 1 sentence.

What we know about the novel thus far:
$novel
"""
)


def generate_setting(novel):
    schema = get_subschema("setting")
    prompt = generate_setting_prompt.substitute(novel=encode_xml(novel))
    return gpt4_xml(xml_schema=schema, system_prompt=prompt)


generate_characters_prompt = Template(
    """
You are a renowned, award-winning novelist.
Write out 5 characters for your next novel.

What we know about the novel thus far:
$novel
"""
)


def generate_characters(novel):
    schema = get_subschema("characters")
    prompt = generate_characters_prompt.substitute(novel=encode_xml(novel))
    return gpt4_xml(xml_schema=schema, system_prompt=prompt)


compress_characters_prompt = """
Compress the User's message as much as possible.
It doesn't have to be legible to humans,
as long as you can understand the gist of it.

You MUST NOT use ANY of the following
characters in your output: < > ( ) & , ' "
"""


def compress_characters(novel):
    characters_text = encode_xml(novel.xpath(".//characters")[0])
    compressed = gpt4(
        system_prompt=compress_characters_prompt, user_prompt=characters_text
    )
    element = etree.Element("compressedCharacters")
    element.text = compressed
    return element


def generate_chapters(novel):
    novel = deepcopy(novel)
    # remove <characters> from the novel
    characters = novel.xpath(".//characters")[0]
    novel.remove(characters)
    prompt = Template(
        """
You are a renowned, award-winning novelist.
Given a <summary> of the book, write 20 <chapter>s,
each with a <name>, <beginning>, and <ending>.
<beginning> must be a 1 -sentence summary of the state
of the plot at the start of the chapter.
<ending> must be a 1-sentence summary of the state
of the plot at the end of the chapter.

What we know about the novel thus far:
$novel
"""
    )
    chapters_schema = get_subschema("chapters")
    # delete "moments" from the schema
    moments = chapters_schema.find(
        ".//xsd:element[@name='moments']",
        namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"},
    )
    moments.getparent().remove(moments)
    return gpt4_xml(
        xml_schema=chapters_schema,
        system_prompt=prompt.substitute(novel=encode_xml(novel)),
    )


def generate_moments(novel, chapter):
    novel = deepcopy(novel)
    # create slim_novel, empty except for <summary>, <setting>, <compressedCharacters>
    slim_novel = etree.Element("novel")
    slim_novel.append(novel.xpath(".//summary")[0])
    slim_novel.append(novel.xpath(".//setting")[0])
    slim_novel.append(novel.xpath(".//compressedCharacters")[0])
    slim_novel.append(chapter)
    prompt = Template(
        """
You are a renowned, award-winning novelist.

Given a summary of the book and this current chapter,
break the chapter into 20 <moments>.

What we know about the novel thus far:
$novel
    """
    )
    moments_schema = get_subschema("moments")
    # remove <prose> element from schema
    prose = moments_schema.find(
        ".//xsd:element[@name='prose']",
        namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"},
    )
    prose.getparent().remove(prose)

    return gpt4_xml(
        xml_schema=moments_schema,
        system_prompt=prompt.substitute(novel=encode_xml(slim_novel)),
    )


def get_subschema(name):
    schema = load_schema_xml()
    found_subschema = schema.find(
        f".//xsd:element[@name='{name}']",
        namespaces={"xsd": "http://www.w3.org/2001/XMLSchema"},
    )
    return found_subschema


SCHEMA = None


def load_schema_xml():
    # global SCHEMA
    # if SCHEMA:
    #     return SCHEMA

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
