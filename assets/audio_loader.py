# Handles audio file request and returns appropriate directory path to parent file.
# NOTE: Only returns directory path as STRING and does NOT return AUDIO data!

assets = 'assets/audio'
effects = assets + '/effects/'
music = assets + '/music/'
menu_music = music + '/menus/'
gameplay_music = music + 'gameplay/'

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
impacts = general + 'impacts/'
interactions = general + 'interactions/'
menu_sounds = general + 'menu_sounds/'
negative_sounds = general + 'negative_sounds/'
pause_sounds = general + 'pause_sounds/'
positive_sounds = general + 'positive_sounds/'

movement = effects + 'movement/'
vehicles = movement + 'vehicles/'

weapons = effects + 'weapons/'
machine_guns = weapons + 'machine_guns/'


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


def explosion(length: str, ver: int):
    if length == 'medium':
        return exp_medium + 'sfx_exp_medium' + str(ver) + '.wav'
    else:
        raise ValueError('audio_loader.py | explosion length invalid | length = ' + str(length))


def alarm(ver: int):
    return alarms + 'sfx_alarm_loop' + str(ver) + '.wav'


def bleep(ver: int):
    return bleeps + 'sfx_sounds_blip' + str(ver) + '.wav'


def impact(ver: int):
    return impacts + 'sfx_sounds_impact' + str(ver) + '.wav'


def interaction(ver: int):
    return interactions + 'sfx_sounds_interaction' + str(ver) + '.wav'


def menu(ver: int, select=False):
    if not select:
        return menu_sounds + 'sfx_menu_move' + str(ver) + '.wav'
    else:
        return menu_sounds + 'sfx_menu_select' + str(ver) + '.wav'


def negative(category: str, ver: int):
    return negative_sounds + 'sfx_sounds_' + category + str(ver) + '.wav'


def pause_sound(ver: int, out=False):
    if out:
        return pause_sounds + 'sfx_sounds_pause' + str(ver) + '_out.wav'
    else:
        return pause_sounds + 'sfx_sounds_pause' + str(ver) + '_in.wav'


def positive(ver: int):
    return positive_sounds + 'sfx_sounds_powerup' + str(ver) + '.wav'


def vehicle(veh: str, ver=1):
    if veh == 'brakes':
        return vehicles + 'sfx_vehicle_breaks.wav'
    elif veh == 'car':
        return vehicles + 'sfx_vehicle_carloop' + str(ver) + '.wav'
    elif veh == 'engine':
        return vehicles + 'sfx_vehicle_engineloop.wav'
    else:
        raise ValueError('audio_loader | incorrect vehicle argument - ' + str(veh))


def machine_gun(ver: int):
    return machine_guns + 'sfx_wpn_machinegun_loop' + str(ver) + '.wav'
