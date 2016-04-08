#!/usr/bin/env python3

import csv
import Pmw
import tkinter

class WordController(object):
    def __init__(self, parent_view, delegate, word):
        self.word = word
        self.button = tkinter.Button(parent_view, text=word, command=self.toggle_word_button)
        self.delegate = delegate
        self.selected = False

    def toggle_word_button(self):
        if self.selected:
            self.button.config(relief=tkinter.RAISED)
            print('deselect', self.word)
        else:
            self.button.config(relief=tkinter.SUNKEN)
            print('select', self.word)

        self.selected = not self.selected
        self.delegate.update_selected_words()


    def destroy(self):
        self.button.destroy()


class SoundController(object):
    def __init__(self, sys, parent_view, delegate, sound):
        self.sound = sound
        self.sys = sys
        self.delegate = delegate
        self.candidate_words_arrays = self.sys.sound_to_words_arrays(sound)
        self.selected = False

        self.sound_button = tkinter.Button(parent_view, text=sound, command=self.toggle_sound_button)
        self.words_frame = tkinter.Frame(parent_view)

        self.word_controllers= []
        self.selected_words = set()

    def toggle_sound_button(self):
        if self.selected:
            self.sound_button.config(relief=tkinter.RAISED)
            print('deselect', self.sound)
            self.deselect_sound(self.sound)
        else:
            self.sound_button.config(relief=tkinter.SUNKEN)
            print('select', self.sound)
            self.select_sound(self.sound)

        self.selected = not self.selected

    def select_sound(self, sound):
        for i, a in enumerate(self.candidate_words_arrays):
            for j, word in enumerate(a):
                try:
                    wc = WordController(self.words_frame, self, word)
                    wc.button.grid(row=i, column=j)
                    self.word_controllers.append(wc)
                except Exception as e:
                    print(e)


    def deselect_sound(self, sound):
        for wc in self.word_controllers:
            wc.destroy()
        self.word_controllers = []
        self.update_selected_words()


    def update_selected_words(self):
        self.selected_words = set()

        for wc in self.word_controllers:
            if wc.selected:
                 self.selected_words.add(wc.word)
        self.delegate.update_selected_words()


class WordSelectController(object):
    def __init__(self, sys, parent_view, delegate):
        self.sys = sys
        self.delegate = delegate
        sf = Pmw.ScrolledFrame(parent_view, labelpos=tkinter.N, label_text='音 & 字')
        sf.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self.sf = sf
        self.selected_words = set()

        self.sound_controllers= []
        self.create_sound_buttons_and_words_frames(sf.interior())

    def create_sound_buttons_and_words_frames(self, frame):
        for i, sound in enumerate(self.sys.sounds):
            sc = SoundController(self.sys, frame, self, sound)
            self.sound_controllers.append(sc)

            sc.sound_button.grid(row=i, column=0, sticky=tkinter.NW+tkinter.SE)
            sc.words_frame.grid(row=i, column=1, sticky=tkinter.NW)

    def update_selected_words(self):
        self.selected_words = set()

        for sc in self.sound_controllers:
            if sc.selected:
                self.selected_words.update(sc.selected_words)
        print('WSC: SELECTED WORDS:', self.selected_words)
        self.delegate.selected_words_updated(self.selected_words)


class NameSelectController(object):
    def __init__(self, sys, parent_view):
        self.sys = sys
        self.candidate_words = set()
        self.word_scores = {}
        self.candidate_names = []   # (w1, w2, score)
        self.refused_names = set()  # (w1, w2)
        self.selected_names = set() # (w1, w2)
        self.candidate_name = None  # (w,1 w2)

        self.frame = tkinter.Frame(parent_view)

        # selected names
        self.selected_slb = Pmw.ScrolledListBox(self.frame, labelpos=tkinter.N, label_text='還不錯')
        self.selected_slb.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        # refused names
        self.refused_slb = Pmw.ScrolledListBox(self.frame, labelpos=tkinter.N, label_text='不要的')
        self.refused_slb.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        # candidate
        self.candidate_label = tkinter.Label(self.frame)
        self.candidate_label.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

        choice_bb = Pmw.ButtonBox(self.frame)
        choice_bb.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self.select_button = choice_bb.add('✔', state=tkinter.DISABLED, command=self.select_current_candidate_name)
        self.refuse_button = choice_bb.add( '✖', state=tkinter.DISABLED, command=self.refuse_current_candidate_name)

    def update_candidate_words(self, selected_words):
        for word in selected_words:
            if word not in self.word_scores:
                self.word_scores[word] = 0

        self.candidate_words = selected_words
        self.update_candidate_names()

    def update_candidate_names(self):
        names = []
        for w1 in self.candidate_words:
            for w2 in self.candidate_words:
                if (w1, w2) in self.refused_names or (w1, w2) in self.selected_names:
                    continue
                score = self.word_scores[w1] + self.word_scores[w2]
                names.append((w1, w2, score))
        self.candidate_names = sorted(names, key=lambda tup: tup[2])
        print('CN:', self.candidate_names)
        self.update_name_for_selection()

    def update_name_for_selection(self):
        if self.candidate_names:
            (w1, w2, score) = self.candidate_names.pop()
            self.candidate_name = (w1, w2)
            name = w1 + w2
            self.candidate_label.config(text=name)
            self.select_button.config(state=tkinter.NORMAL)
            self.refuse_button.config(state=tkinter.ACTIVE)
        else:
            self.candidate_name = None
            self.candidate_label.config(text='')
            self.select_button.config(state=tkinter.DISABLED)
            self.refuse_button.config(state=tkinter.DISABLED)

    def select_current_candidate_name(self):
        (w1, w2) = self.candidate_name
        self.word_scores[w1] += 1
        self.word_scores[w2] += 1

        self.selected_names.add(self.candidate_name)
        names = [w1 + w2 for (w1, w2) in self.selected_names]
        self.selected_slb.setlist(names)
        self.update_name_for_selection()

    def refuse_current_candidate_name(self):
        (w1, w2) = self.candidate_name
        self.word_scores[w1] -= 1
        self.word_scores[w2] -= 1

        self.refused_names.add(self.candidate_name)
        names = [w1 + w2 for (w1, w2) in self.refused_names]
        self.refused_slb.setlist(names)
        self.update_name_for_selection()


class App(object):
    def __init__(self, root, sys):
        self.sys = sys

        wsc = WordSelectController(sys, root, self)
        wsc.sf.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

        self.nsc = NameSelectController(sys, root)
        self.nsc.frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

        self.button = tkinter.Button(root, text="QUIT", fg="red", command=root.quit)
        self.button.pack(side=tkinter.LEFT)

    def selected_words_updated(self, selected_words):
        self.nsc.update_candidate_words(selected_words)

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


class RomanizedSystem(object):
    def __init__(self):
        self.bopomofo_to_romanic_dict = {}


    def add_mapping(self, bopomofo, romanic):
        self.bopomofo_to_romanic_dict[bopomofo] = romanic


    def bopomofo_to_romanic(bopomofo):
        return self.bopomofo_to_romanic_dict[bopomofo]


class NamingSystem(object):
    def __init__(self, phone_mapping, sounds, romanized_system):
        self.phone_mapping = phone_mapping
        self.sounds = sounds
        self.romanized_system = romanized_system

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
    wade_giles = RomanizedSystem()
    phonetic2 = RomanizedSystem()
    tongyong = RomanizedSystem()
    pinyin = RomanizedSystem()

    with open(filename) as f:
        csvreader = csv.reader(f)
        csvreader.__next__()
        for row in csvreader:
            sounds.append(row[0])
            wade_giles.add_mapping(row[0], row[1])
            phonetic2.add_mapping(row[0], row[2])
            tongyong.add_mapping(row[0], row[3])
            pinyin.add_mapping(row[0], row[4])

    return sounds, wade_giles, phonetic2, tongyong, pinyin


def main():
    sounds, wade_giles, phonetic2, tongyong, pinyin = read_phonetic_systems_csv('phonetics.csv')
    pm = PhoneMapping('phone.cin')
    sys = NamingSystem(pm, sounds, wade_giles)

    root = tkinter.Tk()
    #root.option_readfile('optionDB')
    Pmw.initialise()
    app = App(root, sys)
    root.mainloop()
    root.destroy()

if __name__ == "__main__":
    main()
