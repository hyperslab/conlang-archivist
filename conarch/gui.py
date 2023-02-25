import tkinter as tk
from conarch import db
from conarch.gui_word_form import WordFormWindow, NewWordFormWindow
from conarch.gui_sound import NewSoundWindow, SoundSelectWindow, SoundWindow
from conarch.gui_word import NewWordWindow, WordWindow
from conarch.gui_sound_change import NewSoundChangeWindow, SoundChangeWindow
from conarch.gui_language import NewLanguageWindow, CloneLanguageWindow, BranchLanguageWindow, LanguageWindow


class Application:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)

        db.check_create_db()

        self.language_list_frame = tk.LabelFrame(self.frame, text='Choose a Language')
        self.languages = db.fetch_all_languages()
        self.language_list_scrollbar = tk.Scrollbar(self.language_list_frame, orient='vertical')
        self.language_list = tk.Listbox(self.language_list_frame, height=8,
                                        yscrollcommand=self.language_list_scrollbar.set)
        self.language_list_scrollbar.configure(command=self.language_list.yview)
        i = 0
        for language in self.languages:
            self.language_list.insert(i, language.name if language.source_language is None else
                                      ('  ' * language.get_branch_depth()) + '↳' + language.name)
            i = i + 1
        self.language_list.bind('<Double-1>', self.open_language_from_list)
        self.new_language_button = tk.Button(self.language_list_frame, text='Add New Language',
                                             command=self.popup_new_language_window)

        self.current_language = None

        self.language_list.grid(row=1, column=1, padx=(4, 0), pady=2)
        self.language_list_scrollbar.grid(row=1, column=2, sticky='ns', padx=(0, 4), pady=2)
        self.new_language_button.grid(row=2, column=1, pady=2, columnspan=2)
        self.language_list_frame.grid(column=1, row=1, padx=8, pady=6)

        self.clone_language_button = tk.Button(self.frame, text='Clone This Language',
                                               command=self.popup_clone_language_window)
        self.branch_language_button = tk.Button(self.frame, text='Branch This Language',
                                                command=self.popup_branch_language_window)
        self.clone_language_button.grid(row=2, column=1, pady=2)
        self.branch_language_button.grid(row=3, column=1, pady=2)
        self.clone_language_button.configure(state='disabled')
        self.branch_language_button.configure(state='disabled')

        self.language_info_frame = tk.LabelFrame(self.frame, text='Language Information')
        self.language_sounds = None
        self.language_sound_list_type = tk.StringVar()
        self.language_sound_list_type.set('Modern Sounds')
        self.language_sound_list_label = tk.Label(self.language_info_frame, text='Sound Inventory')
        self.language_sound_list_type_menu = tk.OptionMenu(self.language_info_frame,
                                                           self.language_sound_list_type,
                                                           *['Modern Sounds', 'Original Sounds'],
                                                           command=self.language_sound_list_type_changed)
        self.language_sound_list_scrollbar = tk.Scrollbar(self.language_info_frame, orient='vertical')
        self.language_sound_list = tk.Listbox(self.language_info_frame, width=18,
                                              yscrollcommand=self.language_sound_list_scrollbar.set)
        self.language_sound_list_scrollbar.configure(command=self.language_sound_list.yview)
        self.language_sound_list.bind('<Double-1>', self.open_current_language_sound)
        self.add_sound_button = tk.Button(self.language_info_frame, text='Add New Sound',
                                          command=self.popup_new_sound_window)
        self.language_words = None
        self.language_word_list_label = tk.Label(self.language_info_frame, text='Stem Dictionary')
        self.language_word_list_scrollbar = tk.Scrollbar(self.language_info_frame, orient='vertical')
        self.language_word_list = tk.Listbox(self.language_info_frame, width=20,
                                             yscrollcommand=self.language_word_list_scrollbar.set)
        self.language_word_list_scrollbar.configure(command=self.language_word_list.yview)
        self.language_word_list.bind('<Double-1>', self.open_current_language_word)
        self.add_word_button = tk.Button(self.language_info_frame, text='Add New Word',
                                         command=self.popup_new_word_window)
        self.language_history = None
        self.language_history_list_label = tk.Label(self.language_info_frame, text='Language History')
        self.language_history_list_scrollbar = tk.Scrollbar(self.language_info_frame, orient='vertical')
        self.language_history_list = tk.Listbox(self.language_info_frame, width=44,
                                                yscrollcommand=self.language_history_list_scrollbar.set)
        self.language_history_list_scrollbar.configure(command=self.language_history_list.yview)
        self.language_history_list.bind('<Double-1>', self.open_history_item)
        self.add_sound_change_button = tk.Button(self.language_info_frame, text='Add Historical Sound Change',
                                                 command=self.popup_new_sound_change_window)
        self.add_word_form_button = tk.Button(self.language_info_frame, text='Add Word Form',
                                              command=self.popup_new_word_form_window)

        self.language_frame = tk.Frame(self.language_info_frame)
        self.view_language_at_stage_button = tk.Button(self.language_frame,
                                                       text='View Language at an Older Stage:',
                                                       command=self.popup_current_language_older_stage)
        self.view_language_at_stage_stage = tk.StringVar()
        self.view_language_at_stage_stage.set('0')
        self.view_language_at_stage_stage_menu = tk.OptionMenu(self.language_frame,
                                                               self.view_language_at_stage_stage,
                                                               *['0'])
        self.edit_language_button = tk.Button(self.language_frame, text='Edit Language',
                                              command=self.edit_current_language)

        self.popup_language_window = None
        self.last_opened_popup_language = None
        self.popup_language_sounds = None
        self.popup_language_words = None
        self.popup_language_history = None

        # self.language_sound_list_label.grid(row=1, column=1)
        self.language_sound_list_type_menu.grid(row=1, column=1, columnspan=2)  # TODO ugly
        self.language_sound_list.grid(row=2, column=1)
        self.language_sound_list_scrollbar.grid(row=2, column=2, sticky='ns')
        self.add_sound_button.grid(row=3, column=1, columnspan=2)
        self.language_word_list_label.grid(row=1, column=3)
        self.language_word_list.grid(row=2, column=3)
        self.language_word_list_scrollbar.grid(row=2, column=4, sticky='ns')
        self.add_word_button.grid(row=3, column=3, columnspan=2)
        self.language_history_list_label.grid(row=1, column=5)
        self.language_history_list.grid(row=2, column=5)
        self.language_history_list_scrollbar.grid(row=2, column=6, sticky='ns')
        self.add_sound_change_button.grid(row=3, column=5, columnspan=2, sticky='w')
        self.add_word_form_button.grid(row=3, column=5, columnspan=2, sticky='e')
        self.language_info_frame.grid(column=2, row=1, padx=8, pady=6, rowspan=3)
        for child in self.language_info_frame.winfo_children():
            try:
                child['state'] = 'disabled'
            except tk.TclError:
                pass

        self.view_language_at_stage_button.grid(row=1, column=1)
        self.view_language_at_stage_stage_menu.grid(row=2, column=1, pady=(0, 4))
        self.edit_language_button.grid(row=3, column=1, pady=(4, 0))
        self.language_frame.grid(column=7, row=1, rowspan=3, padx=6)
        for child in self.language_frame.winfo_children():
            try:
                child['state'] = 'disabled'
            except tk.TclError:
                pass

        self.frame.grid()

    def popup_new_language_window(self, confirm_command=None, edit_language=None):
        if confirm_command is None:
            confirm_command = self.create_language if edit_language is None else self.update_edit_language
        new_language_window = tk.Toplevel(self.frame)
        NewLanguageWindow(new_language_window, confirm_command, edit_language)

    def create_language(self, new_language):
        db.insert_language(new_language)
        self.language_list.insert(len(self.languages), new_language.name)
        self.languages.append(new_language)

    def update_edit_language(self, edit_language):
        db.update_language(edit_language)
        self.reload_current_language()

    def popup_clone_language_window(self):
        iteration = 2
        while self.current_language.name + ' ' + str(iteration) in [lang.name for lang in self.languages]:
            iteration = iteration + 1
        clone_language_window = tk.Toplevel(self.frame)
        CloneLanguageWindow(clone_language_window, self.current_language, self.create_language, iteration=iteration)

    def popup_branch_language_window(self):
        branch_language_window = tk.Toplevel(self.frame)
        BranchLanguageWindow(branch_language_window, self.current_language, self.branch_language)

    def branch_language(self, new_language):
        db.insert_language(new_language)
        self.language_list.insert(self.languages.index(self.current_language) + 1,
                                  ('  ' * new_language.get_branch_depth()) + '↳' + new_language.name)
        self.languages.insert(self.languages.index(self.current_language) + 1, new_language)

    def open_language_from_list(self, event):
        language = self.languages[event.widget.curselection()[0]]
        db.reload_language(language)
        self.open_language(language)

    def open_language(self, language):
        for child in self.language_info_frame.winfo_children():
            try:
                child['state'] = 'normal'
            except tk.TclError:
                pass
        self.clone_language_button.configure(state='normal')
        self.branch_language_button.configure(state='normal')
        for child in self.language_frame.winfo_children():
            try:
                child['state'] = 'normal'
            except tk.TclError:
                pass

        self.language_info_frame['text'] = 'Language Information: ' + language.name

        self.language_sound_list_type.set('Modern Sounds')
        self.language_sound_list.delete(0, tk.END)
        self.language_sounds = list()
        i = 0
        for sound in language.modern_phonetic_inventory:
            sound_name = sound.orthographic_transcription
            if sound.ipa_transcription is not None:
                sound_name = sound_name + ' /' + sound.ipa_transcription + '/'
            self.language_sound_list.insert(i, sound_name)
            self.language_sounds.append(sound)
            i = i + 1

        self.language_word_list.delete(0, tk.END)
        self.language_words = list()
        i = 0
        for word in language.words:
            word_stem = word.get_modern_stem_string(include_ipa=True)
            self.language_word_list.insert(i, word_stem)
            self.language_words.append(word)
            i = i + 1

        self.language_history_list.delete(0, tk.END)
        self.language_history = list()
        i = 0  # language stage
        j = 0  # position in list
        for sound_change in language.sound_changes:
            for word_form in language.get_forms_added_at_stage(i):  # get all forms in a stage (move to own window?)
                form = word_form.categories + ' form: ' + word_form.name
                self.language_history_list.insert(j, form)
                self.language_history.append(word_form)
                j = j + 1
            history = 'Sound Change: ' + str(sound_change)  # then advance the stage with a sound change
            self.language_history_list.insert(j, history)
            self.language_history.append(sound_change)
            j = j + 1
            i = i + 1
        for word_form in language.get_forms_added_at_stage(i):  # get all forms in the current stage
            form = word_form.categories + ' form: ' + word_form.name
            self.language_history_list.insert(j, form)
            self.language_history.append(word_form)
            j = j + 1

        menu = self.view_language_at_stage_stage_menu['menu']
        menu.delete(0, tk.END)
        for i in range(0, language.get_current_stage()):
            menu.add_command(label=str(i), command=lambda value=str(i): self.view_language_at_stage_stage.set(value))

        self.current_language = language

    def edit_current_language(self):
        self.popup_new_language_window(edit_language=self.current_language)

    def reload_current_language(self):
        self.open_language(self.current_language)

    def popup_open_language(self, language, label=None):
        language_window = tk.Toplevel(self.frame)
        LanguageWindow(language_window, language, label=label)

    def popup_current_language_older_stage(self):
        self.popup_open_language(self.current_language.copy_language_at_stage(
            language_stage=int(self.view_language_at_stage_stage.get())),
            label=self.current_language.name + ' - Stage ' + self.view_language_at_stage_stage.get())

    def language_sound_list_type_changed(self, _):
        if 'modern' in self.language_sound_list_type.get().lower():
            inventory = self.current_language.modern_phonetic_inventory
        else:
            inventory = self.current_language.original_phonetic_inventory
        self.language_sound_list.delete(0, tk.END)
        self.language_sounds = list()
        i = 0
        for sound in inventory:
            sound_name = sound.orthographic_transcription
            if sound.ipa_transcription is not None:
                sound_name = sound_name + ' /' + sound.ipa_transcription + '/'
            self.language_sound_list.insert(i, sound_name)
            self.language_sounds.append(sound)
            i = i + 1

    def popup_new_sound_window(self, confirm_command=None, edit_sound=None):
        if confirm_command is None:
            confirm_command = self.create_sound if edit_sound is None else self.update_edit_sound
        new_sound_window = tk.Toplevel(self.frame)
        NewSoundWindow(new_sound_window, confirm_command, edit_sound)

    def create_sound(self, new_sound):
        self.current_language.add_original_sound(new_sound)
        db.insert_sound(new_sound)
        db.insert_language_sound(self.current_language.language_id, new_sound)
        self.reload_current_language()

    def update_edit_sound(self, edit_sound):
        db.update_sound(edit_sound)
        db.update_language_sound(self.current_language.language_id, edit_sound)
        self.reload_current_language()

    def popup_new_word_window(self, confirm_command=None, edit_word=None):
        if confirm_command is None:
            confirm_command = self.create_word if edit_word is None else self.update_edit_word
        new_word_window = tk.Toplevel(self.frame)
        NewWordWindow(new_word_window, self.current_language, confirm_command, edit_word=edit_word)

    def create_word(self, new_word):
        self.current_language.add_word(new_word, new_word.original_language_stage)
        db.insert_word(new_word, self.current_language.language_id)
        self.language_word_list.insert(len(self.language_words), new_word.get_modern_stem_string(include_ipa=True))
        self.language_words.append(new_word)

    def update_edit_word(self, edit_word):
        db.update_word(edit_word, refresh_sounds=True, refresh_definitions=True)
        self.reload_current_language()

    def popup_sound_select_window(self, select_command=None, new_sound_command=None):
        sound_select_window = tk.Toplevel(self.frame)
        SoundSelectWindow(sound_select_window, self.current_language.get_full_sound_inventory(), select_command,
                          new_sound_command=new_sound_command)

    def popup_new_sound_change_window(self, confirm_command=None, edit_sound_change=None):
        if confirm_command is None:
            confirm_command = self.create_sound_change if edit_sound_change is None else self.update_edit_sound_change
        new_sound_change_window = tk.Toplevel(self.frame)
        NewSoundChangeWindow(new_sound_change_window, self.current_language, confirm_command,
                             edit_sound_change=edit_sound_change, new_sound_command=self.create_sound)

    def create_sound_change(self, new_sound_change):
        db.insert_sound_change_rule(new_sound_change)
        db.insert_language_sound_change_rule(self.current_language.language_id, new_sound_change.sound_change_rule_id,
                                             ordering=len(self.language_history))
        self.current_language.apply_sound_change(new_sound_change)
        self.reload_current_language()

    def update_edit_sound_change(self, edit_sound_change):
        db.update_sound_change_rule(edit_sound_change)
        self.reload_current_language()

    def popup_new_word_form_window(self, confirm_command=None, edit_word_form=None):
        if confirm_command is None:
            confirm_command = self.create_word_form if edit_word_form is None else self.update_edit_sound_change
        new_word_form_window = tk.Toplevel(self.frame)
        NewWordFormWindow(new_word_form_window, self.current_language, confirm_command, edit_word_form)
        return

    def create_word_form(self, word_form):
        self.current_language.add_word_form(word_form)
        db.insert_word_form_rule(word_form, self.current_language.language_id)
        self.reload_current_language()

    def update_edit_word_form(self, word_form):
        db.update_word_form_rule(word_form, refresh_sound_change_rules=True)
        self.reload_current_language()

    def open_sound(self, sound, allow_edit=True):
        sound_window = tk.Toplevel(self.frame)
        edit_command = self.update_edit_sound if allow_edit else None
        SoundWindow(sound_window, sound, edit_command)

    def open_current_language_sound(self, event):
        self.open_sound(self.language_sounds[event.widget.curselection()[0]])

    def open_word(self, word, allow_edit=True):
        word_window = tk.Toplevel(self.frame)
        WordWindow(word_window, self.current_language, word,
                   edit_word_command=self.update_edit_word if allow_edit else None)

    def open_current_language_word(self, event):
        self.open_word(self.language_words[event.widget.curselection()[0]])

    def open_sound_change(self, sound_change, history_stage, allow_edit=True):
        sound_change_window = tk.Toplevel(self.frame)
        SoundChangeWindow(sound_change_window, self.current_language, sound_change, history_stage,
                          edit_sound_change_command=self.update_edit_sound_change if allow_edit else None,
                          new_sound_command=self.create_sound)

    def open_current_language_sound_change(self, event):
        self.open_sound_change(self.language_history[event.widget.curselection()[0]],
                               event.widget.curselection()[0])

    def open_history_item(self, event):
        item = self.language_history[event.widget.curselection()[0]]
        order = event.widget.curselection()[0]
        if 'SoundChangeRule' in str(type(item)):  # 'type(x) is y' does not work anymore for some reason
            self.open_sound_change(item, order)
        elif 'WordFormRule' in str(type(item)):
            word_form_window = tk.Toplevel(self.frame)
            WordFormWindow(word_form_window, language=self.current_language, word_form=item,
                           edit_word_form_command=self.update_edit_word_form)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Conlang Archivist')
    app = Application(root)
    root.mainloop()
