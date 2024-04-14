import pygame
from src.config import *
from src.game import *
from src.title import *
from src.menu import *

###################################################
##		Run this is to play the game.            ##
##		To train the model                       ##
##		run the agent.py file                    ##
###################################################

# Try turning AUTOMATIC_PLAY to True to see the manualy program avoidance in action 
AUTOMATIC_PLAY = False

class MissShmup():
	def __init__(self):
		pygame.init()
		self.display_surface = pygame.display.set_mode((RESOLUTION_X,RESOLUTION_Y))
		pygame.display.set_caption('Miss Shmup')
		self.clock = pygame.time.Clock()
		self.game = GameAI(auto_play = AUTOMATIC_PLAY)
		self.title = Title()
		self.menu = Menu()
		self.running_state = 'title'
		self.game_over = False

	def run(self):
		while True:

			# Switch from Title sreen to game
			if self.title.toggle == True:
				self.running_state = 'game'
				self.game.reinit()
				self.title.toggle = False

			# Switch from game to menu or gameover
			if self.game.toggle == True:
				if self.game_over: 
					self.running_state = 'title'
				else:
					self.running_state = 'menu'
				self.game.toggle = False
			
			# Switch from menu to game.
			if self.menu.toggle == True:
				self.running_state = 'game'
				if self.menu.toggle_init == True:
					self.game.reinit()
					self.menu.toggle_init = False
				self.menu.toggle = False

			# Run
			if self.running_state == 'title':
				self.title.run(self.game_over, self.game.score)
			elif self.running_state == 'game':
				self.game_over = self.game.run(0)[2]
			elif self.running_state == 'menu':
				self.menu.run()

			pygame.display.update()


if __name__ == '__main__':
	main = MissShmup()
	main.run()