// utility functions

function msgPush(line) {
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

function isAdjacent(target, origin) {
    if (typeof target == 'string') msgPush("ASSERT FAILED isAdjacent(): target is string instead of Zone");
    origin = fixZoneParameter(origin, 'string');

    for (var i = 0; i < target.adjacencies.length; i++) {
        console.log('isAdjacent() ' + target.adjacencies[i] + ' == ' + origin + '?');
        if (target.adjacencies[i] == origin)
            return true;
    }
    return false;
}

function getZone(zoneName) {
	if (typeof zoneName !== 'string') msgPush('ASSERT FAILED getZone(): zoneName is already a zone');

	for (var key in game.map) {
		var zone = game.map[key];
		if (zone.name == zoneName) {
			return zone;
		}
	}
	return false;
}

function getMomentumCards() {
    var momentum = [];
	var cardZone = getZone("Momentum");
	for (var i = 0; i < cardZone.pieces.length; i++) {
		var piece = cardZone.pieces[i];
		var periodIndex = piece.name.indexOf('.');
		if (piece.name.charAt(0) != ' ' && periodIndex > 0 && periodIndex < 3) {
			var cardNumber = piece.name.substring(0, periodIndex);
			if (cardNumber.charAt(0) == '0') cardNumber = cardNumber.substring(1);
			momentum.push(parseInt(cardNumber));
		}
	}
	return momentum;
}

function zoneControl(zone) {
	var aedui = zoneAedui(zone);
	var arverni = zoneArverni(zone);
	var belgic = zoneBelgic(zone);
	var germanic = zoneGermanic(zone);
	var roman = zoneRoman(zone);
	var totalPieces = aedui + arverni + belgic + roman + germanic;
	if (aedui > totalPieces) return 'Aedui Control';
	if (arverni > totalPieces) return 'Arverni Control';
	if (belgic > totalPieces) return 'Belgic Control';
	if (roman > totalPieces) return 'Roman Control';
	if (germanic > totalPieces) return 'Germanic Control';
	return 'No Control';
}

function zoneAedui(zone) {
	return zone.aedui_tribe + zone.aedui_citadel + zone.aedui_warbands + zone.aedui_warbands_revealed;
}

function zoneArverni(zone) {
	return zone.arverni_tribe + zone.arverni_citadel + zone.arverni_warbands + zone.arverni_warbands_revealed + zone.arverni_leader;
}

function zoneBelgic(zone) {
	return zone.belgic_tribe + zone.belgic_citadel + zone.belgic_warbands + zone.belgic_warbands_revealed + zone.belgic_leader;
}

function zoneRoman(zone) {
	return zone.roman_tribe + zone.roman_fort + zone.roman_auxilia + zone.roman_legion + zone.roman_leader;
}

function zoneGermanic(zone) {
	return zone.germanic_tribe + zone.germanic_warbands + zone.germanic_warbands_revealed;
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