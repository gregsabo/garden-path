"""
Garden-path

Generate a concept for a full-length novel, then
generate it in its entirety, by only prompting
with the last sentence of the previous paragraph.
"""
import os
from datetime import datetime
from pprint import pprint
from dotenv import load_dotenv
import openai
from lxml import etree

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def main():
    concept = generate_concept()
    print(concept)
    dest = save_concept(concept)
    tree = etree.fromstring(concept)
    title = tree.xpath(".//title")[0].text.strip()
    concept_description = tree.xpath(".//acceptedIdea")[0].text.strip()
    characters = ""
    for d in tree.xpath(".//characters")[0].iterdescendants():
        if d.text:
            characters += d.text.strip()
    last_sentence = tree.xpath(".//firstSentence")[0].text.strip()
    generate_repeatedly(dest, title, concept_description, characters, last_sentence)


def generate_repeatedly(dest, title, concept_description, characters, last_sentence):
    text = last_sentence
    while count_words(text) < 100_000:
        print("Word count:", count_words(text))
        new_text = generate_more(
            title,
            concept_description,
            characters,
            final_sentence(text)
        )
        print(new_text)
        text += "\n"
        text += new_text
        file_path = os.path.join(dest, "novel.txt")
        with open(file_path, "w") as file:
            file.write(text)


def count_words(text):
    """Return the number of words in the text."""
    return len(text.split())


def save_concept(concept):
    """Save the concept to a file."""
    tree = etree.fromstring(concept)
    title_tag = tree.xpath(".//title")[0]
    assert title_tag is not None
    title_text = title_tag.text.strip()
    title_text = title_text.lower().replace(" ", "_")
    title_text = f"{datetime.now().isoformat()}_{title_text}"

    output_dir = f"output/{title_text}"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "concept.xml")
    with open(file_path, "w") as file:
        file.write(concept)
    return output_dir


def generate_more(title, concept, characters, last_sentence):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"""
Continue writing a novel.
The User will give you the previous sentence in the novel.
DO proceed immediately with the text of the novel.
Do NOT add any additional commentary before or after the text.
Do NOT write any sentences longer than 10 words.
Do NOT use adjectives or adverbs.
DO include dialog.
Concept: {concept}
Characters: {characters} """,
            },
            {"role": "user", "content": last_sentence},
        ],
        temperature=1,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response.choices[0].message.content


def final_sentence(text):
    """Return the final sentence of the text."""
    sentences = text.strip().split('. ')
    while sentences:
        last_sentence = sentences.pop().strip()
        if last_sentence:
            return last_sentence + '.'
    print("Warning, no final sentence found. Returning last 500 chars instead.")
    return text[-500:]


def generate_concept():
    """Generate a concept for a full-length novel."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": """
Generate a concept for a full-length novel.
DO enocde your entire response in XML.
DO make the root tag <novelConcept>.
DO include <rejectedIdeas>, <acceptedIdea>, <title>,
    <cover>, <characters>, <firstSentence> tags
    within the root <novelConcept> tag.
DO make the <rejectedIdeas> tag a short brainstorm of three dramatically
    different directions.
DO make the <acceptedIdea> tag a fourth idea that's better
    than the rejected ones.
DO make the <title> the title of the book.
DO make the <cover> tag a description of the cover art.
DO make the <characters> tag a list of the main characters
    and their motivations.
DO make the <firstSentence> tag the first sentence of the book.
DO make the genre dramatic literary fiction appropriate for a Pulitzer.""",
            },
            {"role": "user", "content": ""},
        ],
        temperature=1,
        max_tokens=4009,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    main()
