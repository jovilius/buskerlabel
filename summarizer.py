import os
import json
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY").strip("\""),
)

def filter_and_summarize_ai_music(story: str) -> json:
    prompt = f"""
You are an expert journalist and curator about AI (Artificial Intelligence) and music.

Check if the given story discusses AI (Artificial Intelligence) and music together. Specifically, look for topics that involve AI being used in music creation, composition, production, analysis, or performance.

If check is "Yes", return as a summary a catchy, compelling, click-bait and short description that highlights the key points about AI and music.

If the check is "No", return "off-topic" as summary.

Story: '''{story}'''

Return a JSON with the fields "check" and "summary".
"""
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o-mini",
    )
    reply = response.choices[0].message.content.strip().strip("```").strip("json").strip()
    return json.loads(reply)
