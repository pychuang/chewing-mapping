#!/usr/bin/env python3

import csv
import os
import pickle
import Pmw
import tkinter

class NameSelectController(object):
    def __init__(self, parent_view):
        self.candidate_words = set()
        self.word1_scores = {}
        self.word2_scores = {}
        self.refused_names = set()  # (w1, w2)
        self.selected_names = set() # (w1, w2)

        self.candidate_names = []   # (w1, w2, score)
        self.candidate_name = None  # (w,1 w2)

        self.frame = tkinter.Frame(parent_view)

        # selected names
        self.selected_slb = Pmw.ScrolledListBox(self.frame, labelpos=tkinter.N, label_text='還不錯')
        self.selected_slb.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        # refused names
        #self.refused_slb = Pmw.ScrolledListBox(self.frame, labelpos=tkinter.N, label_text='不要的')
        #self.refused_slb.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        # candidate
        self.num_candidates_label = tkinter.Label(self.frame)
        self.num_candidates_label.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

        self.candidate_label = tkinter.Label(self.frame)
        self.candidate_label.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

        choice_bb = Pmw.ButtonBox(self.frame)
        choice_bb.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self.select_button = choice_bb.add('✔', state=tkinter.DISABLED, command=self.select_current_candidate_name)
        self.refuse_button = choice_bb.add( '✖', state=tkinter.DISABLED, command=self.refuse_current_candidate_name)

        # restore state
        self.load_state()

    def load_state(self):
        file_path = '.word_scores.pkl'
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                state = pickle.load(f)
                print('LOAD:', state)
                self.word1_scores = state['word1_scores']
                self.word2_scores = state['word2_scores']

        file_path = 'selected_words.txt'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                for line in f:
                    for word in line:
                        if word not in self.word1_scores:
                            self.word1_scores[word] = 0
                        if word not in self.word2_scores:
                            self.word2_scores[word] = 0
                        self.candidate_words.add(word)
            print('LOAD candidate_words:', self.candidate_words)

        file_path = 'selected_names.txt'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                for line in f:
                    w1 = line[0]
                    w2 = line[1]
                    self.selected_names.add((w1, w2))
                #print('LOAD selected_names:', self.selected_names)

        file_path = 'refused_names.txt'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                for line in f:
                    w1 = line[0]
                    w2 = line[1]
                    self.refused_names.add((w1, w2))
                #print('LOAD refused_names:', self.refused_names)

        self.update_selected_names_view()

        #names = [w1 + w2 for (w1, w2) in self.refused_names]
        #self.refused_slb.setlist(names)

    def save_state(self):
        with open('.word_scores.pkl', 'wb') as f:
            state = {}
            state['word1_scores'] = self.word1_scores
            state['word2_scores'] = self.word2_scores
            pickle.dump(state, f)

        with open('selected_names.txt', 'w') as f:
            names = sorted([w1 + w2 for (w1, w2) in self.selected_names])
            for name in names:
                f.write(name + '\n')

        with open('refused_names.txt', 'w') as f:
            names = sorted([w1 + w2 for (w1, w2) in self.refused_names])
            for name in names:
                f.write(name + '\n')

    def update_candidate_names(self):
        names = []
        for w1 in self.candidate_words:
            for w2 in self.candidate_words:
                if (w1, w2) in self.refused_names or (w1, w2) in self.selected_names:
                    continue
                score = self.word1_scores[w1] + self.word2_scores[w2]
                names.append((w1, w2, score))
        self.candidate_names = sorted(names, key=lambda tup: tup[2])
        #print(self.candidate_names)
        self.update_name_for_selection()
        self.num_candidates_label.config(text=len(self.candidate_names))

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
        self.word1_scores[w1] += 1
        self.word2_scores[w2] += 1

        self.selected_names.add(self.candidate_name)
        self.update_selected_names_view()
        #self.update_name_for_selection()
        self.update_candidate_names()

    def update_selected_names_view(self):
        names = sorted([w1 + w2 for (w1, w2) in self.selected_names])
        self.selected_slb.setlist(names)

    def refuse_current_candidate_name(self):
        (w1, w2) = self.candidate_name
        self.word1_scores[w1] -= 1
        self.word2_scores[w2] -= 1

        self.refused_names.add(self.candidate_name)
        #names = [w1 + w2 for (w1, w2) in self.refused_names]
        #self.refused_slb.setlist(names)
        #self.update_name_for_selection()
        self.update_candidate_names()


class App(object):
    def __init__(self, root):
        self.root = root

        self.nsc = NameSelectController(root)
        self.nsc.frame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        self.button = tkinter.Button(root, text='離開', fg="red", command=self.quit)
        self.button.pack(side=tkinter.RIGHT)

        self.button = tkinter.Button(root, text='儲存後離開', fg="red", command=self.save_and_quit)
        self.button.pack(side=tkinter.RIGHT)

        self.button = tkinter.Button(root, text='儲存', fg="red", command=self.save)
        self.button.pack(side=tkinter.RIGHT)

        self.nsc.update_candidate_names()

    def save(self):
        self.nsc.save_state()

    def save_and_quit(self):
        self.nsc.save_state()
        self.root.quit()

    def quit(self):
        self.root.quit()


def main():
    root = tkinter.Tk()
    root.option_readfile('picknames.tkinter.options')
    root.wm_title('取名字')
    Pmw.initialise()
    app = App(root)
    root.mainloop()
    root.destroy()

if __name__ == "__main__":
    main()
