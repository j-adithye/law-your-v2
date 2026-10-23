import pdfplumber as plumber
import re



chunks = []

def to_chunks(page,chunks):
    {
		"section_number": 0,
		"chapter": "",
		"title": "",
		"paragraphs": [],
		"illustrations": [],
	}
    
    pattern = re.compile(r'^[1-9]{1,3}\.')
    for line in page:
        start_of_line = line['x0']
        if any('Bold','bold','BOLD') in line['chars']['fontname']:
            if pattern.match(line['text'][:4]):
                pass
            else:
                title += (line + ' ')
        else:
            pass
            
                
            
    
    

with plumber.open("./data/raw/BNS2023.pdf") as pdf:
    page = pdf.pages[74]                  #taking page 74 
    height = page.height
    width = page.width
    cropped = page.crop((0,0,width,height))     #cropping top
    full_text = cropped.extract_text_lines()

n = -2
print(full_text[n]['text'])
print(round(full_text[n]['bottom']-full_text[n-1]['bottom']))
print()

# print(*(x['text'] for x in full_text))
# 23.779999999999973
