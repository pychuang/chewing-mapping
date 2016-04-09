#!/usr/bin/env python3

import csv
import os
import pickle


class PhoneMapping(object):
    def __init__(self, cin_filename):
        self.key_to_phone_dict = {}
        self.phone_to_key_dict = {}
        self.keys_to_words_dict = {}

        with open(cin_filename) as f:
            self.read_cin_file(f)

        #print(self.key_to_phone_dict)
        #print(self.phone_to_key_dict)
        #for k, v in self.keys_to_words_dict.items():
        #    print(k, v)

    def read_cin_file(self, f):
        STATE_INIT = 0
        STATE_KEYNAME = 1
        STATE_CHARDEF = 2
        state = STATE_INIT
        for line in f:
            if line[0] == '#':
                continue
            e = line.split()
            if e[0] == '%keyname':
                if e[1] == 'begin':
                    state = STATE_KEYNAME
            elif e[0] == '%chardef':
                if e[1] == 'begin':
                    state = STATE_CHARDEF
            elif state == STATE_KEYNAME:
                self.key_to_phone_dict[e[0]] = e[1]
                self.phone_to_key_dict[e[1]] = e[0]
            elif state == STATE_CHARDEF:
                if e[0] not in self.keys_to_words_dict:
                    self.keys_to_words_dict[e[0]] = []
                self.keys_to_words_dict[e[0]].append(e[1])


    def key_to_phone(self, key):
        return self.key_to_phone_dict[key]


    def phone_to_key(self, phone):
        return self.phone_to_key_dict[phone]


    def keys_to_words(self, keys):
        if keys not in self.keys_to_words_dict:
            return None
        return self.keys_to_words_dict[keys]


class NamingSystem(object):
    def __init__(self, phone_mapping, sounds):
        self.phone_mapping = phone_mapping
        self.sounds = sounds

    def sound_to_words_arrays(self, sound):
        keys = ''.join([self.phone_mapping.phone_to_key(phone) for phone in sound])
        arrays = []
        for tone in ['', '6', '3', '4', '7']:
            words = self.phone_mapping.keys_to_words(keys+tone)
            if not words:
                continue
            arrays.append(words)
        return arrays

def read_phonetic_systems_csv(filename):
    sounds = []

    with open(filename) as f:
        csvreader = csv.reader(f)
        csvreader.__next__()
        for row in csvreader:
            sounds.append(row[0])

    return sounds


def main():
    sounds = read_phonetic_systems_csv('phonetics.csv')
    pm = PhoneMapping('phone.cin')
    sys = NamingSystem(pm, sounds)

    sounds_to_words_arrays = {}
    for sound in sounds:
        sounds_to_words_arrays[sound] = sys.sound_to_words_arrays(sound)

    data = {}
    data['sounds'] = sounds
    data['words'] = sounds_to_words_arrays

    with open('pickwords.pkl', 'wb') as f:
        pickle.dump(data, f)
if __name__ == "__main__":
    main()
