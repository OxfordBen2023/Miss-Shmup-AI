from src.Config import *
import pygame

class Bullet(pygame.sprite.Sprite):
	def __init__(self,emit):
		super().__init__()
		self.image = pygame.Surface([7, 7])
		self.image.fill((230,230,230))
		self.rect = self.image.get_rect(center = (emit))

	def shoot_forward(self):
		self.rect.x += 20

	def update(self):
		self.shoot_forward()
		self.destroy()

	def destroy(self):
		if self.rect.x < 0 or self.rect.x >RESOLUTION_X or self.rect.y < 0 or self.rect.y > RESOLUTION_Y :
			self.kill()
