import random
import numpy as np
from feature_extractor import extractor
from APC import APCEnv

FEATURES = 8

class Trainer():
  def __init__(self, episodes=10000, alpha=0.5, discount=0.9, epsilon=0.9, active_player=0, dst_file="weights.txt", debug=False):
    self.game = APCEnv()
    self.game.reset()
    self.weights = np.random.rand(FEATURES)
    self.episodes = episodes
    self.alpha = alpha
    self.discount = discount
    self.epsilon = epsilon
    self.dst_file = dst_file
    self.active_player = active_player
    self.debug = debug

  def train(self, test=False):
    print("------------------------ Training Start ------------------------")
    for episode in range(self.episodes):
      print(f"Episode {episode}")
      print(f"Current Weights: {self.weights}")
      turn = 0
      cum_reward = 0
      tt_r = 0
      saved_feature = None
      while True:
        player = turn % 4
        feature, reward, done = self.step_game(player)
        tt_r += reward
        if player == self.active_player:
          saved_feature = feature
        cum_reward += reward
        if (player + 1) % 4 == self.active_player:
          feature_prime, action_prime = self.get_best_action("q", self.active_player)
          difference = cum_reward + (self.discount * (self.weights @ feature_prime)) - (self.weights @ saved_feature)
          self.weights += self.alpha * difference * saved_feature
          self.weights = self.weights / np.linalg.norm(self.weights)
          cum_reward = 0
        if done:
          self.game.reset()
          break
        turn += 1

  # def update_weights(self, feature, reward, action_prime):
  #   difference = 

  # def test(self, rounds=1000):
  #   self.game.reset()
  #   for i in range(rounds):


  def step_game(self, player):
    """
    Step given player's round of the game.
    :return: total reward earned by the player and whether game ended this round
    """
    total_reward = 0
    strategy = "q" if player == self.active_player else "random"
    feature, action = self.get_best_action(strategy, player)
    state, reward, done, info = self.game.step(action)
    # self.game.render()
    total_reward += reward[self.active_player]
    while info["bonus"]:
      feature, action = self.get_best_action(strategy, player)
      state, reward, done, info = self.game.step(action)
      # self.game.render()
      total_reward += reward[self.active_player]
    return feature, total_reward, done

  
  def get_best_action(self, strategy, player):
    """
    Get the best action for the given player based on given strategy
    :return: the best action and the feature of this action
    """
    actions = self.game.get_actions(player)
    action = None
    if not actions:
      action = (player, None)
    elif strategy == "q":
      action = actions[np.argmax([self.weights @ extractor(self.game, a) for a in actions])]
    elif strategy == "random":
      action = actions[random.randint(0, len(actions) - 1)]
    feature = extractor(self.game.copy(), action)
    return feature, action



if __name__ == "__main__":
    trainer = Trainer()
    trainer.train()