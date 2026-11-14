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
		{"role": "developer", "content": f'''You answer questions about the Bharatiya Nyaya Sanhita (BNS), 2023.\
Rules:
- Use ONLY the sections provided below. Do not use outside knowledge.
- Cite the section number for every claim.
- If the sections do not answer the question, set found to false
and do not guess.
- Reply in JSON with the keys: answer, citations, found.'''},
		{"role":"system","content":f"{context}"},
		{"role":"user","content":f"{question}"}],
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

def ask():
    question = input('qn? : ')
    context = get_context(question)
    print(get_answer(question,context))
    
    
    
