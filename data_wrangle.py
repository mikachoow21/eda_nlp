import json
import codecs
from tqdm import tqdm
from pprint import pprint
import re 

with open("data/new_aug_squad.json", 'r') as file: 
    data = file.read()
    data_dict = json.loads(data)
    file.close()

bad_answers = 0
total_ans = 0

for subject in data_dict["data"]:
    for i, paragraph in enumerate(subject["paragraphs"]):
        #paragraph["context"] = codecs.decode(paragraph["context"], 'unicode_escape')
        #print("Paragraph {}: length = {}".format(i,len(paragraph["context"])))
        for j, qa in enumerate(paragraph["qas"]):
            #qa["answers"][0]["text"] = codecs.decode(qa["answers"][0]["text"], 'unicode_escape')
            s = qa["answers"][0]["text"] 
            total_ans +=1
            matches = re.finditer(s, paragraph["context"])
            mat_pos = [match.start() for match in matches]  
            if qa["answers"][0]["answer_start"] in mat_pos or paragraph["context"].count(s) > 0:
                pass
            else:
                bad_answers+=1
                paragraph["qas"].remove(qa)
               # print("Subject {}: Paragraph {}: Question {}".format(subject["title"], i,j))
                # pprint(paragraph["context"])
                # pprint(qa)
                #print("start {}: find {}".format(qa["answers"][0]["answer_start"],paragraph["context"].find(s)))
print("{} total answers".format(total_ans))
print("{} bad answers".format(bad_answers))

with open("data/new_aug_squad.json", 'w') as writer:
    writer.write(json.dumps(data_dict))
    writer.close()

# Get list of all of the "contexts"/paragraphs in SQUAD
# prog_bar = tqdm(data_dict["data"])
# for subject in prog_bar:
#     for paragraph in subject["paragraphs"]:
#         paragraph["context"] = codecs.decode(paragraph["context"], 'unicode_escape')
#         prog_bar.set_description("%s" % subject["title"])
#         # print('[{} / {}] subjects'.format(i+1, len(data_dict["data"])) + '[{} / {}] paragraph'.format(j+1, len(subject["paragraphs"])))
#         for qa in paragraph["qas"]:
#             sentence = codecs.decode(qa["answers"][0]["text"], 'unicode_escape')
#             qa["question"] = codecs.decode(qa["question"], 'unicode_escape')
#             aug_sentences = set(eda(sentence, alpha_sr=alpha, alpha_ri=alpha, alpha_rs=alpha, p_rd=alpha, num_aug=num_aug))
#             new_sentence = random.sample(aug_sentences,1)[0] # choose a random new setence 
#             paragraph["context"] = paragraph["context"].replace(sentence, new_sentence)
#             qa["answers"][0]["text"] = new_sentence

# Write list of 
# writer = open(output_file, 'w', encoding='utf-8', errors="ignore")
# with open(output_file, 'w', encoding='utf-8', errors="ignore") as f:
#     for title,sent in contexts:
    