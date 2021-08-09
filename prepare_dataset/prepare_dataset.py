import random
import json

# path to dataset that you want to split into test_uniq, dev_uniq, test,
# dev, train
path_to_dataset = 'validated.tsv'
dataset = open(path_to_dataset, 'r', encoding='utf-8')

# duration file
with open("cv-7.0-validated.json", encoding="utf-8") as f:
    duration_data_list = [json.loads(line) for line in f.readlines()]

train = open('train.tsv', 'w', encoding="utf-8")
test_uniq = open('test_uniq.tsv', 'w', encoding="utf-8")
dev_uniq = open('dev_uniq.tsv', 'w', encoding="utf-8")
test = open('test.tsv', 'w', encoding="utf-8")
dev = open('dev.tsv', 'w', encoding="utf-8")


speaker_dict = {}
tuniq_sentence = []
duniq_sentence = []
duniq_duration = 0
tuniq_duration = 0
test_duration = 0
dev_duration = 0
train_duration = 0
count_duniq_spk = 0
count_tuniq_spk = 0
count_dev_spk = 0
count_test_spk = 0
count_train_spk = 0


def create_spk_dict():
    header_line = next(dataset)
    for line in dataset:
        l = line.strip().split("\t")
        speaker_id = l[0]
        audio_filepath = l[1]
        sentence = l[2]

        if speaker_id in speaker_dict:
            speaker_dict[speaker_id]["sentence"].append(sentence)
            speaker_dict[speaker_id]["line"].append(line)
            speaker_dict[speaker_id]["audio_filepath"].append(
                audio_filepath)

        else:
            speaker_dict[speaker_id] = {
                "sentence": [sentence],
                "test_count": 0,
                "dev_count": 0,
                "line": [line],
                "audio_filepath": [audio_filepath]
            }

    print("finish create speaker dict")

    return header_line


# write header line to all files
def write_header(header_line):
    test_uniq.write(header_line)
    dev_uniq.write(header_line)
    test.write(header_line)
    dev.write(header_line)
    train.write(header_line)

# write file, remove speaker, count duration
def add_spk2set(spk, duration, count_spk, file):
    count_spk += 1
    tmp_st = speaker_dict[spk]["sentence"]
    tmp_line = speaker_dict[spk]["line"]
    for i in range(len(tmp_st)):
        file.write(tmp_line[i])
        if file == test_uniq and tmp_st[i] not in tuniq_sentence:
            tuniq_sentence.append(tmp_st[i])
        elif file == dev_uniq and tmp_st[i] not in duniq_sentence:
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
        if len(new_st) == 0:
            speaker_dict.pop(spk)
        else:
            speaker_dict[spk]["sentence"] = new_st
            speaker_dict[spk]["line"] = new_line

# Find next speaker (prioritize speaker that has high intersect with
# unique set)
def sort_spk(speaker_dict, uniq_sentence_list, count):
    for spk in speaker_dict:
        for st in speaker_dict[spk]["sentence"]:
            if st in uniq_sentence_list:
                speaker_dict[spk][count] += 1
    sorted_list = sorted(speaker_dict.items(), key=lambda x: (
        x[1][count], -len(x[1]["sentence"])))
    speaker_dict = dict(sorted_list)
    max_count_spk = sorted_list[len(speaker_dict) - 1][0]
    len_max_spk = len(speaker_dict[max_count_spk]["sentence"])
    for i in range(2, len(sorted_list) + 1):
        if len_max_spk < 100 or len_max_spk > 1000:
            max_count_spk = sorted_list[len(speaker_dict) - i][0]
            len_max_spk = len(speaker_dict[max_count_spk]["sentence"])
        else:
            return max_count_spk
    return max_count_spk


def create_uniq_set(
        duration,
        min_duration,
        count_spk,
        uniq_sentence,
        file,
        filename):
    rand_spk = random.choice(tuple(speaker_dict))
    len_rand_spk = len(speaker_dict[rand_spk]["sentence"])
    while len_rand_spk < 100 or len_rand_spk > 1000:
        rand_spk = random.choice(tuple(speaker_dict))
        len_rand_spk = len(speaker_dict[rand_spk]["sentence"])
    duration, count_spk = add_spk2set(rand_spk, duration, count_spk, file)

    while duration < min_duration:
        maxcount_spk = sort_spk(speaker_dict, uniq_sentence, "test_count")
        duration, count_spk = add_spk2set(
            maxcount_spk, duration, count_spk, file)

    remove_duplicate_uniq(uniq_sentence)

    print("finish create", filename)
    print(
        filename,
        ": duration = ",
        duration,
        "number of speakers = ",
        count_spk,
        "number of unique sentences = ",
        len(uniq_sentence),
        "\n")


def create_set(duration, min_duration, count_spk, file, filename):
    tmp_spk_list = [spk for spk in speaker_dict.keys()]
    for spk in tmp_spk_list:
        if duration < min_duration:
            duration, count_spk = add_spk2set(spk, duration, count_spk, file)

    print("finish create", filename)
    print(
        filename,
        ": duration = ",
        duration,
        "number of speakers = ",
        count_spk,
        "\n")


def create_train(duration, count_spk, file):
    for spk in speaker_dict.keys():
        duration, count_spk = add_spk2set(spk, duration, count_spk, file)

    print("finish create train")
    print(

        "train: duration = ",
        duration,
        "number of speakers = ",
        count_spk,
        "\n")


def main():
    header_line = create_spk_dict()
    write_header(header_line)
    create_uniq_set(
        tuniq_duration,
        7200,
        count_tuniq_spk,
        tuniq_sentence,
        test_uniq, "test_uniq")
    create_uniq_set(
        duniq_duration,
        7200,
        count_duniq_spk,
        duniq_sentence,
        dev_uniq, "dev_uniq")
    create_set(
        test_duration,
        10800,
        count_test_spk,
        test, "test"
    )
    create_set(
        dev_duration,
        10800,
        count_dev_spk,
        dev, "dev"
    )
    create_train(train_duration, count_train_spk, train)


if __name__ == "__main__":
    main()


dataset.close()
train.close()
test_uniq.close()
dev_uniq.close()
test.close()
dev.close()
f.close()
