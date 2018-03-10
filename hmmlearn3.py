import collections
import json
import sys

filename = sys.argv[1]
training_file = open(filename, encoding='utf-8')
tag_counts = dict()
word_tag_counts = dict()
total_sentence_count = 0
beginning_tag_count = dict()
transition_counts = dict()
transition_out_counts = dict()
distinct_tags = []
end_transition = dict()

for line in training_file:
    total_sentence_count += 1
    words_and_tags = line.split()
    beginning = True
    prev_tag = ""
    sentenceLength = len(words_and_tags)
    for i in range(0, sentenceLength):
        word_tag = words_and_tags[i].rsplit('/', 1)
        word = word_tag[0]
        tag = word_tag[1]
        if tag in tag_counts:
            old_count = tag_counts[tag]
            tag_counts[tag] = old_count+1
            if beginning:
                if tag in beginning_tag_count:
                    temp_count = beginning_tag_count[tag]
                    beginning_tag_count[tag] = temp_count + 1
                else:
                    beginning_tag_count[tag] = 1
                beginning = False
            else:
                if prev_tag in transition_counts:
                    temp_count = transition_out_counts[prev_tag]
                    transition_out_counts[prev_tag] = temp_count + 1
                    if tag in transition_counts[prev_tag]:
                        temp_count = transition_counts[prev_tag][tag]
                        transition_counts[prev_tag][tag] = temp_count + 1
                    else:
                        transition_counts[prev_tag][tag] = 1
                else:
                    transition_counts[prev_tag] = {tag: 1}
                    transition_out_counts[prev_tag] = 1
        else:
            tag_counts[tag] = 1

        prev_tag = tag

        if word in word_tag_counts:
            found = False
            for tag_for_word in word_tag_counts[word]:
                if tag == tag_for_word:
                    old_count_for_tag = word_tag_counts[word][tag]
                    word_tag_counts[word][tag] = old_count_for_tag + 1
                    found = True
            if not found:
                word_tag_counts[word][tag] = 1

        else:
            word_tag_counts[word] = {tag: 1}

        if i == sentenceLength-1:
            if tag not in end_transition:
                end_transition[tag] = 1
            else:
                old_end_count = end_transition[tag]
                end_transition[tag] = old_end_count + 1


ordered_tag_counts = collections.OrderedDict(sorted(tag_counts.items()))

dict_to_write_json = dict()
dict_to_write_json['emission probabilities'] = {}
tag_count = 0
# adding code below for add one smoothing
# word_tag_counts["unknown word"] = {}
# end of code added for add one smoothing

for tag in ordered_tag_counts:
    dict_to_write_json['emission probabilities'][tag] = {}
    tag_count += 1
    distinct_tags.append(tag)
    # adding code below for add one smoothing
    # old_tag_count = ordered_tag_counts[tag]
    # ordered_tag_counts[tag] = old_tag_count + 1
    # word_tag_counts["unknown word"][tag] = 1
    # end of code added for add one smoothing
# print("total tag count is %d" % tag_count)

ordered_word_tag_counts = collections.OrderedDict(sorted(word_tag_counts.items()))

dict_to_write_json['new emission'] = {}
# new code added below to check alternate way of emission prob
for word in ordered_word_tag_counts:
    dict_to_write_json['new emission'][word] = {}
    for tag_for_word in word_tag_counts[word]:
        count = word_tag_counts[word][tag_for_word]
        total_tag_count = tag_counts[tag_for_word]
        emission_prob = count / total_tag_count
        dict_to_write_json['new emission'][word][tag_for_word] = emission_prob

word_count = 0
word_tag_comb_count = 0
for word in ordered_word_tag_counts:
    # print(word)
    word_count += 1
    for tag_for_word in word_tag_counts[word]:
        # print(tag_for_word, word_tag_counts[word][tag_for_word])
        count = word_tag_counts[word][tag_for_word]
        total_tag_count = tag_counts[tag_for_word]
        emission_prob = count/total_tag_count
        dict_to_write_json['emission probabilities'][tag_for_word][word] = emission_prob
        word_tag_comb_count += 1

# print("total words are %d and word tag combination is %d" % (word_count, word_tag_comb_count))

dict_to_write_json['transition probabilities'] = {}
for tag in transition_out_counts:
    dict_to_write_json['transition probabilities'][tag] = {}

# code for add one smoothing - new
for tag in distinct_tags:
    dict_to_write_json['transition probabilities'][tag] = {}
    if tag not in beginning_tag_count:
        beginning_tag_count[tag] = 0.5
    if tag not in end_transition:
        end_transition[tag] = 0.5

total_tag_count = len(distinct_tags)
# print(total_tag_count)
dict_to_write_json['total_tag_count'] = total_tag_count


for tag in distinct_tags:
    if tag not in transition_counts:
        transition_counts[tag] = {}
        for next_tag in distinct_tags:
            transition_counts[tag][next_tag] = 1
            transition_out_counts[tag] = len(distinct_tags)
    for next_tag in distinct_tags:
        if next_tag not in transition_counts[tag]:
            transition_counts[tag][next_tag] = 1
            transition_out_count_old = transition_out_counts[tag]
            transition_out_counts[tag] = transition_out_count_old + 1

'''
for prev_tag in transition_counts:
    # print(prev_tag)
    for tag in distinct_tags:
        if tag not in transition_counts[prev_tag]:
            # print('adding tag')
            # below for add one smoothing of transition probabilities
            transition_counts[prev_tag][tag] = 1
            transition_out_count_old = transition_out_counts[prev_tag]
            transition_out_counts[prev_tag] = transition_out_count_old + 1
'''
for prev_tag in transition_counts:
    for next_tag in transition_counts[prev_tag]:
        count = transition_counts[prev_tag][next_tag]
        total_tag_out_count = transition_out_counts[prev_tag]
        transition_probability = count/total_tag_out_count
        dict_to_write_json['transition probabilities'][prev_tag][next_tag] = transition_probability

dict_to_write_json['beginning transition probabilities'] = {}


# added below for add one smoothing
beginning_tag_sum = 0
for tag in beginning_tag_count:
    beginning_tag_sum += beginning_tag_count[tag]

for tag in beginning_tag_count:
    transition_probability = beginning_tag_count[tag]/beginning_tag_sum
    dict_to_write_json['beginning transition probabilities'][tag] = transition_probability

end_tag_sum = 0
for tag in beginning_tag_count:
    end_tag_sum += beginning_tag_count[tag]
dict_to_write_json['end transition probabilities'] = {}
for tag in end_transition:
    transition_probability = end_transition[tag]/end_tag_sum
    dict_to_write_json['end transition probabilities'][tag] = transition_probability

with open('hmmmodel.txt', 'w', encoding='utf-8') as outfile:
    json.dump(dict_to_write_json, outfile, indent=4, ensure_ascii=False)

with open('hmmmodel.json', 'w', encoding='utf-8') as outfile:
    json.dump(dict_to_write_json, outfile, indent=4, ensure_ascii=False)