import cmd
import sys
import json

RELEASE = "0.14082016x"


class Region:
    app = None
    name = ""
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

    def __init__(self, theapp, thename, thecontrol, theaedui_warband, theaedui_tribe, theaedui_citadel, thearverni_leader, thearverni_warband, thearverni_tribe, thearverni_citadel, thebelgic_leader, thebelgic_warband, thebelgic_tribe, thebelgic_citadel, thegermanic_warband, thegermanic_tribe, theroman_leader, theroman_fort, theroman_auxilia, theroman_legion, theroman_tribe, thedispersed_gathering, thedevastated, themax_cities, themax_citadel):
        self.app = theapp
        self.name = thename
        self.control = thecontrol
        self.aedui_warband = theaedui_warband
        self.aedui_tribe = theaedui_tribe
        self.aedui_citadel = theaedui_citadel
        self.arverni_leader = thearverni_leader
        self.arverni_warband = thearverni_warband
        self.arverni_tribe = thearverni_tribe
        self.arverni_citadel = thearverni_citadel
        self.belgic_leader = thebelgic_leader
        self.belgic_warband = thebelgic_warband
        self.belgic_tribe = thebelgic_tribe
        self.belgic_citadel = thebelgic_citadel
        self.germanic_warband = thegermanic_warband
        self.germanic_tribe = thegermanic_tribe
        self.roman_leader = theroman_leader
        self.roman_auxilia = theroman_auxilia
        self.roman_fort = theroman_fort
        self.roman_legion = theroman_legion
        self.roman_tribe = theroman_tribe
        self.dispersed_gathering = thedispersed_gathering
        self.devastated = thedevastated
        self.max_cities = themax_cities
        self.max_citadel = themax_citadel


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

    map = {}
    cards = {}

    def __init__(self, thescenario):
            cmd.Cmd.__init__(self)
            self.scenario = thescenario
            self.scenariosetup()
            self.map = {}
            self.mapsetup()

            print ""
            print "** COMMAND LIST **"
            print "senate, ca, sda, off_map_legions          -"
            print "map, available                            -"
            print "aedui, arverni, belgic, germanic, roman   -"
            print "aedui_flow                                -"
            self.prompt = "Command: "

    def postcmd(self, stop, line):
        if line == "quit":
            return True

    def help_quit(self):
        print "Quits game."

    def emptyline(self):
        print ""
        print 'Year: %s' % self.currentyear
        print 'Enter help for a list of commands.'

    def scenariosetup(self):
        print ""
        print 'Running Scenario Setup: %s' % self.scenario
        if self.scenario == 1:
            self.campaign = 1

        elif self.scenario == 2:
            self.campaign = 1
            self.yearfrom = 1234
            self.yearto = 5678
            self.currentyear = "53BC"

            self.other_most_allies = 7

            self.off_map_legions = 4
            self.subdued_dispersed_allies = 14
            self.control_allies = 15

            self.aedui_resources = 15
            self.arverni_resources = 10
            self.belgic_resources = 10
            self.germanic_resources = 0
            self.roman_resources = 20

            self.aedui_warband_available = 11
            self.aedui_tribe_available = 4
            self.aedui_citadel_available = 1
            self.arverni_leader_available = 0
            self.arverni_warband_available = 22
            self.arverni_tribe_available = 7
            self.arverni_citadel_available = 3
            self.belgic_leader_available = 0
            self.belgic_warband_available = 10
            self.belgic_tribe_available = 3
            self.belgic_citadel_available = 1
            self.germanic_warband_available = 6
            self.germanic_tribe_available = 3
            self.roman_leader_available = 0
            self.roman_auxilia_available = 8
            self.roman_fort_available = 3
            self.roman_legion_available = 4
            self.roman_tribe_available = 5

    def mapsetup(self):
        print ""
        print 'Running Map Setup: %s' % self.scenario
        if self.scenario == 1:
            self.scenario = 1

        elif self.scenario == 2:
            self.map["AED"] = Region(self, "Aedui", "Aedui Control", 3, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1)
            self.map["ARV"] = Region(self, "Arverni", "Arverni Control", 0, 0, 0, 1, 6, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1)
            self.map["ATR"] = Region(self, "Atrebates", "Belgic Control", 0, 0, 0, 0, 0, 0, 0, 0, 3, 2, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 3, 0)
            self.map["BIT"] = Region(self, "Bituriges", "Aedui Control", 3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1)
            self.map["CAT"] = Region(self, "Catuvellauni", "No Control", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0)
            self.map["GAR"] = Region(self, "Garnutes", "Arverni Control", 0, 0, 0, 0, 4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1)
            self.map["HEL"] = Region(self, "Helvii", "Roman Control", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 6, 4, 0, 0, 0, 1, 0)
            self.map["MAN"] = Region(self, "Mandubii", "No Control", 3, 1, 0, 0, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1)
            self.map["MOR"] = Region(self, "Morini", "Belgic Control", 0, 0, 0, 0, 0, 0, 0, 0, 4, 2, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 2, 0)
            self.map["NER"] = Region(self, "Nervii", "Belgic Control", 0, 0, 0, 0, 0, 0, 0, 1, 4, 2, 0, 1, 0, 0, 1, 2, 2, 0, 0, 0, 2, 0)
            self.map["PIC"] = Region(self, "Pictones", "No Control", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0)
            self.map["SEQ"] = Region(self, "Sequani", "No Control", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1)
            self.map["SUG"] = Region(self, "Sugambri", "German Control", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0)
            self.map["TRE"] = Region(self, "Treveri", "Belgic Control", 0, 0, 0, 0, 0, 0, 0, 0, 4, 1, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 1, 0)
            self.map["UBI"] = Region(self, "Ubii", "German Control", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1, 0, 0, 0, 0, 0, 0, 0, 2, 0)
            self.map["VEN"] = Region(self, "Veneti", "No Control", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 2, 0)

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

    def do_available(self, rest):
        print ""
        self.aedui_warband_available = raw_input("Aedui Warband Available [" + str(self.aedui_warband_available) + "] Change to [0-100] ? ")
        self.aedui_tribe_available = raw_input("Aedui Tribe Available [" + str(self.aedui_tribe_available) + "] Change to [0-100] ? ")
        self.aedui_citadel_available = raw_input("Aedui Citadel Available [" + str(self.aedui_citadel_available) + "] Change to [0-100] ? ")
        self.arverni_leader_available = raw_input("Arverni Leader Available [" + str(self.arverni_leader_available) + "] Change to [0-100] ? ")
        self.arverni_warband_available = raw_input("Roman Resources [" + str(self.arverni_warband_available) + "] Change to [0-100] ? ")
        self.arverni_tribe_available = raw_input("Arverni Warband Available [" + str(self.arverni_tribe_available) + "] Change to [0-100] ? ")
        self.arverni_citadel_available = raw_input("Arverni Citadel Available [" + str(self.arverni_citadel_available) + "] Change to [0-100] ? ")
        self.belgic_leader_available = raw_input("Belgic Leader Available [" + str(self.belgic_leader_available) + "] Change to [0-100] ? ")
        self.belgic_warband_available = raw_input("Belgic Warband Available [" + str(self.belgic_warband_available) + "] Change to [0-100] ? ")
        self.belgic_tribe_available = raw_input("Belgic Tribe Available [" + str(self.belgic_tribe_available) + "] Change to [0-100] ? ")
        self.belgic_citadel_available = raw_input("Belgic Citadel Available [" + str(self.belgic_citadel_available) + "] Change to [0-100] ? ")
        self.germanic_warband_available = raw_input("Germanic Warband Available [" + str(self.germanic_warband_available) + "] Change to [0-100] ? ")
        self.germanic_tribe_available = raw_input("Germanic Tribe Available [" + str(self.germanic_tribe_available) + "] Change to [0-100] ? ")
        self.roman_leader_available = raw_input("Roman Leader Available [" + str(self.roman_leader_available) + "] Change to [0-100] ? ")
        self.roman_auxilia_available = raw_input("Roman Auxilia Available [" + str(self.roman_auxilia_available) + "] Change to [0-100] ? ")
        self.roman_fort_available = raw_input("Roman Fort Available [" + str(self.roman_fort_available) + "] Change to [0-100] ? ")
        self.roman_legion_available = raw_input("Roman Legion Available [" + str(self.roman_legion_available) + "] Change to [0-100] ? ")
        self.roman_tribe_available = raw_input("Roman Tribe Available [" + str(self.roman_tribe_available) + "] Change to [0-100] ? ")

    def control_change_check(self):
        print ""
        print "Checking Control Changes...."
        for region in self.map:
            aedui_control = int(self.map[region].aedui_warband) + int(self.map[region].aedui_tribe) + int(self.map[region].aedui_citadel)
            arverni_count = int(self.map[region].arverni_leader) + int(self.map[region].arverni_warband) + int(self.map[region].arverni_tribe) + int(self.map[region].arverni_citadel)
            belgic_count = int(self.map[region].belgic_leader) + int(self.map[region].belgic_warband) + int(self.map[region].belgic_tribe) + int(self.map[region].belgic_citadel)
            roman_count = int(self.map[region].roman_leader) + int(self.map[region].roman_auxilia) + int(self.map[region].roman_fort) + int(self.map[region].roman_legion) + int(self.map[region].roman_tribe)
            germanic_count = int(self.map[region].aedui_warband) + int(self.map[region].aedui_tribe)

            if aedui_control > arverni_count + belgic_count + roman_count + germanic_count:
                if self.map[region].control != "Aedui Control":
                    print "ACTION: Control changed in: %s from %s to Aedui Control" % (self.map[region].name, self.map[region].control)
                    self.map[region].control = "Aedui Control"

            if arverni_count > aedui_control + belgic_count + roman_count + germanic_count:
                if self.map[region].control != "Arverni Control":
                    print "ACTION: Control changed in: %s from %s to Arverni Control" % (self.map[region].name, self.map[region].control)
                    self.map[region].control = "Arverni Control"

            if belgic_count > aedui_control + arverni_count + roman_count + germanic_count:
                if self.map[region].control != "Belgic Control":
                    print "ACTION: Control changed in: %s from %s to Belgic Control" % (self.map[region].name, self.map[region].control)
                    self.map[region].control = "Belgic Control"

            if roman_count > aedui_control + arverni_count + belgic_count + germanic_count:
                if self.map[region].control != "Roman Control":
                    print "ACTION: Control changed in: %s from %s to Roman Control" % (self.map[region].name, self.map[region].control)
                    self.map[region].control = "Roman Control"

            if germanic_count > aedui_control + arverni_count + belgic_count + roman_count:
                if self.map[region].control != "Germanic Control":
                    print "ACTION: Control changed in: %s from %s to Germanic Control" % (self.map[region].name, self.map[region].control)
                    self.map[region].control = "Germanic Control"

        print ""
        print "Control Change Complete."
        print ""

    def do_map(self, rest):
        try:
            print ""
            print "Region Codes:"
            print "[AED] Aedui, [ARV] Arverni, [ATR] Atrebates"
            print "[BIT] Bituriges, [CAT] Catuvellauni, [GAR] Garnites"
            print "[HEL] Helvii, [MAN] Mandubii, [MOR] Morini, [NER] Nervii"
            print "[PIC] Pictones, [SEQ] Sequani, [SUG] Sugambri"
            print "[TRE] Treveri [UBI] Ubii, [VEN] Veneti"
            print ""

            region = raw_input("Enter Region code to change: ").upper()
            print ""
            print 'Name: %s' % self.map[region].name
            print 'Control: %s' % self.map[region].control


            self.map[region].aedui_warband = int(raw_input("Aeduit Warband [" + str(self.map[region].aedui_warband) + "] Change to [0-100] : "))

            self.map[region].aedui_warband = int(raw_input("Aeduit Tribe [" + str(self.map[region].aedui_warband) + "] Change to [0-100] : "))

            self.map[region].aedui_citadel = int(raw_input("Aeduit Citadel [" + str(self.map[region].aedui_citadel) + "] Change to [0-100] : "))

            self.map[region].arverni_leader = int(raw_input("Arverni Leader [" + str(self.map[region].arverni_leader) + "] Change to [0-1] : "))

            self.map[region].arverni_warband = int(raw_input("Arverni Warband [" + str(self.map[region].arverni_warband) + "] Change to [0-100] : "))

            self.map[region].arverni_tribe = int(raw_input("Arverni Tribe [" + str(self.map[region].arverni_tribe) + "] Change to [0-100] : "))

            self.map[region].arverni_citadel = int(raw_input("Arverni Citadel [" + str(self.map[region].arverni_citadel) + "] Change to [0-100] : "))

            self.map[region].belgic_leader = int(raw_input("Belgic Leader [" + str(self.map[region].belgic_leader) + "] Change to [0-100] : "))

            self.map[region].belgic_warband = int(raw_input("Belgic Warband [" + str(self.map[region].belgic_warband) + "] Change to [0-100] : "))

            self.map[region].belgic_tribe = int(raw_input("Belgic Tribe [" + str(self.map[region].belgic_tribe) + "] Change to [0-100] : "))

            self.map[region].belgic_citadel = int(raw_input("Belgic Citadel [" + str(self.map[region].belgic_citadel) + "] Change to [0-100] : "))

            self.map[region].germanic_warband = int(raw_input("Germanic Warband [" + str(self.map[region].germanic_warband) + "] Change to [0-100] : "))

            self.map[region].germanic_tribe = int(raw_input("Germanic Tribe [" + str(self.map[region].germanic_tribe) + "] Change to [0-100] : "))

            self.map[region].roman_leader = int(
                raw_input("Roman Leader [" + str(self.map[region].roman_leader) + "] Change to [0-100] : "))

            self.map[region].roman_auxilia = int(
                raw_input("Roman Auxilia [" + str(self.map[region].roman_auxilia) + "] Change to [0-100] : "))

            self.map[region].roman_fort = int(
                raw_input("Roman Fort [" + str(self.map[region].roman_fort) + "] Change to [0-100] : "))

            self.map[region].roman_legion = int(
                raw_input("Roman Legion [" + str(self.map[region].roman_legion) + "] Change to [0-100] : "))

            self.map[region].roman_tribe = int(
                raw_input("Roman Tribe [" + str(self.map[region].roman_tribe) + "] Change to [0-100] : "))

            self.map[region].dispersed_gathering = int(
                raw_input("Dispersed Gathering [" + str(self.map[region].dispersed_gathering) + "] Change to [-1 > 0] : "))

            self.control_change_check()
        except:
            print "Unknown location. Enter command again."

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
    
    inputdata = json.loads(jsonstr)
    print inputdata
    
#    app = FY(scenario)

#    app.cmdloop()


if __name__ == "__main__":
    main()