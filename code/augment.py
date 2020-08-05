# Easy data augmentation techniques for Question and Answer using SQUAD 
# By Micah Weitzman 
# Based on agument.py by Jason Wei and Kai Zou

from eda import eda
import progressbar 
import random

#arguments to be parsed from command line
import argparse
import json 
ap = argparse.ArgumentParser()
ap.add_argument("--input", required=True, type=str, help="input file of unaugmented data")
ap.add_argument("--output", required=False, type=str, help="output file of unaugmented data")
ap.add_argument("--num_aug", required=False, type=int, help="number of augmented sentences per original sentence")
ap.add_argument("--alpha", required=False, type=float, help="percent of words in each sentence to be changed")
args = ap.parse_args()

#the output file
output = None
if args.output:
    output = args.output
else:
    from os.path import dirname, basename, join
    output = join(dirname(args.input), 'eda_' + basename(args.input))

#number of augmented sentences to generate per original sentence
num_aug = 9 #default
if args.num_aug:
    num_aug = args.num_aug

#how much to change each sentence
alpha = 0.1#default
if args.alpha:
    alpha = args.alpha

#generate more data with standard augmentation
def gen_eda(train_orig, output_file, alpha, num_aug=9):
    # output_data = {"data": []}
    # 
    # {data : list() [
    #       "title": "title", 
    #       "paragraphs": list() [
    #           "context": Text itself, 
    #           "qas": list() [
    #               {"answers": list() [
    #                   "answer_start": int(), 
    #                   "text": Answer text
    #                   ]
    #                "question": question text, 
    #                "id": question id 
    #               },
    #           ]
    #       ]
    #   ]}

    writer = open(output_file, 'w')
    with open(train_orig, 'r') as file: 
        data_dict = json.load(file)
        file.close()

    
    # Going through each question, the following creates a few augmented answers 
    #   and randomly selects one to replace. It then replaces the oringal answer with 
    #   the newly augmented one in the orignal pararaph

    #  TODO: maybe use more augmented sections
    for i, subject in enumerate(data_dict["data"]):
        print('[{} / {}] subjects'.format(i+1, len(data_dict["data"])))
        for j, paragraph in enumerate(subject["paragraphs"]):
            print('[{} / {}] subjects'.format(i+1, len(data_dict["data"])) + '[{} / {}] paragraph'.format(j+1, len(subject["paragraphs"])))
            for qa in paragraph["qas"]:
                sentence = qa["answers"][0]["text"] 
                aug_sentences = set(eda(sentence, alpha_sr=alpha, alpha_ri=alpha, alpha_rs=alpha, p_rd=alpha, num_aug=num_aug))
                new_sentence = random.sample(aug_sentences,1)[0] # choose a random new setence 
                paragraph["context"] = paragraph["context"].replace(sentence, new_sentence)
                qa["answers"][0]["text"] = new_sentence
                qa["answers"][0]["answer_start"] = paragraph["context"].find(new_sentence) # update new location of answer 
        
    
    writer.write(json.dumps(data_dict))
    writer.close()
    print("generated augmented sentences with eda for " + train_orig + " to " + output_file + " with num_aug=" + str(num_aug))

#main function
if __name__ == "__main__":

    #generate augmented sentences and output into a new file
    gen_eda(args.input, output, alpha=alpha, num_aug=num_aug)