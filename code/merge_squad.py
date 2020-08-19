from tqdm import tqdm
import json
import sys 
from data_wrangle import wrangle
from data_test import data_test

d = {"data": [], "version": "1.1"}

output = sys.argv[1]+"_all.json"

for i in ["A", "B", "C", "D"]:
    input_file = sys.argv[1] + i+".json"

    # get rid of bad examples 
    while wrangle(input_file, input_file) != 0:
        wrangle(input_file, input_file)

    # realign answer
    data_test(input_file, input_file)

    data_dict = dict()
    with open(input_file, 'r') as f: 
        data = f.read()
        data_dict = json.loads(data)
        f.close()
    print("Working on " + input_file)

    prog_bar = tqdm(data_dict["data"])
    for subject in prog_bar:
        d["data"].append(subject)

with open(output, 'w') as writer:
    writer.write(json.dumps(d))
    writer.close()

print("Saved all data in " + output)

