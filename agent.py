import torch
import random
import numpy as np
from collections import deque
from game import *
from model import Linear_Qnet, QTrainer
from helper import plot

# - Un model d'evitement des collosions
    # liberer mvt de droite a gauche
    # ajouter des boxs
    # multiplier le spawn d'ennemy
    # ajouter une cible safe
        # diviser l'ecran en 6 (pour commencer) et calculer le point le plus safe.
    # revoir les recompences

# - Un model d'abbatage de cibles

# - Tester les deux models enssemble
# - Un jeu qui lit les models in game

# - Un vrais level de miss shmup

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent():
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 #control the randomness
        self.gamma=0.9 #discount rate
        self.memory = deque(maxlen = MAX_MEMORY) #popleft
        self.model = Linear_Qnet(11 , 256 , 5)
        self.trainer = QTrainer(self.model, lr=LR , gamma= self.gamma )


    def game_state(self, game):
        player_y = game.player.rect.center[1]
        player_nose = game.player.rect.right
        state = []
        up = 0
        down = 0
        collide_up = 0
        collide_down = 0
        collide_left = 0
        collide_right = 0

        for enemy in game.enemy_group:
            if enemy.rect.y > player_y and enemy.rect.left > player_nose:
                down += 1
            elif enemy.rect.y < player_y and enemy.rect.left > player_nose:
                up +=1
        #state.append(up)
        #state.append(down)
        state.append(game.player.rect.centerx/RESOLUTION_X)
        state.append(game.player.rect.centery/RESOLUTION_Y)
        #state.append(int(game.auto_fire()))    

        for zone in game.player.collider_zones_group:
            if zone.name == 'up' and pygame.sprite.spritecollide(zone, game.enemy_group, False):
                collide_up = 1
                print ("COLLISION UP DETECTED")
            elif zone.name == 'down' and pygame.sprite.spritecollide(zone, game.enemy_group, False):
                collide_down = 1
                print ("COLLISION DOWN DETECTED")
            elif zone.name == 'left' and pygame.sprite.spritecollide(zone, game.enemy_group, False):
                collide_left = 1
                print ("COLLISION LEFT DETECTED")
            elif zone.name == 'right' and pygame.sprite.spritecollide(zone, game.enemy_group, False):
                collide_right = 1
                print ("COLLISION RIGHT DETECTED")


        state.append(collide_up)
        state.append(collide_down)
        state.append(collide_left)
        state.append(collide_right)
        
        w = game.player.rect.width
        h = game.player.rect.height

        state.append(game.danger_level((0,0) , 1 , 1, w*1.1, h*1.1))
        state.append(game.danger_level((50,0) , 1 , 1, w/2, h))
        state.append(game.danger_level((-50,0) , 1 , 1, w/2, h))
        state.append(game.danger_level((0,-50) , 1 , 1, w, h*1.5))
        state.append(game.danger_level((0,50) , 1 , 1, w, h*1.5))

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) #popleft if maxmemory is reached


    def train_lomg_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # returns a list of tuples
        else :
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step( states, actions, rewards, next_states, dones)


    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step( state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves, tradeoff between exploration and expoitation.
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0,0,0]
        if random.randint(0,200) < self.epsilon:
            move = random.randint(0,4)
            final_move[move]=1
        else:
            state0 = torch.tensor(state, dtype = torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move]=1
        return final_move

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    best_score = 0
    score = 0
    agent = Agent()
    game = GameAI()
    while True:
        # get the old state
        state_old = agent.game_state(game)

        # get the move
        final_move = agent.get_action(state_old)

        # perform the move and get new state
        reward, score, done = game.run(final_move) # final_move
        if reward > 1:
            print(f'REWARD {reward} !!!!!') 
        state_new = agent.game_state(game)

        #train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        #remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train the long memory, plot the result
            agent.n_games += 1
            agent.train_lomg_memory()

            if score > best_score:
                best_score = score
                agent.model.save()
            print('Games : ', agent.n_games, 'Score', score, 'Record:', best_score)
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)
            game.reinit()


if __name__ == '__main__':
    train()