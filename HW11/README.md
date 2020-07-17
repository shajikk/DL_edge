# Homework 11 : OpenAI Gym

## What parameters did you change?

I changed below

- density_first_layer
- density_second_layer
- batch_size
- epsilon_min
- epsilon_decay
- gamma
- lr

## What values did you try?

```text
Changed from default :     

self.density_first_layer = 32
self.density_second_layer = 8

Tried these batch sizes :

self.batch_size = 64
self.batch_size = 72
self.batch_size = 96

Tried these epsilon values
self.epsilon_min = 0.23

Tried these epsilon decay values

self.epsilon_decay = 0.9955
self.epsilon_decay = 0.965
self.epsilon_decay = 0.975

Tried these gammas :

self.gamma = 0.99
self.gamma = 0.97

Learning rates

self.lr = 0.001
self.lr = 0.007
self.lr = 0.002
```

## Did you try any other changes that made things better or worse?
I changed higher learning rates that made it worse.

## Did they improve or degrade the model? Did you have a test run with 100% of the scores above 200?
I did not have a test run with 100% of the scores above 200

## Based on what you observed, what conclusions can you draw about the different parameters and their values?
Changing the density of first layers seemed to help in converging from initial runs.

## What is the purpose of the epsilon value?
Acting randomly in reinforcement learning is important since it allows the agent to explore and discover new states.
Changing this allowes agent to do that.

## Describe "Q-Learning".
Q-Learning algorithm is a model free algorithm to learn a policy telling an agent what action to take under what circumstances. It can handle problems with stochastic transitions and rewards.
