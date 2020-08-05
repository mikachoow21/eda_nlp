import json

with open("data/squad-v1.1.json", "r") as f:
    sq_dict = json.load(f)

fst_entry = sq_dict["data"][0]
data = sq_dict["data"]


# Get list of all of the "contexts"/paragraphs in SQUAD
contexts = list()
for i, para in enumerate(data):
    for j, p in enumerate(para["paragraphs"]): 
        contexts.append((i,p["context"]))

# Write list of 
with open("data/contexts.txt", "w+") as f:
    for title,sent in contexts:
        f.write(str(title) + "\t" + sent.lower().replace("\n", "\-n") + "\n")