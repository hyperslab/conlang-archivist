import random
import tkinter as tk
from tkinter.messagebox import showinfo
from conarch.language import Language
from conarch.gui_sound import SoundWindow
from conarch.gui_word import WordWindow
from conarch.gui_sound_change import SoundChangeWindow
from conarch.gui_word_form import WordFormWindow


class LanguageWindow:
    def __init__(self, master, language, label=None):
        self.master = master
        self.frame = tk.Frame(master)

        self.language = language
        if label is None:
            label = 'Language Information: ' + language.name
        else:
            label = 'Language Information: ' + str(label)

        language_info_frame = tk.LabelFrame(self.frame,
                                            text=label)
        self.popup_language_sounds = list()
        language_sound_list_label = tk.Label(language_info_frame, text='Sound Inventory')
        language_sound_list_scrollbar = tk.Scrollbar(language_info_frame, orient='vertical')
        language_sound_list = tk.Listbox(language_info_frame, width=18,
                                         yscrollcommand=language_sound_list_scrollbar.set)
        language_sound_list_scrollbar.configure(command=language_sound_list.yview)
        language_sound_list.bind('<Double-1>', self.open_sound_window)
        self.popup_language_words = list()
        language_word_list_label = tk.Label(language_info_frame, text='Stem Dictionary')
        language_word_list_scrollbar = tk.Scrollbar(language_info_frame, orient='vertical')
        language_word_list = tk.Listbox(language_info_frame, width=20,
                                        yscrollcommand=language_word_list_scrollbar.set)
        language_word_list_scrollbar.configure(command=language_word_list.yview)
        language_word_list.bind('<Double-1>', self.open_word_window)
        self.popup_language_history = list()
        language_history_list_label = tk.Label(language_info_frame, text='Language History')
        language_history_list_scrollbar = tk.Scrollbar(language_info_frame, orient='vertical')
        language_history_list = tk.Listbox(language_info_frame, width=44,
                                           yscrollcommand=language_history_list_scrollbar.set)
        language_history_list_scrollbar.configure(command=language_history_list.yview)
        language_history_list.bind('<Double-1>', self.open_history_item)

        i = 0
        for sound in language.modern_phonetic_inventory:
            sound_name = sound.orthographic_transcription
            if sound.ipa_transcription is not None:
                sound_name = sound_name + ' /' + sound.ipa_transcription + '/'
            language_sound_list.insert(i, sound_name)
            self.popup_language_sounds.append(sound)
            i = i + 1

        i = 0
        for word in language.words:
            word_stem = word.get_modern_stem_string(include_ipa=True)
            language_word_list.insert(i, word_stem)
            self.popup_language_words.append(word)
            i = i + 1

        i = 0  # language stage
        j = 0  # position in list
        for sound_change in language.sound_changes:
            for word_form in language.get_forms_added_at_stage(i):  # get all forms in a stage (move to own window?)
                form = word_form.categories + ' form: ' + word_form.name
                language_history_list.insert(j, form)
                self.popup_language_history.append(word_form)
                j = j + 1
            history = 'Sound Change: ' + str(sound_change)  # then advance the stage with a sound change
            language_history_list.insert(j, history)
            self.popup_language_history.append(sound_change)
            j = j + 1
            i = i + 1
        for word_form in language.get_forms_added_at_stage(i):  # get all forms in the current stage
            form = word_form.categories + ' form: ' + word_form.name
            language_history_list.insert(j, form)
            self.popup_language_history.append(word_form)
            j = j + 1

        language_sound_list_label.grid(row=1, column=1, columnspan=2)
        language_sound_list.grid(row=2, column=1)
        language_sound_list_scrollbar.grid(row=2, column=2, sticky='ns')
        language_word_list_label.grid(row=1, column=3)
        language_word_list.grid(row=2, column=3)
        language_word_list_scrollbar.grid(row=2, column=4, sticky='ns')
        language_history_list_label.grid(row=1, column=5)
        language_history_list.grid(row=2, column=5)
        language_history_list_scrollbar.grid(row=2, column=6, sticky='ns')
        language_info_frame.grid(column=2, row=1, padx=8, pady=6, rowspan=3)

        self.frame.grid()

    def open_sound_window(self, event):
        sound_window = tk.Toplevel(self.master)
        SoundWindow(sound_window, self.popup_language_sounds[event.widget.curselection()[0]])

    def open_word_window(self, event):
        word_window = tk.Toplevel(self.master)
        WordWindow(word_window, self.language, self.popup_language_words[event.widget.curselection()[0]])

    def open_history_item(self, event):
        item = self.popup_language_history[event.widget.curselection()[0]]
        order = event.widget.curselection()[0]
        if 'SoundChangeRule' in str(type(item)):  # 'type(x) is y' does not work anymore for some reason
            sound_change_window = tk.Toplevel(self.master)
            SoundChangeWindow(sound_change_window, self.language, item, order)
        elif 'WordFormRule' in str(type(item)):
            word_form_window = tk.Toplevel(self.master)
            WordFormWindow(word_form_window, self.language, item)


class NewLanguageWindow:
    def __init__(self, master, new_language_command, edit_language=None):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.new_language_command = new_language_command
        self.edit_language = edit_language
        self.new_language_name = tk.StringVar()
        self.new_language_phonotactics = tk.StringVar()

        if edit_language is not None:
            self.new_language_name.set(edit_language.name)
            self.new_language_phonotactics.set(edit_language.phonotactics)

        self.new_language_name_label = tk.Label(self.frame, text='Enter Language Name')
        self.new_language_name_entry = tk.Entry(self.frame, textvariable=self.new_language_name)
        self.new_language_phonotactics_label = tk.Label(self.frame, text='Enter Language Phonotactics')
        self.new_language_phonotactics_entry = tk.Entry(self.frame,
                                                        textvariable=self.new_language_phonotactics)
        self.new_language_confirm_button = tk.Button(self.frame,
                                                     text='Create Language' if edit_language is None else
                                                     'Save Language',
                                                     command=self.create_language if edit_language is None else
                                                     self.update_language)

        self.new_language_name_label.grid(column=1, row=1)
        self.new_language_name_entry.grid(column=1, row=2)
        self.new_language_phonotactics_label.grid(column=1, row=3)
        self.new_language_phonotactics_entry.grid(column=1, row=4)
        self.new_language_confirm_button.grid(column=1, row=5)

        self.frame.grid()

    def create_language(self):
        # input validation
        if not self.new_language_name.get():
            showinfo('Invalid Input', 'Language must have a name!')
            return

        # create the language, call the callback, and close the window
        new_language = Language(name=self.new_language_name.get(), phonetic_inventory=list(),
                                phonotactics=self.new_language_phonotactics.get())
        self.new_language_command(new_language)
        self.master.destroy()

    def update_language(self):
        # input validation
        if not self.new_language_name.get():
            showinfo('Invalid Input', 'Language must have a name!')
            return

        # update the language, call the callback, and close the window
        new_language = self.edit_language
        new_language.name = self.new_language_name.get()
        new_language.phonotactics = self.new_language_phonotactics.get()
        self.new_language_command(new_language)
        self.master.destroy()


class CloneLanguageWindow:
    def __init__(self, master, source_language, new_language_command, iteration=2):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.source_language = source_language
        self.new_language_command = new_language_command
        self.new_language_name = tk.StringVar()
        self.new_language_name.set(self.source_language.name + ' ' + str(iteration))
        self.new_language_phonotactics = tk.StringVar()
        self.new_language_phonotactics.set(self.source_language.phonotactics)
        self.new_language_source_stage = tk.StringVar()
        self.new_language_source_stage.set(str(self.source_language.get_current_stage()))

        source_language_name_label = tk.Label(self.frame, text='Cloning Language from ' +
                                                               self.source_language.name)
        new_language_name_label = tk.Label(self.frame, text='Enter New Language Name')
        new_language_name_entry = tk.Entry(self.frame, textvariable=self.new_language_name)
        new_language_phonotactics_label = tk.Label(self.frame, text='Enter Language Phonotactics')
        new_language_phonotactics_entry = tk.Entry(self.frame,
                                                   textvariable=self.new_language_phonotactics)
        new_language_confirm_button = tk.Button(self.frame, text='Create Language',
                                                command=self.clone_language)
        new_language_source_stage_label = tk.Label(self.frame,
                                                   text='Enter Source Language Stage (0 - ' +
                                                        str(self.source_language.get_current_stage()) + ')')
        new_language_source_stage_entry = tk.Entry(self.frame,
                                                   textvariable=self.new_language_source_stage)

        source_language_name_label.grid(column=1, row=0)
        new_language_name_label.grid(column=1, row=1)
        new_language_name_entry.grid(column=1, row=2)
        new_language_phonotactics_label.grid(column=1, row=3)
        new_language_phonotactics_entry.grid(column=1, row=4)
        new_language_source_stage_label.grid(column=1, row=5)
        new_language_source_stage_entry.grid(column=1, row=6)
        new_language_confirm_button.grid(column=1, row=7)

        self.frame.grid()

    def clone_language(self):
        # input validation
        if not self.new_language_name.get():
            showinfo('Invalid Input', 'Language must have a name!')
            return
        try:
            source_stage = int(self.new_language_source_stage.get())
        except ValueError:
            showinfo('Invalid Input', 'Source stage must be an integer!')
            return

        # clone the language, call the callback, and close the window
        new_language = self.source_language.copy_language_at_stage(source_stage)
        new_language.name = self.new_language_name.get()
        new_language.phonotactics = self.new_language_phonotactics.get()
        self.new_language_command(new_language)
        self.master.destroy()


class BranchLanguageWindow:
    def __init__(self, master, source_language, new_language_command):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.source_language = source_language
        self.new_language_command = new_language_command
        self.new_language_name = tk.StringVar()
        name = self.source_language.name
        branch_names = ['New ' + name, 'Modern ' + name, name + ' Offshoot', name + ' Branch', 'Regional ' + name,
                        name + ' Dialect', 'Neo-' + name, name + ' Derivation', 'Colonial ' + name, 'High ' + name,
                        'Low ' + name, 'Northern ' + name, 'Southern ' + name, 'Eastern ' + name, 'Western ' + name]
        self.new_language_name.set(random.choice(branch_names))
        self.new_language_phonotactics = tk.StringVar()
        self.new_language_phonotactics.set(self.source_language.phonotactics)
        self.new_language_source_stage = tk.StringVar()
        self.new_language_source_stage.set(str(self.source_language.get_current_stage()))

        source_language_name_label = tk.Label(self.frame, text='Branching Language from ' +
                                                               self.source_language.name)
        new_language_name_label = tk.Label(self.frame, text='Enter New Language Name')
        new_language_name_entry = tk.Entry(self.frame, textvariable=self.new_language_name)
        new_language_phonotactics_label = tk.Label(self.frame, text='Enter Language Phonotactics')
        new_language_phonotactics_entry = tk.Entry(self.frame,
                                                   textvariable=self.new_language_phonotactics)
        new_language_confirm_button = tk.Button(self.frame, text='Create Language',
                                                command=self.branch_language)
        new_language_source_stage_label = tk.Label(self.frame,
                                                   text='Enter Source Language Stage (0 - ' +
                                                        str(self.source_language.get_current_stage()) + ')')
        new_language_source_stage_entry = tk.Entry(self.frame,
                                                   textvariable=self.new_language_source_stage)

        source_language_name_label.grid(column=1, row=0)
        new_language_name_label.grid(column=1, row=1)
        new_language_name_entry.grid(column=1, row=2)
        new_language_phonotactics_label.grid(column=1, row=3)
        new_language_phonotactics_entry.grid(column=1, row=4)
        new_language_source_stage_label.grid(column=1, row=5)
        new_language_source_stage_entry.grid(column=1, row=6)
        new_language_confirm_button.grid(column=1, row=7)

        self.frame.grid()

    def branch_language(self):
        # input validation
        if not self.new_language_name.get():
            showinfo('Invalid Input', 'Language must have a name!')
            return
        try:
            source_stage = int(self.new_language_source_stage.get())
        except ValueError:
            showinfo('Invalid Input', 'Source stage must be an integer!')
            return

        # branch the language, call the callback, and close the window
        new_language = self.source_language.branch_language_at_stage(source_stage)
        new_language.name = self.new_language_name.get()
        new_language.phonotactics = self.new_language_phonotactics.get()
        self.new_language_command(new_language)
        self.master.destroy()
