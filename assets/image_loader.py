# Handles assets requests and returns appropriate directory path to parent file
# NOTE: Only returns directory path as STRING and does NOT return IMAGE data!

assets = 'assets/images'
animations = assets + '/animations'
cars = assets + '/cars'
characters = assets + '/characters'
motorcycles = assets + '/motorcycles'
objects = assets + '/objects'
powerups = assets + '/powerups'
tiles = assets + '/tiles'


def icon():
    return assets + '/icon.ico'


def animation(ver: str, frame: str or int):
    frame = str(frame)
    if ver == 'lightning':
        return animations + '/lightning/frame_' + frame + '.png'


def controller():
    return objects + '/controller.png'


def controller_button(ver: str):
    ver = ver.lower()
    return objects + '/controller_button_' + ver + '.png'


def car(colour: str or tuple[int, int, int], ver: str or int, small=False):
    if type(colour) == tuple:  # If colour is not string then convert
        if colour == (232, 106, 23) or colour == (255, 0, 0):
            colour = 'red'
        elif colour == (255, 204, 0) or colour == (255, 255, 0):
            colour = 'yellow'
        elif colour == (57, 194, 114) or colour == (0, 255, 0):
            colour = 'green'
        elif colour == (47, 149, 208) or colour == (0, 0, 255):
            colour = 'blue'
        elif colour == (93, 91, 91) or colour == (0, 0, 0):
            colour = 'black'
        else:
            raise ValueError('colour could not be found: ' + str(colour))
    if type(ver) == str:
        ver = ver.lower()
        if ver == 'family car':
            ver = '1'
        elif ver == 'sports car':
            ver = '2'
        elif ver == 'luxury car':
            ver = '3'
        elif ver == 'truck':
            ver = '4'
        elif ver == 'race car':
            ver = '5'
        else:
            raise ValueError('Car could not be found: ' + str(ver))
    ver = str(ver)
    if small:
        return cars + '/car_' + colour + '_small_' + ver + '.png'
    else:
        return cars + '/car_' + colour + '_' + ver + '.png'


def car_damage(ver: str, dmg: int or str):
    ver = str(ver).replace(' ', '_').lower()
    return cars + '/' + ver + '_damage_' + str(dmg) + '.png'


def bike(colour: str):
    return motorcycles + '/motorcycle_' + colour + '.png'


def char(colour: str, racer=False):
    if racer:
        return characters + '/racer_' + colour + '.png'
    else:
        return characters + '/character_' + colour + '.png'


def arrow(colour: str):
    return objects + '/arrow_' + colour + '.png'


def barrel(colour: str, lying=False):
    if lying:
        return objects + '/barrel_' + colour + '_down.png'
    else:
        return objects + '/barrel_' + colour + '.png'


def barrier(colour: str, race=False):
    if race:
        return objects + '/barrier_' + colour + '_race.png'
    else:
        return objects + '/barrier_' + colour + '.png'


def cone(lying=False):
    if lying:
        return objects + '/cone_down.png'
    else:
        return objects + '/cone_straight.png'


def light(ver: str):
    ver = str(ver)
    if ver == 'white':
        return objects + '/light_white.png'
    elif ver == 'yellow':
        return objects + '/light_yellow.png'
    elif ver == 'street':
        return objects + '/lights.png'
    else:
        raise ValueError("[light] ver != 'white' or 'yellow' or 'street'")


def traffic_light(ver: int or str):
    ver = str(ver)
    return objects + '/traffic_light_' + ver + '.png'


def oil():
    return objects + 'oil.png'


def rock(ver: int or str):
    ver = str(ver)
    return objects + 'rock' + ver + '.png'


def skid_mark(ver: int or str, long=False):
    ver = str(ver)
    if long:
        return objects + '/skidmark_long_' + ver + '.png'
    else:
        return objects + '/skidmark_short_' + ver + '.png'


def tent(colour: str, race=False):
    if race:
        return objects + '/tent_' + colour + '_large.png'
    else:
        return objects + '/tent_' + colour + '.png'


def tire(colour: str, filled=False):
    if filled:
        return objects + '/tires_' + colour + '_alt.png'
    else:
        return objects + '/tires_' + colour + '.png'


def tree(small=False):
    if small:
        return objects + '/tree_small.png'
    else:
        return objects + '/tree_large.png'


def tribune(full=True):
    if full:
        return objects + '/tribune_full.png'
    else:
        return objects + '/tribune_empty.png'


def tribune_overhang(striped=True):
    if striped:
        return objects + '/tribune_overhang_striped.png'
    else:
        return objects + '/tribune_overhang_red.png'


def power_up(ver: str, active=True):
    ver = str(ver)
    if active:
        return powerups + '/' + ver + '_1.png'
    else:
        return powerups + '/' + ver + '_0.png'


def tile(material, ver: int or str):
    if material == 'dirt':
        if ver < 10:
            ver = str(ver)
            return tiles + '/dirt/land_dirt0' + ver + '.png'
        else:
            ver = str(ver)
            return tiles + '/dirt/land_dirt' + ver + '.png'

    elif material == 'dirt road':
        if ver < 10:
            ver = str(ver)
            return tiles + '/dirt_road/road_dirt0' + ver + '.png'
        else:
            ver = str(ver)
            return tiles + '/dirt_road/road_dirt' + ver + '.png'

    elif material == 'grass':
        if ver < 10:
            ver = str(ver)
            return tiles + '/grass/land_grass0' + ver + '.png'
        else:
            ver = str(ver)
            return tiles + '/grass/land_grass' + ver + '.png'

    elif material == 'road':
        if ver < 10:
            ver = str(ver)
            return tiles + '/road/road_asphalt0' + ver + '.png'
        else:
            ver = str(ver)
            return tiles + '/road/road_asphalt' + ver + '.png'

    elif material == 'sand':
        if ver < 10:
            ver = str(ver)
            return tiles + '/sand/land_sand0' + ver + '.png'
        else:
            ver = str(ver)
            return tiles + '/sand/land_sand' + ver + '.png'

    elif material == 'sand road':
        if ver < 10:
            ver = str(ver)
            return tiles + '/sand_road/road_sand0' + ver + '.png'
        else:
            ver = str(ver)
            return tiles + '/sand_road/road_sand' + ver + '.png'
