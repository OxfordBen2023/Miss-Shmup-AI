from src.Config import *
from src.Utils.TextUtil import TextUtil
from sys import exit

import pygame

class Menu:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()
		self.toggle = False
		self.toggle_init = False
		self.menu_items = ['Continue', 'Restart', 'Quit']
		self.selected = 0
		self.FONT_DEFAULT = pygame.font.Font(FONT_PATH,60)

	# CBB : Could use the size and a less generic font object. 
	def write(self, screen, text, text_color, size,  x, y):
		img = self.FONT_DEFAULT.render(text, True, text_color)
		screen.blit(img, (x,y))

	def event_loop(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
			if event.type == pygame.KEYDOWN :
				# Menu navigation
				if event.key == pygame.K_DOWN :
					self.selected+=1
					# Infinite loop over menu elements
					if(self.selected > len(self.menu_items) -1 ):
						self.selected = 0
				if event.key == pygame.K_UP  :
					self.selected-=1
					if(self.selected == -1 ):
						self.selected = len(self.menu_items) -1
				# quitting Menu
				if event.key == pygame.K_m or event.key == pygame.K_ESCAPE:
					self.toggle = True
				# Any menu element is selected
				if event.key == pygame.K_RETURN:
					if self.selected == 0 :
						self.toggle = True
					if self.selected == 1:
						self.toggle = True
						self.toggle_init = True
					if self.selected == 2 :
						pygame.quit()
						exit()

	def build_menu(self):
		# Init
		spacing = 50
		startY = 50
		fontSize = 80
		positionY = startY
		# Blit the menu
		for index, choice in enumerate(self.menu_items) :
			color = 'black'
			if index == self.selected:
				color =  'white'
			self.write(self.display_surface, choice, color , fontSize, 50,  positionY)
			positionY += spacing
		
	def run (self ):
		self.display_surface.fill('grey')
		self.build_menu()
		self.event_loop()
