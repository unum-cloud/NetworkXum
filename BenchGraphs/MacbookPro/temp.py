
import json

json_stats = []
json_pontdb = []
json_pygraphdb = []
with open('bench/MacbookPro/stats.json', 'r') as file:
    json_stats = json.load(file)

for obj in json_stats:
    if obj['database'].startswith('PontDB'):
        json_pontdb.append(obj)
    else:
        json_pygraphdb.append(obj)

with open("bench/MacbookPro/stats_pontdb.json", "w") as file:
    file.write(json.dumps(json_pontdb))
with open("bench/MacbookPro/stats_pygraphdb.json", "w") as file:
    file.write(json.dumps(json_pygraphdb))
