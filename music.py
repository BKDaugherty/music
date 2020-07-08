from enum import Enum
class BaseNote(Enum):
    E = 0
    F = 1
    G = 3
    A = 5
    B = 7
    C = 8
    D = 10

class Modifier(Enum):
    SHARP = 1
    FLAT = -1

class Note:
    def __init__(self, note, modi=None):
        self.note = note
        self.modi = modi
    def get_value(self):
        value = self.note.value
        if self.modi:
            value = value + self.modi.value
        return value
    def get_name(self):
        name = self.note.name
        if self.modi:
            if self.modi == Modifier.SHARP:
                name = name + "#"
            else:
                name = name + "b"
        return name
    def get_base(self):
        return self.note
    def __str__(self):
        return self.get_name()

class String:
    def __init__(self, root, frets=24):
        self.root = root
        self.frets = frets
    def play(self, fret):
        # Doesn't account for different octaves... (also find best name...)
        return get_interval(notes, self.root, Interval(fret % 12))[0]
    def get_frets(self):
        return self.frets
    def get_root(self):
        return self.root
    
class Interval(Enum):
    Identity = 0
    MinorSecond = 1
    MajorSecond = 2
    MinorThird = 3
    MajorThird = 4
    PerfectFourth = 5
    Tritone = 6
    PerfectFifth = 7
    MinorSixth = 8
    MajorSixth = 9
    MinorSeventh = 10
    MajorSeventh = 11
    Octave = 12

# This is basically the same thing
Half = Interval.MinorSecond
Whole = Interval.MajorSecond

IONIAN_SCALE = [
    Interval.MajorSecond,
    Interval.MajorThird,
    Interval.PerfectFourth,
    Interval.PerfectFifth,
    Interval.MajorSixth,
    Interval.MajorSeventh,
    Interval.Octave
]

def interval_modify(interval, value):
    return Interval(interval.value + value)

def get_scale(scale_map, base_scale=IONIAN_SCALE):
    resulting_scale = []
    for index, value in enumerate(scale_map):
        interval = interval_modify(base_scale[index], value)
        resulting_scale.append(interval)
    return resulting_scale

def get_interval(notes, root, interval):
    valid_notes = []
    target_value = (root.get_value() + interval.value) % 12
    for note in notes:
        if note.get_value() == target_value:
            valid_notes.append(note)
    return valid_notes

def get_scale_quality(scale_map):
    scale_map = scale_map or [0]
    return sum(scale_map)

def choose_best_notes(root, valid_notes_in_scale):
    notes_in_scale = []
    seen = set([])
    for note_group in valid_notes_in_scale:
        choice = None
        for candidate in note_group:
            if candidate.get_base() not in seen:
                choice = candidate
                notes_in_scale.append(candidate)
                seen.add(candidate.get_base())
                break
        if choice == None:
            notes_in_scale.append(note_group[0])
    return notes_in_scale

class Mode(Enum):
    IONIAN = 1
    DORIAN = 2
    PHRYGIAN = 3
    LYDIAN = 4
    MIXOLYDIAN = 5
    AOLIAN = 6
    LOCRIAN = 7

scale_maps = {
    Mode.IONIAN : [0,0,0,0,0,0,0],
    Mode.DORIAN : [0,-1,0,0,0,-1,0],
    Mode.PHRYGIAN : [-1,-1,0,0,-1,-1,0],
    Mode.LYDIAN : [0,0,1,0,0,0,0],
    Mode.MIXOLYDIAN : [0,0,0,0,0,-1,0],
    Mode.AOLIAN : [0,-1,0,0,-1,-1,0],
    Mode.LOCRIAN : [-1,-1,0,-1,-1,-1,0],
}

class Scale:
    def __init__(self, root, scale_map=None, interval_scale=None):
        assert(scale_map or interval_scale)
        if scale_map:
            self.interval_scale = get_scale(scale_map)
        else:
            self.interval_scale = interval_scale
        
        self.root = root
        self.quality = get_scale_quality(scale_map)
        valid_notes_in_scale = [[root]]
        for interval in self.interval_scale:
            next_valid_notes = get_interval(notes, root, interval)
            valid_notes_in_scale.append(next_valid_notes)
        self.valid_notes = valid_notes_in_scale
    def display_notes(self):
        notes = choose_best_notes(self.root, self.valid_notes)
        to_print = ""
        for note in notes:
            to_print += f" {note.get_name()}"
        return to_print
    def get_quality(self):
        return self.quality

    # Returns None if not in scale
    def get_note_degree(self, note):
        for degree, note_group in enumerate(self.valid_notes):
            if note_membership(note, note_group):
                return degree
        return None
    
def print_scale(scale_name, scale):
    to_print = f"  {scale_name} {scale.get_quality()}:"
    to_print += scale.display_notes()
    print(to_print)

def note_equivalence(note, other_note):
    return note.get_value() == other_note.get_value()

def note_membership(note,container):
    for check in container:
        if note_equivalence(note, check):
            return True
    return False

def print_scale_on_instrument(string_instrument, scale, use_degree=False, guide_frets=[]):
    max_fret = max([string.get_frets() for string in string_instrument])
    to_print = "0 |"
    for fret_number in range(0, max_fret + 1):
        if fret_number in guide_frets:
            if len(str(fret_number)) > 1:
                to_print += f"__{fret_number}___|"
            else:
                to_print += f"__{fret_number}__|"

        else:
            to_print += "_____|" 
    print(to_print)
    for string in string_instrument:
        string_name = string.get_root().get_name()
        if len(string_name) == 2:
            to_print = f"{string_name}"
        else:
            to_print = f"{string_name} "
        for fret in range(string.get_frets() + 1):
            note = string.play(fret)
            to_print += "|"
            degree = scale.get_note_degree(note)
            if degree != None:
                if use_degree:
                    to_print += f"  {degree}  "
                else:
                    if len(note.get_name()) == 2:
                        to_print += f"  {note.get_name()} "
                    else:
                        to_print += f"  {note.get_name()}  "
            else:
                to_print += "     "
        print(to_print)


notes = set()
for base_note in BaseNote:
    note = Note(base_note)
    notes.add(note)
    for modi in Modifier:
        modi_note = Note(base_note, modi=modi)
        notes.add(modi_note)

# Internal only plz
names_to_notes = {}        
for note in notes:
    names_to_notes[note.get_name()] = note
        
notes_to_scales = {}
for note in sorted(notes, key=lambda note: note.get_value()):
    note_to_scales = {}
    for scale_name, scale_map in scale_maps.items():
        scale = Scale(note, scale_map=scale_map)
        note_to_scales[scale_name] = scale
    notes_to_scales[note] = note_to_scales

#scale = Scale(root, interval_scale=[Interval.MajorThird, Interval.PerfectFifth, Interval.MajorSixth, Interval.MinorSeventh])

def create_instrument(tuning, instrument_name):
    return [String(names_to_notes[name], frets=12) for name in tuning], instrument_name

## Display code
bass_tuning = reversed(["E", "A", "D", "G"])
Bass = [String(names_to_notes[name], frets=12) for name in bass_tuning]
uke_tuning = reversed(["G", "C", "E", "A"])
custom_uke_tuning = reversed(["D", "G", "B", "E"])
guitar_tuning = reversed(["E", "A", "D", "G", "B", "E"])

instruments = [create_instrument(tuning, name) for (tuning, name) in [(uke_tuning, "uke"), (custom_uke_tuning, "custom_uke"), (guitar_tuning, "guitar")]]
completed_notes = set()
for note, scales in notes_to_scales.items():
    if note_membership(note, completed_notes):
        continue
    else:
        completed_notes.add(note)
        for scale_name, scale in scales.items():
            for (instrument, instrument_name) in instruments:
                print(f"{note.get_name()} {scale_name.name} for {instrument_name}")
                print_scale_on_instrument(instrument, scale, use_degree=False, guide_frets=[0,3,5,7,9,12])
                print("")





