from bs4 import BeautifulSoup
import requests
import feedparser
import random
import stanza
import json
import pymorphy2
from fuzzywuzzy import fuzz

class RSSInferenceWorker():
    def __call__(self, t, d):
        if t == "link":
            parsed_feed = feedparser.parse(d)
            for text in self.texts_from_rss(parsed_feed):
                yield "text", text, "load"
        else:
            yield None

    def texts_from_rss(self, parsed_feed):
        p = random.choice(parsed_feed.entries)
        try:
            html = requests.get(p.link).content.decode("utf-8")
            soup = BeautifulSoup(html, 'html.parser')
            texts = soup.findAll(text=True)
            good_tags = ['p']
            text = p.title + "; " + u" ".join(t.strip() for t in texts if good_tags.count(t.parent.name) > 0)
        except Exception:
            print("RSS parser error")
        yield text


class NERInferenceWorker():
    
    def __init__(self):
        self.nlp = stanza.Pipeline(lang='ru', processors='tokenize,ner')
        self.morph = pymorphy2.MorphAnalyzer()

    def __call__(self, t, d):
        datas = []
        if t == "text":
            doc = self.nlp(d)
            for sent in doc.sentences:
                for ent in sent.ents:  
                    ent = json.loads(str(ent))
                    type = ent["type"]
                    data = ent["text"]
                    f = False
                    for od in datas:
                        if fuzz.ratio(od, data) > 30:
                            f = True
                            break
                    if f:
                        continue    
                    if type == "LOC":
                        yield type, data, "NER"
                    else:
                        yield type, data, "NER"
                    datas.append(data)

class NERDistanceWorker():

    def __call__(self, t1, d1, t2, d2):
        typelist = ["ORG", "PER", "LOC", "S-PER", "S-ORG", "S-LOC"]
        if t1 in typelist and t2 in typelist:
            r = fuzz.ratio(d1, d2) / 100
            if r > 0.7:
                return "sim", str(r), "similarity"
            else:
                return None
            
        





#if __name__ == "__main__":
#    build_model(configs.ner.ner_rus_bert_torch, download=True)