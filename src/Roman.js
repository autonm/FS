// AI

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
            if ('aedui' in game.retreatPermission && game.retreatPermission.aedui) return true;
            if (game.aeduiNP) return true;
            askFactions.aedui = true;
        } else if (control == 'Arverni Control' && attacker != 'Arverni') {
            if ('arverni' in game.retreatPermission && game.retreatPermission.arverni) return true;
            if (!game.arverniNP)
                askFactions.arverni = true;
        } else if (control == 'Belgic Control' && attacker != 'Belgic') {
            if ('belgic' in game.retreatPermission && game.retreatPermission.belgic) return true;
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
        if (!(f in game.retreatPermission)) {
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
        var rampage = (zone.belgicLeaderPresentOrAdjacent() && zone.belgic_warband &&
                !zone.roman_fort && !zone.roman_leader && zone.romanForces());
        var rampageAuxilia = 0;
        var rampageLegion = 0;
        if  (rampage) {
            // rampage
            rampageAuxilia = Math.min(zone.romanAuxilia(), zone.belgic_warband);
            if (rampageAuxilia < zone.belgic_warband)
                rampageLegion = Math.min(zone.roman_legion, zone.belgic_warband - rampageAuxilia);
            
            if (rampageLegion && !romanCanRetreat(zone, 'Belgic')) return true;

            // battle after rampage
            var aux = zone.romanAuxilia() - rampageAuxilia;
            var halfLosses = zone.roman_fort > 0;
            var losses = zone.belgicLosses();
            if (halfLosses) losses = Math.floor(losses / 2);
            if (losses > aux) {
                // losses > auxilia, so remaining hits are on leader/legion
                // check to see if retreat can help
                var retreatCap = zone.roman_tribe + zone.roman_fort + aux;
                var retreatLosses = halfLosses ? losses : Math.floor(losses / 2);
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
        var canAmbush = zone.belgicLeaderPresentOrAdjacent() && (zone.belgic_warband > zone.roman_auxilia);
        var halfLosses = zone.roman_fort > 0;
        var losses = zone.belgicLosses();
        if (halfLosses) losses = Math.floor(losses / 2);
        if (losses > zone.romanAuxilia()) {
            // losses > auxilia, so remaining hits are on leader/legion
            // check to see if retreat can help
            var retreatCap = zone.roman_tribe + zone.roman_fort + zone.romanAuxilia();
            var retreatLosses = halfLosses ? losses : Math.floor(losses / 2);
            if (retreatLosses <= retreatCap) {
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
            var romanLosses = Math.floor(roman / 3);
            var aux = zone.romanAuxilia() - romanLosses;
            if (aux < 0) {
                // must remove legion
                return true;
            }
            var warb = Math.floor(zone.arverniWarband() / 4);

            // battle after devastate
            var halfLosses = zone.roman_fort > 0;
            var losses = zone.arverniLosses();
            if (halfLosses) losses = Math.floor(losses / 2);
            if (losses > aux) {
                // losses > auxilia, so remaining hits are on leader/legion
                // check to see if retreat can help
                var retreatCap = zone.roman_tribe + zone.roman_fort + aux;
                var retreatLosses = halfLosses ? losses : Math.floor(losses / 2);
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
        var canAmbush = zone.arverniLeaderPresentOrAdjacent() && (zone.arverni_warband > zone.roman_auxilia);
        var halfLosses = zone.roman_fort > 0;
        var losses = zone.arverniLosses();
        if (halfLosses) losses = Math.floor(losses / 2);
        if (losses > zone.romanAuxilia()) {
            // losses > auxilia, so remaining hits are on leader/legion
            // check to see if retreat can help
            var retreatCap = zone.roman_tribe + zone.roman_fort + zone.romanAuxilia();
            var retreatLosses = halfLosses ? losses : Math.floor(losses / 2);
            if (retreatLosses <= retreatCap) {
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
        var halfLosses = zone.roman_fort > 0;
        var losses = zone.aeduiLosses();
        if (halfLosses) losses = Math.floor(losses / 2);
        if (losses > zone.romanAuxilia()) {
            // losses > auxilia, so remaining hits are on leader/legion
            // check to see if retreat can help
            var retreatCap = zone.roman_tribe + zone.roman_fort + zone.romanAuxilia();
            var retreatLosses = halfLosses ? losses : Math.floor(losses / 2);
            if (retreatLosses <= retreatCap) {
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
        var canAmbush = zone.germanic_warband > zone.roman_auxilia;
        if (canAmbush) {
            var halfLosses = !canAmbush && (zone.roman_fort > 0);
            var losses = zone.germanicLosses();
            if (halfLosses) losses = Math.floor(losses / 2);
            if (losses > zone.romanAuxilia()) {
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
        console.log('8.8.1: check for subdue in ' + zone.name + '; ' + zone.status());
        return (zone.roman_legion || zone.roman_leader) && 
            battleCheckGaulPresence(zone);
    });
    // if (zones.length > 0) return true;

    // condition 2: threat?  
    var zones = filterZones(zoneList(), function (zone) {
        console.log('8.8.1: check for threat in ' + zone.name + '; ' + zone.status());
        if (!zone.roman_legion && !zone.roman_leader) return false;
        var battleForceLoss = battleCheckEnemyForcesLoss(zone);
        console.log('8.8.1: threat in ' + zone.name + '? ' + battleForceLoss);
        return battleForceLoss;
    });
    if (interrupt) return false;

    return (zones.length > 0);
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

function doRoman() {
    game.faction = "Roman";

    // check answer
    if (answer.length > 0) {
        switch (answerdata.q) {
            case "retreat_permission":
                if (answerdata.options.indexOf(';') == -1) {
                    // single faction
                    game.retreatPermission[answerdata.options] = answerdata.reply.toUpperCase() == 'YES';
                } else {
                    // multiple factions
                    var factions = answerdata.options.split(';');
                    var replies = answerdata.reply.split(';');
                    for (var f = 0; f < factions.length; f++) {
                        var faction = factions[f].toLowerCase();
                        var rf = false;
                        for (var r = 0; r < replies.length && !rf; r++)
                            rf = rf || replies[r].toLowerCase() == faction;
                        game.retreatPermission[faction] = rf;
                    }
                    console.log(game.retreatPermission);
                }
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
                game.state = 'battle';
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
                if (answer.length > 0 && answerdata.q == 'event-ineffective') {
                    if (answerdata.reply.toUpperCase() == 'YES') {
                        game.state = '8.8.3';
                    } else {
                        // execute the event
                        msgPush('# Execute the Unshaded event text (see 8.2.1)');
                        game.state = '';
                    }
                } else {
                    askQuestion(QUESTION_YESNO, 'event-ineffective', 'Is the event ineffective?', '');
                }
            } else {
                game.state = '8.8.3';
            }
            break;
        case '8.8.3':
            // can't play event, should we March or Recuit?
            console.log('8.8.3: ' + game.roman_auxilia_available);
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
            msgPush('TODO: Recruit');
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