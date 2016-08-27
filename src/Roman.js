// AI

function sortZonesClosestToSupplyLine(zones) {
    var z = zones.sort(function (a, b) {
        a = fixZoneParameter(a);
        b = fixZoneParameter(b);
        var aSupply = a.inSupplyLine(false);
        var bSupply = b.inSupplyLine(false); 
        if (aSupply && bSupply) {
            return 0;
        } else if (aSupply && !bSupply) {
            return -1;
        } else if (!aSupply && bSupply) {
            return 1;
        } else {
            var aDistance = a.distanceToSupplyLine();
            var bDistance = b.distanceToSupplyLine();
            return bDistance - aDistance;
        }
    });
    consoleLog('sortZonesClosestToSupplyLine()', z);
    return z;
}

function reduceRomanResources(amount) {
    // 8.6.6: Aedui NP give Roman resources under certain conditions
    game.roman_resources -= amount;
    if (game.roman_resources < 2 && game.aedui_resources > 8 && game.aeduiNP) {
        game.aedui_resources -= 2;
        game.roman_resources += 2;
        msgPush('# Reduce Aedui resources by 2 to', game.aedui_resources);
        amount += 2;
        if (amount == 0) {
            msgPush('# Roman resources stay at', game.roman_resources);
        } else if (amount < 0) {
            msgPush('# Reduce Roman resources by', amount, 'to', game_roman_resources);
        } else {
            msgPush('# Add Roman resources by', amount, 'to', game_roman_resources);
        }
    } else {
        msgPush('# Reduce Roman resources by', amount, 'to', game.roman_resources);
    }
}

function battleCheckGaulPresence(zone) {
    // see if there is an enemy tribe / citadel / control
    var control = zone.control();
    return zone.aedui_tribe || zone.aedui_citadel || control == 'Aedui Control' ||
        zone.arverni_tribe || zone.arverni_citadel || control == 'Arverni Control' ||
        zone.belgic_tribe || zone.belgic_citadel || control == 'Belgic Control' ||
        zone.germanic_tribe || control == 'Germanic Control';
}

function romanCanRetreat(zone, attacker) {
    // see if any adjacent zone can be retreated to
    // any roman control?
    for (var adj in zone.adjacent) {
        var adjzone = getZone(adj);
        var control = adjzone.control();
        
        if (control == 'Roman Control') {
            return true;
        } else if (control == 'Aedui Control' && attacker != 'Aedui') {
            if ('aedui' in game.permissions && game.permissions.aedui) return true;
            if (game.aeduiNP) return true;
            askFactions.aedui = true;
        } else if (control == 'Arverni Control' && attacker != 'Arverni') {
            if ('arverni' in game.permissions && game.permissions.arverni) return true;
            if (!game.arverniNP)
                askFactions.arverni = true;
        } else if (control == 'Belgic Control' && attacker != 'Belgic') {
            if ('belgic' in game.permissions && game.permissions.belgic) return true;
            if (!game.belgicNP)
                askFactions.belgic = true;
        }
    }

    return false;
}

function romanRetreatAsk() {
    var options = '';
    var multiple = false;
    for (var f in askFactions) {
        if (!(f in game.permissions)) {
            if (options.length > 0) {
                options += ';';
                multiple = true;
            }
            options += capitalizeFirstLetter(f);
        }
    }
    if (options.length > 0)
        if (multiple) {
            askQuestion(QUESTION_MULTIPLECHOICE, "retreat_permission", "Do the following factions allow the Roman to retreat?", options);
        } else {
            askQuestion(QUESTION_YESNO, "retreat_permission", "Does " + options + " player allow Roman to retreat?", options);
        }
}

function battleCheckEnemyForcesLoss(zone) {
    // check if enemy presence could force a loss on Roman Leader or Legion
    // simulate an attack from each enemy faction on the Romans with SA and Capabilities

    // Belgic?
    if (zone.belgicForces() > 0) {
        // rampage + battle
        var aux = zone.romanAuxilia();
        // 38 - Diviciacus
        if (hasDiviciacusPermission()) aux += zone.aeduiWarband();

        var rampage = (zone.belgicLeaderPresentOrAdjacent() && zone.belgic_warband &&
                !zone.roman_fort && !zone.roman_leader && zone.romanForces());
        var rampageAuxilia = 0;
        var rampageLegion = 0;
        if  (rampage) {
            // rampage
            rampageAuxilia = Math.min(aux, zone.belgic_warband);
            if (rampageAuxilia < zone.belgic_warband)
                rampageLegion = Math.min(zone.roman_legion, zone.belgic_warband - rampageAuxilia);
            
            if (rampageLegion && !romanCanRetreat(zone, 'Belgic')) return true;

            // battle after rampage
            aux = aux - rampageAuxilia;
            var warb = zone.belgicWarband();
            // 13 - Balearic Slingers
            if (capabilityActive(13, UNSHADED))
                // 59 - Germanic Horse
                warb -= Math.floor(aux * (capabilityActive(59, UNSHADED) ? 1.0 : 0.5));

            var losses = zone.belgic_leader +
                Math.floor(warb * (zone.belgic_leader ? 1 : 0.5) * (capabilityActive(59, SHADED) ? 2.0 : 1.0));
            var finalLosses = losses;
            if (zone.roman_fort) finalLosses = Math.floor(finalLosses * 0.5);
            // 15 - Legio X
            if (capabilityActive(15, UNSHADED) && zone.roman_leader && zone.roman_legion) {
                finalLosses = Math.max(0, finalLosses--);
                if (capabilityActive(59, UNSHADED)) finalLosses = Math.max(0, finalLosses--);
            }
            
            if (finalLosses > aux) {
                // losses > auxilia, so remaining hits are on leader/legion
                // check to see if retreat can help
                var retreatCap = zone.roman_tribe + zone.roman_fort + aux;
                var retreatLosses = Math.floor(losses * 0.5);
                // 15 - Legio X
                if (capabilityActive(15, UNSHADED) && zone.roman_leader && zone.roman_legion) {
                    retreatLosses = Math.max(0, retreatLosses--);
                    if (capabilityActive(59, UNSHADED)) retreatLosses = Math.max(0, retreatLosses--);
                }
                
                if (retreatLosses <= retreatCap) {
                    if (romanCanRetreat(zone, 'Belgic')) {
                        return (retreatLosses > retreatCap);
                    } else
                        return true;
                } else
                    return true;
            }
        }

        // ambush + battle
        var aux = zone.romanAuxilia();
        var aux_hidden = zone.roman_auxilia;
        // 38 - Diviciacus
        if (hasDiviciacusPermission()) {
            aux += zone.aeduiWarband();
            aux_hidden += zone.aedui_warband;
        }
        
        var canAmbush = zone.belgicLeaderPresentOrAdjacent() && (zone.belgic_warband > aux_hidden);

        var warb = zone.belgicWarband();
        // 13 - Balearic Slingers
        if (capabilityActive(13, UNSHADED))
            // 59 - Germanic Horse
            warb -= Math.floor(aux * (capabilityActive(59, UNSHADED) ? 1.0 : 0.5));

        var losses = zone.belgic_leader +
                Math.floor(warb * (zone.belgic_leader ? 1 : 0.5) * (capabilityActive(59, SHADED) ? 2.0 : 1.0));
        var finalLosses = losses;
        if (zone.roman_fort > 0) finalLosses = Math.floor(losses * 0.5);
        // 15 - Legio X
        if (capabilityActive(15, UNSHADED) && zone.roman_leader && zone.roman_legion) {
            finalLosses = Math.max(0, finalLosses--);
            if (capabilityActive(59, UNSHADED)) finalLosses = Math.max(0, finalLosses--);
        }
        console.log('Belgic finalLosses', finalLosses, 'Roman aux', aux);

        if (finalLosses > aux) {
            // losses > auxilia, so remaining hits are on leader/legion
            // check to see if retreat can help
            var retreatCap = zone.roman_tribe + zone.roman_fort + aux;
            var retreatLosses = Math.floor(losses * 0.5);
            // 15 - Legio X
            if (capabilityActive(15, UNSHADED) && zone.roman_leader && zone.roman_legion) {
                retreatLosses = Math.max(0, retreatLosses--);
                if (capabilityActive(59, UNSHADED)) retreatLosses = Math.max(0, retreatLosses--);
            }

            if (!canAmbush && retreatLosses <= retreatCap) {
                if (romanCanRetreat(zone, 'Belgic')) {
                    return (retreatLosses > retreatCap);
                } else
                    return true;
            } else
                return true;
        }
    }

    // Arverni?
    if (zone.arverniForces() > 0) {
        // devastate + battle
        var devastate = zone.control() == 'Arverni Control' && arverniLeaderPresentOrAdjacent(zone);
        if (devastate) {
            var aux = zone.romanAuxilia();
            var romanLosses = Math.floor(aux / 3);
            // 38 - Diviciacus
            if (hasDiviciacusPermission()) aux += zone.aeduiWarband();
            aux -= romanLosses;

            if (aux < 0) {
                // must remove legion
                return true;
            }

            var warb = Math.floor(zone.arverniWarband() * 0.75);
            // 13 - Balearic Slingers
            if (capabilityActive(13, UNSHADED))
                // 59 - Germanic Horse
                warb -= Math.floor(aux * (capabilityActive(59, UNSHADED) ? 1.0 : 0.5));

            // battle after devastate
            // 30 - Vercingetorix's Elite
            if (capabilityActive(30, SHADED) && zone.arverni_leader)
                if (warb > 1) warb += 2; else if (warb > 0) warb ++;
            var losses = zone.arverni_leader + Math.floor(warb * 0.5 * (capabilityActive(59, SHADED) ? 2.0 : 1.0));
            // 26 - Massed Gallic Archers
            if (capabilityActive(26, UNSHADED))
                losses = Math.max(0, losses--);
            var finalLosses = losses;
            if (zone.roman_fort > 0) finalLosses = Math.floor(losses * 0.5);
            // 26 - Massed Gallic Archers
            if (capabilityActive(26, SHADED) && warb >= 6) losses++;
            // 15 - Legio X
            if (capabilityActive(15, UNSHADED) && zone.roman_leader && zone.roman_legion) {
                finalLosses = Math.max(0, finalLosses--);
                if (capabilityActive(59, UNSHADED)) finalLosses = Math.max(0, finalLosses--);
            }

            if (finalLosses > aux) {
                // losses > auxilia, so remaining hits are on leader/legion
                // check to see if retreat can help
                var retreatCap = zone.roman_tribe + zone.roman_fort + aux;
                var retreatLosses = Math.floor(losses * 0.5);
                // 26 - Massed Gallic Archers
                if (capabilityActive(26, SHADED) && warb >= 6) retreatLosses++;
                // 15 - Legio X
                if (capabilityActive(15, UNSHADED) && zone.roman_leader && zone.roman_legion) {
                    retreatLosses = Math.max(0, retreatLosses--);
                    if (capabilityActive(59, UNSHADED)) retreatLosses = Math.max(0, retreatLosses--);
                }

                if (retreatLosses <= retreatCap) {
                    if (romanCanRetreat(zone, 'Arverni')) {
                        return (retreatLosses > retreatCap);
                    } else
                        return true;
                } else
                    return true;
            }
        }

        // battle + ambush
        // ambush + battle
        var aux = zone.romanAuxilia();
        var aux_hidden = zone.roman_auxilia;
        // 38 - Diviciacus
        if (hasDiviciacusPermission()) {
            aux += zone.aeduiWarband();
            aux_hidden += zone.aedui_warband;
        }

        var canAmbush = zone.arverniLeaderPresentOrAdjacent() && (zone.arverni_warband > aux_hidden);
        
        var warb = zone.arverniWarband();
        // 13 - Balearic Slingers
        if (capabilityActive(13, UNSHADED))
            // 59 - Germanic Horse
            warb -= Math.floor(aux * (capabilityActive(59, UNSHADED) ? 1.0 : 0.5));

        var losses = zone.arverni_leader + Math.floor(warb * 0.5 * (capabilityActive(59, SHADED) ? 2.0 : 1.0));
        // 26 - Massed Gallic Archers
        if (capabilityActive(26, UNSHADED)) losses = Math.max(0, losses--);
        var finalLosses = losses;
        if (zone.roman_fort > 0) finalLosses = Math.floor(losses * 0.5);
        // 15 - Legio X
        if (capabilityActive(15, UNSHADED) && zone.roman_leader && zone.roman_legion) {
            finalLosses = Math.max(0, finalLosses--);
            if (capabilityActive(59, UNSHADED)) finalLosses = Math.max(0, finalLosses--);
        }

        if (finalLosses > aux) {
            // losses > auxilia, so remaining hits are on leader/legion
            // check to see if retreat can help
            var retreatCap = zone.roman_tribe + zone.roman_fort + aux;
            var retreatLosses = Math.floor(losses * 0.5);
            // 15 - Legio X
            if (capabilityActive(15, UNSHADED) && zone.roman_leader && zone.roman_legion) {
                retreatLosses = Math.max(0, retreatLosses--);
                if (capabilityActive(59, UNSHADED)) retreatLosses = Math.max(0, retreatLosses--);
            }
            
            if (!canAmbush && retreatLosses <= retreatCap) {
                if (romanCanRetreat(zone, 'Arverni')) {
                    return (retreatLosses > retreatCap);
                } else
                    return true;
            } else
                return true;
        }
    }

    // Aedui?
    if (zone.aeduiForces() > 0) {
        // ambush + battle
        var canAmbush = zone.aedui_warband > zone.roman_auxilia;

        var warb = zone.aeduiWarband();
        // 13 - Balearic Slingers
        if (capabilityActive(13, UNSHADED))
            // 59 - Germanic Horse
            warb -= Math.floor(aux * (capabilityActive(59, UNSHADED) ? 1.0 : 0.5));

        var losses = Math.floor(warb * 0.5 * (capabilityActive(59, SHADED) ? 2.0 : 1.0));
        var finalLosses = losses;
        if (zone.roman_fort > 0) finalLosses = Math.floor(losses * 0.5);
        // 15 - Legio X
        if (capabilityActive(15, UNSHADED) && zone.roman_leader && zone.roman_legion) {
            finalLosses = Math.max(0, finalLosses--);
            if (capabilityActive(59, UNSHADED)) finalLosses = Math.max(0, finalLosses--);
        }

        if (finalLosses > zone.romanAuxilia()) {
            // losses > auxilia, so remaining hits are on leader/legion
            // check to see if retreat can help
            var retreatCap = zone.roman_tribe + zone.roman_fort + zone.romanAuxilia();
            var retreatLosses = Math.floor(losses * 0.5);
            // 15 - Legio X
            if (capabilityActive(15, UNSHADED) && zone.roman_leader && zone.roman_legion) {
                retreatLosses = Math.max(0, retreatLosses--);
                if (capabilityActive(59, UNSHADED)) retreatLosses = Math.max(0, retreatLosses--);
            }

            if (!canAmbush && retreatLosses <= retreatCap) {
                if (romanCanRetreat(zone, 'Aedui')) {
                    return (retreatLosses > retreatCap);
                } else
                    return true;
            } else
                return true;
        }
    }

    // Germanic?
    if (zone.aeduiForces() > 0) {
        // ambush + battle
        var aux = zone.romanAuxilia();
        var aux_hidden = zone.roman_auxilia;
        // 38 - Diviciacus
        if (hasDiviciacusPermission()) {
            aux += zone.aeduiWarband();
            aux_hidden += zone.aedui_warband;
        }
        
        var canAmbush = zone.germanic_warband > aux_hidden;
        if (canAmbush) {
            var warb = zone.germanicWarband();
            // 13 - Balearic Slingers
            if (capabilityActive(13, UNSHADED))
                // 59 - Germanic Horse
                warb -= Math.floor(aux * (capabilityActive(59, UNSHADED) ? 1.0 : 0.5));

            var losses = Math.floor(warb * 0.5);
            var finalLosses = losses;
            if (zone.roman_fort > 0) finalLosses = Math.floor(losses * 0.5);
            // 15 - Legio X
            if (capabilityActive(15, UNSHADED) && zone.roman_leader && zone.roman_legion) {
                finalLosses = Math.max(0, finalLosses--);
                if (capabilityActive(59, UNSHADED)) finalLosses = Math.max(0, finalLosses--);
            }
            
            if (finalLosses > aux) {
                // losses > auxilia, so remaining hits are on leader/legion
                return true;
            }
        }
    }

    romanRetreatAsk();
    
    return false;
}

function doRomanEmergencyBattleCheck() {
    var result = false;

    // condition 1: subdue?
    var zones = filterZones(zoneList(), function(zone) {
        consoleLog('8.8.1: check for subdue in ' + zone.name + '; ' + zone.status());
        return (zone.roman_legion || zone.roman_leader) && 
            battleCheckGaulPresence(zone);
    });
    if (zones.length > 0) result = zones;

    // condition 2: threat?  
    var zones = filterZones(zoneList(), function (zone) {
        consoleLog('8.8.1: check for threat in ' + zone.name + '; ' + zone.status());
        if (!zone.roman_legion && !zone.roman_leader) return false;
        var battleForceLoss = battleCheckEnemyForcesLoss(zone);
        consoleLog('8.8.1: threat in ' + zone.name + '? ' + battleForceLoss);
        return battleForceLoss;
    });
    if (interrupt) return false;
    if (zones.length > 0) result = result.concat(zones);

    return result;
}

function doRomanCanPlayEventCheck() {
    // check if by sequence of play (eligibility) Roman can play the event
    return game.roman_eligibility == 'Eligible Factions' &&
        (game.aedui_eligibility != '1st Faction Event' && game.aedui_eligibility != '1st Faction Command Only' &&
        !game.aedui_eligibility.startsWith('2nd ')) &&
        (game.arverni_eligibility != '1st Faction Event' && game.arverni_eligibility != '1st Faction Command Only' &&
        !game.arverni_eligibility.startsWith('2nd ')) &&
        (game.belgic_eligibility != '1st Faction Event' && game.belgic_eligibility != '1st Faction Command Only' &&
        !game.belgic_eligibility.startsWith('2nd '));
}

function canRomanRecruit() {
    // 8.8.4: see if Roman can recruit, return true / false only
    var aedui = game.aedui_resources;
    var resources = game.roman_resources;
    var aux_available = game.roman_auxilia_available;
    var allies_placed = 0;
    var aux_placed = 0;
    var activated = [];

    // Find valid placement regions for recruit
    var zonesAllies = filterZones(zoneList(), function (zone) {
        return (zone.roman_leader || zone.control() == 'Roman Control') &&
            zone.subduedTribesAvailable('Roman') > 0;
    });
    var zonesAuxSupply = filterZones(zoneList(), function (zone) {
        return (zone.roman_leader || zone.roman_tribe || zone.roman_fort) &&
            zone.inSupplyLine(false);
    });
    var zonesAuxNoSupply = filterZones(zoneList(), function (zone) {
        return (zone.roman_leader || zone.roman_tribe || zone.roman_fort) &&
            !zone.inSupplyLine(false);
    });

    // place allies
    for (var i = 0; i < zonesAllies.length; i++) {
        if (!activated.includes(zonesAllies[i])) {
            var zone = getZone(zonesAllies[i]);
            var valid = false;
            var insupply = zone.inSupplyLine(false);
            if (insupply) {
                valid = true;
                allies_placed++;
            } else {
                if (resources >= 2) {
                    valid = true;
                    allies_placed++;
                    if (game.aeduiNP && aedui > 8 && resources < 2) {
                        aedui -= 2;
                    } else {
                        resources -= 2;
                    }
                }
            }
            if (valid)
                activated.push(zone.name);
        }
    }
    if (allies_placed >= 2) return true;

    // place aux - in supply
    for (var i = 0; i < zonesAuxSupply.length; i++) {
        if (!activated.includes(zonesAllies[i])) {
            var zone = getZone(zonesAllies[i]);
            var valid = false;
            var insupply = zone.inSupplyLine(false);
            if (insupply) {
                valid = true;
                allies_placed++;
            } else {
                if (resources >= 2) {
                    valid = true;
                    allies_placed++;
                    if (game.aeduiNP && aedui > 8 && resources < 2) {
                        aedui -= 2;
                    } else {
                        resources -= 2;
                    }
                }
            }
            if (valid)
                activated.push(zone.name);
        }
    }
    if (aux_placed >= 3) return true;

    // place aux - ask for supply
    zonesAuxNoSupply = sortZonesClosestToSupplyLine(zonesAuxNoSupply);

    for (var i = 0; i < zonesAuxSupply.length; i++) {
        if (!activated.includes(zonesAllies[i])) {
            var zone = getZone(zonesAllies[i]);
            var valid = false;
            var insupply = zone.inSupplyLine(true);
            if (insupply) {
                valid = true;
                allies_placed++;
            } else {
                if (resources >= 2) {
                    valid = true;
                    allies_placed++;
                    if (game.aeduiNP && aedui > 8 && resources < 2) {
                        aedui -= 2;
                    } else {
                        resources -= 2;
                    }
                }
            }
            if (valid)
                activated.push(zone.name);
        }
    }
    if (interrupt) return false;
    if (aux_placed >= 3) return true;

    return false;
}

function doRoman() {
    game.faction = "Roman";

    // check answer
    if (hasAnswer()) {
        switch (answerdata.q) {
            case "retreat_permission":
                if (answerdata.options.indexOf(';') == -1) {
                    // single faction
                    game.permissions[answerdata.options] = answerdata.reply.toUpperCase() == 'YES';
                } else {
                    // multiple factions
                    var factions = answerdata.options.split(';');
                    var replies = answerdata.reply.split(';');
                    for (var f = 0; f < factions.length; f++) {
                        var faction = factions[f].toLowerCase();
                        var rf = false;
                        for (var r = 0; r < replies.length && !rf; r++)
                            rf = rf || replies[r].toLowerCase() == faction;
                        game.permissions[faction] = rf;
                    }
                    consoleLog(game.permissions);
                }
                break;
            case "diviciacus_permission":
                game.permissions['diviciacus'] = answerdata.reply.toUpperCase() == 'YES'; 
                break;
        }
    }

    while (game.state != '' && !interrupt) {
        var state = game.state;
        switch (state) {
        case "8.8.1":
            // 8.8.1: check for emergency battles or subdue opportunities
            var emergencyBattleSubdue = doRomanEmergencyBattleCheck();
            if (interrupt) return;

            if (emergencyBattleSubdue) {
                emergencyBattleSubdue = uniq(emergencyBattleSubdue);
                console.log('Battle in:', emergencyBattleSubdue);

                game.state = 'battle';
                game.battlecandidates = emergencyBattleSubdue;
            } else {
                game.state = '8.8.2';
            }
            break;
        case "8.8.2":
            // 8.8.2: check sequence of play for use of Event
            var canPlayEvent = doRomanCanPlayEventCheck();

            if (canPlayEvent) {
                game.state = '8.8.2-effective'
            } else {
                game.state = '8.8.3';
            }
            break;
        case '8.8.2-effective':
            // is the event effective?
            // check for icon on card
            var cardData = kCardIndex[game.currentcard.num];
            var hasSwords = false;
            for (var i = 0; i < cardData.length; i++)
                if (cardData[i] == 'RoS')
                    hasSwords = true;

            if (!hasSwords) {
                // check human answer
                if (hasAnswer() && answerdata.q == 'event-ineffective') {
                    if (answerdata.reply.toUpperCase() == 'YES') {
                        game.state = '8.8.3';
                    } else {
                        // execute the event
                        msgPush('# Execute the Unshaded event text (see 8.2.1)');
                        game.state = '';
                    }
                } else {
                    askQuestion(QUESTION_YESNO, 'event-ineffective', 'Is the event on \'' + game.currentcard.name + '\' ineffective?', '');
                }
            } else {
                game.state = '8.8.3';
            }
            break;
        case '8.8.3':
            // can't play event, should we March or Recuit?
            consoleLog('8.8.3: Roman Auxilia Available', game.roman_auxilia_available, '> 8 ?');
            if (game.roman_auxilia_available > 8) {
                game.state = 'recruit';
            } else {
                game.state = 'march';
            }
            break;
        case "battle":
            // Battle
            msgPush('TODO: Battle');
            game.state = '';
            break;
        case "march":
            // March
            msgPush('TODO: March');
            game.state = '';
            break;
        case "recruit":
            // Recruit
            var didRecruit = canRomanRecruit();
            if (interrupt) return;

            msgPush('TODO outcome of canRomanRecruit() =', didRecruit);
            game.state = '';
            break;
        case "seize":
            // Seize
            msgPush('TODO: Seize');
            game.state = '';
            break;
        }
    }
}