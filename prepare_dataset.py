import random
import json

train = open('train.tsv','w', encoding="utf-8")
test_uniq = open('test_uniq.tsv','w', encoding="utf-8")
dev_uniq = open('dev_uniq.tsv','w', encoding="utf-8")
test = open('test.tsv','w', encoding="utf-8")
dev= open('dev.tsv','w', encoding="utf-8")
with open("cv-7.0-validated.json", encoding="utf-8") as f:
  duration_data_list = [json.loads(line) for line in f.readlines()]

speaker_dict = {}
tuniq_sentence = []
duniq_sentence = []
duniq_duration = 0
tuniq_duration= 0
test_duration = 0
dev_duration = 0
train_duration = 0
count_duniq_spk = 0
count_tuniq_spk = 0
count_dev_spk = 0
count_test_spk = 0
count_train_spk = 0
all_spk = 0

# write file, remove speaker, count duration
def add_spk2set(spk, duration, count_spk, file) :
    count_spk+=1
    tmp_st = speaker_dict[spk]["sentence"]
    tmp_line = speaker_dict[spk]["line"]
    for i in range(len(tmp_st)):
        file.write(tmp_line[i])
        if  file == test_uniq and tmp_st[i] not in tuniq_sentence:
            tuniq_sentence.append(tmp_st[i])
        elif file == dev_uniq and tmp_st[i] not in duniq_sentence :
            duniq_sentence.append(tmp_st[i])
        for d in duration_data_list:
            if d['audio_filepath'] == speaker_dict[spk]["audio_filepath"][i]:
                duration += d["duration"]
                break
    if file != train:
        speaker_dict.pop(spk)
    return duration, count_spk

# remove duplicate sentence of unique set
def remove_duplicate_uniq(data):
    tmp_spk_list = [spk for spk in speaker_dict.keys()]
    for spk in tmp_spk_list:
        tmp_st = speaker_dict[spk]["sentence"]
        new_st = []
        new_line = []
        for i in range(len(tmp_st)):
            if tmp_st[i] not in data:
                new_st.append(tmp_st[i])
                new_line.append(speaker_dict[spk]["line"][i])
        if len(new_st) == 0 :
            speaker_dict.pop(spk)
        else :
            speaker_dict[spk]["sentence"] = new_st
            speaker_dict[spk]["line"] = new_line

# Find next speaker (prioritize speaker that has high intersect with unique set)
def sort_spk(speaker_dict, uniq_sentence_list, count):
    for spk in speaker_dict:
        for st in speaker_dict[spk]["sentence"]:
            if st in uniq_sentence_list:
                speaker_dict[spk][count] +=1
    sorted_list =  sorted(speaker_dict.items(), key = lambda x: (x[1][count], -len(x[1]["sentence"]) ))
    speaker_dict = dict(sorted_list)
    return sorted_list[len(speaker_dict)-1][0]

#########################################################################


# create speaker_dict
with open('validated.tsv', encoding='utf-8') as validated:
    header_line = next(validated)
    for line in validated:
        l = line.strip().split("\t")
        speaker_id = l[0]
        audio_filepath = l[1]
        sentence = l[2]
    
        if speaker_id in speaker_dict:
            speaker_dict[speaker_id]["sentence"].append(sentence)
            speaker_dict[speaker_id]["line"].append(line)
            speaker_dict[speaker_id]["audio_filepath"].append(audio_filepath)

        else :
            all_spk +=1
            speaker_dict[speaker_id] = {
                "sentence": [sentence],
                "test_count": 0,
                "dev_count": 0,
                "line": [line],
                "audio_filepath": [audio_filepath]
            }

print("finish create speaker dict")

#write header line to all files
test_uniq.write(header_line)
dev_uniq.write(header_line)
test.write(header_line)
dev.write(header_line)
train.write(header_line)

#test_uniq
rand_spk = random.choice(tuple(speaker_dict))     
tuniq_duration, count_tuniq_spk = add_spk2set(rand_spk, tuniq_duration, count_tuniq_spk, test_uniq)

while tuniq_duration < 7200:
    maxcount_spk =  sort_spk(speaker_dict, tuniq_sentence, "test_count")
    tuniq_duration, count_tuniq_spk = add_spk2set(maxcount_spk, tuniq_duration, count_tuniq_spk,test_uniq)

remove_duplicate_uniq(tuniq_sentence)

print("all speaker = ", all_spk,"\n")

print("finish test_uniq")
print(" test_uniq: duration = ", tuniq_duration, "number of speakers = ", count_tuniq_spk ,"number of unique sentences = ", len(tuniq_sentence),"\n")

#dev_uniq
rand_spk = random.choice(tuple(speaker_dict))     
duniq_duration, count_duniq_spk = add_spk2set(rand_spk, duniq_duration,count_duniq_spk, dev_uniq)

while duniq_duration < 7200:
    maxcount_spk = sort_spk(speaker_dict, duniq_sentence, "dev_count")
    duniq_duration, count_duniq_spk = add_spk2set(maxcount_spk, duniq_duration,count_duniq_spk, dev_uniq)

remove_duplicate_uniq(duniq_sentence)

print("finish dev_uniq")
print(" dev_uniq: duration = ", duniq_duration, "number of speakers = ", count_duniq_spk,"number of unique sentences = ", len(duniq_sentence),"\n")

#test
while test_duration < 10800:
    rand_spk = random.choice(tuple(speaker_dict)) 
    test_duration, count_test_spk = add_spk2set(rand_spk, test_duration, count_test_spk, test)

print("finish test")
print(" test: duration = ", test_duration, "number of speakers = ", count_test_spk,"\n")

#dev
while dev_duration < 10800:
    rand_spk = random.choice(tuple(speaker_dict)) 
    dev_duration, count_dev_spk = add_spk2set(rand_spk, dev_duration, count_dev_spk, dev)

print("finish dev")
print(" dev: duration = ", dev_duration, "number of speakers = ", count_dev_spk,"\n")

#train
for spk in speaker_dict.keys():
    train_duration, count_train_spk = add_spk2set(spk, train_duration, count_train_spk, train)

print("finish train")
print(" train: duration = ", train_duration, "number of speakers = ", count_train_spk,"\n")

validated.close()
train.close()
test_uniq.close()
dev_uniq.close()
test.close()
dev.close()
f.close()