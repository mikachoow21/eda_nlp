# Easy data augmentation techniques for Question and Answer using SQUAD 
# By Micah Weitzman 
# Based on agument.py by Jason Wei and Kai Zou

from eda import eda
from tqdm import tqdm
import random
import codecs
import re

#arguments to be parsed from command line
import argparse
import json 
ap = argparse.ArgumentParser()
ap.add_argument("--input", required=True, type=str, help="input file of unaugmented data")
ap.add_argument("--output", required=False, type=str, help="output file of unaugmented data")
ap.add_argument("--num_aug", required=False, type=int, help="number of augmented sentences per original sentence")
ap.add_argument("--alpha", required=False, type=float, help="percent of words in each sentence to be changed")
ap.add_argument("--percent_data", required=False, type=int, help="percentage of data to train")
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

# percentage of data to augment 
percent_data = 100#default 
if args.percent_data and args.percent_data > 0 and args.percent_data < 100: 
    percent_data = args.percent_data

# W
def find_all_substring_loc(big_str, sub_str):
    i = big_str.find(sub_str)
    while i != -1: 
        yield i
        i = big_str.find(sub_str, i+1)

#generate more data with standard augmentation
def gen_eda(train_orig, output_file, alpha, num_aug=9):

    with open(train_orig, 'r') as file: 
        data = file.read()
        data_dict = json.loads(data)
        file.close()

    
    # Going through each question, the following creates a few augmented answers 
    #   and randomly selects one to replace. It then replaces the oringal answer with 
    #   the newly augmented one in the orignal pararaph
    
    print("Augmenting questions")
    prog_bar = tqdm(data_dict["data"])
    #  TODO: maybe use more augmented sections
    omit_answers = 0
    for subject in prog_bar:
        subject["title"] = codecs.decode(subject["title"], 'unicode_escape')
        for paragraph in subject["paragraphs"]:
            paragraph["context"] = codecs.decode(paragraph["context"], 'unicode_escape')
            prog_bar.set_description("%s" % subject["title"])
            # print('[{} / {}] subjects'.format(i+1, len(data_dict["data"])) + '[{} / {}] paragraph'.format(j+1, len(subject["paragraphs"])))
            for qa in paragraph["qas"]:
                qa["answers"][0]["text"] = codecs.decode(qa["answers"][0]["text"], 'unicode_escape')
                old_sentence = qa["answers"][0]["text"]
                #find best match in context 
                mat_pos = [i for i in find_all_substring_loc(paragraph["context"], old_sentence)]
                if len(mat_pos) and np.random()*100 <= percent_data:
                    start_question = min(mat_pos, key=lambda x : abs(x-qa["answers"][0]["answer_start"]))
                else: # if we can't find the answer, remove it 
                    paragraph["qas"].remove(qa)
                    omit_answers += 1
                    continue
                qa["answers"][0]["answer_start"] = start_question
                #qa["question"] = codecs.decode(qa["question"], 'unicode_escape')
                #augment sentence find all spubstring matches 
                aug_sentences = eda(old_sentence, alpha_sr=alpha, alpha_ri=alpha, alpha_rs=alpha, p_rd=alpha, num_aug=num_aug)
                aug_sentences = set([i for i in aug_sentences if i ])
                if len(aug_sentences) == 0:
                    paragraph["qas"].remove(qa)
                    omit_answers += 1
                    continue
                new_sentence = random.sample(aug_sentences,1)[0] # choose a random new setence 
                split_context = [
                    paragraph["context"][: start_question],
                    new_sentence, 
                    paragraph["context"][start_question+len(old_sentence) :]]
                paragraph["context"] = ''.join(split_context)
                qa["answers"][0]["text"] = new_sentence


    # print("Finding answer locations")
    # ans_time_bar = tqdm(data_dict["data"])
    # omit_answers = 0
    # for subject in ans_time_bar:
    #     for paragraph in subject["paragraphs"]:
    #         for qa in paragraph["qas"]:
    #             s= qa["answers"][0]["text"]
    #             matches = re.finditer(s, paragraph["context"])
    #             mat_pos = [match.start() for match in matches]
    #             if len(mat_pos) and paragraph["context"].find(s) != -1:
    #                 qa["answers"][0]["answer_start"] = min(mat_pos, key=lambda x:abs(x-qa["answers"][0]["answer_start"]))
    #             else: 
    #                 paragraph["qas"].remove(qa)
    #                 omit_answers += 1
                    
    # print("Questions omitted: %d" % omit_answers)
    # with open(output_file, 'w', encoding="utf-8") as writer:
    #     json.dump(data_dict, writer, ensure_ascii=False)
    #     writer.close()
    # print("generated augmented sentences with eda for " + train_orig + " to " + output_file + " with num_aug=" + str(num_aug))
    print("Questions omitted: %d" % omit_answers)
    with open(output_file, 'w') as writer:
        json.dump(data_dict, writer)
        writer.close()
    print("generated augmented sentences with eda for " + train_orig + " to " + output_file + " with num_aug=" + str(num_aug))

#main function
if __name__ == "__main__":

    #generate augmented sentences and output into a new file
    gen_eda(args.input, output, alpha=alpha, num_aug=num_aug)