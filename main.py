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
    save_concept(concept)


def save_concept(concept):
    """Save the concept to a file."""
    tree = etree.fromstring(concept)
    title_tag = tree.xpath('.//title')[0]
    assert title_tag is not None
    title_text = title_tag.text.strip()
    # make title text lowercase, replace whitespace with _
    title_text = title_text.lower().replace(' ', '_')
    # prepend timestamp ISO
    title_text = f'{datetime.now().isoformat()}_{title_text}'

    output_dir = f'output/{title_text}'
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, 'concept.xml')
    with open(file_path, 'w') as file:
        file.write(concept)


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
DO include <rejectedIdeas>, <acceptedIdea>, <title>, <cover>, <firstSentence>
    tags within the <novelConcept> tag.
DO make the <rejectedIdeas> tag a short brainstorm of three dramatically
    different directions.
DO make the <acceptedIdea> tag a fourth idea that's better
    than the rejected ones.
DO make the <title> the title of the book.
DO make the <cover> tag a Midjourney prompt for generating the cover art.
DO make the <firstSentence> tag the first sentence of the book.
DO make the genre dramatic literary fiction appropriate for a Pulitzer."""
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
