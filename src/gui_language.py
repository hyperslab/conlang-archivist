import tkinter as tk
from tkinter.messagebox import showinfo
from src.language import Language


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
