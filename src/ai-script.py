import cmd
import sys
import json
import os
import string
import tempfile
import itertools
import random
import math

RELEASE = "0.25082016b"

QUESTION_YESNO = "yesno"
QUESTION_SINGLECHOICE = "single"
QUESTION_MULTIPLECHOICE = "multi"

def d6():
    return random.randint(1, 6)

class Game:
    def __init__(self):
        self.map = {}
        self.currentcard = ""
        self.upcomingcard = ""
        self.action = ""
        self.capabilities = []

        self.aedui_eligibility = ""
        self.arverni_eligibility = ""
        self.belgic_eligibility = ""
        self.roman_eligibility = ""

        self.winter_remaining = 0
        self.frost = 0
        self.winter = 0

        self.roman_senate = 2

        self.other_most_allies = 0
        self.off_map_legions = 0
        self.subdued_dispersed_allies = 0
        self.control_allies = 0

        self.colonies = 0

        self.aedui_resources = 0
        self.arverni_resources = 0
        self.belgic_resources = 0
        self.roman_resources = 0

        self.aedui_warband_available = 0
        self.aedui_tribe_available = 0
        self.aedui_citadel_available = 0
        self.arverni_leader_available = 0
        self.arverni_warband_available = 0
        self.arverni_tribe_available = 0
        self.arverni_citadel_available = 0
        self.belgic_leader_available = 0
        self.belgic_warband_available = 0
        self.belgic_tribe_available = 0
        self.belgic_citadel_available = 0
        self.germanic_warband_available = 0
        self.germanic_tribe_available = 0
        self.roman_leader_available = 0
        self.roman_auxilia_available = 0
        self.roman_fort_available = 0
        self.roman_legion_available = 0
        self.roman_tribe_available = 0

        self.bforcedraid = False

        self.aedui_last_command = ""
        self.aedui_ambush = False

class Region:
    app = None
    key = ""
    name = ""
    modname = ""
    control = ""
    pop = 0
    aedui_warband = 0
    aedui_warband_revealed = 0
    aedui_tribe = 0
    aedui_citadel = 0
    arverni_leader = 0
    arverni_warband = 0
    arverni_warband_revealed = 0
    arverni_tribe = 0
    arverni_citadel = 0
    belgic_leader = 0
    belgic_warband = 0
    belgic_warband_revealed = 0
    belgic_tribe = 0
    belgic_citadel = 0
    germanic_warband = 0
    germanic_warband_revealed = 0
    germanic_tribe = 0
    roman_leader = 0
    roman_auxilia = 0
    roman_auxilia_revealed = 0
    roman_fort = 0
    roman_legion = 0
    roman_tribe = 0
    dispersed_gathering = 0
    devastated = 0
    max_cities = 0
    max_citadel = 0
    adjacent = {}

    def __init__(self, theapp, thekey, thename, adjacencies):
        self.app = theapp
        self.key = thekey
        self.name = thename

        # name of this region in the json data
        self.modname = theapp.mapIndex[thekey]

        # adjancencies to this region
        self.adjacent = adjacencies

class Answer:
    def __init__(self):
        self.q = ""
        self.reply = ""
        self.faction = ""

# used when converting self.game to a JSON object for temporary storage in a file
class GameEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, FY):
            return ""
        if isinstance(obj, Region):
            return obj.__dict__
        if isinstance(obj, Game):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)


class FY(cmd.Cmd):

    allRegions = ["AED", "ARV", "ATR", "BIT", "CAT", "CAR", "HEL", "MAN", "MOR", "NER", "PIC", "SEQ", "SUG", "TRE", "UBI", "VEN"]
    mapIndex = {
        "AED": "Celctica (Aedui)",
        "ARV": "Celtica (Arverni, Cadurci, Volcae)",
        "ATR": "Belcica (Atrebates, Bellovaci, Remi)",
        "BIT": "Celtica (Bituriges)",
        "CAT": "Britannia",
        "CAR": "Celtica (Aulerci, Carnutes)",
        "HEL": "Provincia",
        "MAN": "Celtica (Senones, Mandubii, Lingones)",
        "MOR": "Belgica (Morini, Menapii)",
        "NER": "Belgica (Nervii)",
        "PIC": "Celctica (Pictones, Santones)",
        "SEQ": "Celtica (Sequani, Helvetii)",
        "SUG": "Germania (Sugambri, Suebi)",
        "TRE": "Celtica (Treveri)",
        "UBI": "Germania (Ubii, Suebi)",
        "VEN": "Celtica (Veneti, Namnetes)"
        }
    mapAdjacencies = {
        "AED": {"MAN": "L", "SEQ": "L", "HEL": "L", "ARV": "L", "BIT": "L"},
        "ARV": {"AED": "L", "HEL": "L", "PIC": "L", "BIT": "L"},
        "ATR": {"MOR": "L", "NER": "L", "TRE": "L", "MAN": "L", "CAR": "L", "VEN": "L", "CAT": "S"},
        "BIT": {"MAN": "L", "AED": "L", "ARV": "L", "PIC": "L", "CAR": "L"},
        "CAT": {"MOR": "S", "ATR": "S", "VEN": "S"},
        "CAR": {"ATR": "L", "MAN": "L", "BIT": "L", "PIC": "L", "VEN": "L"},
        "HEL": {"ARV": "L", "AED": "L", "SEQ": "L"},
        "MAN": {"ATR": "L", "TRE": "L", "SEQ": "L", "AED": "L", "BIT": "L", "CAR": "L"},
        "MOR": {"SUG": "R", "NER": "L", "ATR": "L", "CAT": "S"},
        "NER": {"SUG": "R", "TRE": "L", "ATR": "L", "MOR": "L"},
        "PIC": {"VEN": "L", "CAR": "L", "BIT": "L", "ARV": "L"},
        "SEQ": {"TRE": "L", "UBI": "R", "HEL": "L", "AED": "L", "MAN": "L"},
        "SUG": {"UBI": "L", "TRE": "R", "NER": "R", "MOR": "R"},
        "TRE": {"SUG": "R", "UBI": "R", "SEQ": "L", "MAN": "L", "ATR": "L", "NER": "L"},
        "UBI": {"SEQ": "R", "TRE": "R", "SUG": "L"},
        "VEN": {"CAT": "S", "ATR": "L", "CAR": "L", "PIC": "L"}
    }
    allySpaces = {
        "Catuvalauni": {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Morini":      {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Menapii":     {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Nervii":      {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Atrebates":   {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Bellovaci":   {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Remi":        {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Veneti":      {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Namnetes":    {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Aulerci":     {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Pictones":    {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Santones":    {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Cadurci":     {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Volcae":      {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Senones":     {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Lingones":    {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Helvetii":    {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Treveri":     {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Sugambri":    {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Suebi North": {"Aedui": False, "Arverni": False, "Belgic": False, "Roman": False, "Germanic": True},
        "Ubii":        {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Suebi South": {"Aedui": False, "Arverni": False, "Belgic": False, "Roman": False, "Germanic": True},
        "Helvii":      {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Eburones":    {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True}
        }
    citadelSpaces = {
        "Carnutes":    {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Bituriges":   {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Arverni":     {"Aedui": False, "Arverni": True,  "Belgic": False, "Roman": False, "Germanic": False},
        "Aedui":       {"Aedui": True,  "Arverni": False, "Belgic": False, "Roman": False, "Germanic": False},
        "Mandubii":    {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True},
        "Sequani":     {"Aedui": True,  "Arverni": True,  "Belgic": True,  "Roman": True,  "Germanic": True}
        }
    # card number: [ faction order + NP Instruction ]
    # factions: (Ro)man, (Ar)verni, (Ae)dui, (Be)lgic
    # NP instructions: (C)arnyx, (L)aurels, (S)words
    cardIndex = {
        1:  ['RoL', 'ArL', 'AeS', 'BeL'],
        2:  ['RoL', 'ArC', 'AeL', 'BeL'],
        3:  ['Ro ', 'ArL', 'AeS', 'BeL'],
        4:  ['Ro ', 'ArS', 'BeS', 'AeL'],
        5:  ['Ro ', 'ArC', 'BeL', 'AeL'],
        6:  ['Ro ', 'ArL', 'BeL', 'AeL'],
        7:  ['Ro ', 'AeL', 'ArC', 'BeL'],
        8:  ['Ro ', 'AeL', 'Ar ', 'Be '],
        9:  ['Ro ', 'Ae ', 'Ar ', 'Be '],
        10: ['Ro ', 'AeL', 'BeS', 'ArS'],
        11: ['RoL', 'AeL', 'BeL', 'ArL'],
        12: ['Ro ', 'AeL', 'BeL', 'Ar '],
        13: ['Ro ', 'BeL', 'ArC', 'AeL'],
        14: ['Ro ', 'Be ', 'ArC', 'AeL'],
        15: ['Ro ', 'BeL', 'ArC', 'AeL'],
        16: ['Ro ', 'BeL', 'AeL', 'ArL'],
        17: ['RoL', 'BeS', 'AeS', 'Ar '],
        18: ['Ro ', 'Be ', 'Ae ', 'Ar '],
        19: ['ArC', 'RoL', 'AeL', 'Be '],
        20: ['ArL', 'RoS', 'AeS', 'BeS'],
        21: ['ArC', 'RoL', 'AeL', 'BeS'],
        22: ['Ar ', 'Ro ', 'BeL', 'Ae '],
        23: ['ArC', 'Ro ', 'Be ', 'AeS'],
        24: ['ArC', 'RoL', 'BeL', 'Ae '],
        25: ['Ar ', 'AeL', 'RoL', 'BeS'],
        26: ['Ar ', 'Ae ', 'Ro ', 'BeS'],
        27: ['ArC', 'Ae ', 'Ro ', 'BeL'],
        28: ['Ar ', 'Ae ', 'Be ', 'RoS'],
        29: ['Ar ', 'AeS', 'Be ', 'RoS'],
        30: ['ArC', 'Ae ', 'BeL', 'Ro '],
        31: ['Ar ', 'Be ', 'Ro ', 'AeL'],
        32: ['ArL', 'BeS', 'RoL', 'AeS'],
        33: ['ArC', 'BeL', 'Ro ', 'Ae '],
        34: ['ArL', 'BeL', 'Ae ', 'Ro '],
        35: ['Ar ', 'Be ', 'ArL', 'RoS'],
        36: ['Ar ', 'BeL', 'AeL', 'Ro '],
        37: ['Ae ', 'Ro ', 'Ar ', 'BeS'],
        38: ['Ae ', 'Ro ', 'Ar ', 'Be '],
        39: ['Ae ', 'RoS', 'Ar ', 'BeS'],
        40: ['Ae ', 'Ro ', 'BeL', 'Ar '],
        41: ['Ar ', 'Ro ', 'Be ', 'Ar '],
        42: ['AeL', 'Ro ', 'BeL', 'Ar '],
        43: ['Ae ', 'Ar ', 'RoS', 'Be '],
        44: ['AeL', 'ArL', 'Ro ', 'Be '],
        45: ['Ar ', 'Ar ', 'Ro ', 'BeL'],
        46: ['AeL', 'Ar ', 'Be ', 'RoL'],
        47: ['AeS', 'ArS', 'BeS', 'RoS'],
        48: ['Ae ', 'Ar ', 'Ro ', 'BeL'],
        49: ['AeL', 'Be ', 'RoL', 'Ar '],
        50: ['AeL', 'BeL', 'RoL', 'ArL'],
        51: ['Ae ', 'Be ', 'RoS', 'Ar '],
        52: ['AeL', 'BeS', 'ArL', 'RoL'],
        53: ['AeS', 'BeS', 'Ar ', 'RoS'],
        54: ['AeS', 'BeS', 'ArS', 'RoS'],
        55: ['Be ', 'Ro ', 'ArS', 'AeL'],
        56: ['Be ', 'Ro ', 'Ar ', 'AeL'],
        57: ['BeL', 'Ro ', 'Ar ', 'Ae '],
        58: ['Be ', 'Ro ', 'AeS', 'Ar '],
        59: ['Be ', 'Ro ', 'AeL', 'ArC'],
        60: ['Be ', 'Ro ', 'Ae ', 'ArS'],
        61: ['Be ', 'ArS', 'Ro ', 'AeL'],
        62: ['BeL', 'ArL', 'RoL', 'AeL'],
        63: ['Be ', 'Ar ', 'Ro ', 'AeL'],
        64: ['BeL', 'ArS', 'Ae ', 'Ro '],
        65: ['BeL', 'Ar ', 'AeL', 'RoL'],
        66: ['BeL', 'ArS', 'AeL', 'RoL'],
        67: ['Be ', 'Ae ', 'Ro ', 'ArL'],
        68: ['BeL', 'AeL', 'Ro ', 'ArL'],
        69: ['BeS', 'AeS', 'RoS', 'Ar '],
        70: ['Be ', 'AeL', 'Ar ', 'Ro '],
        71: ['Be ', 'Ae ', 'Ar ', 'Ro '],
        72: ['BeL', 'AeS', 'ArL', 'RoL']
    }
    game = None  # Contains all game data we keep track of, anything we need to remember during a session (of possibly multiple executions)

    def __init__(self):
            cmd.Cmd.__init__(self)

            if (answer == None):
                # If no Answer this is an initial run, and not a return from a Question, so we load the JSON from VASSAL format
                self.parse_json(self)
            else:
                # We have an Answer, meaning this is the return from a Question, so we load the JSON from FSBot format
                self.parse_gamedata(self)

            # Which bot to activate?
            if self.game.action == 'Game State':
                self.do_status(self)

            if self.game.action.startswith('Aedui'):
                # check answer key for continuation of flow
                if answer is None:
                    self.do_aedui_flow(self)
                else:
                    if answer.q == 'event_ineffective':
                        if answer.reply.upper() == 'NO':
                            self.do_aedui_flow_execute_event(self)
                        else:
                            if self.do_aedui_flow_862(self) is False:
                                    # Battle would fail
                                if self.do_aedui_flow_863(self) is True:
                                    print ""
                                else:
                                    # Rally check failed so lets Raid
                                    nraid = self.do_aedui_flow_864(self)
                                    if nraid == 1:
                                        print ""
                                    elif nraid == 2:
                                        print ""
                                    else:
                                        # Raid check failed so lets March
                                        if self.do_aedui_flow_865(self) is True:
                                            print ""

                    special_complete = False

                    if self.game.aedui_last_command is "BATTLE":
                        if self.game.aedui_ambush is False:
                            special_complete = self.do_aedui_trade(self)

                    if self.game.aedui_last_command is "RALLY":
                        special_complete = self.do_aedui_trade(self)

                    elif self.game.aedui_last_command is "RAID":
                        special_complete = self.do_aedui_trade(self)

                    elif self.game.aedui_last_command is "MARCH":
                        special_complete = self.do_aedui_trade(self)

                    if special_complete > 2:
                        print "ACTION: Increase Aedui Resources by %s to %s" % (special_complete, self.game.aedui_resources + special_complete)
                        self.game.aedui_resources += special_complete
                        special_complete = True
                    else:
                        print "Trade Failed: Resources available to trade <= 2"
                        special_complete = False

                    if special_complete is False and self.game.aedui_last_command:
                        special_complete = self.do_aedui_suborn(self)


    def capabilityactive(self, num, shaded):
        for data in self.game.capabilities:
            if data[num] == num and data['shaded'] == shaded:
                return True

        return False

    def parse_json(self, rest):
        global inputdata
        inputdata = json.loads(inputdata)

        # Start new Game
        self.game = Game()
        self.game.action = inputdata['action']

        # set up all Regions and load Regions data from inputdata
        self.game.map["AED"] = Region(self, "AED", "Aedui", self.mapAdjacencies["AED"])
        self.load_region(self.game.map["AED"])
        self.game.map["ARV"] = Region(self, "ARV", "Arverni", self.mapAdjacencies["ARV"])
        self.load_region(self.game.map["ARV"])
        self.game.map["ATR"] = Region(self, "ATR", "Atrebates", self.mapAdjacencies["ATR"])
        self.load_region(self.game.map["ATR"])
        self.game.map["BIT"] = Region(self, "BIT", "Bituriges", self.mapAdjacencies["BIT"])
        self.load_region(self.game.map["BIT"])
        self.game.map["CAT"] = Region(self, "CAT", "Britannia", self.mapAdjacencies["CAT"])
        self.load_region(self.game.map["CAT"])
        self.game.map["CAR"] = Region(self, "CAR", "Carnutes", self.mapAdjacencies["CAR"])
        self.load_region(self.game.map["CAR"])
        self.game.map["HEL"] = Region(self, "HEL", "Provincia", self.mapAdjacencies["HEL"])
        self.load_region(self.game.map["HEL"])
        self.game.map["MAN"] = Region(self, "MAN", "Mandubii", self.mapAdjacencies["MAN"])
        self.load_region(self.game.map["MAN"])
        self.game.map["MOR"] = Region(self, "MOR", "Morini", self.mapAdjacencies["MOR"])
        self.load_region(self.game.map["MOR"])
        self.game.map["NER"] = Region(self, "NER", "Nervii", self.mapAdjacencies["NER"])
        self.load_region(self.game.map["NER"])
        self.game.map["PIC"] = Region(self, "PIC", "Pictones", self.mapAdjacencies["PIC"])
        self.load_region(self.game.map["PIC"])
        self.game.map["SEQ"] = Region(self, "SEQ", "Sequani", self.mapAdjacencies["SEQ"])
        self.load_region(self.game.map["SEQ"])
        self.game.map["SUG"] = Region(self, "SUG", "Sugambri", self.mapAdjacencies["SUG"])
        self.load_region(self.game.map["SUG"])
        self.game.map["TRE"] = Region(self, "TRE", "Treveri", self.mapAdjacencies["TRE"])
        self.load_region(self.game.map["TRE"])
        self.game.map["UBI"] = Region(self, "UBI", "Ubii", self.mapAdjacencies["UBI"])
        self.load_region(self.game.map["UBI"])
        self.game.map["VEN"] = Region(self, "VEN", "Veneti", self.mapAdjacencies["VEN"])
        self.load_region(self.game.map["VEN"])

        # units available, cards, resources, eligibility
        self.game.arverni_leader_available = 1
        self.game.belgic_leader_available = 1
        self.game.roman_leader_available = 1
        self.game.vercingetorix = 0  # TODO: need to load from inputdata
        self.game.ambiorix = 0  # TODO: need to load from inputdata
        self.game.caesar = 0  # TODO: need to load from inputdata
        for element, data in inputdata.items():
            # load capabilities
            if element == 'offboard':
                for piece in data:
                    if piece['name'].find(' Capability **') > -1:
                        self.game.capabilities.append(piece['name'])
            # load zones (regions)
            if element == 'zones':
                for zone in data:
                    if zone['name'] == 'Aedui Available Forces':
                        for piece in zone['pieces']:
                            if piece['name'].startswith('Aedui Warband'):
                                self.game.aedui_warband_available += 1
                            if piece['name'] == 'Aedui Ally (Occupied)' or piece['name'] == 'Aedui Citadel (Ally)':
                                self.game.aedui_tribe_available += 1
                            if piece['name'] == 'Aedui Citadel (Occupied)':
                                self.game.aedui_citadel_available += 1
                    if zone['name'] == 'Arverni Available Forces':
                        for piece in zone['pieces']:
                            if piece['name'].startswith('Arverni Warband'):
                                self.game.arverni_warband_available += 1
                            if piece['name'] == 'Arverni Ally (Occupied)' or piece['name'] == 'Arverni Citadel (Ally)':
                                self.game.arverni_tribe_available += 1
                            if piece['name'] == 'Arverni Citadel (Occupied)':
                                self.game.arverni_citadel_available += 1
                    if zone['name'] == 'Belgic Available Forces':
                        for piece in zone['pieces']:
                            if piece['name'].startswith('Belgic Warband'):
                                self.game.belgic_warband_available += 1
                            if piece['name'] == 'Belgic Ally (Occupied)' or piece['name'] == 'Belgic Citadel (Ally)':
                                self.game.belgic_tribe_available += 1
                            if piece['name'] == 'Belgic Citadel (Occupied)':
                                self.game.belgic_citadel_available += 1
                    if zone['name'] == 'Germanic Available Forces':
                        for piece in zone['pieces']:
                            if piece['name'].startswith('Germanic Warband'):
                                self.game.germanic_warband_available += 1
                            if piece['name'] == 'Germanic Ally (Occupied)':
                                self.game.germanic_tribe_available += 1
                    if zone['name'] == 'Roman Available Forces':
                        for piece in zone['pieces']:
                            if piece['name'] == 'Roman Auxilia':
                                self.game.roman_auxilia_available += 1
                            if piece['name'] == 'Roman Fort':
                                self.game.roman_fort_available += 1
                            if piece['name'] == 'Roman Ally (Occupied)':
                                self.game.roman_tribe_available += 1
                            if piece['name'] == 'Roman Legion':
                                self.game.roman_legion_available += 1
                    # check for Winter or Frost
                    if zone['name'] == 'Upcoming':
                        for piece in zone['pieces']:
                            if piece['name'].endswith(' - Winter'):
                                self.game.frost = 1
                    if zone['name'] == 'Current':
                        for piece in zone['pieces']:
                            if piece['name'].endswith(' - Winter'):
                                self.game.winter = 1
                    # check for leaders on the map, colonies on map, resources, eligibility
                    for piece in zone['pieces']:
                        if piece['name'] == 'Ambiorix' or piece['name'] == 'Belgic Successor':
                            self.game.belgic_leader_available = 0
                        if piece['name'] == 'Vercingetorix' or piece['name'] == 'Arverni Successor':
                            self.game.arverni_leader_available = 0
                        if piece['name'] == 'Caesar' or piece['name'] == 'Roman Successor':
                            self.game.roman_leader_available = 0
                        if piece['name'] == 'Colony Added':
                            self.game.colonies += 1
                        # Aedui Resources
                        if piece['name'].startswith('Aedui Resources ('):
                            self.game.aedui_resources = int(zone['name'])
                        # Aedui Eligibility
                        if piece['name'].startswith('Aedui Eligibility'):
                            self.game.aedui_eligibility = zone['name']
                        # Arverni Resources
                        if piece['name'].startswith('Averni Resources ('):
                            self.game.arverni_resources = int(zone['name'])
                        # Arverni Eligibility
                        if piece['name'].startswith('Averni Eligibility'):
                            self.game.arverni_eligibility = zone['name']
                        # Belgic Resources
                        if piece['name'].startswith('Belgic Resources ('):
                            self.game.belgic_resources = int(zone['name'])
                        # Belgic Eligibility
                        if piece['name'].startswith('Belgic Eligibility'):
                            self.game.belgic_eligibility = zone['name']
                        # Roman Resources
                        if piece['name'].startswith('Roman Resources ('):
                            self.game.roman_resources = int(zone['name'])
                        # Roman Eligibility
                        if piece['name'].startswith('Roman Eligibility'):
                            self.game.roman_eligibility = zone['name']

        # find other_most_allies
        aedui_score = 8 - self.game.aedui_tribe_available - self.game.aedui_citadel_available
        arverni_score = 13 - self.game.arverni_tribe_available - self.game.arverni_citadel_available
        belgic_score = 11 - self.game.belgic_tribe_available - self.game.belgic_citadel_available
        germanic_score = 6 - self.game.germanic_tribe_available
        roman_score = 6 - self.game.roman_tribe_available
        self.game.other_most_allies = max(arverni_score, belgic_score, germanic_score, roman_score)

        # Roman Senate, Legions, Cards
        for element, data in inputdata.items():
            if element == 'zones':
                for zone in data:
                    if zone['name'] == 'Senate - Uproar':
                        for piece in zone['pieces']:
                            if piece['name'] == 'Roman Senate':
                                self.game.roman_senate = 1
                    if zone['name'] == 'Senate - Intrigue':
                        for piece in zone['pieces']:
                            if piece['name'] == 'Roman Senate':
                                self.game.roman_senate = 2
                    if zone['name'] == 'Senate - Adulation':
                        for piece in zone['pieces']:
                            if piece['name'] == 'Roman Senate':
                                self.game.roman_senate = 3
                    if zone['name'] == 'Legions' or zone['name'] == 'Fallen Legions':
                        for piece in zone['pieces']:
                            if piece['name'] == 'Roman Legion':
                                self.game.off_map_legions += 1
                    if zone['name'] == "Current":
                        for piece in zone['pieces']:
                            self.game.currentcard = piece['name']
                    if zone['name'] == "Upcoming":
                        for piece in zone['pieces']:
                            self.game.upcomingcard = piece['name']

        # Roman Victory
        cities = len(self.allySpaces) + len(self.citadelSpaces) + self.game.colonies
        self.game.subdued_dispersed_allies = cities - arverni_score - belgic_score - germanic_score - aedui_score

        # Belgic Victory
        self.game.control_allies = belgic_score
        for key, region in self.game.map.items():
            if region.control == 'Belgic Control':
                self.game.control_allies += region.pop

        # Winter cards left in Deck
        self.game.winter_remaining = inputdata['winter']

    def load_region(self, region):
        # find zone for region in inputdata
        for element, data in inputdata.items():
            if element == 'zones':
                for zone in data:
                    if zone['name'] == region.modname:
                        for piece in zone['pieces']:
                            # find the control piece
                            if piece['name'].endswith('Control)'):
                                region.control = piece['name'][piece['name'].find(' (') + 2:-8] + ' Control'
                                region.pop += int(piece['name'][0:1])
                            if piece['name'] == 'Colony Added':
                                region.pop += 1
                            # count the aedui warbands
                            if piece['name'] == 'Aedui Warband':
                                region.aedui_warband += 1
                            # count the revealed aedui warbands revealed
                            if piece['name'] == 'Aedui Warband Revealed':
                                region.aedui_warband_revealed += 1
                            # count the aedui tribes (allies)
                            if piece['name'] == 'Aedui Ally':
                                region.aedui_tribe += 1
                            # count the aedui citadels
                            if piece['name'] == 'Aedui Citadel':
                                region.aedui_citadel += 1
                            # Arverni leader
                            if piece['name'] == 'Vercingetorix' or piece['name'] == 'Averni Successor':
                                region.arverni_leader = 1
                            # count the arverni warbands
                            if piece['name'] == 'Arverni Warband':
                                region.arverni_warband += 1
                            # count the revealed averni warbands revealed
                            if piece['name'] == 'Arverni Warband Revealed':
                                region.arverni_warband_revealed += 1
                            # count the arverni tribes (allies)
                            if piece['name'] == 'Arverni Ally':
                                region.arverni_tribe += 1
                            # count the arverni citadels
                            if piece['name'] == 'Averni Citadel':
                                region.arverni_citadel += 1
                            # Belgic leader
                            if piece['name'] == 'Ambiorix' or piece['name'] == 'Belgic Successor':
                                region.belgic_leader = 1
                            # count the belgic warbands
                            if piece['name'] == 'Belgic Warband':
                                region.belgic_warband += 1
                            # count the revealed belgic warbands revealed
                            if piece['name'] == 'Belgic Warband Revealed':
                                region.belgic_warband_revealed += 1
                            # count the belgic tribes (allies)
                            if piece['name'] == 'Belgic Ally':
                                region.belgic_tribe += 1
                            # count the belgic citadels
                            if piece['name'] == 'Belgic Citadel':
                                region.belgic_citadel += 1
                            # count the germanic warbands
                            if piece['name'] == 'Germanic Warband':
                                region.germanic_warband += 1
                            # count the revealed germanic warbands revealed
                            if piece['name'] == 'Germanic Warband Revealed':
                                region.germanic_warband_revealed += 1
                            # count the germanic tribes (allies)
                            if piece['name'] == 'Germanic Ally':
                                region.germanic_tribe += 1
                            # Roman leader
                            if piece['name'] == 'Caesar' or piece['name'] == 'Roman Successor':
                                region.roman_leader = 1
                            # count the roman auxilia
                            if piece['name'] == 'Roman Auxilia':
                                region.roman_auxilia += 1
                            # count the roman auxilia revealed
                            if piece['name'] == 'Roman Auxilia (Revealed)':
                                region.roman_auxilia_revealed += 1
                            # count the roman tribes (allies)
                            if piece['name'] == 'Roman Ally':
                                region.roman_tribe += 1
                            # count the roman fort
                            if piece['name'] == 'Roman Fort':
                                region.roman_fort += 1
                            # count the roman legion
                            if piece['name'] == 'Roman Legion':
                                region.roman_legion += 1
                            # count Dispersed tribes
                            if piece['name'].endswith(' (Dispersed)') or piece['name'].endswith(' (Gathering)'):
                                region.dispersed_gathering += 1
                                region.pop -= 1
                            # count Devastated
                            if piece['name'] == 'Devastated':
                                region.devastated += 1
                            # count number of tribes
                            for tribe in self.allySpaces:
                                piecename = piece['name']
                                sep = piecename.find(' (')
                                if sep > -1:
                                    piecename = piecename[:sep]
                                if piecename == tribe:
                                    region.max_cities += 1
                            # counter number of cities (citadel)
                            for tribe in self.citadelSpaces:
                                piecename = piece['name']
                                sep = piecename.find(' (')
                                if sep > -1:
                                    piecename = piecename[:sep]
                                if piecename == tribe:
                                    region.max_cities += 1

    def parse_gamedata(self, datafile):
        # Start new Game
        self.game = Game()

        # set up Regions, but do not load them yet
        self.game.map["AED"] = Region(self, "AED", "Aedui", self.mapAdjacencies["AED"])
        self.game.map["ARV"] = Region(self, "ARV", "Arverni", self.mapAdjacencies["ARV"])
        self.game.map["ATR"] = Region(self, "ATR", "Atrebates", self.mapAdjacencies["ATR"])
        self.game.map["BIT"] = Region(self, "BIT", "Bituriges", self.mapAdjacencies["BIT"])
        self.game.map["CAT"] = Region(self, "CAT", "Catuvellauni", self.mapAdjacencies["CAT"])
        self.game.map["CAR"] = Region(self, "CAR", "Carnutes", self.mapAdjacencies["CAR"])
        self.game.map["HEL"] = Region(self, "HEL", "Helvii", self.mapAdjacencies["HEL"])
        self.game.map["MAN"] = Region(self, "MAN", "Mandubii", self.mapAdjacencies["MAN"])
        self.game.map["MOR"] = Region(self, "MOR", "Morini", self.mapAdjacencies["MOR"])
        self.game.map["NER"] = Region(self, "NER", "Nervii", self.mapAdjacencies["NER"])
        self.game.map["PIC"] = Region(self, "PIC", "Pictones", self.mapAdjacencies["PIC"])
        self.game.map["SEQ"] = Region(self, "SEQ", "Sequani", self.mapAdjacencies["SEQ"])
        self.game.map["SUG"] = Region(self, "SUG", "Sugambri", self.mapAdjacencies["SUG"])
        self.game.map["TRE"] = Region(self, "TRE", "Treveri", self.mapAdjacencies["TRE"])
        self.game.map["UBI"] = Region(self, "UBI", "Ubii", self.mapAdjacencies["UBI"])
        self.game.map["VEN"] = Region(self, "VEN", "Veneti", self.mapAdjacencies["VEN"])

        # parse the JSON to Python lists
        gamedata = json.loads(inputdata)

        # iterate the lists so we can convert them to object attributes
        for item in gamedata:
            if item == "map":
                # we need to treat map uniquely since it contains sub-lists
                for subitem in gamedata[item]:
                    for subprop in gamedata[item][subitem]:
                        setattr(self.game.map[subitem], subprop, gamedata[item][subitem][subprop])
            else:
                setattr(self.game, item, gamedata[item])

    def write_gamedata(self, rest):
        # we dump the self.game object into a JSON string
        gamejson = json.dumps(self.game, cls=GameEncoder)

        # write the dumped game data to a temp file we can read back when the answer returns
        filename = '/tmp/fsbot-temp.%s.dat' % os.getpid()
        temp = open(filename, 'w+b')
        try:
            temp.write(gamejson)
        finally:
            temp.close()

            return temp.name

    def ask_question(self, faction, type, code, question, options):
        if options is None:
            options = ''
        if isvassal:
            datafile = self.write_gamedata(self)
            print json.dumps({"faction": faction, "type": type, "q": code, "question": question, "datafile": datafile, "options": options})
            return ''
        else:
            if type == QUESTION_YESNO:
                reply = raw_input(question + ' [Y/N]: ')
                if reply.upper() == 'Y':
                    return 'YES'
                else:
                    return 'NO'
            elif type == QUESTION_SINGLECHOICE:
                opts = options.split(';')
                numopts = len(opts)
                reply = 0
                while reply < 1 or reply > numopts:

                    print question + ':'
                    for num, o in enumerate(opts):
                        print (num+1), '-', o
                    try:
                        reply = int(raw_input('Type the number of your choice: '))
                    except ValueError:
                        reply = 0

                return opts[reply-1]

            elif type == QUESTION_MULTIPLECHOICE:
                opts = options.split(';')
                numopts = len(opts)
                reply = -1
                selection = []
                while reply != 0:

                    print question + ':'
                    for num, o in enumerate(opts):
                        if o in selection:
                            print (num + 1), '[X]', o
                        else:
                            print (num + 1), '[ ]', o
                    try:
                        reply = int(raw_input('Type the number of your selection, type 0 to finish: '))
                    except ValueError:
                        reply = -1

                    if reply >= 1 and reply <= numopts:
                        if opts[reply-1] in selection:
                            selection.remove(opts[reply-1])
                        else:
                            selection.append(opts[reply-1])

                print ','.join(map(str, selection))
                return ','.join(map(str, selection))

    def control_change_check(self, region):

        aedui_control = int(self.map[region].aedui_warband) + int(self.map[region].aedui_tribe) + int(self.map[region].aedui_citadel)
        arverni_count = int(self.map[region].arverni_leader) + int(self.map[region].arverni_warband) + int(self.map[region].arverni_tribe) + int(self.map[region].arverni_citadel)
        belgic_count = int(self.map[region].belgic_leader) + int(self.map[region].belgic_warband) + int(self.map[region].belgic_tribe) + int(self.map[region].belgic_citadel)
        roman_count = int(self.map[region].roman_leader) + int(self.map[region].roman_auxilia) + int(self.map[region].roman_fort) + int(self.map[region].roman_legion) + int(self.map[region].roman_tribe)
        germanic_count = int(self.map[region].aedui_warband) + int(self.map[region].aedui_tribe)

        if aedui_control > arverni_count + belgic_count + roman_count + germanic_count:
            return "Aedui"
        elif arverni_count > aedui_control + belgic_count + roman_count + germanic_count:
            return "Arverni"
        elif belgic_count > aedui_control + arverni_count + roman_count + germanic_count:
            return "Belgic"
        elif roman_count > aedui_control + arverni_count + belgic_count + germanic_count:
            return "Roman"
        elif germanic_count > aedui_control + arverni_count + belgic_count + roman_count:
            return "Germanic"
        else:
            return "No"

    def region_has_pieces(self, region, side, rest):

        count = 0

        if side == "Aedui":
            count = int(self.game.map[region].aedui_warband) + int(self.game.map[region].aedui_tribe) + int(self.game.map[region].aedui_citadel)

        if side == "Arverni":
            count = int(self.game.map[region].arverni_leader) + int(self.game.map[region].arverni_warband) + int(self.game.map[region].arverni_tribe) + int(self.game.map[region].arverni_citadel)

        if side == "Belgic":
            count = int(self.game.map[region].belgic_leader) + int(self.game.map[region].belgic_warband) + int(self.game.map[region].belgic_tribe) + int(self.game.map[region].belgic_citadel)

        if side == "Roman":
            count = int(self.game.map[region].roman_leader) + int(self.game.map[region].roman_auxilia) + int(self.game.map[region].roman_fort) + int(self.game.map[region].roman_legion) + int(self.game.map[region].roman_tribe)

        if side == "Germanic":
            count = int(self.game.map[region].aedui_warband) + int(self.game.map[region].aedui_tribe)

        if count > 0:
            return True
        else:
            return False

    def region_has_not_warbands(self, region, side, rest):

        count = 0

        if side == "Aedui":
            count = int(self.game.map[region].aedui_tribe) + int(self.game.map[region].aedui_citadel)

        if side == "Arverni":
            count = int(self.game.map[region].arverni_leader) + int(self.game.map[region].arverni_tribe) + int(self.game.map[region].arverni_citadel)

        if side == "Belgic":
            count = int(self.game.map[region].belgic_leader) + int(self.game.map[region].belgic_tribe) + int(self.game.map[region].belgic_citadel)

        if side == "Roman":
            count = int(self.game.map[region].roman_leader) + int(self.game.map[region].roman_fort) + int(self.game.map[region].roman_legion) + int(self.game.map[region].roman_tribe)

        if side == "Germanic":
            count = int(self.game.map[region].aedui_tribe)

        if count > 0:
            return True
        else:
            return False

    def do_status(self, rest):

        print "GMT: Falling Sky; Release", RELEASE
        print ""

        print "** Scenario Status Report **"
        print ""

        for key, country in self.game.map.items():
            print 'Name: %s' % country.name

            if country.control != "No Control":
                print 'Control: %s' % country.control

            if country.aedui_warband + country.aedui_warband_revealed > 0:
                print 'Aeduit Warband: %s' % str(country.aedui_warband + country.aedui_warband_revealed)

            if country.aedui_tribe > 0:
                print 'Aeduit Tribe: %s' % country.aedui_tribe

            if country.aedui_citadel > 0:
                print "Aedui Citadel: %s" % country.aedui_citadel

            if country.arverni_leader > 0:
                print "Arverni Leader: %s" % country.arverni_leader

            if country.arverni_warband + country.arverni_warband_revealed > 0:
                print "Arverni Warband: %s" % str(country.arverni_warband + country.arverni_warband_revealed)

            if country.arverni_tribe > 0:
                print "Arverni Tribe: %s" % country.arverni_tribe

            if country.arverni_citadel > 0:
                print "Arverni Citadel: %s" % country.arverni_citadel

            if country.belgic_leader > 0:
                print "Belgic Leader: %s" % country.belgic_leader

            if country.belgic_warband + country.belgic_warband_revealed > 0:
                print "Belgic Warband: %s" % str(country.belgic_warband + country.belgic_warband_revealed)

            if country.belgic_tribe > 0:
                print "Belgic Tribe: %s" % country.belgic_tribe

            if country.belgic_citadel > 0:
                print "Belgic Citadel: %s" % country.belgic_citadel

            if country.germanic_warband + country.germanic_warband_revealed > 0:
                print "Germanic Warband: %s" % str(country.germanic_warband + country.germanic_warband_revealed)

            if country.germanic_tribe > 0:
                print "Germanic Tribe: %s" % country.germanic_tribe

            if country.roman_leader > 0:
                print "Roman Leader: %s" % country.roman_leader

            if country.roman_auxilia + country.roman_auxilia_revealed > 0:
                print "Roman Auxilia: %s" % country.roman_auxilia + country.roman_auxilia_revealed

            if country.roman_fort > 0:
                print "Roman Fort: %s" % country.roman_fort

            if country.roman_legion > 0:
                print "Roman Legion: %s" % country.roman_legion

            if country.roman_tribe > 0:
                print "Roman Tribes: %s" % country.roman_tribe

            if country.dispersed_gathering != 0:
                print "Dispersed Gathering: %s" % country.dispersed_gathering

            print ""
            
    def do_aedui_flow(self, rest):
        bFlowEnded = False
        bAmbush = False
        bTrade = False
        card_has_swords = False

        print ""
        print "Bot Activated: Aedui"

        # 8.6.1 Is Aedui symbol 1st on the next card AND != 1st on current?

        card_now = int(self.game.currentcard[0:2])
        card_next = int(self.game.upcomingcard[0:2])
        if self.cardIndex[card_next][0][0:2] == 'Ae' and self.cardIndex[card_now][0][0:2] != 'Ae':
            if d6() < 5:
                # 8.6.1 + die roll of 1-4, so Pass
                print "ACTION: Move Aedui to Pass"
                sys.exit()
        for f in self.cardIndex[card_now]:
            if (f.startswith('Ae')):
                card_has_swords = (f[2:1] == 'S')

        # By sequence of play, Aedui can use the Event?
        bnoevent = False
        if (self.game.aedui_eligibility != 'Eligible Factions' or
                    self.game.arverni_eligibility == '1st Faction Event' or self.game.arverni_eligibility == '1st Faction Command Only' or
                    self.game.arverni_eligibility.startswith('2nd ') or
                    self.game.belgic_eligibility == '1st Faction Event' or self.game.belgic_eligibility == '1st Faction Command Only' or
                    self.game.belgic_eligibility.startswith('2nd ') or
                    self.game.roman_eligibility == '1st Faction Event' or self.game.roman_eligibility == '1st Faction Command Only' or
                    self.game.roman_eligibility.startswith('2nd ') or card_has_swords):
            # can't use the event
            bnoevent = True
        else:
            # can choose the event, see if the event has a Swords icon
            # ask the player if the event is effective
            #reply = self.ask_question("Aedui", QUESTION_YESNO, "event_ineffective", "Is the event Ineffective OR adds a Capability during final year?", "")
            reply = 'YES'
            if reply == 'YES':
                bnoevent = True
            elif reply == 'NO':
                self.do_aedui_flow_execute_event(self)

        if bnoevent:
            # continue with 8.6.2
            # if self.do_aedui_flow_862(self) is True:
            #    print "Battled !"

            #else:
            if self.do_aedui_flow_863(self) is True:
                print "Rally !"
            else:
                if self.do_aedui_flow_864(self) is True:
                    print "Raid !"
                else:
                    self.do_aedui_flow_865(self)

            if self.game.aedui_last_command is "BATTLE":
                if self.game.aedui_ambush is False:
                    special_complete = self.do_aedui_trade(self)

            if self.game.aedui_last_command is "RALLY":
                special_complete = self.do_aedui_trade(self)

            elif self.game.aedui_last_command is "RAID":
                special_complete = self.do_aedui_trade(self)

            elif self.game.aedui_last_command is "MARCH":
                special_complete = self.do_aedui_trade(self)

            if special_complete > 2:
                print "ACTION: Increase Aedui Resources by %s to %s" % (special_complete, self.game.aedui_resources + special_complete)
                self.game.aedui_resources += special_complete
                special_complete = True
            else:
                print "Trade Failed"
                special_complete = False

            if special_complete is False and self.game.aedui_last_command:
                special_complete = self.do_aedui_suborn(self)

    def do_aedui_flow_execute_event(self, rest):
        print "ACTION: Execute Event UNSHADED text. Check for Laurels on the Aedui icon."

    def do_aedui_flow_862(self, rest):

        print ""
        battled = False

        if self.game.aedui_resources > 0:
            battled = self.do_aedui_battle(self)
            return battled
        else:
            print "Battle check failed: Resources < 1"
            return False

    def do_aedui_flow_863(self, rest):          #Rally Check
        # TEST - following line forces the correct warband / resources for a Rally.
        # self.game.aedui_warband_available = 16
        # self.game.aedui_resources = 50

        print ""
        print "8.6.3 - Rally Check:"
        self.game.aedui_last_command = "RALLY"

        if self.game.aedui_resources > 0:
            if (20 - self.game.aedui_warband_available) < 5:
                print ""
                print "There are < 5 Aedui Warbands on map, there are %s on the map" % (20 - self.game.aedui_warband_available)
                print ""
                print "Checking available Rally regions"
                region_list = ""

                if self.do_aedui_flow_rally(region_list) is True:
                    return True
                else:
                    print "Rally check failed: Citadel, Ally, or 3+ Warbands could not be placed"
                    return False
            else:
                print "Rally check failed: There are => 5 Aedui Warbands on map, there are %s on the map" % (20 - self.game.aedui_warband_available)
                return False
        else:
            print "Rally check failed: Resources < 1"
            return False

    def do_aedui_flow_864(self, rest):  # Raid Check
        # TEST - following line forces a RAID aedui resources = 3
        # self.game.aedui_resources = 3

        print ""
        print "8.6.4 - Raid Check"
        self.game.aedui_last_command = "RAID"

        region_list = ""
        bfound_raid = False

        if self.game.aedui_resources < 4 or self.game.bforcedraid is True:
            for country in self.game.map:
                if self.game.map[country].devastated is 0:
                    if region_list.find(country) == -1:
                        if self.game.map[country].aedui_warband > 1 and (self.game.map[country].arverni_warband + self.game.map[country].arverni_warband_revealed) > 0:
                            total = self.game.map[country].aedui_warband
                            print "1) %s Aedui Warband(s) available at - %s - against Arverni" % (total, self.game.map[country].name)
                            bfound_raid = True

                        elif self.game.map[country].aedui_warband > 1 and (self.game.map[country].belgic_warband + self.game.map[country].belgic_warband_revealed) > 0:
                            total = self.game.map[country].aedui_warband
                            print "2) %s Aedui Warband(s) available at - %s - against Belgic" % (total, self.game.map[country].name)
                            bfound_raid = True

                        elif self.game.map[country].aedui_warband > 1 and (self.game.map[country].arverni_warband + self.game.map[country].arverni_warband_revealed) == 0 and (self.game.map[country].belgic_warband + self.game.map[country].belgic_warband_revealed) == 0:
                            total = self.game.map[country].aedui_warband
                            print "3) %s Aedui Warband(s) available at - %s - no faction" % (total, self.game.map[country].name)
                            bfound_raid = True

            print ""

            if bfound_raid is True:
                print "INSTRUCTIONS"
                print "Priority is indicated with 1-3 + Instruction"
                print "Reveal/Flip Warband. +1 Resource for each revealed"
                print "Pay NO resources for this command"
                print ""
                print "TODO - 3.3.3 Check for non-germanic enemy, but not romans"
                return 1
            else:
                print "Rally check failed: No valid regions found"
                print "Aedui Pass !!"
                return 2
        else:
            print "Raid check failed: Resources => 4"
            return 3

    def do_aedui_flow_865(self, rest):  # March Check
        print ""
        print "8.6.5 - March Check:"
        print "TODO Check if march in/out britannia 4.1.3"
        self.game.aedui_last_command = "MARCH"

        bmarched = False

        # Bullet Point 2
        for country in self.game.map:

            if bmarched == False:  #as we only want to move out of just one region
                high_count = 0
                high_region = ""
                moved = 0
                bcontrolchange = False

                # check that we are not moving last aedui warband (bullet point 1)
                while self.game.map[country].aedui_warband > 1 and moved < 3:

                    # check that moving will not change AEDUI control
                    if self.game.map[country].control is "Aedui":
                        self.game.map[country].aedui_warband -= 1  # -1 before the check
                        if self.control_change_check(self, country) is not "Aedui":
                            bcontrolchange = True  # We would change control, so we have to skip this region

                        self.game.map[country].aedui_warband += 1  # +1 after the check to reset to pre-check status

                    if bcontrolchange is False:
                        for loc in self.game.map[country].adjacent:
                            if self.game.map[loc].aedui_warband == 0:
                                count = self.game.map[loc].roman_tribe + self.game.map[loc].arverni_tribe + self.game.map[
                                    loc].belgic_tribe + self.game.map[loc].germanic_tribe
                                count += self.game.map[loc].arverni_citadel + self.game.map[loc].belgic_citadel
                                if count > 0 and count > high_count:
                                    high_region = loc

                        if len(high_region) > 0:
                            print "ACTION: Move 1 Aedui Warband from %s to %s - Adjacent Region with most Allies or Citadels" % (country, high_region)
                            self.game.map[country].aedui_warband -= 1
                            self.game.map[high_region].aedui_warband += 1
                            devastated = self.game.map[country].devastated
                            moved += 1
                            bmarched = True

                    if bmarched is False:
                        break

        if bmarched is True:
            if devastated > 0:
                self.game.aedui_resources -= 2
                print "ACTION: Reduce Aedui resource by 2 down to %s" % self.game.aedui_resources
            else:
                self.game.aedui_resources -= 1
            print "ACTION: Reduce Aedui resource by 1 down to %s" % self.game.aedui_resources

            print ""

        # Bullet Point 2
        lowest_required = 0
        lowest_adj_region = ""
        lowest_from_region = ""

        for country in self.game.map:
            if self.game.map[country].aedui_warband > 1:
                for loc in self.game.map[country].adjacent:
                    for num in range(1, self.game.map[country].aedui_warband - 1):
                        if self.game.map[loc].control != ("Aedui Control"):
                            aedui_control = int(self.game.map[loc].aedui_warband) + \
                                            int(self.game.map[loc].aedui_tribe) + \
                                            int(self.game.map[loc].aedui_citadel)

                            arverni_count = int(self.game.map[loc].arverni_leader) + \
                                            int(self.game.map[loc].arverni_warband) + int(
                                self.game.map[loc].arverni_tribe) + \
                                            int(self.game.map[loc].arverni_citadel)

                            belgic_count = int(self.game.map[loc].belgic_leader) + \
                                           int(self.game.map[loc].belgic_warband) + int(
                                self.game.map[loc].belgic_tribe) + \
                                           int(self.game.map[loc].belgic_citadel)

                            roman_count = int(self.game.map[loc].roman_leader) + \
                                          int(self.game.map[loc].roman_auxilia) + int(self.game.map[loc].roman_fort) + \
                                          int(self.game.map[loc].roman_legion) + int(self.game.map[loc].roman_tribe)

                            germanic_count = int(self.game.map[loc].aedui_warband) + int(self.game.map[loc].aedui_tribe)

                            if aedui_control + num > arverni_count + belgic_count + roman_count + germanic_count:
                                if num < lowest_required or lowest_required == 0:
                                    lowest_required = num
                                    lowest_adj_region = loc
                                    lowest_from_region = country
                                break

        if lowest_required > 0:
            print "ACTION: Move %s Aedui Warband from %s to %s - Adds Aedui Control with fewest Warbands possible" % (lowest_required, lowest_from_region, lowest_adj_region)
            if self.game.map[lowest_from_region].devastated > 0:
                self.game.aedui_resources -= 2
                print "ACTION: Reduce Aedui resource by 2 down to %s" % self.game.aedui_resources
            else:
                self.game.aedui_resources -= 1
                print "ACTION: Reduce Aedui resource by 1 down to %s" % self.game.aedui_resources

            print ""

            self.game.map[lowest_from_region].aedui_warband -= lowest_required
            self.game.map[lowest_adj_region].aedui_warband += lowest_required

        if bmarched is False and lowest_required is 0:
            print "March Unavailable - *Forced Raid*"
            self.game.bforcedraid = True

            nraid = self.do_aedui_flow_864(self)
            if nraid == 1:    #Raid occured
                print ""
            elif nraid == 2:  #Pass was returned
                print ""

        return bmarched

    def do_aedui_flow_rally(self, region_list):
        print ""

        brallied_citadel = False
        brallied_tribe = False
        brallied_warband = 0

        for country in self.game.map:
            if self.game.map[country].devastated == 0 and region_list.find(country) == -1:
                if self.game.aedui_citadel_available > 0:
                    if self.game.map[country].max_citadel > 0:
                        total_citadel_placed = int(self.game.map[country].aedui_citadel) + int(self.game.map[country].belgic_citadel) + int(self.game.map[country].arverni_citadel)
                        if total_citadel_placed < self.game.map[country].max_citadel:
                            if self.game.map[country].aedui_tribe > 0:
                                print "1) - Replace Aedui Ally / Tribe with Citadel at - %s" % self.game.map[country].name
                                brallied_citadel = True

                if self.game.aedui_tribe_available > 0:
                    if self.game.map[country].max_cities > 0 and self.game.map[country].control == "Aedui Control":
                        total_tribe_placed = int(self.game.map[country].aedui_tribe) + int(self.game.map[country].belgic_tribe) + int(self.game.map[country].arverni_tribe)
                        total_citadel_placed = int(self.game.map[country].aedui_citadel) + int(self.game.map[country].belgic_citadel) + int(self.game.map[country].arverni_citadel)
                        if total_tribe_placed + total_citadel_placed < self.game.map[country].max_cities:
                            print "2) - Place %s Ally / Tribe at - %s" % (self.game.map[country].max_cities - total_tribe_placed + total_citadel_placed, self.game.map[country].name)
                            brallied_tribe = True

                total = int(self.game.map[country].aedui_tribe) + int(self.game.map[country].aedui_citadel)
                if total > 0:
                    print "3) - Place up to %s Warband(s) at - %s" % (total, self.game.map[country].name)
                    brallied_warband += total

        print ""

        if brallied_citadel is True or brallied_tribe is True or brallied_warband >= 3:
            print "INSTRUCTIONS:"
            print "Priority is indicated with 1-3 + Instruction"
            print "Due to Resources, limit yourself non-player to maximum %s rally regions" % self.game.aedui_resources
            print "Remember to reduce Aedui resources, by the number of regions Rallied in"
            return True
        else:
            return False

    def do_aedui_battle(self, rest):
        print ""
        print "8.6.2 - Battle Check:"

        battled = False
        leader_list = []
        enemy_list = []
        loss_multiplier = 0

        for region in self.game.map:
            if self.region_has_not_warbands(region, "Arverni", self) and self.region_has_pieces(region, "Aedui", self):

                # quick loss check
                if self.game.map[region].arverni_citadel > 0:
                    loss_multiplier = 0.5
                else:
                    loss_multiplier = 1

                a_count = (self.game.map[region].aedui_warband + self.game.map[region].aedui_warband_revealed) * 0.5
                b_count = (self.game.map[region].roman_auxilia * 0.5)
                a_count += b_count
                a_count *= loss_multiplier
                arverni_losses = math.floor(a_count)

                a_count = (self.game.map[region].arverni_warband + self.game.map[region].arverni_warband_revealed) * 0.5
                b_count = self.game.map[region].arverni_leader
                b_count += (self.game.map[region].roman_auxilia * 0.5)
                a_count += b_count
                aedui_losses = math.floor(a_count)

                print "%s - aedui losses %s , arverni_losses %s" % (self.game.map[region].name, aedui_losses, arverni_losses)

                if arverni_losses > 0:
                    # battle
                    leader_list.append(region)

        print "Leader list"
        print len(leader_list)
        print leader_list

        for region in self.game.map:
            if self.region_has_pieces(region, "Arverni", self) and self.region_has_pieces(region, "Aedui", self):

                # quick loss check
                if self.game.map[region].arverni_citadel > 0:
                    loss_multiplier = 0.5
                else:
                    loss_multiplier = 1

                a_count = (self.game.map[region].aedui_warband + self.game.map[region].aedui_warband_revealed) * 0.5
                b_count = (self.game.map[region].roman_auxilia * 0.5)
                a_count += b_count
                a_count *= loss_multiplier
                arverni_losses = math.floor(a_count)

                a_count = (self.game.map[region].arverni_warband + self.game.map[region].aedui_warband_revealed) * 0.5
                b_count = self.game.map[region].arverni_leader
                b_count += (self.game.map[region].roman_auxilia * 0.5)
                a_count += b_count
                aedui_losses = math.floor(a_count)

                if aedui_losses <= arverni_losses and aedui_losses >= 1:
                    # battle location found
                    for item in leader_list:
                        if enemy_list.count(item) is False:
                            enemy_list.append(region)

        random.shuffle(leader_list)
        random.shuffle(enemy_list)

        enemy_list.extend(leader_list)

        print "Extended Battle Region list (ordered): %s " % enemy_list

        first_battle = True
        declare_ambush = False
        retreat_loc = ""

        for region in enemy_list:
            if self.game.map[region].devastated == 1:
                resource_needed = 2
            else:
                resource_needed = 1

            if self.game.aedui_resources >= resource_needed:

                # Check if just Tribes / Citadels - need Warbands to retreat
                battled = True
                print "Step 1 - Battle in: %s " % self.game.map[region].name
                print "Step 1 - Target is Arverni"

                if declare_ambush is False:
                    print "Step 2 - Declare (Check) Retreat"
                    # Check to see if retreat is possible
                    # if Defender is Germanic - then never a retreat
                    # if only has tribe, citadel, for - then never a retreat
                    # must have warbands to attempt a retreat
                    if (self.game.map[region].arverni_warband + self.game.map[region].aedui_warband_revealed) == 1:
                        for loc in self.game.map[region].adjacent:
                            if self.game.map[loc].control == "Arverni":
                                retreat_loc == loc

                    if retreat_loc:  # chance to Ambush
                        if self.game.map[region].aedui_warband > self.game.map[region].arverni_warband:

                            # TODO 8.6.2 AMBUSH. Only if Arverni Retreat would lessen removals

                            # Check if counter attack would cause loss
                            a_count = (self.game.map[region].arverni_warband + self.game.map[region].aedui_warband_revealed) * 0.5
                            b_count = self.game.map[region].arverni_leader
                            b_count += (self.game.map[region].roman_auxilia * 0.5)
                            a_count += b_count
                            if math.floor(a_count) > 0:  # counter attack is possible
                                declare_ambush = True
                                first_battle = True


                if declare_ambush is False and retreat_loc:
                    loss_multiplier = 0.5
                elif self.game.map[region].arverni_citadel > 0:
                    loss_multiplier = 0.5
                else:
                    loss_multiplier = 1

                print "Step 3 - Attack"
                # Aedu is the attacker
                # Arverni is the defender

                # Defender is never against Caesar or Ambiorix - as they are neither Aedui
                a_count = (self.game.map[region].aedui_warband + self.game.map[region].aedui_warband_revealed) * 0.5
                print "A Loss Count: %s" % a_count

                b_count = (self.game.map[region].roman_auxilia * 0.5)
                print "B Loss Count: %s" % b_count

                a_count += b_count
                a_count *= loss_multiplier
                a_count = math.floor(a_count)

                print "Step 3 - Attack - Defender Arverni takes %s loses (Calc: %s %s, rounded down)" % (a_count, "A+B *", loss_multiplier)

                while a_count > 0:
                    print ""

                    if self.game.map[region].arverni_leader > 0 and a_count > 0:
                        foo = [1, 2, 3, 4, 5, 6]
                        roll = random.choice(foo)

                        print "Rolled %s for remove Leader: " % roll

                        if roll < 4:
                            print "ACTION: Remove 1 Arverni Leader from %s " % self.game.map[region].name
                            self.game.map[region].arverni_leader -= 1
                            self.game.arverni_leader_available += 1
                        else:
                            print "Leader is not removed - roll failed."

                        a_count -= 1

                    elif self.game.map[region].arverni_tribe > 0 and a_count > 0:
                        print "Remove 1 Arverni Tribe from %s " % self.game.map[region].name
                        self.game.map[region].arverni_tribe -= 1
                        self.game.arverni_tribe_available += 1
                        a_count -= 1

                    elif self.game.map[region].arverni_citadel > 0 and a_count > 0:
                        print "Remove 1 Arverni Citadel from %s " % self.game.map[region].name
                        self.game.map[region].arverni_citadel -= 1
                        self.game.arverni_citadel_available += 1
                        a_count -= 1

                    elif self.game.map[region].arverni_warband > 0:
                        print "ACTION: Remove 1 Arverni Warband from %s " % self.game.map[region].name
                        self.game.map[region].arverni_warband -= 1
                        self.game.arverni_warband_available += 1
                        a_count -= 1

                    elif self.game.map[region].arverni_warband_revealed > 0:
                        print "ACTION: Remove 1 'Revealed' Arverni Warband from %s " % self.game.map[region].name
                        self.game.map[region].arverni_warband_revealed -= 1
                        self.game.arverni_warband_available += 1
                        a_count -= 1

                print ""

                if retreat_loc:
                    print "Step 6 - Retreat - to %s" % self.game.map[retreat_loc].name

                    # We are Aedui ... so Roamns are NOT attacking Gauls
                    if self.game.map[region].arverni_leader > 0:
                        print "ACTION: Move Arverni Leader to %s" % self.game.map[retreat_loc].name
                        self.game.map[retreat_loc].arverni_leader += self.game.map[region].arverni_leader
                        self.game.map[region].arverni_leader = 0

                    if self.game.map[region].arverni_warbands > 0:
                        print "ACTION: Move Arverni Warbands to %s" % self.game.map[retreat_loc].name
                        self.game.map[retreat_loc].arverni_warbands += self.game.map[region].arverni_warbands
                        self.game.map[region].arverni_warbands = 0

                    if self.game.map[region].arverni_warbands_revealed > 0:
                        print "ACTION: Move Arverni Revealed Warbands to %s" % self.game.map[retreat_loc].name
                        self.game.map[retreat_loc].arverni_warbands_revealed += self.game.map[region].arverni_warbands_revealed
                        self.game.map[region].arverni_warbands_revealed = 0

                else:

                    if declare_ambush and first_battle:
                        print "Step 3 - Attack - Ambush"
                        first_battle = False  # As we are done with dealing with Ambush

                        if self.game.map[region].roman_leader == 1 and self.game.caesar == 1:
                            # Prepare a roll value
                            foo = [1, 2, 3, 4, 5, 6]
                            roll = random.choice(foo)
                            if roll >= 4:
                                counter_roll_needed = True
                            else:
                                counter_roll_needed = False
                        else:
                            counter_roll_needed = True

                    else:
                        counter_roll_needed = True


                    print "Step 4 - Counterattack"

                    # Aedu is the Defender
                    # Arverni is the Attacker

                    # Defender is never against Caesar or Ambiorix - as they are neither Aedui
                    a_count = (self.game.map[region].arverni_warband + self.game.map[region].arverni_warband_revealed) * 0.5
                    print "A Loss Count: %s" % a_count

                    b_count = self.game.map[region].arverni_leader
                    b_count += (self.game.map[region].roman_auxilia * 0.5)
                    print "B Loss Count: %s" % b_count

                    a_count += b_count
                    a_count = math.floor(a_count)

                    print "Step 4 - Defender Aedui takes %s loses (Calc: %s, rounded down)" % (a_count, "A+B")

                    while a_count > 0:

                        if self.game.map[region].aedui_warband_revealed > 0:
                            print "ACTION: Remove 1 Aedui 'Revealed' Warband from %s " % self.game.map[region].name
                            self.game.map[region].aedui_warband_revealed -= 1
                            self.game.aedui_warband_available += 1
                            a_count -= 1

                        elif self.game.map[region].aedui_warband > 0:
                            print "ACTION: Remove 1 Aedui Warband from %s " % self.game.map[region].name
                            self.game.map[region].aedui_warband -= 1
                            self.game.aedui_warband_available += 1
                            a_count -= 1

                        elif self.game.map[region].aedui_tribe > 0 and a_count > 0:
                            print "Remove 1 Aedui Tribe from %s " % self.game.map[region].name
                            self.game.map[region].aedui_tribe -= 1
                            self.game.aedui_tribe_available += 1
                            a_count -= 1

                        elif self.game.map[region].aedui_citadel > 0 and a_count > 0:

                            foo = [1, 2, 3, 4, 5, 6]
                            roll = random.choice(foo)

                            if counter_roll_needed:
                                print "Loss Remove roll: %s" % roll

                            if counter_roll_needed is False or roll <= 3:
                                print "Remove 1 Aedui Citadel from %s " % self.game.map[region].name
                                self.game.map[region].aedui_citadel -= 1
                                self.game.aedui_citadel_available += 1
                                a_count -= 1

                        print ""

                    print "Step 5 - All Attacking and Defending survivors flip to Revealed"

                    self.game.map[region].aedui_warband_revealed += self.game.map[region].aedui_warband
                    self.game.map[region].aedui_warband = 0

                    print "ACTION: %s should have %s Aedui Warbands Revealed and %s Aedui Warbands Hidden" % (self.game.map[region].name, self.game.map[region].aedui_warband_revealed, self.game.map[region].aedui_warband)

                    self.game.map[region].arverni_warband_revealed += self.game.map[region].arverni_warband
                    self.game.map[region].arverni_warband = 0

                    print "ACTION: %s should have %s Arverni Warbands Revealed and %s Arverni Warbands Hidden" % (self.game.map[region].name, self.game.map[region].arverni_warband_revealed, self.game.map[region].arverni_warband)

                    if self.game.map[region].devastated == 1:
                        self.game.aedui_resources -= 2
                        print "ACTION: Reduce Aedui resource by 2 down to %s" % self.game.aedui_resources
                    else:
                        self.game.aedui_resources -= 1
                        print "ACTION: Reduce Aedui resource by 1 down to %s" % self.game.aedui_resources


        if battled:
            self.game.aedui_last_command = "BATTLE"
            self.game.aedui_ambush = declare_ambush

        else:
            print "Battle check failed: No valid regions"

        return battled


    def do_aedui_trade(self, rest):
        print "4.4.1 - Special Activity - TRADE"

        # Test - uncomment to force trade.
        # self.game.aedui_resources = 9

        checked = []
        inc_resource = 0

        if self.game.aedui_resources < 10 or self.game.aedui_resources + self.game.roman_resources < 20:

            paths = []
            match = False

            for region in self.game.map:

                currentpath = self.do_aedui_find_all_supply_paths(region, "", [])
                if currentpath:
                    currentpath.sort()

                    for p in paths:
                        if currentpath == p:
                            match = True

                    if match == False:
                        paths.append(currentpath)


            for region in paths:
                for loc in region:
                    if loc not in checked:
                        checked.append(loc)

                        # we presume that romans will always agree.. TODO change this
                        inc_resource += 2 * (self.game.map[loc].aedui_tribe + self.game.map[loc].aedui_citadel)

                        if self.game.map[loc].control == "Aedui Control":
                            inc_resource += 2 * self.game.map[loc].roman_tribe
                            if self.game.map[loc].max_cities > (self.game.map[loc].aedui_tribe + self.game.map[loc].aedui_citadel + self.game.map[loc].arverni_tribe + self.game.map[loc].arverni_citadel + self.game.map[loc].belgic_tribe + self.game.map[loc].belgic_citadel + self.game.map[loc].germanic_tribe + self.game.map[loc].roman_fort + self.game.map[loc].roman_tribe):
                                inc_resource += 2 * (self.game.map[loc].max_cities - (self.game.map[loc].aedui_tribe + self.game.map[loc].aedui_citadel + self.game.map[loc].arverni_tribe + self.game.map[loc].arverni_citadel + self.game.map[loc].belgic_tribe + self.game.map[loc].belgic_citadel + self.game.map[loc].germanic_tribe + self.game.map[loc].roman_fort + self.game.map[loc].roman_tribe))

        return inc_resource

    def do_aedui_find_all_supply_paths(self, region, ask, path):

        current_path = path
        targets = ['HEL', 'SEQ', 'UBI']

        for end_target in targets:
            if end_target == region:

                control = self.game.map[region].control

                if control == "No Control":
                    supplycontrol = True
                if control == "Roman Control":
                    supplycontrol = True
                if control == "Aedui Control":
                    supplycontrol = True
                if control == "Arverni Control":
                    supplycontrol = False
                if control == "Belgic Control":
                    supplycontrol = False
                if control == "German Control":
                    supplycontrol = False

                if supplycontrol == True:
                    current_path.append(end_target)

                return current_path

        control = self.game.map[region].control

        if control == "No Control":
            supplycontrol = True
        if control == "Roman Control":
            supplycontrol = True
        if control == "Aedui Control":
            supplycontrol = True
        if control == "Arverni Control":
            supplycontrol = False
        if control == "Belgic Control":
            supplycontrol = False
        if control == "German Control":
            supplycontrol = False

        if supplycontrol == True:
            current_path.append(region)
            for adj in self.game.map[region].adjacent:
                have_checked = False
                for check_already in current_path:
                    if check_already == adj:
                        have_checked = True
                        break

                if have_checked == False:
                    result = self.do_aedui_find_all_supply_paths(adj, ask, current_path)

            return current_path



    def do_aedui_find_all_supply_paths2(self, region, ask, path):
        contains = False
        is_target = False
        supplycontrol = False
        control = ""
        targets = ['HEL', 'SEQ', 'UBI']
        key = region.key

        for loc in targets:
            if loc == key:
                is_target = True

        control = str(region.control)

        if path:
            mypath = path
            mypath.append(key)
        else:
            path = []
            mypath = []

        #mypath = slice(path)


        if is_target:
            return mypath
        else:
            paths = []
            for adj in region.adjacent:
                for place in mypath:
                    if place == adj:
                        contains = True
                        break
                    else:
                        contains = False

                if contains == False:
                    adjzone = self.game.map[adj]
                    #control = str(adjzone.control)

                    if control == "No Control":
                        supplycontrol = True
                        #break
                    if control == "Roman Control":
                        supplycontrol = True
                        #break
                    if control == "Aedui Control":
                        supplycontrol = True
                        #break
                    if control == "Arverni Control":
                        supplycontrol = False
                        #break
                    if control == "Belgic Control":
                        supplycontrol = False
                        #break

                    if supplycontrol:
                        result = self.do_aedui_find_all_supply_paths(self.game.map[adj], "", mypath)
                        # result = findAllSupplyPaths(getZone(adj), ask, mypath);
                        if result:
                            print path
                            path.append(result)



    def do_aedui_suborn(self, rest):
        print ""
        print "4.4.2 - Special Activity - SUBORN"
        subornplayed = False
        suborncount = 0
        regions = 0

        if self.capabilityactive(43, False) is True:
            regions = 2
        else:
            regions = 1

        for x in range(0, regions):
            for country in self.game.map:
                if self.game.map[country].max_cities > self.game.map[country].roman_tribe + self.game.map[country].arverni_tribe + self.game.map[country].belgic_tribe + self.game.map[country].aedui_tribe + self.game.map[country].germanic_tribe:
                    if self.game.map[country].arverni_warband > 0:
                        if self.game.aedui_tribe_available > 0 and self.game.aedui_resources > 2:
                            self.game.map[country].aedui_tribe += 1
                            self.game.aedui_tribe_available -= 1
                            self.game.aedui_resources -= 1
                            print "ACTION: Place 1 Aedui Tribe / Ally from Available in %s" % self.game.map[country].name
                            print "ACTION: Reduce Aedui resource by 1 down to %s" % self.game.aedui_resources
                            suborncount += 1
                            subornplayed = True
                        else:
                            if self.game.aedui_resources > 2:
                                # calc side with greatest allies + citadels
                                averni_total = self.game.map[country].arverni_tribe + self.game.map[country].arverni_citadel
                                belgic_total = self.game.map[country].belgic_tribe + self.game.map[country].belgic_citadel
                                germanic_total = self.game.map[country].germanic_tribe
                                roman_total = self.game.map[country].roman_tribe

                                if averni_total > belgic_total and averni_total > germanic_total and averni_total > roman_total:
                                    if self.game.map[country].arverni_tribe > 0:
                                        self.game.map[country].arverni_tribe -= 1
                                        self.game.arverni_tribe_available += 1
                                        self.game.aedui_resources -= 1
                                        print "ACTION: Remove 1 Averni Tribe / Ally from %s to Available" % self.game.map[country].name
                                        print "ACTION: Reduce Aedui resource by 1 down to %s" % self.game.aedui_resources
                                        suborncount += 1
                                        subornplayed = True

                                if belgic_total > averni_total and belgic_total > germanic_total and belgic_total > roman_total:
                                    if self.game.map[country].belgic_tribe > 0:
                                        self.game.map[country].belgic_tribe -= 1
                                        self.game.belgic_tribe_available += 1
                                        self.game.aedui_resources -= 1
                                        print "ACTION: Remove 1 Belgic Tribe / Ally from %s to Available" % self.game.map[country].name
                                        print "ACTION: Reduce Aedui resource by 1 down to %s" % self.game.aedui_resources
                                        suborncount += 1
                                        subornplayed = True

                                if germanic_total > averni_total and germanic_total > belgic_total and germanic_total > roman_total:
                                    if self.game.map[country].germanic_tribe > 0:
                                        self.game.map[country].germanic_tribe -= 1
                                        self.game.germanic_tribe_available += 1
                                        self.game.aedui_resources -= 1
                                        print "ACTION: Remove 1 Germanic Tribe / Ally from %s to Available" % self.game.map[country].name
                                        print "ACTION: Reduce Aedui resource by 1 down to %s" % self.game.aedui_resources
                                        suborncount += 1
                                        subornplayed = True

                                if roman_total > averni_total and roman_total > belgic_total and roman_total > germanic_total:
                                    if self.game.map[country].roman_tribe > 0:
                                        self.game.map[country].roman_tribe -= 1
                                        self.game.roman_tribe_available += 1
                                        self.game.aedui_resources -= 1
                                        print "ACTION: Remove 1 Roman Tribe / Ally from %s to Available" % self.game.map[country].name
                                        print "ACTION: Reduce Aedui resource by 1 down to %s" % self.game.aedui_resources
                                        suborncount += 1
                                        subornplayed = True
                            else:
                                print "Not enough Aedui resources to 'place Aedui Ally' / 'remove Enemy pieces', min. 2 resources required"

                            while self.game.aedui_warband_available > 0 and suborncount <= 3 and self.game.aedui_resources > 0:
                                self.game.map[country].arverni_warband += 1
                                self.game.aedui_warband_available -= 1
                                self.game.aedui_resources -= 1
                                suborncount += 1
                                subornplayed = True
                                print "ACTION: Place 1 Aedui Warband from Available in %s" % self.game.map[country].name
                                print "ACTION: Reduce Aedui resource by 1 down to %s" % self.game.aedui_resources

                if subornplayed is True:
                    break

        if subornplayed is False:
            print "Suborn failed - No Special Ability"
        return False


def main():
    args = len(sys.argv)
    if (args < 2 or args > 4):
        print "Invalid number of arguments (", args, "): ", str(sys.argv)
        sys.exit(-1)

    global inputdata
    global isvassal
    global answer

    isvassal = False
    answer = None

    # path to JSON or data file
    fileparam = sys.argv[1]

    # Is this from VASSAL or command line?
    isvassal = ((sys.argv[2]).upper() == "TRUE")

    # load the input file, VASSAL JSON or our gamedata JSON
    file = open(fileparam, 'r')
    inputdata = file.read()
    file.close()

    # write inputdata to vassal-raw
    #from os.path import expanduser
    #home = expanduser("~")
    #with open(home + "/vassal-raw.json", "w") as text_file:
    #    text_file.write(inputdata)

    #if answer is None:
    #    from os.path import expanduser
    #    home = expanduser("~")
    #    with open(home + "/Documents/Projects/COIN-FS/test/raw1.js", "w") as text_file:
    #        text_file.write("inputString = '" + inputdata.replace("'", "\\'") + "';")

    # JSON string with answer information from VASSAL, no argument given if this is not a reply run
    if (args > 3):
        answerparam = sys.argv[3]

        file = open(answerparam, 'r')
        answerdata = json.loads(file.read())
        file.close()

        answer = Answer()

        # iterate the answer list to convert to object attributes
        for item in answerdata:
            setattr(answer, item, answerdata[item])

        # Delete the gamedata file we no longer need
        os.remove(fileparam)

    # start the main program
    app = FY()

if __name__ == "__main__":
    main()