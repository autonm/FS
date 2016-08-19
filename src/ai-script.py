import cmd
import sys
import json
import string

RELEASE = "0.14082016x"


class Region:
    app = None
    key = ""
    name = ""
    modname = ""
    control = ""
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
                            # count the aedui warbands
                            if piece['name'] == 'Aedui Warband':
                                self.aedui_warband += 1
                            # count the aedui tribes (allies)
                            if piece['name'] == 'Aedui Ally':
                                self.aedui_tribe += 1
                            # count the aedui citadels
                            if piece['name'] == 'Aedui Citadel':
                                self.aedui_citadel += 1
                            # Averni leader
                            if piece['name'] == ' (Vercingetorix /) (Averni Successor)':
                                self.averni_leader = 1
                            # count the averni warbands
                            if piece['name'] == 'Averni Warband':
                                self.averni_warband += 1
                            # count the averni tribes (allies)
                            if piece['name'] == 'Averni Ally':
                                self.averni_tribe += 1
                            # count the averni citadels
                            if piece['name'] == 'Averni Citadel':
                                self.averni_citadel += 1
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
    scenario = 0
    campaign = 1
    currentyear = 0

    other_most_allies = 0

    roman_senate = 2

    off_map_legions = 0
    subdued_dispersed_allies = 0
    control_allies = 0

    aedui_resources = 0
    arverni_resources = 0
    belgic_resources = 0
    germanic_resources = 0
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
        "Suebi South"
        }
    citadelSpaces = {
        "Carnutes",
        "Bituriges",
        "Arverni",
        "Aedui",
        "Mandubii",
        "Sequani"        
        }
    map = {}
    cards = {}

    def __init__(self):
            cmd.Cmd.__init__(self)
            
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
            

            print ""
            print "** COMMAND LIST **"
            print "senate, ca, sda, off_map_legions          -"
            print "map, available                            -"
            print "aedui, arverni, belgic, germanic, roman   -"
            print "aedui_flow                                -"
            print ""
            
            for country in self.map:
                print country
                self.do_status(country)

    def do_status(self, rest):

        if rest == 'scenario':
            print ""
            print "** Scenario Status Report **"
            print "Current Year: %s" % self.currentyear
            return

        elif rest:
            print ""
            goodcountry = False
            possible = []
            for country in self.map:
                if rest.lower() == country.lower():
                    possible = []
                    possible.append(country)
                    break

                elif rest.lower() in country.lower():
                    possible.append(country)

            if len(possible) == 0:
                print "Unrecognized country."
                print ""

            elif len(possible) > 1:
                print "Be more specific", possible
                print ""

            else:
                goodcountry = possible[0]

            if goodcountry:
                print '*Location Status Report*'
                print 'Name: %s' % self.map[goodcountry].name
                print 'Control: %s' % self.map[goodcountry].control
                print "Aeduit Warband: %s" % self.map[goodcountry].aedui_warband
                print "Aedui Tribe: %s" % self.map[goodcountry].aedui_tribe
                print "Aedui Citadel: %s" % self.map[goodcountry].aedui_citadel
                print "Arverni Leader: %s" % self.map[goodcountry].arverni_leader
                print "Arverni Warband: %s" % self.map[goodcountry].arverni_warband
                print "Arverni Tribe: %s" % self.map[goodcountry].arverni_tribe
                print "Arverni Citadel: %s" % self.map[goodcountry].arverni_citadel
                print "Belgic Leader: %s" % self.map[goodcountry].belgic_leader
                print "Belgic Warband: %s" % self.map[goodcountry].belgic_warband
                print "Belgic Tribe: %s" % self.map[goodcountry].belgic_tribe
                print "Belgic Citadel: %s" % self.map[goodcountry].belgic_citadel
                print "Germanic Warband: %s" % self.map[goodcountry].germanic_warband
                print "Germanic Tribe: %s" % self.map[goodcountry].germanic_tribe
                print "Roman Leader: %s" % self.map[goodcountry].roman_leader
                print "Roman Auxilia: %s" % self.map[goodcountry].roman_auxilia
                print "Roman Fort: %s" % self.map[goodcountry].roman_fort
                print "Roman Legion: %s" % self.map[goodcountry].roman_legion
                print "Roman Tribes: %s" % self.map[goodcountry].roman_tribe
                print "Dispersed Gathering: %s" % self.map[goodcountry].dispersed_gathering
                print ""

                return
            else:
                return

        for country in self.map:
            print ""
            print 'Name %s' % self.map[country].name

            if self.map[country].control != "No Control":
                print 'Control: %s' % self.map[country].control

            if self.map[country].aedui_warband > 0:
                print 'Aeduit Warband: %s' % self.map[country].aedui_warband

            if self.map[country].aedui_tribe > 0:
                print 'Aeduit Tribe: %s' % self.map[country].aedui_tribe

            if self.map[country].aedui_citadel > 0:
                print "Aedui Citadel: %s" % self.map[country].aedui_citadel

            if self.map[country].arverni_leader > 0:
                print "Arverni Leader: %s" % self.map[country].arverni_leader

            if self.map[country].arverni_warband > 0:
                print "Arverni Warband: %s" % self.map[country].arverni_warband

            if self.map[country].arverni_tribe > 0:
                print "Arverni Tribe: %s" % self.map[country].arverni_tribe

            if self.map[country].arverni_citadel > 0:
                print "Arverni Citadel: %s" % self.map[country].arverni_citadel

            if self.map[country].belgic_leader > 0:
                print "Belgic Leader: %s" % self.map[country].belgic_leader

            if self.map[country].belgic_warband > 0:
                print "Belgic Warband: %s" % self.map[country].belgic_warband

            if self.map[country].belgic_tribe > 0:
                print "Belgic Tribe: %s" % self.map[country].belgic_tribe

            if self.map[country].belgic_citadel > 0:
                print "Belgic Citadel: %s" % self.map[country].belgic_citadel

            if self.map[country].germanic_warband > 0:
                print "Germanic Warband: %s" % self.map[country].germanic_warband

            if self.map[country].germanic_tribe > 0:
                print "Germanic Tribe: %s" % self.map[country].germanic_tribe

            if self.map[country].roman_leader > 0:
                print "Roman Leader: %s" % self.map[country].roman_leader

            if self.map[country].roman_auxilia > 0:
                print "Roman Auxilia: %s" % self.map[country].roman_auxilia

            if self.map[country].roman_fort > 0:
                print "Roman Fort: %s" % self.map[country].roman_fort

            if self.map[country].roman_legion > 0:
                print "Roman Legion: %s" % self.map[country].roman_legion

            if self.map[country].roman_tribe > 0:
                print "Roman Tribes: %s" % self.map[country].roman_tribe

            if self.map[country].dispersed_gathering != 0:
                print "Dispersed Gathering: %s" % self.map[country].dispersed_gathering

    def do_senate(self,rest):
        print ""
        self.roman_senate = raw_input("Roman Senate Level [" + str(self.roman_senate) + "] Change to [1-3] ? ")

    def do_off_map_legions(self,rest):
        print ""
        self.off_map_legions = raw_input("Off Map Legions [" + str(self.off_map_legions) + "] Change to [0-100] ? ")

    def do_sda(self,rest):
        print ""
        self.subdued_dispersed_allies = raw_input("Subdued Dispersed Allies [" + str(self.subdued_dispersed_allies) + "] Change to [0-100] ? ")

    def do_ca(self,rest):
        print ""
        self.control_allies = raw_input("Control Allies [" + str(self.control_allies) + "] Change to [0-100] ? ")

    def do_aedui(self,rest):
        print ""
        self.aedui_resources = raw_input("Aedui Resources [" + str(self.aedui_resources) + "] Change to [0-100] ? ")

    def do_arverni(self,rest):
        print ""
        self.arverni_resources = raw_input("Arverni Resources [" + str(self.arverni_resources) + "] Change to [0-100] ? ")

    def do_belgic(self,rest):
        print ""
        self.belgic_resources = raw_input("Belgic Resources [" + str(self.belgic_resources) + "] Change to [0-100] ? ")

    def do_germanic(self,rest):
        print ""
        self.germanic_resources = raw_input("Gemanic Resources [" + str(self.germanic_resources) + "] Change to [0-100] ? ")

    def do_roman(self,rest):
        print ""
        self.roman_resources = raw_input("Roman Resources [" + str(self.roman_resources) + "] Change to [0-100] ? ")

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

#    app.cmdloop()


if __name__ == "__main__":
    main()