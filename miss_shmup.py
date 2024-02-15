import pygame
from game import GameAI
from src.Config import *

###################################################
##		This is to test the manuel mode          ##
##		To test the ai controled: run 'agent.py' ##
##		It will be too fast for human :          ##
##		SPEED is in game.py                      ##
###################################################


class MissShmup():
	def __init__(self):
		pygame.init()
		self.display_surface = pygame.display.set_mode((RESOLUTION_X,RESOLUTION_Y))
		pygame.display.set_caption('Miss Shmup')
		self.clock = pygame.time.Clock()
		self.game = GameAI()
		self.startTime = 0

	def run(self):
		while True:
			if self.game.toggle == True:
				# REINIT Game
				self.game = GameAI()
				self.startTime = pygame.time.get_ticks()
				self.game.toggle = False

			# runing the game	
			self.game.run(0)

			pygame.display.update()


if __name__ == '__main__':
	main = MissShmup()
	main.run()