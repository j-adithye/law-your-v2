from laws_app.search import hybrid_search
from django.core.management.base import BaseCommand


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
    help = "Hybrid search over BNS sections"
    
    def handle(self, *args, **options):
        for i in range(len(q)):
            self.stdout.write(f"{i+1},{[s.number for s in hybrid_search(q[i], limit=5)]}")
            self.stdout.write(" ")