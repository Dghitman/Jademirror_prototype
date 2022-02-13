# app/main.py

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
import hashlib
import json
from graph import Graph, WorkerPool
import random
import os

wp = WorkerPool()

app = FastAPI(title="FastAPI, Docker, and Traefik")

@app.get("/", response_class=HTMLResponse)
def main_page():
    return open("index.html","r").read()


@app.post("/g")
async def graph_update(request: Request):
    return upd(await request.json())

def upd(request):
    rg = Graph(request)
    return wp(rg)

@app.post("/q")
async def search_nodes(request: Request):
    r = []
    j = await request.json()
    q = j["query"]
    for nn in os.listdir("search"):
        if q.lower() in nn.lower().split(".")[:-1]:
            obj = json.load(open(f"search/{nn}","r"))
            r.append({
                "name": obj["name"],
                "favicon": obj["favicon"]
            })
    return r

@app.post("/n")
async def add_node(request: Request):
    j = await request.json()
    obj = json.load(open(f"nodes/{j['name']}.json","r"))
    if "favicon" not in obj:
        obj["favicon"] = "/".join(obj["data"].split("/")[:3]) + "/favicon.ico"
    return obj
