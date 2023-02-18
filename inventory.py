class Inventory:
    def __init__(self):
        self.V = list()
        self.N = list()
        self.S = list()
        self.A = list()
        self.F = list()
        self.L = list()
        self.W = list()

        self.O = list()
        self.J = list()

    def add_vowels(self, letters):
        for letter in letters:
            self.V.append(letter)
        self.refresh()

    def add_nasals(self, letters):
        for letter in letters:
            self.N.append(letter)
        self.refresh()

    def add_stops(self, letters):
        for letter in letters:
            self.S.append(letter)
        self.refresh()

    def add_affricates(self, letters):
        for letter in letters:
            self.A.append(letter)
        self.refresh()

    def add_fricatives(self, letters):
        for letter in letters:
            self.F.append(letter)
        self.refresh()

    def add_liquids(self, letters):
        for letter in letters:
            self.L.append(letter)
        self.refresh()

    def add_semivowels(self, letters):
        for letter in letters:
            self.W.append(letter)
        self.refresh()

    def refresh(self):
        self.O = self.S + self.A + self.F
        self.J = self.L + self.W


"""
def generate_stem(sound_inventory, tactics, min_syllable=1, max_syllable=3):
    stem = list()
    for i in range(0, random.randint(min_syllable, max_syllable)):
        stem.append(parse_tactics(sound_inventory, tactics))
    return stem


def parse_tactics(sound_inventory, tactics):
    syllable = list()
    i = 0
    while i < len(tactics):
        if tactics[i] == '(':
            chance = 0.5
            if i+1 < len(tactics) and tactics[i+1] in '123456789':
                i = i+1
                chance = float(tactics[i])/10.0
            j = i
            while tactics[j] != ')':
                j = j+1
                assert j < len(tactics)
            if random.random() < chance:
                syllable = syllable + (parse_tactics(sound_inventory, tactics[i+1:j]))
            i = j
        elif tactics[i] == '{':
            j = i
            options = list()
            possible_sounds = list()
            while tactics[j] != '}':
                j = j + 1
                assert j < len(tactics)
                if type(sound_inventory) is Inventory:
                    if tactics[j] in 'VNSAFLWOJ':
                        options.append(tactics[j])
                else:
                    possible_sounds = possible_sounds +\
                                      [s for s in sound_inventory if tactics[j] in s.phonotactics_categories]
            if len(options) > 0:
                syllable = syllable + (parse_tactics(sound_inventory, random.choice(options)))
            elif len(possible_sounds) > 0:
                syllable.append(random.choices([s for s in possible_sounds],
                                               weights=[s.frequency for s in possible_sounds])[0])
            i = j
        elif type(sound_inventory) is Inventory:
            if tactics[i] == 'V':
                syllable.append(Sound(random.choice(sound_inventory.V)))
            elif tactics[i] == 'N':
                syllable.append(Sound(random.choice(sound_inventory.N)))
            elif tactics[i] == 'S':
                syllable.append(Sound(random.choice(sound_inventory.S)))
            elif tactics[i] == 'A':
                syllable.append(Sound(random.choice(sound_inventory.A)))
            elif tactics[i] == 'F':
                syllable.append(Sound(random.choice(sound_inventory.F)))
            elif tactics[i] == 'L':
                syllable.append(Sound(random.choice(sound_inventory.L)))
            elif tactics[i] == 'W':
                syllable.append(Sound(random.choice(sound_inventory.W)))
            elif tactics[i] == 'O':
                syllable.append(Sound(random.choice(sound_inventory.O)))
            elif tactics[i] == 'J':
                syllable.append(Sound(random.choice(sound_inventory.J)))
        else:
            possible_sounds = [s for s in sound_inventory if tactics[i] in s.phonotactics_categories]
            if len(possible_sounds) > 0:
                syllable.append(random.choices([s for s in possible_sounds],
                                               weights=[s.frequency for s in possible_sounds])[0])
        i += 1
    return syllable

koa_inventory = Inventory()
koa_inventory.add_vowels('aeiou')
koa_inventory.add_stops("ptkq'b")
koa_inventory.add_stops(["t'", "k'"])
koa_inventory.add_affricates(['c', 'ch', 'ckh', "c'", "ch'", "ckh'"])
koa_inventory.add_fricatives('sxh')
koa_inventory.add_fricatives(['sh', 'kh'])
koa_inventory.add_nasals('mn')
koa_inventory.add_liquids('rly')
koa_inventory.add_semivowels('jw')
"""