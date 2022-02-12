from bs4 import BeautifulSoup
import requests
import feedparser
from deeppavlov import configs, build_model

class RSSInferenceWorker():
    def __call__(self, t, d):
        if t == "link":
            parsed_feed = feedparser.parse(d)
            for text in self.texts_from_rss(parsed_feed):
                yield "text", text, "load"
        else:
            yield None

    def texts_from_rss(self, parsed_feed):
        for p in parsed_feed.entries:
            try:
                html = requests.get(p.link).content.decode("utf-8")
                soup = BeautifulSoup(html, 'html.parser')
                texts = soup.findAll(text=True)
                good_tags = ['p']
                text = u" ".join(t.strip() for t in texts if good_tags.count(t.parent.name) > 0)
            except Exception:
                print("RSS parser error")
            yield text

class NERInferenceWorker():
    
    def __init__(self):
        self.ner_model = build_model(configs.ner.ner_rus_bert_torch, download=True)

    def __call__(self, t, d):
        if t == "text":
            yield "entities", self.ner_from_text(d), "NER"
        else:
            yield None        

    def ner_from_text(self, text):
        result = self.ner_model([text])
        entities = []
        new_entity = None
        new_tag = None
        for entity, tag in zip(result[0][0], result[1][0]):
            if tag == 'O':
                if new_entity != None:
                    entities.append([new_entity, new_tag])
                    new_tag = None
                    new_entity = None     
            else:
                if tag[0] == 'B': 
                    if new_entity != None:
                        entities.append([new_entity, new_tag])
                    new_entity = entity
                    new_tag = tag[2:]
                if tag[0] == 'I':
                    new_entity += (' ' + entity)
        if new_entity != None:
            entities.append([new_entity, new_tag])
        return entities