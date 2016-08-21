import cmd
import sys
import json
import string

RELEASE = "0.14082016x"
# test

class Region:
    app = None
    key = ""
    name = ""
    modname = ""
    control = ""
    pop = 0
    aedui_warband = 0
    aedui_tribe = 0
    aedui_citadel = 0
    arverni_leader = 0
    arverni_warband = 0
    arverni_tribe = 0
    arverni_citadel = 0
    belgic_leader = 0
    belgic_warband = 0
    belgic_tribe = 0
    belgic_citadel = 0
    germanic_warband = 0
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
        
        # find zone for region in inputdata
        for element, data in inputdata.items():
            if element == 'zones':
                for zone in data:
                    if zone['name'] == self.modname:
                        for piece in zone['pieces']:
                            # find the control piece
                            if piece['name'].endswith('Control)'):
                                self.control = piece['name'][piece['name'].find(' (')+2:-8] + ' Control'
                                self.pop += int(piece['name'][0:1])
                            if piece['name'] == 'Colony Added':
                                self.pop += 1
                            # count the aedui warbands
                            if piece['name'] == 'Aedui Warband':
                                self.aedui_warband += 1
                            # count the aedui tribes (allies)
                            if piece['name'] == 'Aedui Ally':
                                self.aedui_tribe += 1
                            # count the aedui citadels
                            if piece['name'] == 'Aedui Citadel':
                                self.aedui_citadel += 1
                            # Arverni leader
                            if piece['name'] == ' (Vercingetorix /) (Averni Successor)':
                                self.arverni_leader = 1
                            # count the arverni warbands
                            if piece['name'] == 'Averni Warband':
                                self.arverni_warband += 1
                            # count the arverni tribes (allies)
                            if piece['name'] == 'Averni Ally':
                                self.arverni_tribe += 1
                            # count the arverni citadels
                            if piece['name'] == 'Averni Citadel':
                                self.arverni_citadel += 1
                            # Belgic leader
                            if piece['name'] == ' (Ambiorix /) (Belgic Successor)':
                                self.belgic_leader = 1
                            # count the belgic warbands
                            if piece['name'] == 'Belgic Warband':
                                self.belgic_warband += 1
                            # count the belgic tribes (allies)
                            if piece['name'] == 'Belgic Ally':
                                self.belgic_tribe += 1
                            # count the belgic citadels
                            if piece['name'] == 'Belgic Citadel':
                                self.belgic_citadel += 1
                            # count the germanic warbands
                            if piece['name'] == 'Germanic Warband':
                                self.germanic_warband += 1
                            # count the germanic tribes (allies)
                            if piece['name'] == 'Germanic Ally':
                                self.germanic_tribe += 1
                            # Roman leader
                            if piece['name'] == ' (Caesar /) (Roman Successor)':
                                self.roman_leader = 1
                            # count the roman auxilia
                            if piece['name'] == 'Roman Auxilia':
                                self.roman_auxilia += 1
                            # count the roman tribes (allies)
                            if piece['name'] == 'Roman Ally':
                                self.roman_tribe += 1
                            # count the roman fort
                            if piece['name'] == 'Roman Fort':
                                self.roman_fort += 1
                            # count the roman legion
                            if piece['name'] == 'Roman Legion':
                                self.roman_legion += 1
                            # count Dispersed tribes
                            if piece['name'].endswith(' (Dispersed)') or piece['name'].endswith(' (Gathering)'):
                                self.dispersed_gathering += 1
                                self.pop -= 1
                            # count Devastated
                            if piece['name'] == 'Devastated':
                                self.devastated += 1
                            # count number of tribes
                            for tribe in theapp.allySpaces:
                                piecename = piece['name']
                                sep = piecename.find(' (');
                                if sep > -1:
                                    piecename = piecename[:sep]
                                if piecename == tribe:
                                    self.max_cities += 1
                            # counter number of cities (citadel)
                            for tribe in theapp.citadelSpaces:
                                piecename = piece['name']
                                sep = piecename.find(' (');
                                if sep > -1:
                                    piecename = piecename[:sep]
                                if piecename == tribe:
                                    self.max_cities += 1

class FY(cmd.Cmd):
    winter_remaining = 0
    frost = 0
    winter = 0
    
    roman_senate = 2

    other_most_allies = 0
    off_map_legions = 0
    subdued_dispersed_allies = 0
    control_allies = 0
    
    colonies = 0

    aedui_resources = 0
    arverni_resources = 0
    belgic_resources = 0
    roman_resources = 0

    aedui_warband_available = 0
    aedui_tribe_available = 0
    aedui_citadel_available = 0
    arverni_leader_available = 0
    arverni_warband_available = 0
    arverni_tribe_available = 0
    arverni_citadel_available = 0
    belgic_leader_available = 0
    belgic_warband_available = 0
    belgic_tribe_available = 0
    belgic_citadel_available = 0
    germanic_warband_available = 0
    germanic_tribe_available = 0
    roman_leader_available = 0
    roman_auxilia_available = 0
    roman_fort_available = 0
    roman_legion_available = 0
    roman_tribe_available = 0

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
    print cardIndex
    map = {}
    cards = {}

    def __init__(self):
            cmd.Cmd.__init__(self)
            
            # load Regions from inputdata
            self.map["AED"] = Region(self, "AED", "Aedui")
            self.map["ARV"] = Region(self, "ARV", "Arverni")
            self.map["ATR"] = Region(self, "ATR", "Atrebates")
            self.map["BIT"] = Region(self, "BIT", "Bituriges")
            self.map["CAT"] = Region(self, "CAT", "Catuvellauni")
            self.map["CAR"] = Region(self, "CAR", "Carnutes")
            self.map["HEL"] = Region(self, "HEL", "Helvii")
            self.map["MAN"] = Region(self, "MAN", "Mandubii")
            self.map["MOR"] = Region(self, "MOR", "Morini")
            self.map["NER"] = Region(self, "NER", "Nervii")
            self.map["PIC"] = Region(self, "PIC", "Pictones")
            self.map["SEQ"] = Region(self, "SEQ", "Sequani")
            self.map["SUG"] = Region(self, "SUG", "Sugambri")
            self.map["TRE"] = Region(self, "TRE", "Treveri")
            self.map["UBI"] = Region(self, "UBI", "Ubii")
            self.map["VEN"] = Region(self, "VEN", "Veneti")
            
            # find number of resources
            for element, data in inputdata.items():
                if element == 'zones':
                    for zone in data:
                        for piece in zone['pieces']:
                            # Aedui Resources
                            if piece['name'].startswith('Aedui Resources ('):
                                self.aedui_resources = int(zone['name'])
                            # Arverni Resources
                            if piece['name'].startswith('Averni Resources ('):
                                self.arverni_resources = int(zone['name'])
                            # Belgic Resources
                            if piece['name'].startswith('Belgic Resources ('):
                                self.belgic_resources = int(zone['name'])
                            # Roman Resources
                            if piece['name'].startswith('Roman Resources ('):
                                self.roman_resources = int(zone['name'])
            
            # units available, cards
            self.arverni_leader_available = 1
            self.belgic_leader_available = 1
            self.roman_leader_available = 1
            for element, data in inputdata.items():
                if element == 'zones':
                    for zone in data:
                        if zone['name'] == 'Aedui Available Forces':
                            for piece in zone['pieces']:
                                if piece['name'] == 'Aedui Warband':
                                    self.aedui_warband_available += 1
                                if piece['name'] == 'Aedui Ally (Occupied)' or piece['name'] == 'Aedui Citadel (Ally)':
                                    self.aedui_tribe_available += 1
                                if piece['name'] == 'Aedui Citadel (Occupied)':
                                    self.aedui_citadel_available += 1
                        if zone['name'] == 'Arverni Available Forces':
                            for piece in zone['pieces']:
                                if piece['name'] == 'Arverni Warband':
                                    self.arverni_warband_available += 1
                                if piece['name'] == 'Arverni Ally (Occupied)' or piece['name'] == 'Arverni Citadel (Ally)':
                                    self.arverni_tribe_available += 1
                                if piece['name'] == 'Arverni Citadel (Occupied)':
                                    self.arverni_citadel_available += 1
                        if zone['name'] == 'Belgic Available Forces':
                            for piece in zone['pieces']:
                                if piece['name'] == 'Belgic Warband':
                                    self.belgic_warband_available += 1
                                if piece['name'] == 'Belgic Ally (Occupied)' or piece['name'] == 'Belgic Citadel (Ally)':
                                    self.belgic_tribe_available += 1
                                if piece['name'] == 'Belgic Citadel (Occupied)':
                                    self.belgic_citadel_available += 1
                        if zone['name'] == 'Germanic Available Forces':
                            for piece in zone['pieces']:
                                if piece['name'] == 'Germanic Warband':
                                    self.germanic_warband_available += 1
                                if piece['name'] == 'Germanic Ally (Occupied)':
                                    self.germanic_tribe_available += 1
                        if zone['name'] == 'Roman Available Forces':
                            for piece in zone['pieces']:
                                if piece['name'] == 'Roman Auxilia':
                                    self.roman_auxilia_available += 1
                                if piece['name'] == 'Roman Fort':
                                    self.roman_fort_available += 1
                                if piece['name'] == 'Roman Ally (Occupied)':
                                    self.roman_tribe_available += 1
                                if piece['name'] == 'Roman Legion':
                                    self.roman_legion_available += 1
                        # check for Winter or Frost
                        if zone['name'] == 'Upcoming':
                            for piece in zone['pieces']:
                                if piece['name'].endswith(' - Winter'):
                                    self.frost = 1
                        if zone['name'] == 'Current':
                            for piece in zone['pieces']:
                                if piece['name'].endswith(' - Winter'):
                                    self.winter = 1
                        # check for leaders on the map, colonies on map
                        for piece in zone['pieces']:
                            if piece['name'] == 'Ambiorix' or piece['name'] == 'Belgic Successor':
                                self.belgic_leader_available = 0
                            if piece['name'] == 'Vercingetorix' or piece['name'] == 'Arverni Successor':
                                self.arverni_leader_available = 0
                            if piece['name'] == 'Caesar' or piece['name'] == 'Roman Successor':
                                self.roman_leader_available = 0
                            if piece['name'] == 'Colony Added':
                                self.colonies += 1
                        
            # find other_most_allies
            aedui_score = 8 - self.aedui_tribe_available - self.aedui_citadel_available
            arverni_score = 13 - self.arverni_tribe_available - self.arverni_citadel_available
            belgic_score = 11 - self.belgic_tribe_available - self.belgic_citadel_available
            germanic_score = 6 - self.germanic_tribe_available
            roman_score = 6 - self.roman_tribe_available
            self.other_most_allies = max(arverni_score, belgic_score, germanic_score, roman_score)
            
            # Roman Senate, Legions
            for element, data in inputdata.items():
                if element == 'zones':
                    for zone in data:
                        if zone['name'] == 'Senate - Uproar':
                            for piece in zone['pieces']:
                                if piece['name'] == 'Roman Senate':
                                    self.roman_senate = 1
                        if zone['name'] == 'Senate - Intrigue':
                            for piece in zone['pieces']:
                                if piece['name'] == 'Roman Senate':
                                    self.roman_senate = 2
                        if zone['name'] == 'Senate - Adulation':
                            for piece in zone['pieces']:
                                if piece['name'] == 'Roman Senate':
                                    self.roman_senate = 3
                        if zone['name'] == 'Legions':
                            for piece in zone['pieces']:
                                if piece['name'] == 'Roman Legion':
                                    self.off_map_legions += 1
            
            # Roman Victory
            cities = len(self.allySpaces) + len(self.citadelSpaces) + self.colonies
            self.subdued_dispersed_allies = cities - arverni_score - belgic_score - germanic_score - aedui_score
            
            # Belgic Victory
            self.control_allies = belgic_score
            for key, region in self.map.items():
                if region.control == 'Belgic Control':
                    self.control_allies += region.pop
            
            # Winter cards left in Deck
            self.winter_remaining = inputdata['winter']

            # Which bot to activate?
            if inputdata['action'] == 'Aedui':
                self.do_aedui_flow('')
            
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

                print "TEST REMOVE FOLLOWING LINE"
                self.aedui_warband_available = 16
                if (20 - self.aedui_warband_available) < 5:
                    print ""
                    print "Aedui Warbands on map < 5 with only %s on the map" % (20 - self.aedui_warband_available)
                    print ""
                    print "Checking to see if a Rally is available"

                    if self.aedui_rally() == True:
                        print self.bRally
                        place = raw_input("Would Rally place Citadel, Ally, 3x pieces + available resources [Y/N]: ")
                        if place.upper() == "Y":
                            self.bRally = True

                        while True:
                            print self.bRally
                            select = raw_input("Update info where required. Use - 'map' 'aedui' 'available' OR 'QUIT': ")
                            if select.strip().upper() == "QUIT":
                                break
                            else:
                                if select.upper() == "MAP":
                                    self.do_map(self)
                                elif select.upper() == "AEDUI":
                                    self.do_aedui(self)
                                elif select.upper() == "AVAILABLE":
                                    self.do_available(self)
                                print ""

                        self.control_change_check()

                    else:
                        print "Rally Unavailable"

                else:
                    print "Rally check FAILED - %s Warbands already on the map" % (20 - self.aedui_warband_available)

                if self.bRally:
                    if raw_input("Play Special Event - Trade? [Y/N]").upper == "Y":
                        bTrade = True
                else:
                    if self.aedui_resources < 4:
                        print "Aedui has < 4 Resources with %s " % self.aedui_resources
                        self.aedui_raid()
                        ## if no Raid - then PASS

                        if raw_input("Play Special Event - Trade? [Y/N]").upper == "Y":
                            bTrade = True

                    else:
                        print "Aedui has > 4 Resources with %s" % self.aedui_resources
                        self.aedui_march()

                        if raw_input("Play Special Event - Trade? [Y/N]").upper == "Y":
                            bTrade = True

                        ##if none or Frost then raid
                        self.aedui_raid()
                        if raw_input("Play Special Event - Trade? [Y/N]").upper == "Y":
                            bTrade = True

        if bAmbush == True:
            self.aedui_ambush()

        if bTrade == True or bNoAmbush:
            self.aedui_trade

        if bNoTrade:
            self.aedui_Suborn

    def aedui_battle(self):
        bHalfLoss = False

        print ""
        print "BATTLE"

        battle_region = raw_input("Enter region code for Battle: ").upper()
        self.aedui_resources -= 1  # -2 resource if region is devastated

        battle_defender = raw_input("Enter defender code [ARV]erni [BEL]gae [GER]manic [ROM]ans : ")

        if battle_defender == "ARV":
            if self.map[battle_region].arverni_citadel > 0:
                bHalfLoss = True

        elif battle_defender == "BEL":
            if self.map[battle_region].belgic_citadel > 0:
                bHalfLoss = True

        elif battle_defender == "GER":
            bHalfLoss = False

        elif battle_defender == "ROM":
            if self.map[battle_region].roman_fort > 0:
                bHalfLoss = True

        # Defender is never against Caesar or Ambiorix - as they are neither Aedui

        a_count = self.map[battle_region].aedui_warband * 0.5
        a_count += self.map[battle_region].aedui_leader

        if bHalfLoss == True:
            a_count = a_count / 2

        print "Attack round - Losses for %s are %s" % (battle_defender, a_count)
        print "Remove in order Leaders, Allied Tribes, Citadels, Legions"
        self.do_map(self)

        print ""
        print "Counterattack"

        a_count = 0

        if battle_defender == "ARV":
            a_count = self.map[battle_region].arverni_warband * 0.5
            a_count += self.map[battle_region].arverni_leader

        elif battle_defender == "BEL":
            a_count = self.map[battle_region].belgic_warband * 0.5
            a_count += self.map[battle_region].belgic_leader

        elif battle_defender == "GER":
            a_count = self.map[battle_region].germanic_warband * 0.5

        elif battle_defender == "ROM":
            a_count = self.map[battle_region].roman_legion
            a_count += self.map[battle_region].roman_leader

        print "Counter Attack round - Losses for Aedui are %s" % a_count
        print "Remove in order Leaders, Allied Tribes, Citadels, Legions"
        self.do_map(self)


    def aedui_rally(self):
        print ""
        print "***RALLY CHECK***"
        print "Priority is indicated with n) - Instruction"
        print ""

        bfound_rally = False

        for country in self.map:
            if self.map[country].devastated == 0:
                if self.aedui_citadel_available > 0:
                    if self.map[country].max_citadel > 0:
                        total_citadel_placed = int(self.map[country].aedui_citadel) + int(self.map[country].belgic_citadel) + int(self.map[country].arverni_citadel)
                        if total_citadel_placed < self.map[country].max_citadel:
                            if self.map[country].aedui_tribe > 0:
                                print "1) - Replace Aedui Ally / Tribe with Citadel at - %s" % self.map[country].name
                                bfound_rally = True

                if self.aedui_tribe_available > 0:
                    if self.map[country].max_cities > 0 and self.map[country].control == "Aedui Control":
                        total_tribe_placed = int(self.map[country].aedui_tribe) + int(self.map[country].belgic_tribe) + int(self.map[country].arverni_tribe)
                        if total_tribe_placed < self.map[country].max_cities:
                            print "2) - Place Ally / Tribe at - %s" % self.map[country].name
                            bfound_rally = True

                total = int(self.map[country].aedui_tribe) + int(self.map[country].aedui_citadel)
                if total > 0:
                    print "3) - Place Warbands up to %s at - %s" % (total, self.map[country].name)
                    bfound_rally = True

        print ""
        print "Use 'map' command to update"
        print "Use 'aedui' command to update resources 1 per region"
        print "Use 'available' command to adjust available pieces"
        print ""

        return bfound_rally

    def aedui_raid(self):
        print ""
        print "RAID"
        # global bPass
        # if we are unable to raid


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
    
    file = open(sys.argv[1], 'r')
    jsonstr = file.read()
    file.close()
        
    global inputdata
    inputdata = json.loads(jsonstr)
    
    app = FY()


if __name__ == "__main__":
    main()