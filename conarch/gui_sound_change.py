import copy
import tkinter as tk
from conarch.gui_sound import SoundSelectWindow
from conarch.sound_change_rule import SoundChangeRule


class SoundChangeWindow:
    def __init__(self, master, language, sound_change, history_stage, edit_sound_change_command=None,
                 new_sound_command=None):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.language = language
        self.sound_change = sound_change
        self.history_stage = history_stage
        self.edit_sound_change_command = edit_sound_change_command
        self.new_sound_command = new_sound_command

        self.sound_change_label = tk.Label(self.frame)
        self.sound_change_ipa_label = tk.Label(self.frame)
        self.history_stage_label = tk.Label(self.frame, text='Language History Stage:\n' + str(history_stage + 1))
        self.condition_label = tk.Label(self.frame)
        self.set_labels(sound_change)
        self.sound_change_edit_button = tk.Button(self.frame, text='Edit Sound Change',
                                                  command=self.open_edit_sound_change_window)

        self.sound_change_label.grid(row=1)
        self.sound_change_ipa_label.grid(row=2)
        if sound_change.get_condition_string():
            self.condition_label.grid(row=3)
        self.history_stage_label.grid(row=4)
        if edit_sound_change_command:
            self.sound_change_edit_button.grid(row=5)

        self.frame.grid()

    def set_labels(self, sound_change):
        self.sound_change_label.configure(text='Sound Change:\n' + str(sound_change).split(':')[-1].strip())
        self.sound_change_ipa_label.configure(text='Sound Change (IPA):\n' +
                                                   sound_change.ipa_str().split(':')[-1].strip())
        self.condition_label.configure(text='Change Occurs:\n' + sound_change.get_condition_string())

    def open_edit_sound_change_window(self):
        edit_sound_change_window = tk.Toplevel(self.master)
        NewSoundChangeWindow(edit_sound_change_window, self.language, self.edit_sound_change,
                             edit_sound_change=self.sound_change, new_sound_command=self.new_sound_command)

    def edit_sound_change(self, sound_change):
        self.edit_sound_change_command(sound_change)
        self.set_labels(sound_change)


class NewSoundChangeWindow:
    def __init__(self, master, language, new_sound_change_command, edit_sound_change=None, new_sound_command=None):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.language = language
        self.new_sound_change_command = new_sound_change_command
        self.edit_sound_change = edit_sound_change
        self.new_sound_command = new_sound_command
        self.new_sound_change_old_sounds_text = tk.StringVar()
        self.new_sound_change_new_sounds_text = tk.StringVar()
        self.new_sound_change_condition = tk.StringVar()

        if edit_sound_change is None:
            self.new_sound_change_old_sounds = None
            self.new_sound_change_old_sounds_text.set('Ø')
            self.new_sound_change_new_sounds = None
            self.new_sound_change_new_sounds_text.set('Ø')
        else:
            self.new_sound_change_old_sounds = copy.copy(edit_sound_change.old_sounds)
            self.new_sound_change_old_sounds_text.set('')
            if edit_sound_change.old_sounds is not None:
                for sound in edit_sound_change.old_sounds:
                    if sound is not None:
                        self.new_sound_change_old_sounds_text.set(self.new_sound_change_old_sounds_text.get() +
                                                                  sound.orthographic_transcription)
            self.new_sound_change_new_sounds = copy.copy(edit_sound_change.new_sounds)
            self.new_sound_change_new_sounds_text.set('')
            if edit_sound_change.new_sounds is not None:
                for sound in edit_sound_change.new_sounds:
                    if sound is not None:
                        self.new_sound_change_new_sounds_text.set(self.new_sound_change_new_sounds_text.get() +
                                                                  sound.orthographic_transcription)
            self.new_sound_change_condition.set(edit_sound_change.condition)
            self.edit_sound_change = edit_sound_change

        new_sound_change_old_sounds_label = tk.Label(self.frame, text='Old Sounds:')
        new_sound_change_new_sounds_label = tk.Label(self.frame, text='New Sounds:')
        new_sound_change_old_sounds_text_label = tk.Label(self.frame,
                                                          textvariable=self.new_sound_change_old_sounds_text)
        new_sound_change_new_sounds_text_label = tk.Label(self.frame,
                                                          textvariable=self.new_sound_change_new_sounds_text)
        arrow_label = tk.Label(self.frame, text='>')
        add_old_sound_button = tk.Button(self.frame, text='Add Old Sound',
                                         command=self.open_add_old_sound_window)
        add_new_sound_button = tk.Button(self.frame, text='Add New Sound',
                                         command=self.open_add_new_sound_window)
        self.del_old_sound_button = tk.Button(self.frame, text='Remove Old Sound',
                                              command=self.remove_old_sound)
        self.del_new_sound_button = tk.Button(self.frame, text='Remove New Sound',
                                              command=self.remove_new_sound)
        slash_label = tk.Label(self.frame, text='/')
        new_sound_change_condition_label = tk.Label(self.frame, text='Condition:')
        new_sound_change_condition_entry = tk.Entry(self.frame,
                                                    textvariable=self.new_sound_change_condition)
        self.new_sound_change_confirm_button = tk.Button(self.frame,
                                                         text='Create Sound Change' if edit_sound_change is None
                                                         else 'Save Sound Change',
                                                         command=self.create_sound_change if edit_sound_change is None
                                                         else self.update_sound_change)

        if edit_sound_change is None:
            self.del_old_sound_button['state'] = 'disabled'
            self.del_new_sound_button['state'] = 'disabled'
            self.new_sound_change_confirm_button['state'] = 'disabled'

        new_sound_change_old_sounds_label.grid(column=1, row=1)
        new_sound_change_new_sounds_label.grid(column=3, row=1)
        new_sound_change_condition_label.grid(column=5, row=1)
        new_sound_change_old_sounds_text_label.grid(column=1, row=2)
        arrow_label.grid(column=2, row=2)
        new_sound_change_new_sounds_text_label.grid(column=3, row=2)
        slash_label.grid(column=4, row=2)
        new_sound_change_condition_entry.grid(column=5, row=2)
        add_old_sound_button.grid(column=1, row=3)
        add_new_sound_button.grid(column=3, row=3)
        self.del_old_sound_button.grid(column=1, row=4)
        self.del_new_sound_button.grid(column=3, row=4)
        self.new_sound_change_confirm_button.grid(column=1, row=5, columnspan=5, pady=(4, 2))

        self.frame.grid()

    def open_add_old_sound_window(self):
        add_old_sound_window = tk.Toplevel(self.master)
        SoundSelectWindow(add_old_sound_window, self.language.get_full_sound_inventory(), self.add_old_sound,
                          close_on_select=True)

    def add_old_sound(self, sound):
        if self.new_sound_change_old_sounds is None:
            self.new_sound_change_old_sounds = [sound]
            self.new_sound_change_old_sounds_text.set(sound.orthographic_transcription)
        else:
            self.new_sound_change_old_sounds.append(sound)
            self.new_sound_change_old_sounds_text.set(self.new_sound_change_old_sounds_text.get() +
                                                      sound.orthographic_transcription)
        self.del_old_sound_button['state'] = 'normal'
        self.new_sound_change_confirm_button['state'] = 'normal'

    def open_add_new_sound_window(self):
        add_new_sound_window = tk.Toplevel(self.master)
        SoundSelectWindow(add_new_sound_window, self.language.get_full_sound_inventory(), self.add_new_sound,
                          close_on_select=True, new_sound_command=self.new_sound_command)

    def add_new_sound(self, sound):
        if self.new_sound_change_new_sounds is None:
            self.new_sound_change_new_sounds = [sound]
            self.new_sound_change_new_sounds_text.set(sound.orthographic_transcription)
        else:
            self.new_sound_change_new_sounds.append(sound)
            self.new_sound_change_new_sounds_text.set(self.new_sound_change_new_sounds_text.get() +
                                                      sound.orthographic_transcription)
        if self.del_new_sound_button:
            try:
                self.del_new_sound_button['state'] = 'normal'
            except tk.TclError:
                self.del_new_sound_button = None

    def remove_old_sound(self):
        if self.new_sound_change_old_sounds is None or len(self.new_sound_change_old_sounds) == 0:
            return
        self.new_sound_change_old_sounds.pop()
        if len(self.new_sound_change_old_sounds) == 0:
            self.new_sound_change_old_sounds = None
            self.new_sound_change_old_sounds_text.set('Ø')
            if self.del_old_sound_button:
                self.del_old_sound_button['state'] = 'disabled'
            if self.new_sound_change_confirm_button:
                self.new_sound_change_confirm_button['state'] = 'disabled'
        else:
            self.new_sound_change_old_sounds_text.set('')
            for sound in self.new_sound_change_old_sounds:
                self.new_sound_change_old_sounds_text.set(self.new_sound_change_old_sounds_text.get() +
                                                          sound.orthographic_transcription)

    def remove_new_sound(self):
        if self.new_sound_change_new_sounds is None or len(self.new_sound_change_new_sounds) == 0:
            return
        self.new_sound_change_new_sounds.pop()
        if len(self.new_sound_change_new_sounds) == 0:
            self.new_sound_change_new_sounds = None
            self.new_sound_change_new_sounds_text.set('Ø')
            if self.del_new_sound_button:
                self.del_new_sound_button['state'] = 'disabled'
        else:
            self.new_sound_change_new_sounds_text.set('')
            for sound in self.new_sound_change_new_sounds:
                self.new_sound_change_new_sounds_text.set(self.new_sound_change_new_sounds_text.get() +
                                                          sound.orthographic_transcription)

    def create_sound_change(self):
        # create the sound change, call the callback, and close the window
        new_sound_change = SoundChangeRule(self.new_sound_change_old_sounds, self.new_sound_change_new_sounds,
                                           condition=self.new_sound_change_condition.get().strip())
        self.new_sound_change_command(new_sound_change)
        self.master.destroy()

    def update_sound_change(self):
        # update the sound change, call the callback, and close the window
        self.edit_sound_change.old_sounds = self.new_sound_change_old_sounds
        self.edit_sound_change.new_sounds = self.new_sound_change_new_sounds
        self.edit_sound_change.condition = self.new_sound_change_condition.get().strip()
        self.new_sound_change_command(self.edit_sound_change)
        self.master.destroy()
