// utility functions

function msgPush(line) {
	if (interrupt) return;
	msg.push(line);
	console.log('<AI> ' + line);
}

function msgPop() {
	var line = msg.pop();
	console.log('MSG-POP: ' + line);
}

function contains(array, item) {
	for (var i = 0; i < array.length; i++) {
		if (array[i] == item)
			return true;
	}
	return false;
}

function count(array, item) {
	var count = 0;
	for (var i = 0; i < array.length; i++) {
		if (array[i] == item)
			count++;
	}
	return count;
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function d6() {
	return Math.floor(6*Math.random())+1;
}

function die(d) {
	return Math.floor(d*Math.random())+1;
}

function fixZoneParameter(zone, outType) {
    outType = outType || 'object';

    if (typeof zone == outType)
        return zone;

    if (outType == 'string') {
        //console.log('INFO fixZoneParameter() converting from object to string for ' + zone.name);
        return zone.name;
    }
    if (outType == 'object') {
        //console.log('INFO fixZoneParameter() converting from string to object for ' + zone);
        return getZone(zone);
    }
    
    msgPush("ASSERT FAILED fixZoneParameter(): Unknown outType");
}

function getZone(zoneName) {
	if (typeof zoneName !== 'string') msgPush('ASSERT FAILED getZone(): zoneName is already a zone');

	for (var key in game.map) {
		var zone = game.map[key];
		if (key == zoneName || zone.name == zoneName) {
			return zone;
		}
	}
	return false;
}

function setFunctions(zone) {
	zone = fixZoneParameter(zone);

	zone.isAdjacent = function (target) {
		target = fixZoneParameter(target);
		
		for (var adj in this.adjacencies) { 
			console.log('isAdjacent() ' + adj + ' == ' + target.key + '?');
			if (adj == origin.key)
				return true;
		}
		return false;
	}

	zone.aedui = function () {
		return this.aedui_tribe + this.aedui_citadel + this.aeduiForces();
	}

	zone.aeduiForces = function () {
		return this.aeduiWarband();
	}

	zone.aeduiWarband = function () {
		return this.aedui_warband + this.aedui_warband_revealed;
	}

	zone.arverni = function () {
		return this.arverni_tribe + this.arverni_citadel + this.arverniForces();
	}

	zone.arverniForces = function () {
		return this.arverniWarband() + this.arverni_leader;
	}

	zone.arverniWarband = function () {
		return this.arverni_warband + this.arverni_warband_revealed;
	}

	zone.belgic = function () {
		return this.belgic_tribe + this.belgic_citadel + this.belgicForces();
	}

	zone.belgicForces = function () {
		return this.belgicWarband() + this.belgic_leader;
	}

	zone.belgicWarband = function () {
		return this.belgic_warband + this.belgic_warband_revealed;
	}

	zone.roman = function () {
		return this.roman_tribe + this.roman_fort + this.romanForces();
	}

	zone.romanForces = function () {
		return this.romanAuxilia() + this.roman_legion + this.roman_leader;
	}

	zone.romanAuxilia = function () {
		return this.roman_auxilia + this.roman_auxilia_revealed;
	}

	zone.germanic = function () {
		return this.germanic_tribe + this.germanicForces();
	}

	zone.germanicForces = function () {
		return this.germanicWarband();
	}

	zone.germanicWarband = function () {
		return this.germanic_warband + this.germanic_warband_revealed;
	}

	zone.aeduiLosses = function () {
		return Math.floor(this.aeduiWarband() * 0.5);
	}

	zone.arverniLosses = function () {
		return this.arverni_leader + Math.floor(this.arverniWarband() * 0.5);
	}

	zone.belgicLosses = function () {
		return this.belgic_leader + Math.floor(this.belgicWarband() * (this.belgic_leader ? 1 : 0.5));
	}

	zone.germanicLosses = function () {
		return Math.floor(this.germanicWarband() * 0.5);
	}

	zone.control = function () {
		var aedui = zone.aedui();
		var arverni = zone.arverni();
		var belgic = zone.belgic();
		var germanic = zone.germanic();
		var roman = zone.roman();
		var totalPieces = aedui + arverni + belgic + roman + germanic;
		if (aedui > (totalPieces - aedui)) return 'Aedui Control';
		if (arverni > (totalPieces - arverni)) return 'Arverni Control';
		if (belgic > (totalPieces - belgic)) return 'Belgic Control';
		if (roman > (totalPieces - roman)) return 'Roman Control';
		if (germanic > (totalPieces - germanic)) return 'Germanic Control';
		return 'No Control';
	}

	zone.belgicLeaderPresentOrAdjacent = function () {
		if (this.belgic_leader) return true;
		for (var adj in this.adjacent) {
			if (getZone(adj).belgic_leader) return true;
		}
		return false;
	}

	zone.arverniLeaderPresentOrAdjacent = function () {
		if (this.arverni_leader) return true;
		for (var adj in this.adjacent) {
			if (getZone(adj).arverni_leader) return true;
		}
		return false;
	}

	zone.status = function () {
		return (zone.name + ': aedui=' + this.aedui() + ', arverni=' + this.arverni() +
			', belgic=' + this.belgic() + ', roman=' + this.roman() + ', germanic=' +
			this.germanic());
	}
}

function pickRandomZone(candidates, selector) {
	var blackDie = d6();
	var tanDie = d6();
	var greenDie = d6();
	
	console.log("pickRandomZone() BLACK=" + blackDie + ", TAN=" + tanDie + ", GREEN=" + greenDie);
	
	blackDie = Math.ceil(blackDie / 2) - 1;
	tanDie = Math.ceil(tanDie / 2) - 1;
	greenDie = Math.ceil(greenDie / 2) - 1;
	
	var spaceIndex = (tanDie * 9) + (blackDie * 3) + greenDie;
	var safety = kSpacesTable.length + 1;
	
	console.log("pickRandomZone() rolled " + kSpacesTable[spaceIndex]);
	
	do {
		var isCandidate = contains(candidates, kSpacesTable[spaceIndex]);
		var selectorOk = (selector == null || selector(kSpacesTable[spaceIndex]));
		if (isCandidate && selectorOk) {
			safety = -1;
		} else {
			safety--;
			if (spaceIndex == (kSpacesTable.length - 1))
				spaceIndex = 0;
			else
				spaceIndex++;
		}
	} while (safety > 0);
	
	if (safety == 0)
		return false;
		
	console.log("pickRandomZone() selected " + kSpacesTable[spaceIndex]);
	
	return getZone(kSpacesTable[spaceIndex]);
}

function zoneList() {
	var zones = [];
	for (var key in game.map) {
		zones.push(game.map[key].name);
	}
	return zones;
}

function filterZones(candidates, selector) {
	var output = [];
	if (candidates == null || candidates.length == 0) return output;
	for (var i = 0; i < candidates.length; i++) {
		var c = candidates[i];
		var z = getZone(c);
		if (selector(z)) output.push(c);
	}
	return output;
}

function askQuestion(type, code, question, options) {
	if (interrupt) return;

	options = options || '';

	gamedata = JSON.stringify(game);

	msgPush(JSON.stringify(
		{
			faction: game.faction,
			type: type,
			q: code,
			question: question,
			options: options
		}
	));
	interrupt = true;
}