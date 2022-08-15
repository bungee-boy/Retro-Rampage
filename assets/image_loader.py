# Handles assets requests and returns appropriate directory path to parent file
# NOTE: Only returns directory path as STRING and does NOT return IMAGE data!

assets = 'assets/images'
animations = assets + '/animations'
cars = assets + '/cars'
objects = assets + '/objects'
powerups = assets + '/powerups'
tiles = assets + '/tiles'


def icon():
    return assets + '/icon.ico'


def animation(ver: str, frame: str or int):
    if ver == 'lightning':
        return animations + '/lightning/frame_' + str(frame) + '.png'
    else:
        raise ValueError('Incorrect animation ver: ' + str(ver))


def controller():
    return objects + '/controller.png'


def controller_button(ver: str):
    return objects + '/controller_button_' + ver.lower() + '.png'


def car(colour: str or tuple[int, int, int], ver: str or int):
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
    return cars + '/car_' + colour + '_' + str(ver) + '.png'


def car_damage(ver: str, dmg: int or str):
    return cars + '/' + str(ver).replace(' ', '_').lower() + '_damage_' + str(dmg) + '.png'


def traffic_light(ver: int or str):
    return objects + '/traffic_light_' + str(ver) + '.png'


def power_up(ver: str, active=True):
    if active:
        return powerups + '/' + ver + '_1.png'
    else:
        return powerups + '/' + ver + '_0.png'


def tile(material, ver: int or str):
    if material == 'dirt':
        if ver < 10:
            return tiles + '/dirt/land_dirt0' + str(ver) + '.png'
        else:
            return tiles + '/dirt/land_dirt' + str(ver) + '.png'

    elif material == 'dirt road':
        if ver < 10:
            return tiles + '/dirt_road/road_dirt0' + str(ver) + '.png'
        else:
            return tiles + '/dirt_road/road_dirt' + str(ver) + '.png'

    elif material == 'road':
        if ver < 10:
            return tiles + '/road/road_asphalt0' + str(ver) + '.png'
        else:
            return tiles + '/road/road_asphalt' + str(ver) + '.png'

    elif material == 'sand':
        if ver < 10:
            return tiles + '/sand/land_sand0' + str(ver) + '.png'
        else:
            return tiles + '/sand/land_sand' + str(ver) + '.png'

    elif material == 'sand road':
        return tiles + '/sand_road/road_sand' + str(ver) + '.png'
