import os
from dotenv import load_dotenv
from openai import OpenAI
from .search import retrieve

load_dotenv()

API_KEY = os.getenv("NVIDIA_API_KEY")
client = OpenAI(
    base_url = "https://integrate.api.nvidia.com/v1",
    api_key = API_KEY
    )

def get_answer(question:str, context:str) -> str:

	completion = client.chat.completions.create(
	model="nvidia/nemotron-3.5-lightning-30b-a3b",
	messages=[
		{"role": "system", "content": f'''You answer questions about the Bharatiya Nyaya Sanhita (BNS), 2023.
Rules:
- Use ONLY the sections provided below as Context. Do not use outside knowledge. Not even knowledge related to the given context.
- If a user asks about 'IPC' mention that you do not have any information on that.
- Cite the section number for every claim. Return citations as a list of section numbers only.
- If the sections do not answer the question, set found to false
and do not guess.
- Reply in JSON with the keys: answer, citations, found.
- Don't say things like 'according to the context provided' and “don't list or dump all the sections.”
Context:
{context}
'''},{"role":"user","content":f"{question}"}],
	temperature=0.2,
	top_p=0.95,
	max_tokens=1000,
    seed=42,
	# stream='True',
	# service_tier='priority',
	extra_body={"chat_template_kwargs":{"enable_thinking":False}},
	)

	return(completion.choices[0].message.content)
 
 
def get_context(question:str) -> str:
    sections = retrieve(question=question, limit=20, top_n= 5)
    context = ""
    for section in sections:
        curr = f'''
'section_number': {section.number};
'title': {section.title};
'body': {section.body};
'illustrations': {section.illustrations};
'explanations': {section.explanations};
'exceptions': {section.exceptions}; 
\n'''
        context = context + curr
    return context

import json

def parse_answer(raw: str) -> dict:
    text = raw.strip()

    # remove ```json ... ``` fences if the model added them
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"answer": "", "citations": [], "found": False, "error": "bad_json"}

    # make sure the keys exist, even if the model skipped one
    return {
        "answer": data.get("answer", ""),
        "citations": data.get("citations", []),
        "found": bool(data.get("found", False)),
    }

def ask():
    question = input('qn? : ')
    context = get_context(question)
    raw = get_answer(question,context)
    result = parse_answer(raw)
    print(type(result))
    print('iam an ai assistant and can make mistakes this is not legal advice')
    return result
    
    
    
