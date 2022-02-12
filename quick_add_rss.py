import sys
import json

rsslink = sys.argv[1]
name = sys.argv[2]

print(rsslink)

s = {
    "name": name,
    "favicon": "/".join(rsslink.split("/")[:3]) + "/favicon.ico"
}

ss = "search/" + ".".join(sys.argv[2:] + ["rss"]) + ".json"

n = {
    "data": rsslink,
    "type": "link" 
}

nn = "nodes/" + sys.argv[2] + ".json"

json.dump(s, open(ss, "w"))
json.dump(n, open(nn, "w"))

