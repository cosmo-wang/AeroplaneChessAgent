from APC import APCEnv, HOME, TAKEN_OFF, FINAL_STRETCH, BACK_HOME
import numpy as np

TRACK_END_POS = [49, 10, 23, 36]

def extractor(env, action):
  """
  Extract a feature vector from a state and action pair by applying
  the action and observe the update state for a given player.
  [
    number of flying planes, 1
    number of opponent planes flying, -1
    sum of distance to win, -1
    sum of opponents distance to win, 1
    number of planes on final stretch, 1
    number of opponent planes behind within 6 steps, -1
    number of opponent planes ahead within 6 steps, 1
    number of planes back home 1
  ]
  """
  player_idx, plane = action
  # if plane == None:
  #   return [0, 0, 0, 0, 0, 0, 0, 0]
  env_copy = env.copy()
  state, _, _, _ = env_copy.step(action)
  player_state = state.players[player_idx]
  
  # feature 1: number of flying planes
  flying_plane = env_copy.count_flying_planes(player_idx)

  # feature 2: number of opponent planes flying
  oppo_flying_plane = 0
  for oppo in range(state.player_num):
    if not oppo == player_idx:
      oppo_flying_plane += env_copy.count_flying_planes(oppo)

  # feature 3: sum of distance to win
  dist_to_win = count_dist_to_win(player_state, TRACK_END_POS[player_idx])

  # feature 4: sum of opponents distance to win
  oppo_dist_to_win = 0
  for oppo in range(state.player_num):
    if not oppo == player_idx:
      oppo_state = state.players[oppo]
      oppo_dist_to_win += count_dist_to_win(oppo_state, TRACK_END_POS[oppo])

  # feature 5: number of planes on final stretch
  planes_on_final_stretch = 0
  for pos in player_state.plane_positions:
    if pos == FINAL_STRETCH:
      planes_on_final_stretch += 1

  # feature 6: number of opponent planes behind within 6 steps
  oppo_behind = 0
  for pos in player_state.plane_positions:
    if pos and pos >= 0 and pos <= 49:
      positions_behind = [(pos - i) % 52 for i in range(1, 7)]
      for pos_behind in positions_behind:
        planes, _ = env_copy.planes_on_pos(pos_behind, player_idx)
        oppo_behind += len(planes)

  # feature 7: number of opponent planes ahead within 6 steps
  oppo_ahead = 0
  for pos in player_state.plane_positions:
    if pos and pos >= 0 and pos <= 49:
      positions_ahead = [(pos + i) % 52 for i in range(1, 7)]
      for pos_ahead in positions_ahead:
        planes, _ = env_copy.planes_on_pos(pos_ahead, player_idx)
        oppo_ahead += len(planes)

  # feature 8: number of planes back home
  planes_back_home = 0
  for pos in player_state.plane_positions:
    if pos == BACK_HOME:
      planes_back_home += 1

  return np.array([
    flying_plane,
    oppo_flying_plane,
    dist_to_win,
    oppo_dist_to_win,
    planes_on_final_stretch,
    oppo_behind,
    oppo_ahead,
    planes_back_home
  ])

def count_dist_to_win(player_state, track_end_pos):
  dist_to_win = 0
  for i in range(player_state.plane_num):
    plane_pos = player_state.plane_positions[i]
    if plane_pos == HOME:
      dist_to_win += 70
    elif plane_pos == TAKEN_OFF:
      dist_to_win += 60
    elif plane_pos == FINAL_STRETCH:
      dist_to_win += 6 - player_state.final_stretch[i]
    elif plane_pos == BACK_HOME:
      dist_to_win += 0
    else:
      dist_to_win += ((track_end_pos - plane_pos) % 52) + 6
  return dist_to_win
