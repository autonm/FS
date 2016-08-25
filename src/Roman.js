// AI

function battleCheckGaulPresence(zone) {
    // see if there is an enemy tribe / citadel / control
    var control = zoneControl(zone);
    return zone.aedui_tribe || zone.aedui_citadel || control == 'Aedui Control' ||
        zone.arverni_tribe || zone.arverni_citadel || control == 'Arverni Control' ||
        zone.belgic_tribe || zone.belgic_citadel || control == 'Belgic Control' ||
        zone.germanic_tribe || control == 'Germanic Control';
}

function belgicLeaderPresentOrAdjacent(zone) {
    if (zone.belgic_leader) return true;
    for (var adj in zone.adjacent) {
        if (getZone(adj).belgic_leader) return true;
    }
    return false;
}

function romanCanRetreat(zone, attacker) {
    // see if any adjacent zone can be retreated to
    // any roman control?
    for (var adj in zone.adjacent) {
        var control = zoneControl(adj);
        
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
    if (zoneBelgicForces(zone) > 0) {
        var rampage = (belgicLeaderPresentOrAdjacent(zone) && zone.belgic_warbands &&
                !zone.roman_fort && !zone.roman_leader);
        var rampageAuxilia = 0;
        var rampageLegion = 0;
        if  (rampage) {
            // rampage
            if (zoneRomanAuxilia())
                rampageAuxilia = 1;
            else
                rampageLegion = 1;
            
            if (!romanCanRetreat(zone, 'Belgic') && zone.roman_legion) return true;
        }

        // battle + ambush
        var canAmbush = belgicLeaderPresentOrAdjacent(zone) && (zone.belgic_warbands > zone.roman_auxilia);
        var halfLosses = zone.roman_fort > 0;
        var losses = zone.belgic_leader + Math.floor(zoneBelgicWarband(zone) * (zone.belgic_leader ? 1 : 0.5));
        if (halfLosses) losses = Math.floor(losses / 2);
        msgPush(canAmbush + ', ' + halfLosses);
        msgPush(zone.name + ': Belgic losses ' + losses);
        if (losses > zoneRomanAuxilia(zone)) {
            // losses > auxilia, so remaining hits are on leader/legion
            // check to see if retreat can help
            if (romanCanRetreat(zone, 'Belgic')) {
                if (!halfLosses) losses = Math.floor(losses / 2);

                return (losses > zone.roman_tribe + zone.roman_fort + zoneRomanAuxilia(zone));
            } else
                return true;
        }
    }

    // Arverni?
    if (zoneArverniForces(zone) > 0) {
        // TODO: devastate instead of rampage
        // var rampage = (arverniLeaderPresentOrAdjacent(zone) && zone.arverni_warbands &&
        //         !zone.roman_fort && !zone.roman_leader);
        // var rampageAuxilia = 0;
        // var rampageLegion = 0;
        // if  (rampage) {
        //     // TODO devastate!
        //     if (zoneRomanAuxilia())
        //         rampageAuxilia = 1;
        //     else
        //         rampageLegion = 1;
            
        //     if (!romanCanRetreat(zone, 'Belgic') && zone.roman_legion) return true;
        // }

        // battle + ambush
        var canAmbush = arverniLeaderPresentOrAdjacent(zone) && (zone.arverni_warbands > zone.roman_auxilia);
        var halfLosses = zone.roman_fort > 0;
        var losses = zone.arverni_leader + Math.floor(zoneArverniWarband(zone) * 0.5);
        if (halfLosses) losses = Math.floor(losses / 2);
        msgPush(canAmbush + ', ' + halfLosses);
        msgPush(zone.name + ': Arverni losses ' + losses);
        if (losses > zoneRomanAuxilia(zone)) {
            // losses > auxilia, so remaining hits are on leader/legion
            // check to see if retreat can help
            if (romanCanRetreat(zone, 'Arverni')) {
                if (!halfLosses) losses = Math.floor(losses / 2);

                return (losses > zone.roman_tribe + zone.roman_fort + zoneRomanAuxilia(zone));
            } else
                return true;
        }
    }

    // Aedui?
    if (zoneAeduiForces(zone) > 0) {
        // battle + ambush
        var canAmbush = zone.aedui_warbands > zone.roman_auxilia;
        var halfLosses = zone.roman_fort > 0;
        var losses = Math.floor(zoneAeduiWarband(zone) * 0.5);
        if (halfLosses) losses = Math.floor(losses / 2);
        msgPush(canAmbush + ', ' + halfLosses);
        msgPush(zone.name + ': Aedui losses ' + losses);
        if (losses > zoneRomanAuxilia(zone)) {
            // losses > auxilia, so remaining hits are on leader/legion
            // check to see if retreat can help
            if (romanCanRetreat(zone, 'Aedui')) {
                if (!halfLosses) losses = Math.floor(losses / 2);

                return (losses > zone.roman_tribe + zone.roman_fort + zoneRomanAuxilia(zone));
            } else
                return true;
        }
    }

    // Germanic?
    if (zoneAeduiForces(zone) > 0) {
        // battle + ambush
        var canAmbush = zone.germanic_warbands > zone.roman_auxilia;
        if (canAmbush) {
            var halfLosses = !canAmbush && (zone.roman_fort > 0);
            var losses = Math.floor(zoneAeduiWarband(zone) * 0.5);
            if (halfLosses) losses = Math.floor(losses / 2);
            msgPush(zone.name + ': Germanic losses ' + losses);
            if (losses > zoneRomanAuxilia(zone)) {
                // losses > auxilia, so remaining hits are on leader/legion
                return true;
            }
        }
    }

    romanRetreatAsk();
    if (interrupt) return false;

    return false;
}

function doRomanEmergencyBattleCheck() {
    var result = false;

    // condition 1: subdue?
    var zones = filterZones(zoneList(), function(zone) {
        return (zone.roman_legion || zone.roman_leader) && 
            battleCheckGaulPresence(zone);
    });
    // if (zones.length > 0) return true;

    // condition 2: threat?  
    var zones = filterZones(zoneList(), function (zone) {
        msgPush(zone.name + ": " + zone.roman_legion + ", " + zone.roman_leader);
        return (zone.roman_legion || zone.roman_leader) && 
            (battleCheckEnemyForcesLoss(zone));
    });
    if (interrupt) return false;

    return (zones.length > 0);
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

    if (game.state == '8.8.1') {
        // 8.8.1: check for emergency battles or subdue opportunities
        var emergencyBattleSubdue = doRomanEmergencyBattleCheck();
        if (interrupt) return;

        msgPush("?" + emergencyBattleSubdue);
    }
}