#!/usr/bin/env python3

import csv
import os
import pickle
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
        else:
            self.button.config(relief=tkinter.SUNKEN)

        self.selected = not self.selected
        self.delegate.update_selected_words()

    def enable_word_button(self):
        self.selected = True
        self.button.config(relief=tkinter.SUNKEN)

    def destroy(self):
        self.button.destroy()


class SoundController(object):
    def __init__(self, parent_view, delegate, sound, words_arrays, selected_words):
        self.sound = sound
        self.delegate = delegate
        self.candidate_words_arrays = words_arrays
        self.selected = False

        self.sound_button = tkinter.Button(parent_view, text=sound, command=self.toggle_sound_button)
        self.words_frame = tkinter.Frame(parent_view)

        self.word_controllers = []

        if selected_words is not None:
            self.selected_words = selected_words
            self.toggle_sound_button()
        else:
            self.selected_words = set()

    def enable_sound_button(self):
        self.selected = True
        self.sound_button.config(relief=tkinter.SUNKEN)

    def toggle_sound_button(self):
        if self.selected:
            self.sound_button.config(relief=tkinter.RAISED)
            self.deselect_sound(self.sound)
        else:
            self.sound_button.config(relief=tkinter.SUNKEN)
            self.select_sound(self.sound)

        self.selected = not self.selected

    def select_sound(self, sound):
        for i, a in enumerate(self.candidate_words_arrays):
            for j, word in enumerate(a):
                try:
                    wc = WordController(self.words_frame, self, word)
                    if word in self.selected_words:
                        wc.enable_word_button()
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
    def __init__(self, parent_view, delegate):
        data = None
        with open('pickwords.pkl', 'rb') as f:
            data = pickle.load(f)

        sounds = data['sounds']
        words_arrays_dict = data['words']

        file_path = 'selected_words.pkl'
        saved_state = {}
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                saved_state = pickle.load(f)
        print('LOAD:', saved_state)

        self.delegate = delegate
        self.sf = Pmw.ScrolledFrame(parent_view, labelpos=tkinter.N, label_text='音 & 字')
        self.sf.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

        self.selected_words = set()

        self.sound_controllers = []
        frame = self.sf.interior()

        for i, sound in enumerate(sounds):
            if sound in saved_state:
                selected_words = saved_state[sound]
            else:
                selected_words = None

            sc = SoundController(frame, self, sound, words_arrays_dict[sound], selected_words)
            self.sound_controllers.append(sc)

            sc.sound_button.grid(row=i, column=0, sticky=tkinter.NW+tkinter.SE)
            sc.words_frame.grid(row=i, column=1, sticky=tkinter.NW)

    def update_selected_words(self):
        self.selected_words = set()

        for sc in self.sound_controllers:
            if sc.selected:
                self.selected_words.update(sc.selected_words)
        print('WSC: SELECTED WORDS:', self.selected_words)

    def save_state(self):
        state = {}
        for sc in self.sound_controllers:
            if not sc.selected:
                continue
            state[sc.sound] = sc.selected_words

        filename = 'selected_words'
        print('SAVE:', state)
        with open(filename + '.pkl', 'wb') as f:
            pickle.dump(state, f)

        with open(filename + '.txt', 'w') as f:
            for word in self.selected_words:
                f.write(word)


class App(object):
    def __init__(self, root):
        self.root = root

        self.wsc = WordSelectController(root, self)
        self.wsc.sf.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        self.button = tkinter.Button(root, text='離開', fg="red", command=self.quit)
        self.button.pack(side=tkinter.RIGHT)

        self.button = tkinter.Button(root, text='儲存後離開', fg="red", command=self.save_and_quit)
        self.button.pack(side=tkinter.RIGHT)

        self.button = tkinter.Button(root, text='儲存', fg="red", command=self.save)
        self.button.pack(side=tkinter.RIGHT)

        self.wsc.update_selected_words()

    def save(self):
        self.wsc.save_state()

    def save_and_quit(self):
        self.wsc.save_state()
        self.root.quit()

    def quit(self):
        self.root.quit()


def main():
    root = tkinter.Tk()
    root.option_readfile('pickwords.tkinter.options')
    root.wm_title('選字')
    Pmw.initialise()
    app = App(root)
    root.mainloop()
    root.destroy()

if __name__ == "__main__":
    main()
