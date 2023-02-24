import copy
import tkinter as tk
from conarch import gui_sound
from conarch.word_form_rule import WordFormRule
from conarch.sound_change_rule import SoundChangeRule
from tkinter.messagebox import showinfo


class WordFormWindow:
    def __init__(self, master, language, word_form, edit_word_form_command=None):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.language = language
        self.word_form = word_form
        self.edit_word_form_command = edit_word_form_command
        self.word_form_name = tk.StringVar()
        self.word_form_name.set(word_form.name)

        self.word_form_name_label = tk.Label(self.frame)
        self.word_form_categories_label = tk.Label(self.frame)
        self.word_form_original_stage_label = tk.Label(self.frame)
        self.word_form_obsoleted_stage_label = tk.Label(self.frame)
        self.set_labels(word_form)
        self.word_form_sound_changes_list_label = tk.Label(self.frame, text='Conjugation Rules:')
        self.word_form_sound_changes_list_scrollbar = tk.Scrollbar(self.frame, orient='vertical')
        self.word_form_sound_changes_list = tk.Listbox(self.frame, width=50,
                                                       yscrollcommand=self.word_form_sound_changes_list_scrollbar.set)
        self.word_form_sound_changes_list_scrollbar.configure(command=self.word_form_sound_changes_list.yview)
        self.populate_sound_changes_list(word_form)
        self.word_form_edit_button = tk.Button(self.frame, text='Edit Word Form',
                                               command=self.open_edit_word_form_window)

        self.word_form_name_label.grid(column=1, row=1)
        self.word_form_categories_label.grid(column=1, row=2)
        self.word_form_original_stage_label.grid(column=1, row=3)
        if word_form.obsoleted_language_stage > -1:
            self.word_form_obsoleted_stage_label.grid(column=1, row=4)
        self.word_form_sound_changes_list_label.grid(column=1, row=5)
        self.word_form_sound_changes_list.grid(column=1, row=6, sticky='ew')
        self.word_form_sound_changes_list_scrollbar.grid(column=2, row=6, sticky='ns')
        if edit_word_form_command:
            self.word_form_edit_button.grid(column=1, row=7)

        self.frame.grid()

    def set_labels(self, word_form):
        self.word_form_name_label.configure(text='Form Name:\n' + word_form.name)
        self.word_form_categories_label.configure(text='Applies to Words of Type(s):\n' + word_form.categories)
        self.word_form_original_stage_label.configure(text='Added to Language at Stage:\n' +
                                                           str(word_form.original_language_stage))
        self.word_form_obsoleted_stage_label.configure(text='Fell Out of Use at Stage:\n' +
                                                            str(word_form.obsoleted_language_stage))

    def populate_sound_changes_list(self, word_form):
        self.word_form_sound_changes_list.delete(0, tk.END)
        i = 0
        for rule in word_form.get_adjusted_rule_strings():
            self.word_form_sound_changes_list.insert(i, rule)
            i = i + 1

    def open_edit_word_form_window(self):
        edit_word_form_window = tk.Toplevel(self.master)
        NewWordFormWindow(edit_word_form_window, self.language, self.edit_word_form, self.word_form)

    def edit_word_form(self, word_form):
        self.edit_word_form_command(word_form)
        self.set_labels(word_form)
        self.populate_sound_changes_list(word_form)


class NewWordFormWindow:
    def __init__(self, master, language, new_word_form_command, edit_word_form=None):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.language = language
        self.new_word_form_command = new_word_form_command
        self.edit_word_form = edit_word_form
        self.word_form_name = tk.StringVar()
        self.word_form_categories = tk.StringVar()
        self.word_form_original_stage = tk.StringVar()
        self.word_form_obsoleted_stage = tk.StringVar()
        self.word_form_sound_changes = []

        if edit_word_form is None:
            self.word_form_original_stage.set(language.get_current_stage())
        else:
            self.word_form_name.set(edit_word_form.name)
            self.word_form_categories.set(edit_word_form.categories)
            self.word_form_original_stage.set(edit_word_form.original_language_stage)
            self.word_form_obsoleted_stage.set(edit_word_form.obsoleted_language_stage)
            self.word_form_sound_changes = copy.copy(edit_word_form.base_form_rules)  # the naming is unintuitive here

        self.word_form_name_label = tk.Label(self.frame, text='Form Name:')
        self.word_form_name_entry = tk.Entry(self.frame, textvariable=self.word_form_name)
        self.word_form_categories_label = tk.Label(self.frame, text='Applies to Words of Type(s):')
        self.word_form_categories_entry = tk.Entry(self.frame, textvariable=self.word_form_categories)
        self.word_form_original_stage_label = tk.Label(self.frame, text='Added to Language at Stage:')
        self.word_form_original_stage_entry = tk.Entry(self.frame, textvariable=self.word_form_original_stage)
        self.word_form_obsoleted_stage_label = tk.Label(self.frame, text='Fell Out of Use at Stage:')
        self.word_form_obsoleted_stage_entry = tk.Entry(self.frame, textvariable=self.word_form_obsoleted_stage)
        self.word_form_sound_changes_list_label = tk.Label(self.frame, text='Conjugation Rules:')
        self.word_form_sound_changes_list_scrollbar = tk.Scrollbar(self.frame, orient='vertical')
        self.word_form_sound_changes_list = tk.Listbox(self.frame, width=50,
                                                       yscrollcommand=self.word_form_sound_changes_list_scrollbar.set)
        self.word_form_sound_changes_list_scrollbar.configure(command=self.word_form_sound_changes_list.yview)
        i = 0
        for rule in self.word_form_sound_changes:
            self.word_form_sound_changes_list.insert(i, rule.get_as_conjugation_rule_string())
            i = i + 1
        self.add_word_form_sound_change_button = tk.Button(self.frame, text='Add New Conjugation Rule',
                                                           command=self.open_new_conjugation_rule_window)
        self.create_word_form_button = tk.Button(self.frame, text='Create Word Form' if edit_word_form is None
                                                 else 'Save Word Form',
                                                 command=self.create_word_form if edit_word_form is None
                                                 else self.update_word_form)

        self.word_form_name_label.grid(column=1, row=1)
        self.word_form_name_entry.grid(column=2, row=1)
        self.word_form_categories_label.grid(column=1, row=2)
        self.word_form_categories_entry.grid(column=2, row=2)
        self.word_form_original_stage_label.grid(column=1, row=3)
        self.word_form_original_stage_entry.grid(column=2, row=3)
        self.word_form_obsoleted_stage_label.grid(column=1, row=4)
        self.word_form_obsoleted_stage_entry.grid(column=2, row=4)
        self.word_form_sound_changes_list_label.grid(column=1, row=5, columnspan=2)
        self.word_form_sound_changes_list.grid(column=1, row=6, sticky='ew', columnspan=2)
        self.word_form_sound_changes_list_scrollbar.grid(column=3, row=6, sticky='ns')
        self.add_word_form_sound_change_button.grid(column=1, row=7, columnspan=2)
        self.create_word_form_button.grid(column=1, row=8, columnspan=2, pady=6)

        self.frame.grid()

    def add_conjugation_rule(self, sound_change):
        self.word_form_sound_changes.append(sound_change)
        self.word_form_sound_changes_list.delete(0, tk.END)
        i = 0
        for rule in self.word_form_sound_changes:
            self.word_form_sound_changes_list.insert(i, rule.get_as_conjugation_rule_string())
            i = i + 1

    def open_new_conjugation_rule_window(self):
        new_conjugation_rule_window = tk.Toplevel(self.master)
        NewConjugationRuleWindow(new_conjugation_rule_window, self.language, self.add_conjugation_rule)

    def create_word_form(self):
        # input validation
        if not self.word_form_name.get():
            showinfo('Invalid Input', 'Form must have a name!')
            return
        try:
            original_language_stage = int(self.word_form_original_stage.get())
        except ValueError:
            showinfo('Invalid Input', 'Value for "Added to Language at Stage:" must be an integer!')
            return
        obsoleted_language_stage = -1
        if self.word_form_obsoleted_stage.get():
            try:
                obsoleted_language_stage = int(self.word_form_obsoleted_stage.get())
            except ValueError:
                showinfo('Invalid Input', 'Value for "Fell Out of Use at Stage" must be an integer or blank!')
                return
        if len(self.word_form_sound_changes) < 1:
            showinfo('Invalid Input', 'Form must have at least one conjugation rule!')
            return

        # create the word form, call the callback, and close the window
        word_form = WordFormRule(self.word_form_name.get(), self.word_form_categories.get(), original_language_stage)
        word_form.obsoleted_language_stage = obsoleted_language_stage
        for rule in self.word_form_sound_changes:
            word_form.add_custom_rule(rule)
        self.new_word_form_command(word_form)
        self.master.destroy()

    def update_word_form(self):
        # input validation
        if not self.word_form_name.get():
            showinfo('Invalid Input', 'Form must have a name!')
            return
        try:
            original_language_stage = int(self.word_form_original_stage.get())
        except ValueError:
            showinfo('Invalid Input', 'Value for "Added to Language at Stage:" must be an integer!')
            return
        obsoleted_language_stage = -1
        if self.word_form_obsoleted_stage.get():
            try:
                obsoleted_language_stage = int(self.word_form_obsoleted_stage.get())
            except ValueError:
                showinfo('Invalid Input', 'Value for "Fell Out of Use at Stage" must be an integer or blank!')
                return
        if len(self.word_form_sound_changes) < 1:
            showinfo('Invalid Input', 'Form must have at least one conjugation rule!')
            return

        # update the word form, call the callback, and close the window
        word_form = self.edit_word_form
        word_form.name = self.word_form_name.get()
        word_form.categories = self.word_form_categories.get()
        word_form.original_language_stage = original_language_stage
        word_form.obsoleted_language_stage = obsoleted_language_stage
        word_form.clear_rules()
        for rule in self.word_form_sound_changes:
            word_form.add_custom_rule(rule)
        self.new_word_form_command(word_form)
        self.master.destroy()


class NewConjugationRuleWindow:
    def __init__(self, master, language, new_conjugation_rule_command):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.language = language
        self.new_conjugation_rule_command = new_conjugation_rule_command
        self.affix_type = tk.IntVar()
        self.sounds = []
        self.sounds_text = tk.StringVar()
        self.start_end_sound_type = tk.StringVar()

        self.sounds_text.set('-')

        self.prefix_type_radiobutton = tk.Radiobutton(self.frame, text='Prefix', variable=self.affix_type, value=1)
        self.suffix_type_radiobutton = tk.Radiobutton(self.frame, text='Suffix', variable=self.affix_type, value=2)
        self.custom_type_radiobutton = tk.Radiobutton(self.frame, text='Custom', variable=self.affix_type, value=3)
        self.sounds_label = tk.Label(self.frame, text='Sounds:')
        self.sounds_text_label = tk.Label(self.frame, textvariable=self.sounds_text)
        self.add_sound_button = tk.Button(self.frame, text='Add Sound', command=self.open_sound_select_window)
        self.del_sound_button = tk.Button(self.frame, text='Remove Sound', command=self.remove_sound)
        self.del_sound_button.configure(state='disabled')
        self.start_end_sound_type_label = tk.Label(self.frame, text='Occurs before/after sound type:')
        self.start_end_sound_type_entry = tk.Entry(self.frame, textvariable=self.start_end_sound_type)
        self.add_conjugation_rule_button = tk.Button(self.frame, text='Add Conjugation Rule',
                                                     command=self.create_conjugation_rule)
        self.add_conjugation_rule_button.configure(state='disabled')

        self.prefix_type_radiobutton.grid(column=1, row=1)
        self.suffix_type_radiobutton.grid(column=1, row=2)
        # self.custom_type_radiobutton.grid(column=1, row=3)
        self.sounds_label.grid(column=1, row=4)
        self.sounds_text_label.grid(column=1, row=5)
        self.add_sound_button.grid(column=1, row=6)
        self.del_sound_button.grid(column=1, row=7)
        self.start_end_sound_type_label.grid(column=1, row=8)
        self.start_end_sound_type_entry.grid(column=1, row=9)
        self.add_conjugation_rule_button.grid(column=1, row=10)

        self.frame.grid()

    def set_sounds_text(self):
        sounds_text = ''
        for sound in self.sounds:
            sounds_text = sounds_text + sound.orthographic_transcription
        self.sounds_text.set(sounds_text)

    def add_sound(self, sound):
        self.sounds.append(sound)
        self.set_sounds_text()
        self.del_sound_button.configure(state='normal')
        self.add_conjugation_rule_button.configure(state='normal')

    def open_sound_select_window(self):
        sound_select_window = tk.Toplevel(self.master)
        gui_sound.SoundSelectWindow(sound_select_window, self.language.get_full_sound_inventory(), self.add_sound)

    def remove_sound(self):
        if len(self.sounds) < 1:
            return
        self.sounds.pop()
        self.set_sounds_text()
        if len(self.sounds) < 1:
            self.del_sound_button.configure(state='disabled')
            self.add_conjugation_rule_button.configure(state='disabled')
            self.sounds_text.set('-')

    def create_conjugation_rule(self):
        if self.affix_type.get() == 1:  # prefix
            condition = '#_' + self.start_end_sound_type.get()
        elif self.affix_type.get() == 2:  # suffix
            condition = self.start_end_sound_type.get() + '_#'
        else:  # other
            condition = self.start_end_sound_type.get()
        sound_change = SoundChangeRule(None, self.sounds, condition=condition)
        self.new_conjugation_rule_command(sound_change)
        self.master.destroy()
