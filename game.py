import pygame
from sys import exit

from src.Player import Player
from src.Enemy import Enemy
from src.Bullet import Bullet
from src.Impact import Impact
from src.Config import *

#REWARDS
# Die by collision 0 (to implement better later)
# Kill enemy +10
# Max the game +50
# score 4/5 ==> +5
# score < 4 ==> -10

# ACTION
# Move up
# Move down
# fire

# STATES
# has enemy in fire line > function autofire
# how many targatable enemy up
# how many targatable enemy down

# STATES TO IMPLEMENT
# is danger up
# is danger down
# target killed (score)
# missed target

SPEED = 100
DURATION = 800000/SPEED
# Duration was used to end the game. Now reinit arrives only by deah or if len(enemys)==0.
ACTION_SPEED = 2


class GameAI:
	def __init__(self):
		pygame.init()
		self.toggle = False
		self.screen = pygame.display.set_mode((RESOLUTION_X,RESOLUTION_Y))
		pygame.display.set_caption('Miss Shmup')
		self.sky_surface = pygame.image.load('assets/graphics/starSky.png').convert()
		self.reward = 0
		self.score = 0
		self.clock = pygame.time.Clock()
		self.startTime = 0
		self.chrono = 0
		self.reinit()

	def reinit(self):
		self.score = 0
		self.startTime = pygame.time.get_ticks()
		self.player_single_grp = pygame.sprite.GroupSingle()
		self.player = Player()
		self.player_single_grp.add(self.player)
		self.bullet_group = pygame.sprite.Group()
		self.enemy_group = pygame.sprite.Group()
		self.impact_group = pygame.sprite.Group()
		self.enemy_group.add(Enemy((750,60),1.5*ACTION_SPEED))
		self.enemy_group.add(Enemy((700,160),1*ACTION_SPEED))
		self.enemy_group.add(Enemy((720,260),1.9*ACTION_SPEED))
		self.enemy_group.add(Enemy((600,300),1*ACTION_SPEED))
		self.enemy_group.add(Enemy((710,350),2*ACTION_SPEED))
		self.block_hit_list = []

	def auto_fire(self):
		ship_hight = self.player.rect.center[1]
		ship_nose = self.player.rect.right
		can_hit = False
		for enemy in self.enemy_group:
			top_enemy = enemy.rect.y
			down_enemy = enemy.rect.bottom
			front_enemy = enemy.rect.left
			if ship_hight > top_enemy and ship_hight < down_enemy and ship_nose + 2 < front_enemy:
				can_hit = True
		return True if can_hit else False
	
	def player_input(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_UP] and self.player.rect.y > 0:
			self.player.rect.y -= 4
		if keys[pygame.K_DOWN] and self.player.rect.y < RESOLUTION_Y-30:
			self.player.rect.y += 4

	def ai_input(self, action):
		if action == [1,0,0] and self.player.rect.y > 0:
			self.player.rect.y -= 4*ACTION_SPEED
		if action == [0,1,0] and self.player.rect.y < RESOLUTION_Y-30:
			self.player.rect.y += 4*ACTION_SPEED
		if action == [0,0,1]:
			self.bullet_group.add(Bullet(self.player_single_grp.sprite.rect.center))
		
	def run(self, action): 
		self.screen.blit(self.sky_surface,(0,0))
		reward = 0
		done = False
		self.ai_input(action)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
			if	event.type == pygame.KEYDOWN :
				if event.key == pygame.K_SPACE :
					self.bullet_group.add(Bullet(self.player_single_grp.sprite.rect.center))
		self.player_input()

		#Collision of our bullet with ennemies.
		for bullet in self.bullet_group:
			self.block_hit_list = pygame.sprite.spritecollide(bullet, self.enemy_group, True)
			if self.block_hit_list:
				bullet.kill()
				reward = 10
				self.score += 1
				self.impact_group.add(Impact(self.block_hit_list[0].rect.center))

		#Collision of ennemies with the player
		for enemy in self.enemy_group:
			hit = pygame.sprite.spritecollide(enemy, self.player_single_grp, True)
			if hit:
				print("GAME OVER")
				self.toggle = True
				reward = -10
				done = True
				return reward, self.score, done
		#End game when player did not collide
		if len(self.enemy_group)==0:
			print("GAME OVER BY ALL ENEMIES OUT !")
			self.toggle = True
			if self.score == 5:
				reward = 50
			elif self.score == 4:
				reward = 5
			else:
				reward = -10
			done = True
			return reward, self.score, done
			
		self.enemy_group.draw(self.screen)
		self.bullet_group.draw(self.screen)
		self.impact_group.draw(self.screen)
		self.player_single_grp.draw(self.screen)

		self.player.update()
		self.enemy_group.update()
		self.bullet_group.update()
		self.impact_group.update()

		self.clock.tick(SPEED)
		# self.chrono is not used as now.
		self.chrono = pygame.time.get_ticks()-self.startTime
		pygame.display.update()

		return reward, self.score, done
