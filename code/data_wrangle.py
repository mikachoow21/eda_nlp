import json
import codecs
from tqdm import tqdm
from pprint import pprint
import re 
import sys

def wrangle(in_file, output_file): 
    with open(in_file, 'r') as f: 
        data_dict = json.loads(f.read())
        f.close()

    bad_answers = 0 
    total_ans = 0
   # articles_removed = 0 

    for subject in data_dict["data"]:
        for i, paragraph in enumerate(subject["paragraphs"]):
            paragraph["context"] = codecs.decode(paragraph["context"], 'unicode_escape')
            #print("Paragraph {}: length = {}".format(i,len(paragraph["context"])))
            #print("# questions: %d" % len(paragraph["qas"]))
            for j, qa in enumerate(paragraph["qas"]):
                qa["answers"][0]["text"] = codecs.decode(qa["answers"][0]["text"], 'unicode_escape')
                s = qa["answers"][0]["text"] 
                total_ans +=1
                # matches = re.finditer(s, paragraph["context"])
                # mat_pos = [match.start() for match in matches]  
                # if qa["answers"][0]["answer_start"] in mat_pos or paragraph["context"].count(s) > 0:
                #     pass
                if paragraph["context"].find(s) == -1 or s == "": 
                    bad_answers+=1
                    paragraph["qas"].remove(qa)
                    
    print("{} total answers".format(total_ans))
    print("{} bad answers".format(bad_answers))
   # print("Aricles removed: %d" % articles_removed)


    try:
        with open(output_file, 'w') as writer:
            writer.write(json.dumps(data_dict))
            writer.close()
            print("file writtten")
    except: 
        pass
    return bad_answers
