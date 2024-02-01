import torch
import random
import numpy as np
from collections import deque
from game import *
from model import Linear_Qnet, QTrainer
from helper import plot


MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent():
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 #control the randomness
        self.gamma=0.9 #discount rate
        self.memory = deque(maxlen = MAX_MEMORY) #popleft
        self.model = Linear_Qnet(3 , 256 , 3)
        self.trainer = QTrainer(self.model, lr=LR , gamma= self.gamma )

    def game_state(self, game):
        player_y = game.player.rect.center[1]
        player_nose = game.player.rect.right
        state = []
        up = 0
        down = 0
        for enemy in game.enemy_group:
            if enemy.rect.y > player_y and enemy.rect.left > player_nose:
                down += 1
            elif enemy.rect.y < player_y and enemy.rect.left > player_nose:
                up +=1
        state.append(up)
        state.append(down)
        #state.append(game.chrono)

        # TO DO: improve this! This was to force auto_fire to be an int
        toto = 0
        if game.auto_fire():
            toto = 1
        state.append(toto)

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
        final_move = [0,0,0]
        if random.randint(0,200) < self.epsilon:
            move = random.randint(0,2)
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
        if not reward == 0:
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