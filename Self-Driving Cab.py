# -*- coding: utf-8 -*-

#Automatically generated by Colaboratory.

## Self-Driving cab

### Mina Rahmanian 
"""

import gym
import random
import numpy as np
import pandas as pd
import seaborn as sns
from time import sleep
import matplotlib.pyplot as plt
from IPython.display import display
from IPython.display import clear_output

"""# ----------------------------   Q-learning   ----------------------------------

\



<img src="https://drive.google.com/uc?id=1iQgLO47_3Nfzod55ttzWkDA16LrWKCMN" width="650" height="400">
"""

env = gym.make("Taxi-v3").env
env.render()
print("Action Space {}".format(env.action_space))
print("State Space {}".format(env.observation_space))
print('Blue colored letter denotes the pickup location and purple colored letter denotes the drop location.')

state = env.encode(3, 1, 2, 0) # (taxi row, taxi column, passenger index, destination index)
print("State:", state)
env.s=state
env.render()
env.reset()
env.step(5) # any number we can use instead of 5

"""# Environment of  Self-Driving cab



<img src="https://drive.google.com/uc?id=1RAr92SAZ7Ne0clbfkTuZP3jHGQANnGgw" width="350" height="300">

*   Four different locations (R, G, Y, B)
*   Taxi environment has 5(row) × 5(col) × 5 (4+1= five passenger location) × 4(destionation) = 500 total possible states.
*    Six possible actions:   South,  North, West, East, Pickup, Dropoff

## Colored tiles have the following meanings For a particular iteration:

Yellow: The starting position of the taxi./ When the passenger is not in the taxi. & Once the taxi drops the passenger off, it's colour changes back to yellow.
Blue: The position of the passenger./ The pickup spot.\
Purple: The destination of the passenger./ The drop off spot.\
Green: The position of the taxi with the passenger./ The passenger has been picked up by the taxi.
"""

env.P[state]

"""*   $\Large \alpha$ (alpha) is the learning rate (0<$\Large \alpha$<=1) 
*   $\Large \gamma$ (gamma) is the discount factor ($0 \leq \gamma \leq 1$) - determines how much importance we want to give to future rewards. A high value for the discount factor (close to 1) captures the long-term effective award, whereas, a discount factor of 0 makes our agent consider only immediate reward, hence making it greedy.



![q-value euation](https://render.githubusercontent.com/render/math?math=%5CLarge%20Q%28%7B%5Csmall%20state%7D%2C%20%7B%5Csmall%20action%7D%29%20%5Cleftarrow%20%281%20-%20%5Calpha%29%20Q%28%7B%5Csmall%20state%7D%2C%20%7B%5Csmall%20action%7D%29%20%2B%20%5Calpha%20%5CBig%28%7B%5Csmall%20reward%7D%20%2B%20%5Cgamma%20%5Cmax_%7Ba%7D%20Q%28%7B%5Csmall%20next%20%5C%20state%7D%2C%20%7B%5Csmall%20all%20%5C%20actions%7D%29%5CBig%29&mode=display)
"""

def brute_force(episodes):
    print("Running Brute Force....")
    performance_matrix=[]  
    frames=[]
    for episode in range(episodes):
        clear_output(wait=True)
        print(f"Progress: {(episode/episodes)*100}%")
        state=env.reset()
        epochs, penalties, reward, = 0, 0, 0
        done = False
        while not done:
            action = env.action_space.sample()
            state, reward, done, info = env.step(action)
            if reward == -10:
                penalties += 1
            
            frames.append({
                'episode': episode,
                'frame': env.render(mode='ansi'),
                'state': state,
                'action': action,
                'reward': reward})
            
            epochs += 1
        performance_matrix.append([epochs,penalties])

    return performance_matrix,frames



def q_learning(q_table,episodes):
    print("Running Q-Learning...")
    frames = [] 
    performance_matrix=[]
    for episode in range(episodes):
        clear_output(wait=True)
        print(f"Progress: {(episode/episodes)*100}%")
        state = env.reset()
        epochs, penalties, reward = 0, 0, 0
    
        done = False
    
        while not done:
            action = np.argmax(q_table[state])
            state, reward, done, info = env.step(action)

            frames.append({
            'frame': env.render(mode='ansi'),
            'episode':episode,
            'state': state,
            'action': action,
            'reward': reward})

            if reward == -10:
                penalties += 1

            epochs += 1

        performance_matrix.append([epochs,penalties])

    return performance_matrix,frames




def print_frames(frames,sleep_time=0.1,**kwargs):
    if 'episode' in kwargs:
        frames=list(filter(lambda render: render['episode'] == kwargs['episode'], frames))
    for i, frame in enumerate(frames):
        clear_output(wait=True)
        print(frame['frame'])
        print(f"Epsiode: {frame['episode']}")
        print(f"Timestep: {i + 1}")
        print(f"State: {frame['state']}")
        print(f"Action: {frame['action']}")
        print(f"Reward: {frame['reward']}")
        sleep(sleep_time)



def plot_performance(title,performance_matrix,**kwargs):

    epochs=[]
    penalties=[]
    explore=[]
    exploit=[]

    for i,episode_performance in enumerate(performance_matrix):
        if 'interval' in kwargs:
            if i%kwargs['interval']==0:
                epochs.append(episode_performance[0])
                penalties.append(episode_performance[1])
        else:
            epochs.append(episode_performance[0])
            penalties.append(episode_performance[1])
    
    df=pd.DataFrame({'episodes': range(0,len(epochs)), 'epochs': epochs, 'penalties': penalties })
    plt.figure(num=None, figsize=(20, 6), dpi=80, facecolor='w', edgecolor='k')
    #plt.ylim(top=toplimit)

    if 'ylimit' in kwargs:
        plt.ylim(kwargs['ylimit'])
    if 'xlimit' in kwargs:
        plt.xlim(kwargs['xlimit'])
    if 'xlabel' in kwargs:
        plt.xlabel(kwargs['xlabel'])
    if 'ylabel' in kwargs:
        plt.ylabel(kwargs['ylabel'])

    plt.plot( 'episodes', 'epochs', data=df, marker='o', markerfacecolor='navy', markersize=1, color='mediumblue', linewidth=4)
    plt.plot( 'episodes', 'penalties', data=df, marker='o', markerfacecolor='darkred', markersize=1, color='darkred', linewidth=4)
    plt.title(title)
    plt.legend()
    if 'save' in kwargs:
        plt.savefig(f"graphs/{kwargs['save']}")


    plt.show()




def q_learning_train(env,alpha=0.3,gamma=0.85,epsilon=0.5,iterations=1001,**kwargs):

    print(f"Running q_learning with alpha={alpha}, gamma={gamma}, epsilon={epsilon}, and {iterations-1} iterations")
    dh = display('',display_id=True)
    q_table = np.zeros([env.observation_space.n, env.action_space.n])

    #initialize the q-table as a 500 X 6 matrix of zeros as there are 500 states (5*5*5*4) and 6 actions
    all_epochs = []
    all_penalties = []
    q_learning_performance_matrix = []
    frames=[]

    for i in range(1, iterations):
        state = env.reset()

        epochs, penalties, reward = 0, 0, 0
        done = False
    
        while not done:

            if random.uniform(0, 1) < epsilon:
                action = np.argmax(q_table[state]) # Exploit learned values
            else:
                action = env.action_space.sample() # Explore action space

            next_state, reward, done, info = env.step(action) 
            frames.append({
            'frame': env.render(mode='ansi'),
            'episode':i,
            'state': state,
            'action': action,  
            'reward': reward})
        
            old_value = q_table[state, action]
            next_max = np.max(q_table[next_state])
        
            new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
            q_table[state, action] = new_value

            if reward == -10:
                penalties += 1

            state = next_state
            epochs += 1
        q_learning_performance_matrix.append([epochs,penalties])
        if i % 100 == 0:
            #clear_output(wait=True)
            dh.update(f"Episode: {i}")

    print("Training finished.\n")

    return iterations,frames,q_table,q_learning_performance_matrix




def get_performance_df(performance_matrix):
    total=len(performance_matrix)
    sum_epochs,sum_penalties=0,0
    for metric in performance_matrix:
        sum_epochs+=metric[0]
        sum_penalties+=metric[1]
        
    return [sum_epochs/total,sum_penalties/total]

"""# Running through of the environment you can see below:"""

#q_learning_train(env,0.1,0.6,0.5,1001)

iterations,frames1,q_table1,q_learning_performance_matrix1 = q_learning_train(env,alpha=0.3,gamma=0.85)
performance_matrix,frames1 = q_learning(q_table1,1001)
print_frames(frames1,0.1)

"""# Plots"""

iterations,q_learning_frame_greedy,q_table_greedy,q_learning_performance_matrix_greedy = q_learning_train(env,alpha=0.3,gamma=0.85)

title1 = f"Q-learning performance using epsilon-greedy approach. Training with {iterations-1} iterations."
interval=100
plot_performance(title1,q_learning_performance_matrix_greedy,xlabel=f"Iterations (every {interval}th iteration)",interval=interval)

#############################################

q_learning_greedy_epoch_count = []
for i in range(1000):
    q_learning_greedy_epoch_count.append(q_learning_performance_matrix_greedy[i][0])
    
sns.distplot(q_learning_greedy_epoch_count,color='mediumseagreen')
plt.title("Distribution of number of steps needed")


print("An agent using Q Learning Greedy takes about an average of " + str(int(np.mean(q_learning_greedy_epoch_count)))
      + " steps to successfully complete its mission.")

#as epsilon increases we explore more and exploit less and vice versa
#epsilon = 0.1 means explore, epsilon=0.9 means exploit

iterations,q_learning_frame_exploit,q_table_exploit,q_learning_performance_matrix_exploit = q_learning_train(env,alpha=0.3,gamma=0.85,epsilon=0.9)

title1 = f"Q-learning performance using exploit-only approach. Training with {iterations-1} iterations."
interval=100
plot_performance(title1,q_learning_performance_matrix_exploit,xlabel=f"Iterations (every {interval}th iteration)",interval=interval)

###################################################

q_learning_exploit_epoch_count = []
for i in range(1000):
    q_learning_exploit_epoch_count.append(q_learning_performance_matrix_exploit[i][0])
    
sns.distplot(q_learning_exploit_epoch_count,color='mediumseagreen')
plt.title("Distribution of number of steps needed")


print("An agent using Q Learning Exploit takes about an average of " + str(int(np.mean(q_learning_exploit_epoch_count)))
      + " steps to successfully complete its mission.")

iterations,q_learning_frame_explore,q_table_explore,q_learning_performance_matrix_explore = q_learning_train(env,alpha=0.3,gamma=0.85,epsilon=0.1)

title1 = f"Q-learning performance using explore-only approach. Training with {iterations-1} iterations."
interval=100
plot_performance(title1,q_learning_performance_matrix_explore,xlabel=f"Iterations (every {interval}th iteration)",interval=interval)

###################################################

q_learning_explore_epoch_count = []
for i in range(1000):
    q_learning_explore_epoch_count.append(q_learning_performance_matrix_explore[i][0])
    
sns.distplot(q_learning_explore_epoch_count,color='mediumseagreen')
plt.title("Distribution of number of steps needed")


print("An agent using Q Learning Explore takes about an average of " + str(int(np.mean(q_learning_explore_epoch_count)))
      + " steps to successfully complete its mission.")

#performance_matrix_b,frames_brute_force =   brute_force(iterations)

def show_values_on_bars(axs, h_v="v", space=0.4):

    def _show_on_single_plot(ax):
      
        if h_v == "v":
            for p in ax.patches:
                _x = p.get_x() + p.get_width() / 2
                _y = p.get_y() + p.get_height()
                value = int(p.get_height())
                ax.text(_x, _y, value, ha="center") 
        elif h_v == "h":
            for p in ax.patches:
                _x = p.get_x() + p.get_width() + float(space)
                _y = p.get_y() + p.get_height()/2
                value = int(p.get_width())
                ax.text(_x, _y, value ,va="center", ha="left")

    if isinstance(axs, np.ndarray):
        for idx, ax in np.ndenumerate(axs):
            _show_on_single_plot(ax)
    else:
        _show_on_single_plot(axs)

"""# ----------------------------   Deep Q Network   ----------------------------------

\

<img src="https://drive.google.com/uc?id=1Uv1OuqP_qL9AJOf8wqK9bu72aaeWI_kC" width="600" height="230">

**Packages**


First, let's import needed packages. Firstly, we need
`gym <https://gym.openai.com/docs>`__ for the environment
(Install using `pip install gym`).
We'll also use the following from PyTorch:

-  neural networks (``torch.nn``)
-  optimization (``torch.optim``)
-  automatic differentiation (``torch.autograd``)
-  utilities for vision tasks (``torchvision`` - `a separate
   package <https://github.com/pytorch/vision>`__).
"""

import os
assert os.environ['COLAB_TPU_ADDR'], 'Make sure to select TPU from Edit > Notebook settings > Hardware accelerator'
!pip install gym
!pip install torch
!pip install torchvision

# for using torch lib

VERSION = "20200325"  #@param ["1.5" , "20200325", "nightly"]
!curl https://raw.githubusercontent.com/pytorch/xla/master/contrib/scripts/env-setup.py -o pytorch-xla-env-setup.py
!python pytorch-xla-env-setup.py --version $VERSION

import gym
import math
import time
import copy
import torch
import random
import torch_xla
import numpy as np
from PIL import Image
from __future__ import division
import matplotlib.pyplot as plt
import torchvision.transforms as T
from torch.autograd import Variable
import torch_xla.core.xla_model as xm
from IPython.display import clear_output

env = gym.envs.make("Taxi-v3")

dev = xm.xla_device()

def plot_res(values, title=''):   

    ''' Plot the reward curve and histogram of results over time '''
    
    # Update the window after each episode
    clear_output(wait=True)
    
    # Define the figure
    f, ax = plt.subplots(nrows=1, ncols=2, figsize=(12,5))
    f.suptitle(title)
    ax[0].plot(values, label='score per run')
    ax[0].axhline(195, c='red',ls='--', label='goal')
    ax[0].set_xlabel('Episodes')
    ax[0].set_ylabel('Reward')
    x = range(len(values))
    ax[0].legend()


    # Calculate the trend
    try:
        z = np.polyfit(x, values, 1)
        p = np.poly1d(z)
        ax[0].plot(x,p(x),"--", label='trend')
    except:
        print('')
    
    # Plot the histogram of results
    ax[1].hist(values[-50:])
    ax[1].axvline(195, c='red', label='goal')
    ax[1].set_xlabel('Scores per Last 50 Episodes')
    ax[1].set_ylabel('Frequency')
    ax[1].legend()
    
    plt.show()

def plot_performance(title,performance_matrix,**kwargs):


    epochs=[]
    penalties=[]
    explore=[]
    exploit=[]
    
    for i,episode_performance in enumerate(performance_matrix):
        if 'interval' in kwargs:
            if i%kwargs['interval']==0:
                epochs.append(episode_performance[0])
                penalties.append(episode_performance[1])
        else:
            epochs.append(episode_performance[0])
            penalties.append(episode_performance[1])
    
    df=pd.DataFrame({'episodes': range(0,len(epochs)), 'epochs': epochs, 'penalties': penalties })
    plt.figure(num=None, figsize=(20, 6), dpi=80, facecolor='w', edgecolor='k')
    #plt.ylim(top=toplimit)

    if 'ylimit' in kwargs:
        plt.ylim(kwargs['ylimit'])
    if 'xlimit' in kwargs:
        plt.xlim(kwargs['xlimit'])
    if 'xlabel' in kwargs:
        plt.xlabel(kwargs['xlabel'])
    if 'ylabel' in kwargs:
        plt.ylabel(kwargs['ylabel'])

    plt.plot( 'episodes', 'epochs', data=df, marker='o', markerfacecolor='navy', markersize=1, color='mediumblue', linewidth=4)
    plt.plot( 'episodes', 'penalties', data=df, marker='o', markerfacecolor='red', markersize=1, color='darkred', linewidth=4)
    plt.title(title)
    plt.legend()
    if 'save' in kwargs:
        plt.savefig(f"{kwargs['save']}")


    plt.show()

class DQL():
  
    ''' Deep Q Neural Network class '''

    
    __constants__ = ['state_dim', 'action_dim', 'hidden_dim', 'lr', 'dropout']
    
    def __init__(self, state_dim, action_dim, device=None, hidden_dim=64, lr=0.05, dropout=0.4):

            #super(Linear, self).__init__()
            self.state_dim = state_dim
            self.action_dim = action_dim
            self.hidden_dim = hidden_dim
            self.lr = lr
            self.dropout = dropout
            self.criterion = torch.nn.MSELoss()

            self.model = torch.nn.Sequential(
                            torch.nn.Linear(state_dim, hidden_dim),
                            torch.nn.ReLU(),
                            torch.nn.Dropout(dropout),                        
                            torch.nn.Linear(hidden_dim, action_dim)
                    )
            if device is not None:
              self.device=device
              self.model = self.model.to(device)
              
            self.optimizer = torch.optim.Adam(self.model.parameters(), lr)
            self.num_param_updates=0



    def update(self, state, y):
      
        """ Update the weights of the network given a training sample """

        self.model.train()
        state = torch.Tensor(state).to(self.device)
        y = Variable(torch.Tensor(y)).to(self.device)
        y_pred = self.model(state)
        loss = self.criterion(y_pred, y)
        self.optimizer.zero_grad()
        loss.backward()
        xm.optimizer_step(self.optimizer, barrier=True)



    def predict(self, state):
        """ Compute Q values for all actions using the DQL. """

        self.model.eval()
        with torch.no_grad():

            return self.model(torch.Tensor(state).to(self.device))

''' the algorithm is modified to take as input a one-hot vector 
    epresenting one of 500 possible states of the taxi environment.'''

class OneHotGenerator():

    def __init__(self, num_labels):

        self.num_labels = num_labels
        self.one_hot_array = np.eye(num_labels)
    
    
    def get_one_hot(self, label):

        return self.one_hot_array[label]

class ExponentialSchedule():
  
    #Exponential scheduling strategy.
    
    def __init__(self, start_val = 1.0, end_val = 0.05, decay_rate = 200):

        self.start = start_val # initial value (float)
        self.end = end_val # final value (float)
        self.decay = decay_rate # rate of exponential decaying (int), usually steps or episodes


    def value(self, t):
        #Calculates the current value at time t

        return (self.end + (self.start - self.end) * np.exp(-1.0 * t / self.decay))

def learn(model_target, model_train, device, memory, size, n_update, gamma=0.9):
  
        """ Add experience replay to the DQN network class """
        
        # Make sure the memory is big enough
        if len(memory) >= size:
            states = []
            targets = []

            # Sample a batch of experiences from the agent's memory
            batch = random.sample(memory, size)
            # print(batch)

            start_time = time.time()

            batch = np.array(batch)
            # print(batch)

            state_batch = torch.from_numpy(np.stack(batch[:, 0])).type(torch.FloatTensor).to(device)
            # print(state_batch.size())

            action_batch = torch.from_numpy(np.stack(batch[:, 1])).long().to(device)
            # print(action_batch.size())

            next_batch = torch.from_numpy(np.stack(batch[:, 2])).type(torch.FloatTensor).to(device)
            # print(next_batch.size())

            rew_batch = torch.from_numpy(np.stack(batch[:, 3])).to(device)
            # print(rew_batch.size())
            
            not_done_mask = torch.from_numpy(1 - np.stack(batch[:, 4])).to(device)
            # print(not_done_mask.size())

            q_values = model_train.model(state_batch).gather(1, action_batch.unsqueeze(1))

            next_max_q = model_target.model(next_batch).detach().max(1)[0]
            next_q_values = not_done_mask*next_max_q
            target_q_values = rew_batch + (gamma*next_q_values)
          

            for_loop_duration = time.time() - start_time
            # print("For loop took %.2f secs" % for_loop_duration)

            start_time = time.time()

            loss = model_train.criterion(q_values, target_q_values.unsqueeze(1))
            model_train.optimizer.zero_grad()
            loss.backward()
            xm.optimizer_step(model_train.optimizer, barrier=True)


            model_update_time = time.time() - start_time
            # print("Model update took %.2f secs" % model_update_time)

            model_train.num_param_updates += 1
            if model_train.num_param_updates % n_update ==0:
                model_target.model.load_state_dict(model_train.model.state_dict())

def q_learning(env, model_train, model_target, device, episodes, gamma=0.85, 
               epsilon=0.3, eps_decay=0.99, replay=False, replay_size=150, 
               title = 'DQL', double=False, n_update=1000, soft=False):
  
    """ Deep Q Learning algorithm using the DQN """

    final = []
    memory = []
    one_hot_gen =  OneHotGenerator(env.observation_space.n)
    scheduler = ExponentialSchedule()
    epsilon = scheduler.value(0)
    q_learning_performance_matrix = []

    for episode in range(episodes):
        if double and not soft:

            # Update target network every n_update steps
            if episode % n_update == 0:
                model.target_update()
        if double and soft:
            model.target_update()
        
        # Reset state
        state = env.reset()
        state = one_hot_gen.get_one_hot(state)

        done = False
        total = 0
        steps = 0
        penalties = 0
        
        epsilon = scheduler.value(episode+1)

        while not done:
            # Implement greedy search policy to explore the state space
            steps +=1            

            if random.random() < epsilon:
                action = env.action_space.sample()
            else:
                q_values = model_target.predict(state)
                action = torch.argmax(q_values).item()
            
            # Take action and add reward to total
            next_state, reward, done, _ = env.step(action)
            next_state = one_hot_gen.get_one_hot(next_state)

            if reward==-10:
                penalties+=1
            total+=penalties
            memory.append((state, action, next_state, reward, done))

            if steps>100:
                learn(model_target, model_train, device, memory, replay_size, n_update, gamma)
            
            state = next_state
        
        # Update epsilon
        q_learning_performance_matrix.append([steps, penalties])
        final.append(total)
        plot_res(final, title)

    return final, q_learning_performance_matrix

# Num of states
n_state = env.observation_space.n
# Num of actions
n_action = env.action_space.n
# Num of episodes
episodes = 150
# Num of hidden nodes in the DQN
n_hidden = 150
# Learning rate
lr = 0.0003

"""#Plot"""

dqn_train = DQL(n_state, 6, dev, n_hidden, lr)
dqn_target= DQL(n_state, 6, dev, n_hidden, lr)

dqn_train.model.train()
dqn_target.model.eval()

replay = q_learning(env, dqn_train, dqn_target, dev,
                    1000, gamma=0.85, 
                    epsilon=0.3, replay=True, 
                    title='DQL with Replay')

dqn_train = DQL(n_state, 6, dev, n_hidden, lr)
dqn_target= DQL(n_state, 6, dev, n_hidden, lr)

dqn_train.model.train()
dqn_target.model.eval()

final, q_learning_performance_matrix = q_learning(env, dqn_train, dqn_target, dev,
                    1000, gamma=0.85, 
                    epsilon=0.3, replay=True, 
                    title='DQL with Replay')

import pandas as pd

title1 = f"Deep Q-learning performance with 1000 episodes."
interval=100
plot_performance(title1,q_learning_performance_matrix,xlabel=f"Iterations (every {interval}th iteration)")


d_q_learning_epoch_count = []
for i in range(1000):
    d_q_learning_epoch_count.append(q_learning_performance_matrix[i][0])
    
sns.distplot(d_q_learning_epoch_count,color='mediumseagreen')
plt.title("Distribution of number of steps needed")


print("An agent using Deep Q Learning Explore takes about an average of " + str(int(np.mean(d_q_learning_epoch_count)))
      + " steps to successfully complete its mission.")

np.array(q_learning_performance_matrix)[:, 1]



"""# Comparing Algorithms"""

# Table comparing
data = [get_performance_df(q_learning_performance_matrix_greedy), get_performance_df(q_learning_performance_matrix_exploit),
        get_performance_df(q_learning_performance_matrix_explore), get_performance_df(q_learning_performance_matrix)]
df = pd.DataFrame(data,index=['Q-Learning-Greedy','Q-Learning-Exploit','Q-Learning-Explore','Deep Q-Learning'],columns=['Average epochs','Average penalties'])
print(f"Average for {1000} episodes/iterations")
df

# comparing in term of average steps needed in each algorithms  

list1 = ['Q-Learning-Greedy','Q-Learning-Exploit','Q-Learning-Explore','Deep Q-Learning']
list2 = []
list2.append(int(np.mean(q_learning_greedy_epoch_count)))
list2.append(int(np.mean(q_learning_exploit_epoch_count)))
list2.append(int(np.mean(q_learning_explore_epoch_count)))
list2.append(int(np.mean(d_q_learning_epoch_count)))


df = pd.DataFrame(list(zip(list1, list2)), 
               columns =['Algorithms', 'Average Steps Required']) 
df

plt.figure(figsize=(10, 6))
ax = sns.barplot(y="Algorithms", x="Average Steps Required", data=df)
show_values_on_bars(ax, "h", 0.5)

# plot sns: distribution  of  number  of  steps needed in different algorithms

# sns.set(font_scale=1)
plt.figure(figsize=(17, 10))
sns.distplot(q_learning_greedy_epoch_count, hist=False, rug=False, label="Q_learning_greedy")
sns.distplot(q_learning_exploit_epoch_count, hist=False, rug=False, label="Q_learning_exploit")
sns.distplot(q_learning_explore_epoch_count, hist=False, rug=False, label="Q_learning_explore")
sns.distplot(d_q_learning_epoch_count, hist=False, rug=False, label="Deep Q_learning")
