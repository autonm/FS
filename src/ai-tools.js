// utility functions

function consoleLog() {
	var msg = '';
	for (var i = 0; i < arguments.length; i++) {
		if (i > 0) msg += ' ';
		msg += arguments[i];
	}
	console.log(msg + '\n');
}

function msgPush() {
	if (interrupt) return;
	var line = '';
	for (var i = 0; i < arguments.length; i++) {
		if (i > 0) line += ' ';
		line += arguments[i];
	}
	msg.push(line + '\n');
	consoleLog('MSG: ' + line);
}

function msgPop() {
	var line = msg.pop();
	consoleLog('MSG-POP: ' + line);
}

function contains(array, item) {
	for (var i = 0; i < array.length; i++) {
		if (array[i] == item)
			return true;
	}
	return false;
}

function uniq(a) {
    var seen = {};
    return a.filter(function(item) {
        return seen.hasOwnProperty(item) ? false : (seen[item] = true);
    });
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
        return zone.name;
    }
    if (outType == 'object') {
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
			var isAdj = (adj == origin.key); 
			consoleLog('isAdjacent()', adj, ' == ', target.key, '?', isAdj);
			if (isAdj)
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

	zone.subdued = function () {
		var subdued = this.ally -
			(this.aedui_tribe + this.aedui_citadel +
			this.arverni_tribe + this.arverni_citadel +
			this.belgic_tribe + this.belgic_citadel +
			this.roman_tribe + this.germanic_tribe) -
			this.dispersed_gathering;
		consoleLog('zone.subdued()', this.name, subdued);
		return subdued;
	}

	zone.subduedTribesAvailable = function (faction) {
		faction = faction || '';
		if (faction == '') msgPush('ASSERT ERROR: zone.subduedTribesAvailable() should be provided with a faction');

		var subdued = this.subdued();

		if ('aedui_special' in this) {
			// Aedui Special City
			if (status == 'subdued' && faction != 'Aedui')
				subdued--;
		}

		if ('arverni_special' in this) {
			// Arverni Special City
			if (status == 'subdued' && faction != 'Arverni')
				subdued--;
		}

		consoleLog('zone.subduedTribesAvailable()', faction, this.name, subdued);
		return subdued;
	}

	zone.control = function () {
		var aedui = zone.aedui();
		var arverni = zone.arverni();
		var belgic = zone.belgic();
		var germanic = zone.germanic();
		var roman = zone.roman();
		var totalPieces = aedui + arverni + belgic + roman + germanic;
		var control = 'No Control';
		if (aedui > (totalPieces - aedui)) control = 'Aedui Control';
		if (arverni > (totalPieces - arverni)) control = 'Arverni Control';
		if (belgic > (totalPieces - belgic)) control = 'Belgic Control';
		if (roman > (totalPieces - roman)) control = 'Roman Control';
		if (germanic > (totalPieces - germanic)) control = 'Germanic Control';
		//D1: consoleLog('zone.control()', this.name, control, '-', 'aedui=', aedui, 'arverni=', arverni, 'belgic=', belgic, 'roman=', roman, 'germanic=', germanic, 'total=', totalPieces);
		return control;
	}

	zone.belgicLeaderPresentOrAdjacent = function () {
		// is the Belgic leader/Successor in this region?
		if (this.belgic_leader) {
			consoleLog('Belgic leader present in', this.name);
			return true;
		}

		// Belgic leader adjacent works only if Ambiorix, not Successor
		if (game.ambiorix) {
			for (var adj in this.adjacent) {
				var adjZone = getZone(adj);
				if (adjZone.belgic_leader) {
					consoleLog('Belgic leader adjacent to', this.name, 'in', adjZone.name);
					return true;
				}
			}
		}
		return false;
	}

	zone.arverniLeaderPresentOrAdjacent = function () {
		// is the Arverni leader/Successor in this region?
		if (this.arverni_leader) {
			consoleLog('Arverni leader present in', this.name);
			return true;
		}

		// Arverni leader adjacent works only if Vercingetorix, not Successor
		if (game.vercingetorix) {
			for (var adj in this.adjacent) {
				var adjZone = getZone(adj);
				if (adjZone.arverni_leader) {
					consoleLog('Arverni leader adjacent to', this.name, 'in', adjZone.name);
					return true;
				}
			}
		}
		return false;
	}

	zone.status = function () {
		return (zone.name + ': aedui=' + this.aedui() + ', arverni=' + this.arverni() +
			', belgic=' + this.belgic() + ', roman=' + this.roman() + ', germanic=' +
			this.germanic());
	}

	zone.inSupplyLine = function (ask) {
		// 1. find all paths to Target provinces, return array of paths
		// 2. sort paths by shortest distance
		// 3. find a valid path in the set
		// 4. find a valid path in the set again, but ask for permission this time

		console.log('zone.inSupplyLine(', this.key, ')');
		var paths = findAllSupplyPaths(this, ask);
		console.log('PATHS');
		console.log(paths);

		//var supplyLine = findSupplyLine(this, [], ask);
		// TODO
		// see if in supply, if not and not(ask) return false
		// if not and ask find a path to supply line, ask permission if needed
		// if no paths then return false;
		//msgPush('TODO zone.inSupplyLine()', this.name);
		return false;
	}

	zone.distanceToSupplyLine = function () {
		// TARGETS: Cisalpina: 'HEL', 'SEQ', 'UBI'
		var anyInSupply = false;
		var zones = zoneList();
		for (var i = 0; i < zones && !anyInSupply; i++)
			if (getZone(zones[i]).inSupplyLine(false))
				anyInSupply = true;
		
		var distance = findDistanceToSupplyLine(this, [], 99, anyInSupply);
		consoleLog('zone.distanceToSupplyLine()', this.name, distance, anyInSupply);

		return distance;
	}
}

function findAllSupplyPaths(zone, ask, path) {
	// find all paths to targets
	var targets = ['HEL', 'SEQ', 'UBI'];
	var key = zone.key;
	var isTarget = contains(targets, key);
	var control = zone.control();

	path = path || [];
	var mypath = path.slice(); 

	mypath.push(key);
	console.log('-> findAllSupplyPaths(', key, ')', mypath);

	if (isTarget) {
		return mypath;
	} else {
		var paths = [];
		for (var adj in zone.adjacent) {
			if (!contains(mypath, adj)) {
				console.log(mypath, 'does not contain', adj);
				var adjzone = getZone(adj);
				var control = adjzone.control();
				var supplyControl = false;

				switch (control) {
					case 'No Control':
					case 'Roman Control':
						supplyControl = true;
						break;
					case 'Aedui Control':
						if ('supply_aedui' in game.permissions) {
							supplyControl = game.permissions.supply_aedui;
						} else if (ask) {
							supplyControl = true; // return blocked path, to ask faction
						}
						break;
					case 'Arverni Control':
						if ('supply_arverni' in game.permissions) {
							supplyControl = game.permissions.supply_arverni;
						} else if (ask) {
							supplyControl = true; // return blocked path, to ask faction
						}
						break;
					case 'Belgic Control':
						if ('supply_belgic' in game.permissions) {
							supplyControl = game.permissions.supply_belgic;
						} else if (ask) {
							supplyControl = true; // return blocked path, to ask faction
						}
						break;
				}

				if (supplyControl) {
					result = findAllSupplyPaths(getZone(adj), ask, mypath);
					if (result) {
						console.log('R', 'findAllSupplyPaths(', key, ')', result);
						if (result[0].constructor === Array) {
							for (var i = 0; i < result.length; i++) {
								paths.push(result[i]);
							}
						} else {
							paths.push(result);
						}
					}
				}
			}
		}
		console.log('<- findAllSupplyPaths(', key, ')', paths);
		if (paths.length > 0)
			return paths;
		else
			return false;
	}
}

function findSupplyLine(zone, path, ask) {
	// find path to a supply line, if possible
	var targets = ['HEL', 'SEQ', 'UBI'];
	var key = zone.key;
	var isTarget = contains(targets, key);
	var control = zone.control();
	var supplyControl = false;
	switch (control) {
		case 'No Control':
		case 'Roman Control':
			supplyControl = true;
			break;
		case 'Aedui Control':
			if ('supply_aedui' in game.permissions) {
				supplyControl = game.permissions.supply_aedui;
			} else if (ask) {
				msgPush('TODO: Aedui permission for supply line?');
			}
			break;
		case 'Arverni Control':
			if ('supply_arverni' in game.permissions) {
				supplyControl = game.permissions.supply_arverni;
			} else if (ask) {
				msgPush('TODO: Arverni permission for supply line?');
			}
			break;
		case 'Belgic Control':
			if ('supply_belgic' in game.permissions) {
				supplyControl = game.permissions.supply_belgic;
			} else if (ask) {
				msgPush('TODO: Belgic permission for supply line?');
			}
			break;
	}
	if (interrupt) return false;

	if (!supplyControl) return false;

	var result = false;
	for (var adj in zone.adjacent) {
		if (!contains(path, adj)) {
			path.push(adj);
			result = result || findSupplyLine(getZone(adj), path, ask); 
		}
	}
	return dist;
}

function findDistanceToSupplyLine(zone, path, distance, anyInSupply) {
	var targets = ['HEL', 'SEQ', 'UBI'];
	var key = zone.key;
	var isTarget = contains(targets, key);
	var inSupply = zone.inSupplyLine(false);
	var finish = inSupply || (!anyInSupply && isTarget);

	consoleLog('findDistanceToSupplyLine()', key, inSupply, isTarget, finish, distance);

	if (finish) {
		var d = path.length + 1;
		return Math.min(d, distance);
	} else {
		var dist = distance;
		for (var adj in zone.adjacent) {
			if (!contains(path, adj)) {
				path.push(adj);
				dist = Math.min(dist, findDistanceToSupplyLine(getZone(adj), path, dist, anyInSupply));
			}
		}
		return dist;
	}
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

function capabilityActive(num, shaded) {
	for (var i = 0; i < game.capabilities; i++) {
		if (game.capabilities[i].num == num && game.capabilities[i].shaded == shaded)
			return true;
	}
	return false;
}

function totalDispersedGathering() {
	var total = 0;
	for (var key in game.map) {
		var zone = game.map[key];
		total += zone.dispersed_gathering;
		consoleLog('totalDispersedGathering()', zone.name, zone.dispersed_gathering);
	}
	return total;
}

function totalSubdued() {
	var total = 0;
	for (var key in game.map) {
		var zone = game.map[key];
		total += zone.subdued();
	}
	consoleLog('totalSubdued()', total);
	return total;
}

function romanVictoryScore() {
	// Roman Victory

	var score = (6 - game.roman_tribe_available) + 
		totalDispersedGathering() + totalSubdued();
	consoleLog('Roman Victory = ', score);
	return score;
}

function hasDiviciacusPermission() {
	if (!('diviciacus' in game.permissions)) {
		if (!capabilityActive(38, UNSHADED)) return false;

		if (game.action == 'Roman') {
			if (game.aeduiNP)
				game.permissions['diviciacus'] = romanVictoryScore() <= 12;
			else
				askQuestion(QUESTION_YESNO, 'diviciacus_permission', 'Does Aedui player give permission for Diviciacus?');
		} else {
			if (game.romanNP)
				msgPush('TODO: not implemented, aeduiVictoryScore() at hasDiviciacusPermission()');
			else
				askQuestion(QUESTION_YESNO, 'diviciacus_permission', 'Does Roman player give permission for Diviciacus?');
		}
	}
	
	if (!('diviciacus' in game.permissions))
		return game.permissions['diviciacus'];
	else
		return false;
}