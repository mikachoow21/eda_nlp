import json
import sys

from tqdm import tqdm

def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)  # use start += 1 to find overlapping matches


def to_hex(s):
    return " ".join(map(hex, map(ord, s)))


def handle_nobreak(cand, text):
    if cand == text:
        return cand
    if cand.replace(u'\u00A0', ' ') == text:
        return cand
    elif cand == text.replace(u'\u00A0', ' '):
        return text
    raise Exception("{} '{}' {} '{}'".format(cand, to_hex(cand), text, to_hex(text)))


# resolving unicode complication
def data_test(in_path, out_path):
    data = json.load(open(in_path, 'r'))

    wrong_loc_count = 0
    loc_diffs = []

    for article in data['data']:
        for para in article['paragraphs']:
            # para['context'] = para['context'].replace(u'\u000A', '')
           # para['context'] = para['context'].replace(u'\u00A0', ' ')
            context = para['context']
            for qa in para['qas']:
                for answer in qa['answers']:
                  #  answer['text'] = answer['text'].replace(u'\u00A0', ' ')
                    text = answer['text']
                    answer_start = answer['answer_start']
                    if context[answer_start:answer_start + len(text)] == text:
                        if text.lstrip() == text:
                            pass
                        else:
                            answer_start += len(text) - len(text.lstrip())
                            answer['answer_start'] = answer_start
                            text = text.lstrip()
                            answer['text'] = text
                    else:
                        wrong_loc_count += 1
                        text = text.lstrip()
                        answer['text'] = text
                        starts = list(find_all(context, text))
                        if len(starts) == 1:
                            answer_start = starts[0]
                        elif len(starts) > 1:
                            new_answer_start = min(starts, key=lambda s: abs(s - answer_start))
                            loc_diffs.append(abs(new_answer_start - answer_start))
                            answer_start = new_answer_start
                        else:
                            raise Exception()
                        answer['answer_start'] = answer_start

                    answer_stop = answer_start + len(text)
                    answer['answer_stop'] = answer_stop
                    assert para['context'][answer_start:answer_stop] == answer['text'], "{} {}".format(
                        para['context'][answer_start:answer_stop], answer['text'])

    print(wrong_loc_count, loc_diffs)

    mismatch_count = 0
    dep_fail_count = 0
    no_answer_count = 0

    size = sum(len(article['paragraphs']) for article in data['data'])
    pbar = tqdm(range(size))


    #print(mismatch_count, dep_fail_count, no_answer_count)

    print("saving...")
    with open(out_path, 'w') as writer:
            writer.write(json.dumps(data))
            writer.close()
            print("file writtten")
