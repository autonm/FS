// AI

function battleCheckGaulPresence(zone) {
    // see if there is an enemy tribe / citadel / control
    var control = zoneControl(zone);
    return zone.aedui_tribe || zone.aedui_citadel || control == 'Aedui Control' ||
        zone.arverni_tribe || zone.arverni_citadel || control == 'Arverni Control' ||
        zone.belgic_tribe || zone.belgic_citadel || control == 'Belgic Control' ||
        zone.germanic_tribe || control == 'Germanic Control';
}

function battleCheckEnemyForcesLoss(zone) {
    // check if enemy presence could force a loss on Roman Leader or Legion
    
}

function doRomanEmergencyBattleCheck() {
    var result = false;

    // condition: 1
    var zones = filterZones(zoneList(), function (zone) {
        return (zone.roman_legion || zone.roman_leader) && 
            (battleCheckGaulPresence(zone) &&
            (battleCheckEnemyForcesLoss(zone)));
    });
}

function doRoman() {
    // 8.8.1: check for emergency battle
    var emergencyBattle = doRomanEmergencyBattleCheck();
}