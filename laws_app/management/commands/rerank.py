from laws_app.search import hybrid_search, rerank
from django.core.management.base import BaseCommand
from laws_app.models import Section
import time

q = ["What is the punishment for murder?",
     "What is the difference between murder and culpable homicide?",
     "Someone hit me with a stick and broke my arm",
     "A man on a bike grabbed my phone and rode off",
     "A group of ten people attacked a house at night and looted it",
     "He threatened to hurt my family unless I paid him money",
     "My husband and in-laws keep harassing me for dowry",
     "A man keeps following a woman and messaging her after she said no",
     "An employee was trusted with company money and spent it on himself",
     "What is the colour of an apple",
     ]


class Command(BaseCommand):
    help = "Reranking results fo hybrid search over BNS sections"
    
    def handle(self, *args, **options):
        for i in range(len(q)):
            
            sections = hybrid_search(q[i], limit=20)
            candidates = list(Section.objects.filter(number__in=sections))
            start = time.perf_counter()
            result = rerank(q[i], candidates, 5)
            end = time.perf_counter() - start
            
            print(f"Qn.no: {i+1} : time= {end :.2f}s")
            for section, score in result:
                print(f"{score:8.3f} {section.number} ")
            self.stdout.write(" ")