import random
import numpy as np
from feature_extractor import extractor
from APC import APCEnv

FEATURES = 8

class Trainer():
  def __init__(self, episodes=10000, alpha=0.5, discount=0.9, epsilon=0.9, active_player=0, dst_file="weights.txt", debug=False):
    self.game = APCEnv()
    self.game.reset()
    # self.weights = np.array([0.789563, -0.5871338, -0.8963852, 0.36713951, 1.36357122, -1.56593172, 0.36471258, 1.41267423])
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
      saved_feature = None
      while True:
        player = turn % 4
        feature, reward, done = self.step_game(player)
        if player == self.active_player:
          saved_feature = feature
        if (player + 1) % 4 == self.active_player:
          feature_prime, _ = self.get_best_action("q", self.active_player)
          self.update_weights(saved_feature, reward, feature_prime)
        if done:
          self.game.reset()
          break
        turn += 1

  def update_weights(self, feature, reward, feature_prime):
    difference = reward + (self.discount * (self.weights @ feature_prime)) - (self.weights @ feature)
    self.weights += self.alpha * difference * feature
    self.weights = self.weights / np.linalg.norm(self.weights)

  def test(self, rounds=1000):
    self.game.reset()
    wins = [0] * 4
    for i in range(rounds):
      turn = 0
      while True:
        player = turn % 4
        _, _, done = self.step_game(player)
        if done:
          print(f"----------------- Round {i}, WINNER: {self.game.state.winner} -----------------")
          wins[self.game.state.winner] += 1
          self.game.reset()
          break
        turn += 1
    print(wins)



  def step_game(self, player):
    """
    Step given player's round of the game.
    :return: total reward earned by the player and whether game ended this round
    """
    total_reward = 0
    strategy = "q" if player == self.active_player else "random"
    feature, action = self.get_best_action(strategy, player)
    state, reward, done, info = self.game.step(action)
    # print(reward)
    # self.game.render()
    total_reward += reward[self.active_player]
    while info["bonus"]:
      feature, action = self.get_best_action(strategy, player)
      state, reward, done, info = self.game.step(action)
      # print(reward)
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
    # trainer.test()