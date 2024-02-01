from ..Config import *
import pygame

class TextUtil():

	def write(self, screen, text, text_color, size,  x, y):
		font = pygame.font.Font(FONT_DEFAULT , size)
		img = font.render(text, True, text_color)
		screen.blit(img, (x,y))
