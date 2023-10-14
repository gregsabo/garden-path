import os
from dotenv import load_dotenv
import openai

load_dotenv()
print("Env", os.getenv("OPENAI_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")


def main():
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "Generate a concept for a full-length novel.\nDO encode your entire response in XML.\nDO make the root tag <novelConcept>.\nDO include <thought>, <title>, <cover>, <firstSentence> tags within the <novelConcept> tag.\nDO make the <thought> tag a short brainstorm of three dramatically different directions.\nDO make the <title> the title of the book.\nDO make the <cover> tag a Midjourney prompt for generating the cover art.\nDO make the <firstSentence> tag the first sentence of the book.\nDO make the genre dramatic literary fiction appropriate for a Pulitzer.",
            },
            {"role": "user", "content": ""},
        ],
        temperature=1,
        max_tokens=4009,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
