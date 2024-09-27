from groq import Groq
import json

client = Groq( api_key="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" )

# Set the role of the Groq client as the sentimental analysis API
system_role = """
    You are an API designed to process multiple customer reviews and perform sentiment analysis.
    there will be one review given per line, and perform sentimental analysis on each review.
    always remember that you are an api you must not respond like human and your reply should be a valid json string without other text.
    The JSON schema must strictly follow this structure without any additional text:
    
    {
        "scores": [
            {
                "review": "review_text",
                "score": {
                    "positive": "number (0-100)",
                    "negative": "number (0-100)",
                    "neutral": "number (0-100)"
                }
            }
        ]
    }
"""


# Takes batch of reviews and return score for each sentiment as dictionary
def score(reviews):
    # Call the Groq API
    chat_completion = client.chat.completions.create(
        messages=[
            { "role": "system", "content": system_role },
            { "role": "user", "content": reviews, }
        ],
        model="llama3-8b-8192",  
        temperature=0.5,  
        max_tokens=1024,
        top_p=1, 
        stop=None, 
        stream=False,
    )

    # Extract the Response Content
    reply = chat_completion.choices[0].message.content

    # Attempt to Parse the json string in reply
    json_reply = json.loads(reply)

    return json_reply