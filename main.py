import os
from pprint import pprint
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def main():
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
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
