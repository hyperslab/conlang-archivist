import textwrap
import tkinter as tk
from tkinter.messagebox import showinfo
from conarch import sound_helpers, gui_sound
from conarch.word import Word


class WordWindow:
    def __init__(self, master, language, word, edit_word_command=None):
        self.master = master
        self.frame = tk.Frame(master)

        self.language = language
        self.word = word
        self.edit_word_command = edit_word_command

        self.word_modern_stem_label = tk.Label(self.frame)
        self.word_original_stem_label = tk.Label(self.frame)
        self.word_categories_label = tk.Label(self.frame)
        self.word_history_stage_label = tk.Label(self.frame)
        self.word_definition_label = tk.Label(self.frame)
        self.set_labels(language, word)
        self.word_forms_list_label = tk.Label(self.frame, text='Word Forms:')
        self.word_forms_list_scrollbar = tk.Scrollbar(self.frame, orient='vertical')
        self.word_forms_list = tk.Listbox(self.frame, width=60, yscrollcommand=self.word_forms_list_scrollbar.set)
        self.word_forms_list_scrollbar.configure(command=self.word_forms_list.yview)
        self.word_forms_list.bind('<Double-1>', self.open_word_form_window)
        self.populate_forms_list(word)
        self.word_edit_button = tk.Button(self.frame, text='Edit Word', command=self.open_edit_word_window)
        self.word_define_button = tk.Button(self.frame, text='Edit Definitions',
                                            command=self.open_new_definition_window)

        self.master.grid_columnconfigure(1, weight=1)
        self.word_modern_stem_label.grid(row=1, column=1)
        self.word_original_stem_label.grid(row=2, column=1)
        self.word_categories_label.grid(row=3, column=1)
        self.word_history_stage_label.grid(row=4, column=1)
        self.word_definition_label.grid(row=5, column=1)
        self.word_forms_list_label.grid(row=6, column=1)
        self.word_forms_list.grid(row=7, column=1, sticky='ew')
        self.word_forms_list_scrollbar.grid(row=7, column=2, sticky='ns')
        if edit_word_command:
            self.word_define_button.grid(row=8, column=1)
            self.word_edit_button.grid(row=9, column=1)

        self.frame.grid()

    def set_labels(self, language, word):
        self.word_modern_stem_label.configure(text='Word Stem: ' + word.get_modern_stem_string())
        self.word_original_stem_label.configure(text='Original Word Stem: ' + word.get_base_stem_string())
        self.word_categories_label.configure(text='Word Part(s) of Speech: ' + word.categories)
        self.word_history_stage_label.configure(text='Added at Language Stage: ' + str(word.original_language_stage))
        self.word_definition_label.configure(text='Most Recent Definition:\n' + textwrap.fill(
            word.get_definition_at_stage(language.get_current_stage()), 60))

    def populate_forms_list(self, word):
        self.word_forms_list.delete(0, tk.END)
        for i, form_string in enumerate(word.get_all_form_and_name_strings(include_base_stem=False, include_ipa=True,
                                                                           include_modern_stem=False)):
            self.word_forms_list.insert(i, form_string)

    def open_edit_word_window(self):
        edit_word_window = tk.Toplevel(self.master)
        NewWordWindow(edit_word_window, self.language, self.edit_word, edit_word=self.word)

    def edit_word(self, word):
        self.edit_word_command(word)
        self.set_labels(self.language, word)
        self.populate_forms_list(word)

    def open_new_definition_window(self):
        new_definition_window = tk.Toplevel(self.master)
        NewDefinitionWindow(new_definition_window, self.language, self.word, self.edit_definitions)

    def edit_definitions(self, definition, stage):  # a bit of a unique case as far as nested callbacks go
        self.word.add_definition(definition, stage)
        self.edit_word_command(self.word)
        self.set_labels(self.language, self.word)

    def open_word_form_window(self, event):
        word_form_window = tk.Toplevel(self.master)
        WordWindow(word_form_window, self.language, self.word.word_forms[event.widget.curselection()[0]],
                   edit_word_command=self.edit_word_form if self.edit_word_command is not None else None)

    def edit_word_form(self, word_form):
        self.edit_word_command(word_form)
        self.populate_forms_list(self.word)


class NewWordWindow:
    def __init__(self, master, language, new_word_command, edit_word=None):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.language = language
        self.new_word_command = new_word_command
        self.edit_word = edit_word
        self.new_word_categories = tk.StringVar()
        self.new_word_syllable_count = tk.StringVar()
        self.new_word_text = tk.StringVar()
        self.new_word_stage = tk.StringVar()
        self.new_word_stem = [[]]

        if edit_word is None:
            self.new_word_categories.set('N')
            self.new_word_syllable_count.set('1-2')
            self.new_word_text.set('Click to Generate ->')
            self.new_word_stage.set(language.get_current_stage())
        else:
            self.new_word_categories.set(edit_word.categories)
            self.new_word_syllable_count.set(str(len(edit_word.get_base_stem())))
            self.new_word_text.set(edit_word.get_base_stem_string(include_ipa=True))
            self.new_word_stage.set(edit_word.original_language_stage)
            self.new_word_stem = edit_word.base_stem  # TODO how does branching interact with this

        new_word_phonotactics_label = tk.Label(self.frame, text='Syllable Phonotactics: ' + language.phonotactics)
        new_word_categories_label = tk.Label(self.frame, text='Enter Part(s) of Speech')
        new_word_categories_entry = tk.Entry(self.frame, textvariable=self.new_word_categories)
        new_word_syllable_count_label = tk.Label(self.frame, text='Enter Amount of Syllables')
        new_word_syllable_count_entry = tk.Entry(self.frame, textvariable=self.new_word_syllable_count)
        new_word_stage_label = tk.Label(self.frame, text='Enter Language Stage')
        new_word_stage_entry = tk.Entry(self.frame, textvariable=self.new_word_stage)
        new_word_text = tk.Label(self.frame, textvariable=self.new_word_text)
        new_word_generate_button = tk.Button(self.frame,
                                             text='Generate Word' if edit_word is None else 'Regenerate Word',
                                             command=self.generate_word)
        new_word_add_sound_button = tk.Button(self.frame, text='Append Sound',
                                              command=self.open_append_sound_window)
        self.new_word_del_sound_button = tk.Button(self.frame, text='Remove Sound',
                                                   command=self.remove_sound)
        self.new_word_confirm_button = tk.Button(self.frame,
                                                 text='Create This Word' if edit_word is None else 'Save This Word',
                                                 command=self.create_word if edit_word is None else self.update_word)
        if edit_word is None:
            self.new_word_del_sound_button.configure(state='disabled')
            self.new_word_confirm_button.configure(state='disabled')

        if edit_word is not None:
            edit_word_window_header = tk.Label(self.frame,
                                               text="Edit the base (stage " + str(edit_word.original_language_stage) +
                                                    ") stem of this word.\nChanges will propagate to the modern stem "
                                                    "and all word forms.\n(If you want to represent historical "
                                                    "changes, use a Sound Change!)\n--------------------------------")
            edit_word_window_header.grid(row=0, column=1, columnspan=3)
        new_word_phonotactics_label.grid(column=1, row=1, columnspan=3)
        new_word_categories_label.grid(column=1, row=2)
        new_word_categories_entry.grid(column=1, row=3)
        new_word_syllable_count_label.grid(column=2, row=2)
        new_word_syllable_count_entry.grid(column=2, row=3)
        new_word_stage_label.grid(column=3, row=2)
        new_word_stage_entry.grid(column=3, row=3)
        new_word_text.grid(column=1, row=4, columnspan=2)
        new_word_generate_button.grid(column=2, row=4, columnspan=2)
        new_word_add_sound_button.grid(column=1, row=5, columnspan=2)
        self.new_word_del_sound_button.grid(column=2, row=5, columnspan=2)
        self.new_word_confirm_button.grid(column=2, row=6, columnspan=1)

        self.frame.grid()

    def append_sound(self, sound):
        self.new_word_stem[-1].append(sound)
        self.set_new_word_text_from_stem()
        self.new_word_del_sound_button.configure(state='normal')
        self.new_word_confirm_button.configure(state='normal')

    def remove_sound(self):
        self.new_word_stem[-1].pop()
        if len(self.new_word_stem[-1]) == 0 and len(self.new_word_stem) > 0:
            self.new_word_stem.pop()
        self.set_new_word_text_from_stem()
        if len(self.new_word_stem) == 1 and len(self.new_word_stem[0]) == 0:
            self.new_word_del_sound_button.configure(state='disabled')
            self.new_word_confirm_button.configure(state='disabled')

    def set_new_word_text_from_stem(self):
        if len(self.new_word_stem) == 1 and len(self.new_word_stem[0]) == 0:
            self.new_word_text.set('Click to Generate ->')
            return
        orthography = sound_helpers.get_sequence_as_string(self.new_word_stem, use_ipa=False)
        ipa = sound_helpers.get_sequence_as_string(self.new_word_stem, use_ipa=True)
        self.new_word_text.set(orthography + ' /' + ipa + '/')

    def open_append_sound_window(self):
        append_sound_window = tk.Toplevel(self.master)
        gui_sound.SoundSelectWindow(append_sound_window, self.language.get_full_sound_inventory(), self.append_sound)

    def generate_word(self):
        syllable_count = self.new_word_syllable_count.get()
        try:
            if '-' in syllable_count:
                min_syllables = int(syllable_count.split('-')[0])
                max_syllables = int(syllable_count.split('-')[1])
            else:
                min_syllables = int(syllable_count)
                max_syllables = int(syllable_count)
        except ValueError:
            print('Error parsing syllable count')
            return
        stage = -1
        try:
            stage = int(self.new_word_stage.get())
        except ValueError:
            print('Error parsing new_word_stage; using -1 for most recent')
        new_word = self.language.generate_word(min_syllable_length=min_syllables,
                                               max_syllable_length=max_syllables,
                                               category=self.new_word_categories.get(),
                                               language_stage=stage)
        self.new_word_stem = new_word.base_stem
        self.set_new_word_text_from_stem()
        self.new_word_del_sound_button.configure(state='normal')
        self.new_word_confirm_button.configure(state='normal')

    def create_word(self):
        # input validation
        try:
            stage = int(self.new_word_stage.get())
        except ValueError:
            showinfo('Invalid Input', 'Stage must be an integer!')
            return

        # create the word, call the callback, and close the window
        new_word = Word(self.new_word_stem, self.new_word_categories.get(), stage)
        self.new_word_command(new_word)
        self.master.destroy()

    def update_word(self):
        # input validation
        try:
            stage = int(self.new_word_stage.get())
        except ValueError:
            showinfo('Invalid Input', 'Stage must be an integer!')
            return

        # update the word, call the callback, and close the window
        new_word = self.edit_word
        new_word.base_stem = self.new_word_stem
        new_word.categories = self.new_word_categories.get()
        new_word.original_language_stage = stage
        self.new_word_command(new_word)
        self.master.destroy()


class NewDefinitionWindow:
    def __init__(self, master, language, word, new_definition_command):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.language = language
        self.word = word
        self.new_definition_command = new_definition_command
        self.new_definition_stage = tk.StringVar()
        self.new_definition_stage.set(language.get_current_stage())

        new_definition_stage_label = tk.Label(self.frame, text='Choose a Language Stage:')
        new_definition_stage_menu = tk.OptionMenu(self.frame,
                                                  self.new_definition_stage,
                                                  *['0'],
                                                  command=self.new_definition_stage_menu_type_changed)
        menu = new_definition_stage_menu['menu']
        menu.delete(0, tk.END)
        for i in range(word.original_language_stage, language.get_current_stage() + 1):
            if word.has_definition_at_stage(i, exact=True):
                label = '[' + str(i) + ']'
            else:
                label = str(i)
            menu.add_command(label=label, command=lambda value=i: self.new_definition_stage_menu_type_changed(value))
        new_definition_text_label = tk.Label(self.frame, text='Enter Definition:')
        self.new_definition_text = tk.Text(self.frame, width=40, height=12)
        self.new_definition_text.insert(tk.END, word.get_definition_at_stage(int(self.new_definition_stage.get())))
        self.new_definition_confirm_button = tk.Button(self.frame, text='Save Definition',
                                                       command=self.create_definition)

        new_definition_stage_label.grid(row=1, column=1)
        new_definition_stage_menu.grid(row=1, column=2)
        new_definition_text_label.grid(row=2, column=1, columnspan=2)
        self.new_definition_text.grid(row=3, column=1, columnspan=2)
        self.new_definition_confirm_button.grid(row=4, column=1, columnspan=2)

        self.frame.grid()

    def new_definition_stage_menu_type_changed(self, new_value):
        self.new_definition_stage.set(str(new_value))
        self.new_definition_text.delete(1.0, tk.END)
        self.new_definition_text.insert(tk.END, self.word.get_definition_at_stage(new_value, exact=True))

    def create_definition(self):
        # input validation
        definition = self.new_definition_text.get('1.0', 'end-1c')
        try:
            stage = int(self.new_definition_stage.get())
        except ValueError:
            showinfo('Invalid Input', 'Stage must be an integer!')
            return

        # call the callback and close the window
        self.new_definition_command(definition, stage)
        self.master.destroy()
