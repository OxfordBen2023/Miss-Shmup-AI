import pygame
from src.Config import *

class Title():
	def __init__(self):
		self.FONT_DEFAULT =  pygame.font.Font(FONT_PATH, 80)
		self.toggle = False
		self.display_surface = pygame.display.get_surface()

		self.img = pygame.image.load('assets/graphics/tittle_screen.png')
		self.img_rect = self.img.get_rect(center = (RESOLUTION_X/2,180))

		self.game_name = self.FONT_DEFAULT.render('Miss Shmup',False,'white')
		self.game_name_rect = self.game_name.get_rect(center = (RESOLUTION_X/2,50))
		self.game_message = self.FONT_DEFAULT.render('Press space to start',False,'white')
		self.game_over_message = self.FONT_DEFAULT.render('Press space to retry',False,'white')
		self.game_message_rect = self.game_message.get_rect(center = (RESOLUTION_X/2,330))


	def run(self, gameover, score):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
			if event.type == pygame.KEYDOWN :
				if event.key == pygame.K_SPACE:
					self.toggle = True
		self.display_surface.fill('grey')
		self.display_surface.blit(self.img, self.img_rect )
		if gameover:
			self.game_name = self.FONT_DEFAULT.render(f'Score : {score}',False,'white')
			self.game_name_rect = self.game_name.get_rect(center = (RESOLUTION_X/2,50))
			self.display_surface.blit(self.game_name, self.game_name_rect)
			self.display_surface.blit(self.game_over_message, self.game_message_rect)
		else:
			self.display_surface.blit(self.game_name, self.game_name_rect)
			self.display_surface.blit(self.game_message, self.game_message_rect)