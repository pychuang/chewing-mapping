#!/usr/bin/env python3

import csv
import tkinter

class ScrollFrame(tkinter.Frame):
    '''
    Use the 'interior' attribute to place widgets inside the scrollable frame
    '''

    def __init__(self, parent, with_vsb, with_hsb, *args, **kw):
        tkinter.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and scrollbars for scrolling it
        canvas = tkinter.Canvas(self, bd=0, highlightthickness=0, background="#00ff00")
#        canvas.grid(row=0, column=0)

        if with_vsb:
            vscrollbar = tkinter.Scrollbar(self, orient=tkinter.VERTICAL, command=canvas.yview)
            vscrollbar.pack(fill=tkinter.Y, side=tkinter.RIGHT)
            #vscrollbar.grid(row=0, column=1, sticky=tkinter.N+tkinter.S)
            canvas.config(yscrollcommand=vscrollbar.set)

        if with_hsb:
            hscrollbar = tkinter.Scrollbar(self, orient=tkinter.HORIZONTAL, command=canvas.xview)
            hscrollbar.pack(fill=tkinter.X, side=tkinter.BOTTOM)
            #hscrollbar.grid(row=1, column=0, sticky=tkinter.E+tkinter.W)
            canvas.config(xscrollcommand=hscrollbar.set)

        canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tkinter.Frame(canvas, background="#0000ff")
        interior.config(width=10, height=10)
        interior.pack(fill=tkinter.BOTH, expand=True)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=tkinter.NW)

        # track changes to the canvas and frame width and sync them, also updating the scrollbar
        def configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
#            canvas.config(scrollregion=canvas.bbox(tkinter.ALL))
            #interior.config(width=interior.winfo_reqwidth(), height=interior.winfo_reqheight())

            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
            if interior.winfo_reqheight() != canvas.winfo_height():
                # update the canvas's height to fit the inner frame
                canvas.config(height=interior.winfo_reqheight())
            #canvas.configure(scrollregion=canvas.bbox(tkinter.ALL))
            #canvas.configure(scrollregion=interior.bbox(tkinter.ALL))
        interior.bind('<Configure>', configure_interior)

        def configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
            if interior.winfo_reqheight() != canvas.winfo_height():
                # update the inner frame's height to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_height())

#        canvas.bind('<Configure>', configure_canvas)

class SoundButton(tkinter.Button):
    def __init__(self, root, delegate, sound):
        tkinter.Button.__init__(self, root, text=sound, command=self.toggle)
        self.delegate = delegate
        self.sound = sound
        self.selected = False


    def toggle(self):
        #text = self.config('text')[-1]

        if self.selected:
            self.config(relief=tkinter.RAISED)
            print('deselect', self.sound)
            self.delegate.deselect_sound(self.sound)
        else:
            self.config(relief=tkinter.SUNKEN)
            print('select', self.sound)
            self.delegate.select_sound(self.sound)

        self.selected = not self.selected


class WordButton(tkinter.Button):
    def __init__(self, root, word):
        tkinter.Button.__init__(self, root, text=word, command=self.click)
#        self.config(state=tkinter.DISABLED)


    def click(self):
        text = self.config('text')[-1]
        print('clicked', text)


class SoundFrame(tkinter.Frame):
    def __init__(self, root, sys, sound):
        tkinter.Frame.__init__(self, root, background="#ff0000")

        self.sys = sys
        self.sound = sound
        self.candidate_words_arrays = sys.sound_to_words_arrays(sound)
#        print(sound+'====================')
#        print(self.candidate_words_array)
        self.buttons = []

        self.sound_button = SoundButton(self, self, sound)
#        self.sound_button.grid(row=0, column=0)
        self.sound_button.pack(side=tkinter.LEFT)

        self.words_frame = ScrollFrame(self, False, True, width=400)
        #self.words_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self.words_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=False)

#        for i in range(20):
#            tkinter.Label(words_frame.interior, text="%s" % i, width=3, borderwidth="1", relief="solid").pack(side=tkinter.LEFT)

    def select_sound(self, sound):
        for i, a in enumerate(self.candidate_words_arrays):
            for j, word in enumerate(a):
                try:
                    button = WordButton(self.words_frame.interior, word)
                    button.grid(row=i, column=j)
                    self.buttons.append(button)
                except Exception as e:
                    print(e)


    def deselect_sound(self, sound):
        for button in self.buttons:
            button.destroy()


class SoundAndWordsFrame(tkinter.LabelFrame):
    def __init__(self, root, sys):
        tkinter.LabelFrame.__init__(self, root, text='Sounds and Words', background='#ff00ff')

        self.sys = sys

        frame = ScrollFrame(self, True, False, width=600)
        #frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=False)
        #frame.grid(row=0, column=0)

        for i, sound in enumerate(self.sys.sounds):
            sf = SoundFrame(frame.interior, self.sys, sound)
            sf.pack(side=tkinter.TOP, fill=tkinter.X, expand=False)
            #sf.pack(side=tkinter.TOP)


class App(object):
    def __init__(self, root, sys):
        self.sys = sys
        self.initialize_window(root)


    def initialize_window(self, frame):
        #frame = tkinter.Frame(root)
        #frame.pack(fill=tkinter.BOTH)

        #sound_words_frame = tkinter.LabelFrame(frame, text='Sounds and Words')
        sound_words_frame = SoundAndWordsFrame(frame, self.sys)
        sound_words_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        #sound_words_frame.grid(row=0, column=0, sticky=tkinter.N+tkinter.S)

        names_frame = tkinter.LabelFrame(frame, text='Name', background='#0f000f')
        names_frame.pack(side=tkinter.LEFT)
        #names_frame.grid(row=0, column=1)

        self.button = tkinter.Button(
            frame, text="QUIT", fg="red", command=frame.quit
            )
        self.button.pack(side=tkinter.LEFT)
        #self.button.grid(column=1, row=1)


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
    app = App(root, sys)
    root.mainloop()
    root.destroy()

if __name__ == "__main__":
    main()
