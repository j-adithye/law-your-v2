import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=
    os.getenv("NVIDIA_API_KEY"),
)

response = client.embeddings.create(
    model="nvidia/nemotron-3-embed-1b",
    input=["What is the punishment for murder under the BNS?"],
    encoding_format="float",
    extra_body={"input_type": "query"},
)

vector = response.data[0].embedding
print(len(vector))