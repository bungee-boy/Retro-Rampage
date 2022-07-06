# Retro Rampage

Welcome to Retro Rampage! A 2D multiplayer racing game developed using [pygame](https://www.pygame.org/news).

![Intro screenshot](/docs/Screenshots/Gameplay_new.PNG 'In-game screenshot of intro screen')

### Index
- Game summary
- Installation
- Settings
- Credits

## Game summary
Retro Rampage is a 2D racing game that can be played with friends or race against the built-in NPCs.  
The game was created as a Computer Science A-level project,  
but was always intended to be supported long after the course had finished.

It can handle a maximum of 6 players simultaneously and offers a mix of controllers and/or keyboard for controls  
(eg. One person could use WASD/Arrow controls while 3 others use controllers).  
If there are less than 6 players then the rest of the spaces can also be filled in with an optional amount of NPCs.

![Gameplay screenshot](/docs/Screenshots/Gameplay_new.PNG 'Screenshot of an in-game race')

The game features a simplistic design with forwards, backwards left and right controls being the only input,  
however players have the option to enable powerups which can give them an advantage or disadvantage,  
depending on the type they pick up. (NPCs never pick up powerups)

As this game is only 2D and runs purely in Python 3, it is very performant and has several features to try and improve  
on the amount of processing power this game needs to run such as slowing down screen updates if the user tabbs out  
which dramatically decreases the amount of processing the game uses when it is running.

### Vehicles
There are 5 types of cars:
- Family car
- Sports car
- Luxury car
- Truck
- Race car

All cars have different attribues related to them that affect how they behave:  
Speed determines how fast the car goes with no damage  
Cornering determines how fast the car turns for corners  
Durability is the amount of hits or 'damage' the vehicle can take before it is at the slowest speed.
Damage can be obtained by making contact with an object such as the track barrier or another vehicle,  
and is also used by powerups.

Each car also has a choice of 5 colours:
- Red
- Green
- Yellow
- Blue
- Black

NPCs can also be forced to pick a car and colour if the player wants a better contrast between players and non-players.

![Choose vehicle screenshot](/docs/Screenshots/Choose_player_1.PNG 'Screenshot of a player choosing their vehicle')

### Powerups
As mentioned above, powerups can only be used by the player(s) and spawn randomly on the track during a race (if enabled).
There are 4 types of powerups, and not all provide an advantage:
- Repair (Repairs and removes a player's damage)
- Boost (Gives the player a temporary speed boost)
- Lightning (Randomly causes an NPC to crash)
- Bullet (Penalises the player, as if they had been hit by a lightning by not allowing them to move for a time)

![Powerups tutorial screenshot](/docs/Screenshots/Credits_new.PNG 'Screenshot of powerups tutorial')

The spawn rates of powerups is determined by the amount of players and NPCs on the track (less vehicles = less powerups).  
All time related powerups such as the Boost and Bullet are determined by the player's current speed so that  
if a player was in a Race car (speed 5) with no damage then they will have a short Boost, however if the same car is damaged  
and therefore has a speed of 1 they will have a much longer Boost time and will always return to the same speed after a boost.  


## Installation
As this game is still in development, the 'dev-build' only contains the .py version of the game,  
however the 'main' or release version of the game (will) contain an installer that will either fetch the  
.exe file for Windows or .py version for other plaforms. However as python is commonly already installed on most OSs,  
it should run without the installation of python. Furthermore, if the game is launched and fails to `import pygame` then  
a prompt or the user will show and ask them to try and automatically install it for them to minimise hassle.

## Settings
Currently the game includes several settings related to video, audio and optional features.  
The settings that are implemented so far are:
- Resolution option including presets and 'auto' option
- Screen option for multiple monitor setups
- Menu animations can be toggled on or off
- Music volume
- Sound effects volume
- Mute all sound toggle
- Debug mode toggle

All settings are self explanatory except for 'Debug mode', which is used during development and changes the following features:
- Error handling is turned off (requires restart to work)
- Outlines of almost all assets and drawings are shown (where applicable)
- The mouse is always shown and doesn't get hidden during races
- The game will always update the entire screen rather than adaptively changing only the parts that have changed
! Note: As there are a lot more things to draw on the screen (all the outlines) turning Debug mode on  
        will result in a performance drop on low-end machines.

## Credits
- Development and testing -> Anthony Guy
- Game art -> Kenney Vleugels
- Menu music -> Trevor Lentz
- Gameplay music & Sonund effects -> Juhani Junkala
- Guidance & Support -> Jonny Farmer & Keith Brown

![Credits screenshot](/docs/Screenshots/Credits_new.PNG 'Screenshot of credits screen')
