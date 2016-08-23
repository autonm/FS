import cmd
import sys
import json
import string
import os
import tempfile
import itertools

RELEASE = "0.14082016xx"
# test

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
    roman_fort = 0
    roman_legion = 0
    roman_tribe = 0
    dispersed_gathering = 0
    devastated = 0
    max_cities = 0
    max_citadel = 0

    def __init__(self, theapp, thekey, thename):
        self.app = theapp
        self.key = thekey
        self.name = thename

        # name of this region in the json data        
        self.modname = theapp.mapIndex[thekey]

class Game:
    def __init__(self):
        self.map = {}
        self.cards = {}
        self.action = ""

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
    bRally = False

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
    allySpaces = {
        "Catuvalauni",
        "Morini",
        "Menapii",
        "Nervii",
        "Atrebates",
        "Bellovaci",
        "Remi",
        "Veneti",
        "Namnetes",
        "Aulerci",
        "Pictones",
        "Santones",
        "Cadurci",
        "Volcae",
        "Senones",
        "Lingones",
        "Helvetii",
        "Treveri",
        "Sugambri",
        "Suebi North",
        "Ubii",
        "Suebi South",
        "Helvii",
        "Eburones"
        }
    citadelSpaces = {
        "Carnutes",
        "Bituriges",
        "Arverni",
        "Aedui",
        "Mandubii",
        "Sequani"    
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

            self.game.action = "Aedui"

            # Which bot to activate?
            if self.game.action == 'Game State':
                self.do_status(self)

            if self.game.action == 'Aedui':
                # check answer key for continuation of flow
                if (answer is None):
                    self.do_aedui_flow(self)

    def parse_json(self, rest):
        global inputdata
        inputdata = json.loads(inputdata)

        # Start new Game
        self.game = Game()
        self.game.action = inputdata['action']

        # set up all Regions and load Regions data from inputdata
        self.game.map["AED"] = Region(self, "AED", "Aedui")
        self.load_region(self.game.map["AED"])
        self.game.map["ARV"] = Region(self, "ARV", "Arverni")
        self.load_region(self.game.map["ARV"])
        self.game.map["ATR"] = Region(self, "ATR", "Atrebates")
        self.load_region(self.game.map["ATR"])
        self.game.map["BIT"] = Region(self, "BIT", "Bituriges")
        self.load_region(self.game.map["BIT"])
        self.game.map["CAT"] = Region(self, "CAT", "Catuvellauni")
        self.load_region(self.game.map["CAT"])
        self.game.map["CAR"] = Region(self, "CAR", "Carnutes")
        self.load_region(self.game.map["CAR"])
        self.game.map["HEL"] = Region(self, "HEL", "Helvii")
        self.load_region(self.game.map["HEL"])
        self.game.map["MAN"] = Region(self, "MAN", "Mandubii")
        self.load_region(self.game.map["MAN"])
        self.game.map["MOR"] = Region(self, "MOR", "Morini")
        self.load_region(self.game.map["MOR"])
        self.game.map["NER"] = Region(self, "NER", "Nervii")
        self.load_region(self.game.map["NER"])
        self.game.map["PIC"] = Region(self, "PIC", "Pictones")
        self.load_region(self.game.map["PIC"])
        self.game.map["SEQ"] = Region(self, "SEQ", "Sequani")
        self.load_region(self.game.map["SEQ"])
        self.game.map["SUG"] = Region(self, "SUG", "Sugambri")
        self.load_region(self.game.map["SUG"])
        self.game.map["TRE"] = Region(self, "TRE", "Treveri")
        self.load_region(self.game.map["TRE"])
        self.game.map["UBI"] = Region(self, "UBI", "Ubii")
        self.load_region(self.game.map["UBI"])
        self.game.map["VEN"] = Region(self, "VEN", "Veneti")
        self.load_region(self.game.map["VEN"])

        # find number of resources
        for element, data in inputdata.items():
            if element == 'zones':
                for zone in data:
                    for piece in zone['pieces']:
                        # Aedui Resources
                        if piece['name'].startswith('Aedui Resources ('):
                            self.game.aedui_resources = int(zone['name'])
                        # Arverni Resources
                        if piece['name'].startswith('Averni Resources ('):
                            self.game.arverni_resources = int(zone['name'])
                        # Belgic Resources
                        if piece['name'].startswith('Belgic Resources ('):
                            self.game.belgic_resources = int(zone['name'])
                        # Roman Resources
                        if piece['name'].startswith('Roman Resources ('):
                            self.game.roman_resources = int(zone['name'])

        # units available, cards
        self.game.arverni_leader_available = 1
        self.game.belgic_leader_available = 1
        self.game.roman_leader_available = 1
        for element, data in inputdata.items():
            if element == 'zones':
                for zone in data:
                    if zone['name'] == 'Aedui Available Forces':
                        for piece in zone['pieces']:
                            if piece['name'] == 'Aedui Warband':
                                self.game.aedui_warband_available += 1
                            if piece['name'] == 'Aedui Ally (Occupied)' or piece['name'] == 'Aedui Citadel (Ally)':
                                self.game.aedui_tribe_available += 1
                            if piece['name'] == 'Aedui Citadel (Occupied)':
                                self.game.aedui_citadel_available += 1
                    if zone['name'] == 'Arverni Available Forces':
                        for piece in zone['pieces']:
                            if piece['name'] == 'Arverni Warband':
                                self.game.arverni_warband_available += 1
                            if piece['name'] == 'Arverni Ally (Occupied)' or piece['name'] == 'Arverni Citadel (Ally)':
                                self.game.arverni_tribe_available += 1
                            if piece['name'] == 'Arverni Citadel (Occupied)':
                                self.game.arverni_citadel_available += 1
                    if zone['name'] == 'Belgic Available Forces':
                        for piece in zone['pieces']:
                            if piece['name'] == 'Belgic Warband':
                                self.game.belgic_warband_available += 1
                            if piece['name'] == 'Belgic Ally (Occupied)' or piece['name'] == 'Belgic Citadel (Ally)':
                                self.game.belgic_tribe_available += 1
                            if piece['name'] == 'Belgic Citadel (Occupied)':
                                self.game.belgic_citadel_available += 1
                    if zone['name'] == 'Germanic Available Forces':
                        for piece in zone['pieces']:
                            if piece['name'] == 'Germanic Warband':
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
                    # check for leaders on the map, colonies on map
                    for piece in zone['pieces']:
                        if piece['name'] == 'Ambiorix' or piece['name'] == 'Belgic Successor':
                            self.game.belgic_leader_available = 0
                        if piece['name'] == 'Vercingetorix' or piece['name'] == 'Arverni Successor':
                            self.game.arverni_leader_available = 0
                        if piece['name'] == 'Caesar' or piece['name'] == 'Roman Successor':
                            self.game.roman_leader_available = 0
                        if piece['name'] == 'Colony Added':
                            self.game.colonies += 1

        # find other_most_allies
        aedui_score = 8 - self.game.aedui_tribe_available - self.game.aedui_citadel_available
        arverni_score = 13 - self.game.arverni_tribe_available - self.game.arverni_citadel_available
        belgic_score = 11 - self.game.belgic_tribe_available - self.game.belgic_citadel_available
        germanic_score = 6 - self.game.germanic_tribe_available
        roman_score = 6 - self.game.roman_tribe_available
        self.game.other_most_allies = max(arverni_score, belgic_score, germanic_score, roman_score)

        # Roman Senate, Legions
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
                    if zone['name'] == 'Legions':
                        for piece in zone['pieces']:
                            if piece['name'] == 'Roman Legion':
                                self.game.off_map_legions += 1

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
                            if piece['name'] == ' (Vercingetorix /) (Averni Successor)':
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
                            if piece['name'] == ' (Ambiorix /) (Belgic Successor)':
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
                            if piece['name'] == ' (Caesar /) (Roman Successor)':
                                region.roman_leader = 1
                            # count the roman auxilia
                            if piece['name'] == 'Roman Auxilia':
                                region.roman_auxilia += 1
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

    def as_gamedata(self, dct):
        print dct
        return dct

    def parse_gamedata(self, datafile):
        # Start new Game
        self.game = Game()

        # set up Regions, but do not load them yet
        self.game.map["AED"] = Region(self, "AED", "Aedui")
        self.game.map["ARV"] = Region(self, "ARV", "Arverni")
        self.game.map["ATR"] = Region(self, "ATR", "Atrebates")
        self.game.map["BIT"] = Region(self, "BIT", "Bituriges")
        self.game.map["CAT"] = Region(self, "CAT", "Catuvellauni")
        self.game.map["CAR"] = Region(self, "CAR", "Carnutes")
        self.game.map["HEL"] = Region(self, "HEL", "Helvii")
        self.game.map["MAN"] = Region(self, "MAN", "Mandubii")
        self.game.map["MOR"] = Region(self, "MOR", "Morini")
        self.game.map["NER"] = Region(self, "NER", "Nervii")
        self.game.map["PIC"] = Region(self, "PIC", "Pictones")
        self.game.map["SEQ"] = Region(self, "SEQ", "Sequani")
        self.game.map["SUG"] = Region(self, "SUG", "Sugambri")
        self.game.map["TRE"] = Region(self, "TRE", "Treveri")
        self.game.map["UBI"] = Region(self, "UBI", "Ubii")
        self.game.map["VEN"] = Region(self, "VEN", "Veneti")

        # parse the JSON to Python lists
        gamedata = json.loads(inputdata)

        # iterate the lists so we can convert them to object attributes
        for item in gamedata:
            if item == "map":
                # we need to treat map uniquely since it contains sub-lists
                for subitem in gamedata[item]:
                    for subprop in gamedata[item][subitem]:
                        setattr(self.game.map[subitem], subprop, gamedata[item][subitem][subprop])
            elif item == "cards":
                # we probably need to treat Cards uniquely too, but we don't have any yet
                a = 1  # TODO
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
            # Delete file somewhere when done? not here!
            #os.remove(filename)
            return temp.name

    def do_status(self, rest):

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

            if country.roman_auxilia > 0:
                print "Roman Auxilia: %s" % country.roman_auxilia

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

        print ""
        choice = raw_input("Is Aedui symbol 1st on the next card AND != 1st on current? [Y/N]: ").upper()
        if choice == "Y":
            roll = int(raw_input("Roll D6. 1-4 Pass, 5-6 Continue. Enter result: "))
            if roll <= 4:
                print "ACTION: Move Aedui to Pass"
                print ""
                return

        if bFlowEnded == False:
            print ""
            choice = raw_input("By sequence of play, Aedui can use the Event? [Y/N]: ").upper()
            if choice == "Y":
                print ""
                choice = raw_input("Is the event (1)INeffective OR (2)Adds a Capability during final year OR (3)Swords icon 'on Boar' (see 8.2.1) : ").upper()
                if choice == "N":
                    print ""
                    print "ACTION: Execute Event UNSHADED text. Check for Laurels on pig"
                    print ""
                    return

        if bFlowEnded == False:
            print ""
            choice = raw_input("Battle would force loss on Enemy Leader, Ally, Citadel or Legion? [Y/N]: ").upper()
            if choice == "Y":
                self.aedui_battle()
                if raw_input("Play Special Event - Ambush? [Y/N]").upper == "Y":
                    bAmbush = True
            else:

                print ""
                print "***CHECKING TO SEE IF RALLY IS POSSIBLE***"

                #print "TEST FOLLOWING LINE- forces aedui_warband_available = 16"
                #self.aedui_warband_available = 16

                if (20 - self.game.aedui_warband_available) < 5:
                    print ""
                    print "There are < 5 Aedui Warbands on map, there are %s on the map" % (20 - self.game.aedui_warband_available)
                    print "Aedui Resources: %s " % self.game.aedui_resources
                    print ""
                    print "Checking available Rally Points"
                    region_list = ""

                    if self.aedui_rally(region_list) == True:
                        place = raw_input("Would Rally place Citadel, Ally, 3x pieces + available resources [Y/N]: ")
                        if place.upper() == "Y":
                            self.bRally = True
                            region_list = ""
                        while True and place.upper() == "Y":
                            select = raw_input("Enter MAP to update Rally counts or QUIT: ")
                            if select.strip().upper() == "QUIT":
                                break
                            else:
                                if select.upper() == "MAP":
                                    region = raw_input("Enter 3 CHAR Region Code to Rally in: ").upper()
                                    region_list += region
                                    region_list += " "
                                    ac_count = int(raw_input("How many Aedui Citadel added to %s ? " % self.game.map[region].name))
                                    at_count = int(raw_input("How many Aedui Tribe added to %s ? " % self.game.map[region].name))
                                    aw_count = int(raw_input("How many Aedui Warband added to %s ? " % self.game.map[region].name))

                                    self.game.map[region].aedui_citadel += ac_count
                                    self.game.map[region].aedui_tribe += at_count
                                    self.game.map[region].aedui_warband += aw_count
                                    self.game.aedui_citadel_available -= ac_count
                                    self.game.aedui_tribe_available -= at_count
                                    self.game.aedui_warband_available -= aw_count
                                    self.game.aedui_resources -= 1
                                    print "Aedui Resources %s :" % self.game.aedui_resources

                                print ""
                                print "Checking Further Available Rally points"

                                if self.aedui_rally(region_list) == False and self.game.aedui_resources == 0:
                                    break

                    else:
                        print "Rally Unavailable"

                else:
                    print "RALLY check FAILED - %s Aedui Warbands already on the map" % (20 - self.game.aedui_warband_available)

                print ""
                if self.bRally:
                    if raw_input("Play Special Event - Trade? [Y/N]").upper == "Y":
                        bTrade = True
                else:
                    print ""
                    print "***CHECKING TO SEE IF RAID IS POSSIBLE"
                    # print "TEST FOLLOWING LINE- forces aedui resources = 3
                    self.game.aedui_resources = 3

                    region_list = ""

                    if self.aedui_raid(region_list) == True and self.game.aedui_resources < 4:
                        place = raw_input("Would Raid gain > 2 Resources Total [Y/N]: ")
                        if place.upper() == "Y":
                            region_list = ""
                        while True and place.upper() == "Y":
                            select = raw_input("Enter MAP to update Raid - with Aedui Revealed counts or QUIT: ")
                            if select.strip().upper() == "QUIT":
                                break
                            else:
                                if select.upper() == "MAP":
                                    region = raw_input("Enter 3 CHAR Region Code to Raid in: ").upper()
                                    region_list += region
                                    region_list += " "
                                    aw_count = int(raw_input("How many Aedui Warband(s) are Revealed in %s ? " % self.game.map[region].name))

                                    self.game.map[region].aedui_warband_revealed += aw_count
                                    self.game.aedui_resources -= aw_count
                                    print "Aedui Resources %s :" % self.game.aedui_resources

                                print ""
                                print "Checking Further Available Raid points"

                                if self.aedui_raid(region_list) == False and self.game.aedui_resources == 0:
                                    break

                        else:
                            print ""
                            print "RAID UNAVAILABLE"
                            bTrade = False
                            print "Pass !!"

                        print ""
                        if bTrade == True:
                            if raw_input("Play Special Event - Trade? [Y/N]").upper == "Y":
                                bTrade = True

                    else:
                        print "RAID check FAILED Aedui has > 3 Resources with %s" % self.game.aedui_resources
                        self.aedui_march()

                        if raw_input("Play Special Event - Trade? [Y/N]").upper == "Y":
                            bTrade = True

                        ##if none or Frost then raid
                        self.aedui_raid()
                        if raw_input("Play Special Event - Trade? [Y/N]").upper == "Y":
                            bTrade = True

        #if bAmbush == True:
        #    self.aedui_ambush()

        #if bTrade == True or bNoAmbush:
        #    self.aedui_trade

        #if bNoTrade:
        #    self.aedui_Suborn

    def aedui_rally(self, region_list):
        print ""
        print "***RALLY CHECK***"
        print "Priority is indicated with 1-3) + Instruction"
        print "Aedui Resources: %s " % self.game.aedui_resources
        print ""

        bfound_rally = False

        for country in self.game.map:
            if self.game.map[country].devastated == 0 and region_list.find(country) == -1:
                if self.game.aedui_citadel_available > 0:
                    if self.game.map[country].max_citadel > 0:
                        total_citadel_placed = int(self.game.map[country].aedui_citadel) + int(self.game.map[country].belgic_citadel) + int(self.game.map[country].arverni_citadel)
                        if total_citadel_placed < self.game.map[country].max_citadel:
                            if self.game.map[country].aedui_tribe > 0:
                                print "1) - Replace Aedui Ally / Tribe with Citadel at - %s" % self.game.map[country].name
                                bfound_rally = True

                if self.game.aedui_tribe_available > 0:
                    if self.game.map[country].max_cities > 0 and self.game.map[country].control == "Aedui Control":
                        total_tribe_placed = int(self.game.map[country].aedui_tribe) + int(self.game.map[country].belgic_tribe) + int(self.game.map[country].arverni_tribe)
                        total_citadel_placed = int(self.game.map[country].aedui_citadel) + int(self.game.map[country].belgic_citadel) + int(self.game.map[country].arverni_citadel)
                        if total_tribe_placed + total_citadel_placed < self.game.map[country].max_cities:
                            print "2) - Place %s Ally / Tribe at - %s" % (self.game.map[country].max_cities - total_tribe_placed + total_citadel_placed, self.game.map[country].name)
                            bfound_rally = True

                total = int(self.game.map[country].aedui_tribe) + int(self.game.map[country].aedui_citadel)
                if total > 0:
                    print "3) - Place up to %s Warband(s) at - %s" % (total, self.game.map[country].name)
                    bfound_rally = True

        print ""

        return bfound_rally

    def aedui_battle(self):
        bHalfLoss = False

        print ""
        print "BATTLE"

        battle_region = raw_input("Enter region code for Battle: ").upper()
        self.game.aedui_resources -= 1  # -2 resource if region is devastated

        battle_defender = raw_input("Enter defender code [ARV]erni [BEL]gae [GER]manic [ROM]ans : ")

        if battle_defender == "ARV":
            if self.game.map[battle_region].arverni_citadel > 0:
                bHalfLoss = True

        elif battle_defender == "BEL":
            if self.game.map[battle_region].belgic_citadel > 0:
                bHalfLoss = True

        elif battle_defender == "GER":
            bHalfLoss = False

        elif battle_defender == "ROM":
            if self.game.map[battle_region].roman_fort > 0:
                bHalfLoss = True

        # Defender is never against Caesar or Ambiorix - as they are neither Aedui

        a_count = self.game.map[battle_region].aedui_warband * 0.5
        a_count += self.game.map[battle_region].aedui_leader

        if bHalfLoss == True:
            a_count = a_count / 2

        print "Attack round - Losses for %s are %s" % (battle_defender, a_count)
        print "Remove in order Leaders, Allied Tribes, Citadels, Legions"
        self.do_map(self)

        print ""
        print "Counterattack"

        a_count = 0

        if battle_defender == "ARV":
            a_count = self.game.map[battle_region].arverni_warband * 0.5
            a_count += self.game.map[battle_region].arverni_leader

        elif battle_defender == "BEL":
            a_count = self.game.map[battle_region].belgic_warband * 0.5
            a_count += self.game.map[battle_region].belgic_leader

        elif battle_defender == "GER":
            a_count = self.game.map[battle_region].germanic_warband * 0.5

        elif battle_defender == "ROM":
            a_count = self.game.map[battle_region].roman_legion
            a_count += self.game.map[battle_region].roman_leader

        print "Counter Attack round - Losses for Aedui are %s" % a_count
        print "Remove in order Leaders, Allied Tribes, Citadels, Legions"
        self.do_map(self)

    def aedui_raid(self, region_list):
        print ""
        print "***RAID CHECK***"
        print "Priority 1) Arverni, 2) Belgic, 3) No Faction. "
        print " - Never Roman - never Last Hidden Warband - "
        print ""
        print "Raid locations are as follows"
        print ""

        bfound_raid = False

        for country in self.game.map:
            if country == "MAN":
                bfound_raid = False

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

        return bfound_raid

    def aedui_march(self):
        print ""
        print "MARCH"
        global bNoMarch
        ##if we are unable to march goes to Raid


    def aedui_ambush(self):
        print ""
        print "AMBUSH"
        global bNoAmbush


    def aedui_trade(self):
        print ""
        print "TRADE"
        global bNoTrade


    def aedui_suborn(self):
        print ""
        print "SUBORN"


def main():
    print "GMT: Falling Sky; Release", RELEASE

    args = len(sys.argv)
    if (args < 2 or args > 4):
        print "Invalid number of arguments"
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

    # JSON string with answer information from VASSAL, "{}" if running from VASSAL initially
    if (args > 3):
        answer = json.loads(sys.argv[3])
    file = open(fileparam, 'r')
    inputdata = file.read()
    file.close()

    app = FY()

    # TEST STUFF for return from q&a
    # outfile = app.write_gamedata(app)
    # print "before erase app:", app.game.action
    # app = None
    # print outfile
    # print app
    # answer = {}
    #
    # file = open(outfile, 'r')
    # inputdata = file.read()
    # file.close()
    #
    # print inputdata
    # app = FY()


if __name__ == "__main__":
    main()