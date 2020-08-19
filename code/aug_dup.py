# Easy data augmentation techniques for Question and Answer using SQUAD 
# By Micah Weitzman 
# Based on agument.py by Jason Wei and Kai Zou

from eda import eda
from tqdm import tqdm
import numpy as np
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

# W
def find_all_substring_loc(big_str, sub_str):
    i = big_str.find(sub_str)
    a = []
    while i != -1: 
        a.append([i,i+len(sub_str)])
        i = big_str.find(sub_str, i+1)
    return np.array(a)

percent_data = 100#default 
if args.percent_data and args.percent_data > 0 and args.percent_data < 100: 
    percent_data = args.percent_data


big_data = None
#generae more data with standard augmentation
def gen_eda(train_orig, output_file, alpha, num_aug=9):

    with open(train_orig, 'r') as file: 
        data = file.read()
        data_dict = json.loads(data)
        file.close()

    
    # Going through each question, the following creates a few augmented answers 
    #   and randomly selects one to replace. It then replaces the oringal answer with 
    #   the newly augmented one in the orignal pararaph
    over = 0.0
    total_questions = 0.0
    if percent_data < 100: 
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
                    sentence = codecs.decode(qa["answers"][0]["text"], 'unicode_escape')
                    sentence = qa["answers"][0]["text"]
                    total_questions += 1.0
                    if np.random.randint(0, 100) > percent_data:
                        over += 1.0
                        paragraph["qas"].remove(qa)

        print("Questions omitted: %d" % omit_answers)
        print("Total questions: %d" % total_questions)
        print("Percent: %f" % (float(total_questions - omit_answers) / float(total_questions)))
        print("over %d" % over)
        with open(output_file , 'w') as writer:
            try:
                writer.write(json.dumps(data_dict))
            except:
                writer.write(data_dict)
            writer.close()
        print("Saved augmented " + str(percent_data))
        exit()

    prog_bar = tqdm(data_dict["data"])
    omit_answers = 0
    for subject in prog_bar:
        subject["title"] = codecs.decode(subject["title"], 'unicode_escape')
        for paragraph in subject["paragraphs"]:
            paragraph["context"] = codecs.decode(paragraph["context"], 'unicode_escape')
            prog_bar.set_description("%s" % subject["title"])
            # print('[{} / {}] subjects'.format(i+1, len(data_dict["data"])) + '[{} / {}] paragraph'.format(j+1, len(subject["paragraphs"])))
            for qa in paragraph["qas"]:
                sentence = codecs.decode(qa["answers"][0]["text"], 'unicode_escape')
                sentence = qa["answers"][0]["text"]
                #Find the start and end indicies where the original answer occurs in the context
                sentence_idxs = find_all_substring_loc(paragraph['context'], sentence)
                #Get the start indicies only
                if sentence_idxs.size == 0:
                    paragraph["qas"].remove(qa)
                    omit_answers += 1
                    continue
                
                idx_starts = sentence_idxs[:,0]
                #Get the (index of the) best starting index - the one that is closest to the original starting index
                best_start_idx = np.argmin(np.abs(idx_starts - qa['answers'][0]["answer_start"]))
                #Define the answer span as the span starting with the best starting index and ending with its associated ending index
                answer_span = sentence_idxs[best_start_idx, :]
                #Augment the sentences
                aug_sentences = set(eda(sentence, alpha_sr=alpha, alpha_ri=alpha, alpha_rs=alpha, p_rd=alpha, num_aug=num_aug))
                new_sentence = random.sample(aug_sentences,1)[0] # choose a random new setence
                qa["answers"][0]["text"] = new_sentence
                #Replace the location of the original answer in the context with the new answer
                paragraph['context'] = paragraph['context'][0:answer_span[0]] + new_sentence + paragraph['context'][answer_span[1]: -1]
                #update the starting index parameter
                qa["answers"][0]['answer_start'] = int(answer_span[0])
    # print("Questions omitted: %d" % omit_answers)
    # with open(output_file, 'w', encoding="utf-8") as writer:
    #     json.dump(data_dict, writer, ensure_ascii=False)
    #     writer.close()
    # print("generated augmented sentences with eda for " + train_orig + " to " + output_file + " with num_aug=" + str(num_aug))
    print("Questions omitted: %d" % omit_answers)
    with open(output_file, 'w') as writer:
        try:
            writer.write(json.dumps(data_dict))
        except:
            writer.write(data_dict)
        writer.close()
    print("generated augmented sentences with eda for " + train_orig + " to " + output_file + " with num_aug=" + str(num_aug))
#main function
if __name__ == "__main__":

    #generate augmented sentences and output into a new file
    gen_eda(args.input, output, alpha=alpha, num_aug=num_aug)