import os

RESOLUTION_X = 800
RESOLUTION_Y = 400

MENU_BG_COLOR = (155, 155, 155)
MENU_DEFAULT_TEXT_COLOR = (50, 50, 50)
MENU_SELECTED_TEXT_COLOR = (200, 200, 200)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__+ '/../'))
NO_MENU_SCREEN = True
FONT_PATH = ROOT_DIR + '/assets/font/Pixeltype.ttf'

#def clamp01(value):
#    return max(min(value, 1), 0)