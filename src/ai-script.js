// setup

var inputdata = {};
var answerdata = {};
var gamedata = {};

var game = {};
var msg = [];
var askFactions = {};

var interrupt = false;

function reset() {
	inputdata = {};
	answerdata = {};
	gamedata = {};
	askFactions = {};

	game = {};
	msg = [];

	interrupt = false;
}

var QUESTION_YESNO = "yesno";
var QUESTION_SINGLECHOICE = "single";
var QUESTION_MULTIPLECHOICE = "multi";

var SHADED = true;
var UNSHADED = false;

var pieceLabel = {
	"coalition_base": "Coalition Base", 
	"coalition_troops": "Coalition Troops",
	"government_base": "GOVT Base",
	"troops": "Troops",
	"police": "Police",
	"taliban_base": "Taliban Base",
	"taliban_guerrilla": "Taliban Guerrilla",
	"taliban_guerrilla_underground": "Taliban Guerrilla",
	"taliban_guerrilla_active": "Taliban Guerrilla Active",
	"warlords_base": "Warlords Base",
	"warlords_guerrilla": "Warlords Guerrilla",
	"warlords_guerrilla_underground": "Warlords Guerrilla",
	"warlords_guerrilla_active": "Warlords Guerrilla Active"
}

var kMapAdjacencies = {
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

var kAllySpaces = {
	"Catuvalauni": {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Morini":      {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Menapii":     {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Nervii":      {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Atrebates":   {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Bellovaci":   {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Remi":        {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Veneti":      {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Namnetes":    {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Aulerci":     {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Pictones":    {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Santones":    {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Cadurci":     {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Volcae":      {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Senones":     {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Lingones":    {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Helvetii":    {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Treveri":     {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Sugambri":    {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Suebi North": {"Aedui": false, "Arverni": false, "Belgic": false, "Roman": false, "Germanic": true},
	"Ubii":        {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Suebi South": {"Aedui": false, "Arverni": false, "Belgic": false, "Roman": false, "Germanic": true},
	"Helvii":      {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Eburones":    {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true}
}

var kCitadelSpaces = {
	"Carnutes":    {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Bituriges":   {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Arverni":     {"Aedui": false, "Arverni": true,  "Belgic": false, "Roman": false, "Germanic": false},
	"Aedui":       {"Aedui": true,  "Arverni": false, "Belgic": false, "Roman": false, "Germanic": false},
	"Mandubii":    {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true},
	"Sequani":     {"Aedui": true,  "Arverni": true,  "Belgic": true,  "Roman": true,  "Germanic": true}
}

var kEnlistSpaces = ["SUG", "UBI", "MOR", "NER", "TRE", "SEQ"];

// card number: [ faction order + NP Instruction ]
// factions: (Ro)man, (Ar)verni, (Ae)dui, (Be)lgic
// NP instructions: (C)arnyx, (L)aurels, (S)words
var kCardIndex = {
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

function loadGameFromInputData() {
	game.permissions = {};
	game.capabilities = [];
	game.state = "8.8.1";

	game.action = inputdata.action;
	game.aeduiNP = inputdata.npaedui;
	game.arverniNP = inputdata.nparverni;
	game.romanNP = inputdata.nproman;
	game.belgicNP = inputdata.npbelgic;
	
	game.aedui_warband_available = 0;
	game.aedui_tribe_available = 0;
	game.aedui_citadel_available = 0;
	game.arverni_warband_available = 0;
	game.arverni_tribe_available = 0;
	game.arverni_citadel_available = 0;
	game.belgic_warband_available = 0;
	game.belgic_tribe_available = 0;
	game.belgic_citadel_available = 0;
	game.germanic_warband_available = 0;
	game.germanic_tribe_available = 0;
	game.roman_auxilia_available = 0;
	game.roman_fort_available = 0;
	game.roman_tribe_available = 0;
	game.roman_legion_available = 0;
	game.vercingetorix = 0;
	game.ambiorix = 0;
	game.caesar = 0;

	// regions
	game.map = {
		AED: {
			key: "AED",
			name: "Aedui",
			modname: "Celctica (Aedui)",
			ally: 1,
			citadel: 1
		},
		ARV: {
			key: "ARV",
			name: "Arverni",
			modname: "Celtica (Arverni, Cadurci, Volcae)",
			ally: 3,
			citadel: 1
		},
		ATR: {
			key: "ATR",
			name: "Atrebates",
			modname: "Belcica (Atrebates, Bellovaci, Remi)",
			ally: 3,
			citadel: 0
		},
		BIT: {
			key: "BIT",
			name: "Bituriges",
			modname: "Celtica (Bituriges)",
			ally: 1,
			citadel: 1
		},
		CAT: {
			key: "CAT",
			name: "Britannia",
			modname: "Britannia",
			ally: 1,
			citadel: 0
		},
		CAR: {
			key: "CAR",
			name: "Carnutes",
			modname: "Celtica (Aulerci, Carnutes)",
			ally: 2,
			citadel: 1
		},
		HEL: {
			key: "HEL",
			name: "Provincia",
			modname: "Provincia",
			ally: 1,
			citadel: 0
		},
		MAN: {
			key: "MAN",
			name: "Mandubii",
			modname: "Celtica (Senones, Mandubii, Lingones)",
			ally: 3,
			citadel: 1
		},
		MOR: {
			key: "MOR",
			name: "Morini",
			modname: "Belgica (Morini, Menapii)",
			ally: 2,
			citadel: 0
		},
		NER: {
			key: "NER",
			name: "Nervii",
			modname: "Belgica (Nervii)",
			ally: 2,
			citadel: 0
		},
		PIC: {
			key: "PIC",
			name: "Pictones",
			modname: "Celctica (Pictones, Santones)",
			ally: 2,
			citadel: 0
		},
		SEQ: {
			key: "SEQ",
			name: "Sequani",
			modname: "Celtica (Sequani, Helvetii)",
			ally: 2,
			citadel: 1
		},
		SUG: {
			key: "SUG",
			name: "Sugambri",
			modname: "Germania (Sugambri, Suebi)",
			ally: 2,
			citadel: 0
		},
		TRE: {
			key: "TRE",
			name: "Treveri",
			modname: "Celtica (Treveri)",
			ally: 1,
			citadel: 0
		},
		UBI: {
			key: "UBI",
			name: "Ubii",
			modname: "Germania (Ubii, Suebi)",
			ally: 2,
			citadel: 0
		},
		VEN: {
			key: "VEN",
			name: "Veneti",
			modname: "Celtica (Veneti, Namnetes)",
			ally: 2,
			citadel: 0
		}
	};
	
	for (var key in game.map) {
		var region = game.map[key];
		for (var z = 0; z < inputdata["zones"].length; z++) {
			var zone = inputdata["zones"][z];
			if (zone.name == region.modname) {
				// init
				region.aedui_warband = 0;
				region.aedui_warband_revealed = 0;
				region.aedui_tribe = 0;
				region.aedui_citadel = 0;
				region.arverni_leader = 0;
				region.arverni_warband = 0;
				region.arverni_warband_revealed = 0;
				region.arverni_tribe = 0;
				region.arverni_citadel = 0;
				region.belgic_leader = 0;
				region.belgic_warband = 0;
				region.belgic_warband_revealed = 0;
				region.belgic_tribe = 0;
				region.belgic_citadel = 0;
				region.germanic_warband = 0;
				region.germanic_warband_revealed = 0;
				region.germanic_tribe = 0;
				region.roman_leader = 0;
				region.roman_auxilia = 0;
				region.roman_auxilia_revealed = 0;
				region.roman_fort = 0;
				region.roman_legion = 0;
				region.roman_tribe = 0;
				region.dispersed_gathering = 0;
				region.devastated = 0;
				region.score = region.ally + region.citadel;
				region.adjacent = kMapAdjacencies[key];

				if (region.key == 'AED') {
					// special case, citadel of Aedui
					var status = 'subdued';
					for (var p = 0; p < zone["pieces"].length; p++) {
						var pieceName = zone["pieces"][p].name;
						if (zone["pieces"][p]["x"] == 2519 && zone["pieces"][p]["y"] == 1588) {
							if (pieceName == 'Aedui Ally') status = 'ally';
							if (pieceName == 'Aedui Citadel') status = 'citadel';
						}
					}
					region.aedui_special = status;
					consoleLog('Special City Aedui:', status);
				}

				if (region.key == 'ARV') {
					// special case, citadel of Arverni
					var status = 'subdued';
					for (var p = 0; p < zone["pieces"].length; p++) {
						var pieceName = zone["pieces"][p].name;
						if (zone["pieces"][p]["x"] == 2414 && zone["pieces"][p]["y"] == 1978) {
							if (pieceName == 'Arverni Ally') status = 'ally';
							if (pieceName == 'Averni Citadel') status = 'citadel';
						}
					}
					region.arverni_special = status;
					consoleLog('Special City Arverni:', status);
				}

				for (var p = 0; p < zone["pieces"].length; p++) {
					var pieceName = zone["pieces"][p].name;
					// Colony
					if (pieceName == 'Colony Added') {
						region.ally++;
						region.score++;
					}
					// count the aedui warbands
					if (pieceName == 'Aedui Warband')
						region.aedui_warband++;
					// count the revealed aedui warbands revealed
					if (pieceName == 'Aedui Warband Revealed')
						region.aedui_warband_revealed++;
					// count the aedui tribes (allies)
					if (pieceName == 'Aedui Ally')
						region.aedui_tribe++;
					// count the aedui citadels
					if (pieceName == 'Aedui Citadel')
						region.aedui_citadel++;
					// Arverni leader
					if (pieceName == 'Vercingetorix' || pieceName == 'Averni Successor')
						region.arverni_leader = 1;
						if (pieceName == 'Vercingetorix')
							game.vercingetorix = 1;
					// count the arverni warbands
					if (pieceName == 'Arverni Warband')
						region.arverni_warband++;
					// count the revealed averni warbands revealed
					if (pieceName == 'Arverni Warband Revealed')
						region.arverni_warband_revealed++;
					// count the arverni tribes (allies)
					if (pieceName == 'Arverni Ally')
						region.arverni_tribe++;
					// count the arverni citadels
					if (pieceName == 'Averni Citadel')
						region.arverni_citadel++;
					// Belgic leader
					if (pieceName == 'Ambiorix' || pieceName == 'Belgic Successor')
						region.belgic_leader = 1;
						if (pieceName == 'Ambiorix')
							game.ambiorix = 1;
					// count the belgic warbands
					if (pieceName == 'Belgic Warband')
						region.belgic_warband++;
					// count the revealed belgic warbands revealed
					if (pieceName == 'Belgic Warband Revealed')
						region.belgic_warband_revealed++;
					// count the belgic tribes (allies)
					if (pieceName == 'Belgic Ally')
						region.belgic_tribe++;
					// count the belgic citadels
					if (pieceName == 'Belgic Citadel')
						region.belgic_citadel++;
					// count the germanic warbands
					if (pieceName == 'Germanic Warband')
						region.germanic_warband++;
					// count the revealed germanic warbands revealed
					if (pieceName == 'Germanic Warband Revealed')
						region.germanic_warband_revealed++;
					// count the germanic tribes (allies)
					if (pieceName == 'Germanic Ally')
						region.germanic_tribe++;
					// Roman leader
					if (pieceName == 'Caesar' || pieceName == 'Roman Successor')
						region.roman_leader = 1;
						if (pieceName == 'Caesar')
							game.caesar = 1;
					// count the roman auxilia
					if (pieceName == 'Roman Auxilia')
						region.roman_auxilia++;
					// count the roman auxilia revealed
					if (pieceName == 'Roman Auxilia Revealed')
						region.roman_auxilia++;
					// count the roman tribes (allies)
					if (pieceName == 'Roman Ally')
						region.roman_tribe++;
					// count the roman fort
					if (pieceName == 'Roman Fort')
						region.roman_fort++;
					// count the roman legion
					if (pieceName == 'Roman Legion')
						region.roman_legion++;
					// count Dispersed tribes
					if (pieceName.endsWith(' (Dispersed)') || pieceName.endsWith(' (Gathering)')) {
						region.dispersed_gathering++;
						region.score--;
					}
					// count Devastated
					if (pieceName == 'Devastated')
						region.devastated++;
				}
			}
		}
	}

	for (var z = 0; z < inputdata["zones"].length; z++) {
		var zone = inputdata["zones"][z];
		for (var p = 0; p < zone["pieces"].length; p++) {
			var pieceName = zone["pieces"][p].name;
			// Aedui Resources
			if (pieceName.startsWith('Aedui Resources ('))
				game.aedui_resources = parseInt(zone.name);
			// Aedui Eligibility
			if (pieceName.startsWith('Aedui Eligibility'))
				game.aedui_eligibility = zone.name;
			// Arverni Resources
			if (pieceName.startsWith('Averni Resources ('))
				game.arverni_resources = parseInt(zone.name);
			// Arverni Eligibility
			if (pieceName.startsWith('Averni Eligibility'))
				game.arverni_eligibility = zone.name;
			// Belgic Resources
			if (pieceName.startsWith('Belgic Resources ('))
				game.belgic_resources = parseInt(zone.name);
			// Belgic Eligibility
			if (pieceName.startsWith('Belgic Eligibility'))
				game.belgic_eligibility = zone.name;
			// Roman Resources
			if (pieceName.startsWith('Roman Resources ('))
				game.roman_resources = parseInt(zone.name);
			// Roman Eligibility
			if (pieceName.startsWith('Roman Eligibility'))
				game.roman_eligibility = zone.name;
		}
	}

	game.arverni_leader_available = 1;
	game.belgic_leader_available = 1;
	game.roman_leader_available = 1;

	for (var p = 0; p < inputdata["offboard"].length; p++) {
		var pieceName = inputdata["offboard"][p].name;
		if (pieceName.indexOf(' Capability **') > -1) {
			var cardName = pieceName.substring(0, pieceName.indexOf(' **'));
			var cardNumber = parseInt(pieceName.substring(0, 2));
			var shadedCapability = pieceName.indexOf('** Shaded ') > -1;
			var cap = {card: cardName, num: cardNumber, shaded: shadedCapability}; 
			game.capabilities.push(cap);
			console.log('Capability: ', cap);
		}
	}

	for (var z = 0; z < inputdata["zones"].length; z++) {
		var zone = inputdata["zones"][z];
		for (var p = 0; p < zone["pieces"].length; p++) {
			var pieceName = zone["pieces"][p].name;
			if (zone.name == 'Aedui Available Forces') {
				if (pieceName.startsWith('Aedui Warband'))
					game.aedui_warband_available++;
				if (pieceName == 'Aedui Ally (Occupied)' || pieceName == 'Aedui Citadel (Ally)')
					game.aedui_tribe_available++;
				if (pieceName == 'Aedui Citadel (Occupied)')
					game.aedui_citadel_available++;
			}
			if (zone.name == 'Arverni Available Forces') {
				if (pieceName.startsWith('Arverni Warband'))
					game.arverni_warband_available++;
				if (pieceName == 'Arverni Ally (Occupied)' || pieceName == 'Arverni Citadel (Ally)')
					game.arverni_tribe_available++;
				if (pieceName == 'Arverni Citadel (Occupied)')
					game.arverni_citadel_available++;
			}
			if (zone.name == 'Belgic Available Forces') {
				if (pieceName.startsWith('Belgic Warband'))
					game.belgic_warband_available++;
				if (pieceName == 'Belgic Ally (Occupied)' || pieceName == 'Belgic Citadel (Ally)')
					game.belgic_tribe_available++;
				if (pieceName == 'Belgic Citadel (Occupied)')
					game.belgic_citadel_available++;
			}
			if (zone.name == 'Germanic Available Forces') {
				if (pieceName.startsWith('Germanic Warband'))
					game.germanic_warband_available++;
				if (pieceName == 'Germanic Ally (Occupied)')
					game.germanic_tribe_available++;
			}
			if (zone.name == 'Roman Available Forces') {
				if (pieceName.startsWith('Roman Auxilia'))
					game.roman_auxilia_available++;
				if (pieceName.startsWith('Roman Fort'))
					game.roman_fort_available++;
				if (pieceName == 'Roman Ally (Occupied)')
					game.roman_tribe_available++;
				if (pieceName == 'Roman Legion')
					game.roman_legion_available++;
			}
			if (zone.name == 'Upcoming') {
				game.upcomingcard = {name: pieceName, num: parseInt(pieceName.substring(0, 2))};
				if (game.upcomingcard.name.endsWith(' - Winter'))
					game.frost = true;
			}
			if (zone.name == 'Current') {
				game.currentcard = {name: pieceName, num: parseInt(pieceName.substring(0, 2))};
				if (game.currentcard.name.endsWith(' - Winter'))
					game.winter = true;
			}
			if (pieceName == 'Colony Added')
				game.colonies++;
			if (pieceName == 'Ambiorix' || pieceName == 'Belgic Successor')
				game.belgic_leader_available = 0;
			if (pieceName == 'Vercingetorix' || pieceName == 'Arverni Successor')
				game.arverni_leader_available = 0;
			if (pieceName == 'Caesar' || pieceName == 'Roman Successor')
				game.roman_leader_available = 0;
			if (zone.name == 'Senate - Uproar')
                if (pieceName == 'Roman Senate')
                    game.roman_senate = 1;
            if (zone.name == 'Senate - Intrigue')
                if (pieceName == 'Roman Senate')
                    game.roman_senate = 2;
            if (zone.name == 'Senate - Adulation')
                if (pieceName == 'Roman Senate')
                    game.roman_senate = 3;
            if (zone.name == 'Legions')
                if (pieceName == 'Roman Legion')
                    game.off_map_legions++;
		}
	}

	game.winter_remaining = inputdata['winter'];

	/*
        # find other_most_allies
        aedui_score = 8 - self.game.aedui_tribe_available - self.game.aedui_citadel_available
        arverni_score = 13 - self.game.arverni_tribe_available - self.game.arverni_citadel_available
        belgic_score = 11 - self.game.belgic_tribe_available - self.game.belgic_citadel_available
        germanic_score = 6 - self.game.germanic_tribe_available
        roman_score = 6 - self.game.roman_tribe_available
        self.game.other_most_allies = max(arverni_score, belgic_score, germanic_score, roman_score)

        # Belgic Victory
        self.game.control_allies = belgic_score
        for key, region in self.game.map.items():
            if region.control == 'Belgic Control':
                self.game.control_allies += region.pop
	*/
}

function hasAnswer() {
	var haveanswer = (typeof answer !== 'undefined') && (answer !== '');
	consoleLog('Have answer? ' + haveanswer);
	return haveanswer;
}

function isVassal() {
	return (typeof isvasal !== 'undefined' && isvassal);
}

function joinMsg() {
	msg = msg.join("");
}

function main() {
	// load input data

	inputdata = JSON.parse(inputString);
	if (hasAnswer()) {
		answerdata = JSON.parse(answer);
		game = inputdata;
	} else {
		loadGameFromInputData();

		msgPush("# Activated Bot: " + game.action);
	}
	
	for (var zone in game.map) {
		setFunctions(zone);
	}

	// Actions

	if (game.action == "Roman") {
		// Roman

		doRoman();
	
		// final

		msgPush('# Bot Complete');
	}

	joinMsg();
}

main();
