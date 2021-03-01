import random
from feature_extractor import extractor
from APC import APCEnv

if __name__ == "__main__":
    env = APCEnv()
    env.reset()
    turn = 0
    total_reward = [0] * 4
    for i in range(100):
      while True:
        player = turn % 4
        actions = env.get_actions(player)
        action = actions[random.randint(0, len(actions) - 1)] if actions else (player, None)
        if player == 0:
          print(extractor(env, action))
        state, reward, done, info = env.step(action)
        total_reward = [sum(x) for x in zip(total_reward, reward)]
        env.render()
        while info["bonus"]:
          actions = env.get_actions(player)
          action = actions[random.randint(0, len(actions) - 1)] if actions else (player, None)
          if player == 0:
            print(extractor(env, action))
          state, reward, done, info = env.step(action)
          total_reward = [sum(x) for x in zip(total_reward, reward)]
          env.render()
        if done:
          print(f"WINNER: {state.winner}")
          break
        turn += 1
      env.reset()
    