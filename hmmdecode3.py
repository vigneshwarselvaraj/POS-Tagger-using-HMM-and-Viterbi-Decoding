import json
import sys

with open('hmmmodel.txt', encoding='utf-8') as json_data:
    model_data = json.load(json_data)

emission_probabilities = model_data['new emission']
transition_probabilities = model_data['transition probabilities']
beginning_transition = model_data['beginning transition probabilities']
old_emission_probabilities = model_data['emission probabilities']
total_tag_count = model_data['total_tag_count']
end_probabilities = model_data['end transition probabilities']

filename = sys.argv[1]
# filename = "en_dev_raw.txt"
file_to_tag = open(filename, encoding='utf-8')
string_to_write_file = ""
unknown_words_count = 0
count_check = 0

for line in file_to_tag:
    tagAssigned = []
    words = line.split()
    prev_tag = ""
    beginning_word = True
    word_order = []
    prev_assigned_tags = dict()
    num_of_words = len(words)
    for i in range(0, num_of_words):
        prev_tag = ""
        assigned_tags = dict()

        if beginning_word:
            for tag in transition_probabilities: # just to get all distinct tags
                if beginning_transition.get(tag):
                    transition_probability = beginning_transition[tag]
                else:
                    transition_probability = 0.0
                if words[i] in emission_probabilities:
                    if tag in emission_probabilities[words[i]]:
                        emission_probability = emission_probabilities[words[i]][tag]
                    else:
                        emission_probability = 0.0
                else:
                    emission_probability = 1/total_tag_count
                totalProb = emission_probability * transition_probability
                assigned_tags[tag] = {}
                assigned_tags[tag]["prob_value"] = totalProb
                assigned_tags[tag]["backtrack"] = "beginning word"
            word_order.append(assigned_tags)
            prev_assigned_tags = assigned_tags
            beginning_word = False
        else:
            if words[i] in emission_probabilities:
                for tag in emission_probabilities[words[i]]:
                    emission_probability = emission_probabilities[words[i]][tag]
                    for prev_tag in list(prev_assigned_tags):
                        if prev_tag in transition_probabilities:
                                transition_probability = transition_probabilities[prev_tag][tag]
                                totalProb = prev_assigned_tags[prev_tag]["prob_value"] * emission_probability \
                                            * transition_probability
                                if tag in assigned_tags:
                                    oldProb = assigned_tags[tag].get("prob_value")
                                    if totalProb > oldProb:
                                        assigned_tags[tag]["prob_value"] = totalProb
                                        assigned_tags[tag]["backtrack"] = prev_tag
                                else:
                                    assigned_tags[tag] = {}
                                    assigned_tags[tag]["prob_value"] = totalProb
                                    assigned_tags[tag]["backtrack"] = prev_tag

                if assigned_tags:
                    word_order.append(assigned_tags)
                    prev_assigned_tags = assigned_tags
                
            else:
                for tag in transition_probabilities:
                    for prev_tag in prev_assigned_tags:
                            emission_probability = 1/total_tag_count
                            transition_probability = transition_probabilities[prev_tag][tag]
                            totalProb = prev_assigned_tags[prev_tag]["prob_value"] * transition_probability \
                                        * emission_probability
                            if tag in assigned_tags:
                                oldProb = assigned_tags[tag].get("prob_value")
                                if totalProb > oldProb:
                                    assigned_tags[tag]["prob_value"] = totalProb
                                    assigned_tags[tag]["backtrack"] = prev_tag
                            else:
                                assigned_tags[tag] = {}
                                assigned_tags[tag]["prob_value"] = totalProb
                                assigned_tags[tag]["backtrack"] = prev_tag
                if assigned_tags:
                    word_order.append(assigned_tags)
                    prev_assigned_tags = assigned_tags
                unknown_words_count += 1

    for tag in prev_assigned_tags:
        prev_assigned_tags[tag]["prob_value"] *= end_probabilities[tag]

    maxProb = float("-inf")
    lastTag = ""
    for tag in prev_assigned_tags:
        if prev_assigned_tags[tag].get("prob_value") > maxProb:
            maxProb = prev_assigned_tags[tag]["prob_value"]
            lastTag = tag
    line_tagged = ""

    for length in range(len(word_order), 0, -1):
        curr_word = word_order[length - 1]
        line_tagged = words[length - 1] + "/" + lastTag + " " + line_tagged
        tag = curr_word[lastTag]["backtrack"]
        lastTag = tag

    string_to_write_file += line_tagged + "\n"
with open('hmmoutput.txt', 'w', encoding='utf-8') as outfile:
    outfile.write(string_to_write_file)