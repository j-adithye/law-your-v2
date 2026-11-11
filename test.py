import os
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NVIDIA_API_KEY")
# URL = "https://ai.api.nvidia.com/v1/retrieval/nvidia/nemotron-3.5-rerank-8b/reranking"

# headers = {
#     "Authorization": f"Bearer {API_KEY}",
#     "Accept": "application/json",
# }

# query = "What is the punishment for murder under the BNS?"

# passages = [
#     "Section 303. Theft: whoever intends to take dishonestly any movable property out of the possession of any person...",
#     "Section 103. Punishment for murder: whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine.",
#     "Section 115. Voluntarily causing hurt: whoever does any act with the intention of causing hurt to any person...",
#     "Section 101. Murder: culpable homicide is murder if the act by which the death is caused is done with the intention of causing death...",
# ]

# payload = {
#     "model": "nvidia/nemotron-3.5-rerank-8b",
#     "query": {"text": query},
#     "passages": [{"text": p} for p in passages],
# }

# response = requests.post(URL, headers=headers, json=payload, timeout=60)
# response.raise_for_status()
# data = response.json()
# print(data)  # look at the raw shape first

# for r in sorted(data["rankings"], key=lambda r: r["logit"], reverse=True):
#     print(f'{r["logit"]:8.3f}  {passages[r["index"]][:70]}')
    
    
    
from openai import OpenAI

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = API_KEY
)

start = time.perf_counter()

completion = client.chat.completions.create(
  model="nvidia/nemotron-3.5-lightning-30b-a3b",
  messages=[{"role":"user","content":"Write a punishment for theft from bank in a fictional city of zolonia."}],
  temperature=0,
  top_p=0.1,
  max_tokens=1000,
  extra_body={"chat_template_kwargs":{"enable_thinking":False}},
)
end = time.perf_counter() - start

print(completion.choices[0].message.content)
print(end)
