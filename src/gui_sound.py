import tkinter as tk
from src.sound import Sound
from tkinter.messagebox import showinfo


class SoundWindow:
    def __init__(self, master, sound, edit_sound_command=None):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.sound = sound
        self.edit_sound_command = edit_sound_command

        self.sound_orthography_label = tk.Label(self.frame)
        self.sound_ipa_label = tk.Label(self.frame)
        self.sound_categories_label = tk.Label(self.frame)
        self.sound_frequency_label = tk.Label(self.frame)
        self.sound_description_label = tk.Label(self.frame)
        self.set_labels(sound)
        self.sound_edit_button = tk.Button(self.frame, text='Edit Sound', command=self.open_edit_sound_window)

        self.sound_orthography_label.grid(row=1)
        self.sound_ipa_label.grid(row=2)
        self.sound_categories_label.grid(row=3)
        self.sound_frequency_label.grid(row=4)
        if sound.description:
            self.sound_description_label.grid(row=5)
        if edit_sound_command:
            self.sound_edit_button.grid(row=6)

        self.frame.grid()

    def set_labels(self, sound):
        self.sound_orthography_label.configure(text='Sound Orthography:\n' + sound.orthographic_transcription)
        self.sound_ipa_label.configure(text='IPA Transcription:\n' + sound.ipa_transcription)
        # noinspection SpellCheckingInspection
        self.sound_categories_label.configure(text='Sound Categories\n([C]onsonant, [V]owel etc.):\n' +
                                                   sound.phonotactics_categories)
        self.sound_frequency_label.configure(text='Frequency in language:\n' + str(sound.frequency))
        self.sound_description_label.configure(text='Description:\n' + sound.description)

    def open_edit_sound_window(self):
        edit_sound_window = tk.Toplevel(self.master)
        NewSoundWindow(edit_sound_window, self.edit_sound, edit_sound=self.sound)

    def edit_sound(self, sound):
        self.edit_sound_command(sound)
        self.set_labels(sound)


class NewSoundWindow:
    def __init__(self, master, new_sound_command, edit_sound=None):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.new_sound_command = new_sound_command
        self.edit_sound = edit_sound
        self.new_sound_orthography = tk.StringVar()
        self.new_sound_ipa = tk.StringVar()
        self.new_sound_categories = tk.StringVar()
        self.new_sound_frequency = tk.StringVar()
        self.new_sound_description = tk.StringVar()
        self.new_sound_option_initial = tk.IntVar()
        self.new_sound_option_final = tk.IntVar()
        self.new_sound_option_onset = tk.IntVar()
        self.new_sound_option_nucleus = tk.IntVar()
        self.new_sound_option_coda = tk.IntVar()
        self.new_sound_option_clusters = tk.IntVar()
        self.new_sound_option_double = tk.IntVar()
        self.new_sound_option_boundary = tk.IntVar()

        if edit_sound is None:
            self.new_sound_option_initial.set(1)
            self.new_sound_option_final.set(1)
            self.new_sound_option_onset.set(1)
            self.new_sound_option_nucleus.set(1)
            self.new_sound_option_coda.set(1)
            self.new_sound_option_clusters.set(1)
            self.new_sound_option_double.set(1)
            self.new_sound_option_boundary.set(1)
        else:
            self.new_sound_orthography.set(edit_sound.orthographic_transcription)
            self.new_sound_ipa.set(edit_sound.ipa_transcription)
            self.new_sound_categories.set(edit_sound.phonotactics_categories)
            self.new_sound_frequency.set(edit_sound.frequency)
            self.new_sound_description.set(edit_sound.description)
            self.new_sound_option_initial.set(edit_sound.can_appear_word_initially)
            self.new_sound_option_final.set(edit_sound.can_appear_word_finally)
            self.new_sound_option_onset.set(edit_sound.can_appear_in_onset)
            self.new_sound_option_nucleus.set(edit_sound.can_appear_in_nucleus)
            self.new_sound_option_coda.set(edit_sound.can_appear_in_coda)
            self.new_sound_option_clusters.set(edit_sound.can_appear_in_clusters)
            self.new_sound_option_double.set(edit_sound.can_cluster_self)
            self.new_sound_option_boundary.set(edit_sound.can_duplicate_across_syllable_boundaries)
            self.edit_sound = edit_sound

        new_sound_window_header = tk.Label(self.frame, text="Add a new sound to the language's "
                                                            "original (stage 0) phonetic "
                                                            "inventory.\n(If you want to add a "
                                                            "sound at a later stage, use a Sound "
                                                            "Change!)")

        new_sound_orthography_label = tk.Label(self.frame, text='Enter Sound Orthography')
        new_sound_orthography_entry = tk.Entry(self.frame, textvariable=self.new_sound_orthography)
        new_sound_ipa_label = tk.Label(self.frame, text='Enter Sound IPA Representation')
        new_sound_ipa_entry = tk.Entry(self.frame, textvariable=self.new_sound_ipa)
        new_sound_categories_label = tk.Label(self.frame, text='Enter Sound Categories')
        new_sound_categories_entry = tk.Entry(self.frame, textvariable=self.new_sound_categories)
        new_sound_frequency_label = tk.Label(self.frame, text='Enter Sound Frequency')
        new_sound_frequency_entry = tk.Entry(self.frame, textvariable=self.new_sound_frequency)
        new_sound_description_label = tk.Label(self.frame, text='Enter Sound Description')
        new_sound_description_entry = tk.Entry(self.frame, textvariable=self.new_sound_description)
        new_sound_confirm_button = tk.Button(self.frame,
                                             text='Create Sound' if edit_sound is None else 'Save Sound',
                                             command=self.create_sound if edit_sound is None else self.update_sound)

        new_sound_options_label = tk.Label(self.frame, text='Automatic Word Generation Options')
        new_sound_option_initial_checkbutton = tk.Checkbutton(self.frame, text='Allow Word Initially',
                                                              variable=self.new_sound_option_initial)
        new_sound_option_final_checkbutton = tk.Checkbutton(self.frame, text='Allow Word Finally',
                                                            variable=self.new_sound_option_final)
        new_sound_option_onset_checkbutton = tk.Checkbutton(self.frame,
                                                            text='Allow in Syllable Onset',
                                                            variable=self.new_sound_option_onset)
        new_sound_option_nucleus_checkbutton = tk.Checkbutton(self.frame,
                                                              text='Allow in Syllable Nucleus',
                                                              variable=self.new_sound_option_nucleus)
        new_sound_option_coda_checkbutton = tk.Checkbutton(self.frame,
                                                           text='Allow in Syllable Coda',
                                                           variable=self.new_sound_option_coda)
        new_sound_option_clusters_checkbutton = tk.Checkbutton(self.frame,
                                                               text='Allow in Clusters',
                                                               variable=self.new_sound_option_clusters)
        new_sound_option_double_checkbutton = tk.Checkbutton(self.frame,
                                                             text='Allow Doubling in Clusters',
                                                             variable=self.new_sound_option_double)
        new_sound_option_boundary_checkbutton = tk.Checkbutton(self.frame,
                                                               text='Allow Doubling Across Syllable Boundaries',
                                                               variable=self.new_sound_option_boundary)

        if edit_sound is None:
            new_sound_window_header.grid(column=1, row=0, columnspan=2)
        new_sound_orthography_label.grid(column=1, row=1)
        new_sound_orthography_entry.grid(column=1, row=2)
        new_sound_ipa_label.grid(column=1, row=3)
        new_sound_ipa_entry.grid(column=1, row=4)
        new_sound_categories_label.grid(column=1, row=5)
        new_sound_categories_entry.grid(column=1, row=6)
        new_sound_frequency_label.grid(column=1, row=7)
        new_sound_frequency_entry.grid(column=1, row=8)
        new_sound_description_label.grid(column=1, row=9)
        new_sound_description_entry.grid(column=1, row=10)
        new_sound_options_label.grid(column=2, row=1)
        new_sound_option_initial_checkbutton.grid(column=2, row=2)
        new_sound_option_final_checkbutton.grid(column=2, row=3)
        new_sound_option_onset_checkbutton.grid(column=2, row=4)
        new_sound_option_nucleus_checkbutton.grid(column=2, row=5)
        new_sound_option_coda_checkbutton.grid(column=2, row=6)
        new_sound_option_clusters_checkbutton.grid(column=2, row=7)
        new_sound_option_double_checkbutton.grid(column=2, row=8)
        new_sound_option_boundary_checkbutton.grid(column=2, row=9)
        new_sound_confirm_button.grid(column=1, row=11, columnspan=2)

        self.frame.grid()

    def create_sound(self):
        # input validation
        try:
            frequency = float(self.new_sound_frequency.get())
        except ValueError:
            showinfo('Invalid Input', 'Frequency must be a number!')
            return

        # create the sound, call the callback, and close the window
        new_sound = Sound(orthographic_transcription=self.new_sound_orthography.get(),
                          ipa_transcription=self.new_sound_ipa.get(),
                          phonotactics_categories=self.new_sound_categories.get(),
                          description=self.new_sound_description.get(),
                          frequency=frequency)
        new_sound.can_appear_word_initially = self.new_sound_option_initial.get() == 1
        new_sound.can_appear_word_finally = self.new_sound_option_final.get() == 1
        new_sound.can_appear_in_onset = self.new_sound_option_onset.get() == 1
        new_sound.can_appear_in_nucleus = self.new_sound_option_nucleus.get() == 1
        new_sound.can_appear_in_coda = self.new_sound_option_coda.get() == 1
        new_sound.can_appear_in_clusters = self.new_sound_option_clusters.get() == 1
        new_sound.can_cluster_self = self.new_sound_option_double.get() == 1
        new_sound.can_duplicate_across_syllable_boundaries = self.new_sound_option_boundary.get() == 1
        self.new_sound_command(new_sound)
        self.master.destroy()

    def update_sound(self):
        # input validation
        try:
            frequency = float(self.new_sound_frequency.get())
        except ValueError:
            showinfo('Invalid Input', 'Frequency must be a number!')
            return

        # update the sound, call the callback, and close the window
        new_sound = self.edit_sound
        new_sound.orthographic_transcription = self.new_sound_orthography.get()
        new_sound.ipa_transcription = self.new_sound_ipa.get()
        new_sound.phonotactics_categories = self.new_sound_categories.get()
        new_sound.description = self.new_sound_description.get()
        new_sound.frequency = frequency
        new_sound.can_appear_word_initially = self.new_sound_option_initial.get() == 1
        new_sound.can_appear_word_finally = self.new_sound_option_final.get() == 1
        new_sound.can_appear_in_onset = self.new_sound_option_onset.get() == 1
        new_sound.can_appear_in_nucleus = self.new_sound_option_nucleus.get() == 1
        new_sound.can_appear_in_coda = self.new_sound_option_coda.get() == 1
        new_sound.can_appear_in_clusters = self.new_sound_option_clusters.get() == 1
        new_sound.can_cluster_self = self.new_sound_option_double.get() == 1
        new_sound.can_duplicate_across_syllable_boundaries = self.new_sound_option_boundary.get() == 1
        self.new_sound_command(new_sound)
        self.master.destroy()


class SoundSelectWindow:
    def __init__(self, master, sounds, select_command, new_sound_command=None, close_on_select=False):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.sounds = sounds
        self.select_command = select_command
        self.new_sound_command = new_sound_command
        self.close_on_select = close_on_select

        self.sound_select_list_label = tk.Label(self.frame, text='Select a Sound')
        self.sound_select_list_scrollbar = tk.Scrollbar(self.frame, orient='vertical')
        self.sound_select_list = tk.Listbox(self.frame, width=16,
                                            yscrollcommand=self.sound_select_list_scrollbar.set)
        self.sound_select_list_scrollbar.configure(command=self.sound_select_list.yview)
        self.populate_list_from_sounds()
        self.sound_select_list.bind('<Double-1>', self.call_select_command)
        new_sound_button = tk.Button(self.frame, text='Create New Sound', command=self.open_new_sound_window)

        self.sound_select_list_label.grid(row=1, column=1)
        self.sound_select_list.grid(row=2, column=1)
        self.sound_select_list_scrollbar.grid(row=2, column=2, sticky='ns')
        if new_sound_command:
            new_sound_button.grid(row=3, column=1, columnspan=2)

        self.frame.grid()

    def populate_list_from_sounds(self):
        self.sound_select_list.delete(0, tk.END)
        i = 0
        for sound in self.sounds:
            sound_name = sound.orthographic_transcription
            if sound.ipa_transcription is not None:
                sound_name = sound_name + ' /' + sound.ipa_transcription + '/'
            self.sound_select_list.insert(i, sound_name)
            i = i + 1

    def call_select_command(self, event):
        self.select_command(self.sounds[event.widget.curselection()[0]])
        if self.close_on_select:
            self.master.destroy()

    def open_new_sound_window(self):
        new_sound_window = tk.Toplevel(self.master)
        NewSoundWindow(new_sound_window, self.new_sound_created)

    def new_sound_created(self, sound):
        self.new_sound_command(sound)
        self.sounds.append(sound)
        self.populate_list_from_sounds()
