import os 
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

completion = client.chat.completions.create(
    model="moonshotai/Kimi-K2-Instruct",
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ]
)

print(completion.choices[0].message.content)