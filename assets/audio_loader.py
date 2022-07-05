# Handles audio file request and returns appropriate directory path to parent file.
# NOTE: Only returns directory path as STRING and does NOT return AUDIO data!

assets = 'assets/audio'
effects = assets + '/effects/'
music = assets + '/music/'
menu_music = music + '/menus/'
gameplay_music = music + 'gameplay/'

screams = effects + '/death_screams/'

explosions = effects + '/explosions/'
exp_cluster = explosions + 'clusters/'
exp_double = explosions + 'double/'
exp_long = explosions + 'long/'
exp_medium = explosions + 'medium/'
exp_odd = explosions + 'odd/'
exp_short = explosions + 'short/'
exp_shortest = explosions + 'shortest/'
exp_various = explosions + 'various/'

general = effects + 'general/'
alarms = general + 'alarms/'
bleeps = general + 'bleeps/'
buttons = general + 'buttons/'
coins = general + 'coins/'
damages = general + 'damage_sounds/'
fanfares = general + 'fanfares/'
high_pitches = general + 'high_pitched/'
impacts = general + 'impacts/'
interactions = general + 'interactions/'
menu_sounds = general + 'menu_sounds/'
misc_sounds = general + 'misc_sounds/'
negative_sounds = general + 'negative_sounds/'
neutral_sounds = general + 'neutral_sounds/'
pause_sounds = general + 'pause_sounds/'
positive_sounds = general + 'positive_sounds/'

movement = effects + 'movement/'
doors = movement + 'doors/'
falling_sounds = movement + 'falling_sounds/'
footsteps = movement + 'footsteps/'
jumps = movement + 'jumps/'
ladders = movement + 'ladders/'
portals = movement + 'portals/'
stairs = movement + 'stairs/'
vehicles = movement + 'vehicles/'

weapons = effects + 'weapons/'
cannons = weapons + 'cannons/'
grenades = weapons + 'grenade_whistles/'
lasers = weapons + 'lasers/'
machine_guns = weapons + 'machine_guns/'
melees = weapons + 'melee/'
out_of_ammo_dir = weapons + 'out_of_ammo/'
shotguns = weapons + 'shotgun/'
single_shots = weapons + 'single_shots/'


def menu_track(track_no: int):
    if track_no == 0:
        return menu_music + 'chiptune_racer.mp3'
    elif track_no == 1:
        return menu_music + 'cruise_control.mp3'
    elif track_no == 2:
        return menu_music + 'final_lap.mp3'
    elif track_no == 3:
        return menu_music + 'lets_ride.mp3'
    elif track_no == 4:
        return menu_music + 'night_race.mp3'
    elif track_no == 5:
        return menu_music + 'retired_racer.mp3'
    elif track_no == 6:
        return menu_music + 'rival_racer.mp3'
    elif track_no == 7:
        return menu_music + 'select_your_vehicle.mp3'
    elif track_no == 8:
        return menu_music + 'start_your_engines.mp3'
    elif track_no == 9:
        return menu_music + 'the_championship.mp3'
    elif track_no == 10:
        return menu_music + 'track_selection.mp3'
    elif track_no == 11:
        return menu_music + 'upgrades.mp3'
    else:
        raise ValueError('audio_loader.py | track_no is not between 0 and 12')


def game_track(track_no: int):
    if track_no == 0:
        return gameplay_music + 'intro.wav'
    elif track_no == 1:
        return gameplay_music + 'lap_1.wav'
    elif track_no == 2:
        return gameplay_music + 'lap_2.wav'
    elif track_no == 3:
        return gameplay_music + 'lap_3.wav'
    elif track_no == 4:
        return gameplay_music + 'leaderboard.wav'
    else:
        raise ValueError('audio_loader.py | track_no is not between 0 and 4')


def scream(humanoid: str, ver: int):
    if humanoid == 'alien':
        return screams + 'sfx_deathscream_alien' + str(ver) + '.wav'
    elif humanoid == 'android':
        return screams + 'sfx_deathscream_android' + str(ver) + '.wav'
    elif humanoid == 'human':
        return screams + 'sfx_deathscream_human' + str(ver) + '.wav'
    elif humanoid == 'robot':
        return screams + 'sfx_deathscream_robot' + str(ver) + '.wav'
    else:
        raise ValueError('audio_loader.py | humanoid is not [alien, android, human, robot]')


def explosion(length: str, ver: int, hard=False):
    if length == 'cluster':
        return exp_cluster + 'sfx_exp_cluster' + str(ver) + '.wav'
    elif length == 'double':
        return exp_double + 'sfx_exp_double' + str(ver) + '.wav'
    elif length == 'long':
        return exp_long + 'sfx_exp_long' + str(ver) + '.wav'
    elif length == 'medium':
        return exp_medium + 'sfx_exp_medium' + str(ver) + '.wav'
    elif length == 'short':
        if hard:
            return exp_short + 'sfx_exp_short_hard' + str(ver) + '.wav'
        else:
            return exp_short + 'sfx_exp_short' + str(ver) + '.wav'
    elif length == 'shortest':
        if hard:
            return exp_shortest + 'sfx_exp_shortest_hard' + str(ver) + '.wav'
        else:
            return exp_shortest + 'sfx_exp_shortest_soft' + str(ver) + '.wav'
    elif length == 'odd':
        return exp_odd + 'sfx_exp_odd' + str(ver) + '.wav'
    elif length == 'various':
        return exp_various + 'sfx_exp_various' + str(ver) + '.wav'
    else:
        raise ValueError('audio_loader.py | explosion length invalid | length = ' + str(length))


def alarm(ver: int, low_health=False):
    if low_health:
        return alarms + 'sfx_lowhealth_alarmloop' + str(ver) + '.wav'
    else:
        return alarms + 'sfx_alarm_loop' + str(ver) + '.wav'


def bleep(ver: int):
    return bleeps + 'sfx_sounds_blip' + str(ver) + '.wav'


def button(ver: int):
    return buttons + 'sfx_sounds_button' + str(ver) + '.wav'


def coin(ver: int, amount: str):
    if amount == 'cluster':
        return coins + 'sfx_coin_cluster' + str(ver) + '.wav'
    elif amount == 'double':
        return coins + 'sfx_coin_double' + str(ver) + '.wav'
    else:
        return coins + 'sfx_coin_single' + str(ver) + '.wav'


def damage(ver: int):
    return damages + 'sfx_damage_hit' + str(ver) + '.wav'


def fanfare(ver: int):
    return fanfares + 'sfx_sounds_fanfare' + str(ver) + '.wav'


def high_pitch(ver: int):
    return high_pitches + 'sfx_sounds_high' + str(ver) + '.wav'


def impact(ver: int):
    return impacts + 'sfx_sounds_impact' + str(ver) + '.wav'


def interaction(ver: int):
    return interactions + 'sfx_sounds_interaction' + str(ver) + '.wav'


def menu(ver: int, select=False):
    if not select:
        return menu_sounds + 'sfx_menu_move' + str(ver) + '.wav'
    else:
        return menu_sounds + 'sfx_menu_select' + str(ver) + '.wav'


def misc(sound_name: str):
    return misc_sounds + 'sfx_sound_' + str(sound_name) + '.wav'


def negative(category: str, ver: int):
    return negative_sounds + 'sfx_sounds_' + category + str(ver) + '.wav'


def neutral(ver: int):
    return neutral_sounds + 'sfx_sound_neutral' + str(ver) + '.wav'


def pause_sound(ver: int, out=False):
    if out:
        return pause_sounds + 'sfx_sounds_pause' + str(ver) + '_out.wav'
    else:
        return pause_sounds + 'sfx_sounds_pause' + str(ver) + '_in.wav'


def positive(ver: int):
    return positive_sounds + 'sfx_sounds_powerup' + str(ver) + '.wav'


def door(ver: int):
    return doors + 'sfx_movement_door' + str(ver) + '.wav'


def falling(ver: int):
    return falling_sounds + 'sfx_sounds_falling' + str(ver) + '.wav'


def footstep(ver: int, loop=False, fast=False):
    if loop:
        if fast:
            return footsteps + 'sfx_movement_footstepsloop' + str(ver) + 'fast.wav'
        else:
            return footsteps + 'sfx_movement_footstepsloop' + str(ver) + 'slow.wav'
    else:
        return footsteps + 'sfx_movement_footsteps' + str(ver) + '.wav'


def jump(ver: int, landing=False):
    if landing:
        return jumps + 'sfx_movement_jump' + str(ver) + '_landing.wav'
    else:
        return jumps + 'sfx_movement_jump' + str(ver) + '.wav'


def ladder(ver: int, loop=False):
    if loop:
        return ladders + 'sfx_movement_ladder' + str(ver) + 'loop.wav'
    else:
        return ladders + 'sfx_movement_ladder' + str(ver) + '.wav'


def portal(ver: int):
    return portals + 'sfx_movement_portal' + str(ver) + '.wav'


def stair(ver: int, loop=False):
    if loop:
        return stairs + 'sfx_movement_stairs' + str(ver) + 'loop.wav'
    else:
        return stairs + 'sfx_movement_stairs' + str(ver) + '.wav'


def vehicle(veh: str, ver: int):
    if veh == 'breaks':
        return vehicles + 'sfx_vehicle_breaks.wav'
    elif veh == 'car':
        return vehicles + 'sfx_vehicle_carloop' + str(ver) + '.wav'
    elif veh == 'engine':
        return vehicles + 'sfx_vehicle_engineloop.wav'
    elif veh == 'helicopter':
        return vehicles + 'sfx_vehicle_helicopterloop' + str(ver) + '.wav'
    elif veh == 'plain':
        return vehicles + 'sfx_vehicle_plainloop.wav'
    else:
        raise ValueError('audio_loader | incorrect vehicle argument - ' + str(veh))


def cannon(ver: int):
    return cannons + 'sfx_wpn_cannon' + str(ver) + '.wav'


def grenade(ver: int):
    return grenades + 'sfx_wpn_grenadewhistle' + str(ver) + '.wav'


def missile_launch():
    return cannons + 'sfx_wpn_missilelaunch.wav'


def laser(ver: int):
    return lasers + 'sfx_wpn_laser' + str(ver) + '.wav'


def machine_gun(ver: int):
    return machine_guns + 'sfx_wpn_machinegun_loop' + str(ver) + '.wav'


def melee(weapon: str, ver: int):
    if weapon == 'dagger':
        return melees + 'sfx_wpn_dagger.wav'
    elif weapon == 'punch':
        return melees + 'sfx_wpn_punch' + str(ver) + '.wav'
    elif weapon == 'sword':
        return melees + 'sfx_wpn_sword' + str(ver) + '.wav'
    else:
        raise ValueError('audio_loader | incorrect weapon argument - ' + str(weapon))


def out_of_ammo(ver: int):
    return out_of_ammo_dir + 'sfx_wpn_no_ammo' + str(ver) + '.wav'


def reload():
    return out_of_ammo_dir + 'sfx_wpn_reload.wav'


def shotgun(ver: int):
    return shotguns + 'sfx_weapon_shotgun' + str(ver) + '.wav'


def single_shot(ver: int):
    return single_shots + 'sfx_weapon_single_shot' + str(ver) + '.wav'
