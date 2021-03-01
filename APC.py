import gym
import random
from utils import read_game_board

# game board constants
PLANE_NUM = 4           # number of planes for each player
TRACK_LEN = 56
PLAYER_TO_COLOR = {0: "B", 1: "Y", 2: "G", 3: "R"}
# position constants
HOME = None
TAKEN_OFF = -1
FINAL_STRETCH = -2
BACK_HOME = -3
# some rewards for different situation
PASS_REWARD = -1
FINAL_STRETCH_OVERKILL_REWARD = 0
BACK_HOME_REWARD = 10
BlOCKED_REWARD = -1
GET_ON_FINAL_STRETCH_REWARD = 5
BIG_FLY_REWARD = 4
SMALL_FLY_REWARD = 2
NORMAL_REWARD = 1
ATTACK_BONUS_REWARD = 3
SACRIFICE_PENALTY = -2
ATTACKED_PENALTY = -3
WINNING_REWARD = 100
LOSING_PANELTY = -100
# feature constants
# [
  # 1 if get one plane out of home, 0 otherwise
  # 1 if get one plane to home, 0 otherwise
  # 1 if plane is blocked or overkills final stretch, 0 otherwise
  # 1 if plane gets on final stretch, 0 otherwise
  # 1 if plane big fly, 0 otherwise
  # 1 if plane small fly, 0 otherwise
  # 1 if plane kills opponents, 0 otherwise
  # 1 if plane sacrificed, 0 otherwise
  # 1 if plane moves normally, 0 otherwise
  # 1 if player won the game, 0 otherwise
  # 1 if no moves possible, 0 otherwise
# ]
FEATURES = 11
TAKE_OFF_IDX = 0
BACK_HOME_IDX = 1
BLOCKED_IDX = 2
GET_ON_FINAL_STRETCH_IDX = 3
BIG_FLY_IDX = 4
SMALL_FLY_IDX = 5
ATTACK_IDX = 6
SACRIFICE_IDX = 7
NORMAL_IDX = 8
WINNING_IDX = 9
NO_MOVE_IDX = 10
# position mapping
POS_TO_BOARDPOS = {
  "0": [(51, 30), (50, 30), (52, 30)],
  "1": [(47, 28), (46, 28), (48, 28)],
  "2": [(43, 28), (42, 28), (44, 28)],
  "3": [(39, 32), (38, 32), (40, 32)],
  "4": [(38, 26), (37, 26), (39, 26)],
  "5": [(39, 20), (38, 20), (40, 20)],
  "6": [(39, 12), (38, 12), (40, 12)],
  "7": [(39, 6), (38, 6), (40, 6)],
  "8": [(35, 4), (34, 4), (36, 4)],
  "9": [(31, 4), (30, 4), (32, 4)],
  "10": [(27, 3), (26, 3), (28, 3)],
  "11": [(23, 3), (22, 3), (24, 3)],
  "12": [(19, 3), (18, 3), (20, 3)],
  "13": [(15, 6), (14, 6), (16, 6)],
  "14": [(15, 11), (14, 11), (16, 11)],
  "15": [(15, 19), (14, 19), (16, 19)],
  "16": [(16, 26), (15, 26), (17, 26)],
  "17": [(15, 32), (14, 32), (16, 32)],
  "18": [(11, 27), (10, 27), (12, 27)],
  "19": [(7, 27), (6, 27), (8, 27)],
  "20": [(3, 30), (2, 30), (4, 30)],
  "21": [(3, 35), (2, 35), (4, 35)],
  "22": [(3, 43), (2, 43), (4, 43)],
  "23": [(3, 51), (2, 51), (4, 51)],
  "24": [(3, 59), (2, 59), (4, 59)],
  "25": [(3, 67), (2, 67), (4, 67)],
  "26": [(3, 74), (2, 74), (4, 74)],
  "27": [(7, 75), (6, 75), (8, 75)],
  "28": [(11, 75), (10, 75), (12, 75)],
  "29": [(15, 72), (14, 72), (16, 72)],
  "30": [(16, 78), (15, 78), (17, 78)],
  "31": [(15, 83), (14, 83), (16, 83)],
  "32": [(15, 91), (14, 91), (16, 91)],
  "33": [(15, 98), (14, 98), (16, 98)],
  "34": [(19, 99), (18, 99), (20, 99)],
  "35": [(23, 99), (22, 99), (24, 99)],
  "36": [(27, 99), (26, 99), (28, 99)],
  "37": [(31, 99), (30, 99), (32, 99)],
  "38": [(35, 99), (34, 99), (36, 99)],
  "39": [(39, 98), (38, 98), (40, 98)],
  "40": [(39, 91), (38, 91), (40, 91)],
  "41": [(39, 83), (38, 83), (40, 83)],
  "42": [(38, 78), (37, 78), (39, 78)],
  "43": [(39, 72), (38, 72), (40, 72)],
  "44": [(43, 75), (42, 75), (44, 75)],
  "45": [(47, 75), (46, 75), (48, 75)],
  "46": [(51, 74), (50, 74), (52, 74)],
  "47": [(51, 67), (50, 67), (52, 67)],
  "48": [(51, 59), (50, 59), (52, 59)],
  "49": [(51, 51), (50, 51), (52, 51)],
  "50": [(51, 43), (50, 43), (52, 43)],
  "51": [(51, 35), (50, 35), (52, 35)],
  "BB0": (45, 3),
  "BB1": (45, 10),
  "BB2": (49, 3),
  "BB3": (49, 10),
  "-1B": [(50, 19), (51, 19), (52, 19), (53, 19)],
  "fB0": [(47, 51), (46, 51), (48, 51)],
  "fB1": [(43, 51), (42, 51), (44, 51)],
  "fB2": [(39, 51), (38, 51), (40, 51)],
  "fB3": [(35, 51), (34, 51), (36, 51)],
  "fB4": [(31, 51), (30, 51), (32, 51)],
  "YY0": (5, 3),
  "YY1": (5, 10),
  "YY2": (9, 3),
  "YY3": (9, 10),
  "-1Y": [(1, 19), (2, 19), (3, 19), (4, 19)],
  "fY0": [(27, 11), (26, 11), (28, 11)],
  "fY1": [(27, 19), (26, 19), (28, 19)],
  "fY2": [(27, 27), (26, 27), (28, 27)],
  "fY3": [(27, 35), (26, 35), (28, 35)],
  "fY4": [(27, 43), (26, 43), (28, 43)],
  "GG0": (5, 93),
  "GG1": (5, 100),
  "GG2": (9, 93),
  "GG3": (9, 100),
  "-1G": [(1, 85), (2, 85), (3, 85), (4, 85)],
  "fG0": [(7, 51), (6, 51), (8, 51)],
  "fG1": [(11, 51), (10, 51), (12, 51)],
  "fG2": [(15, 51), (14, 51), (16, 51)],
  "fG3": [(19, 51), (18, 51), (20, 51)],
  "fG4": [(23, 51), (22, 51), (24, 51)],
  "RR0": (45, 93),
  "RR1": (45, 100),
  "RR2": (49, 93),
  "RR3": (49, 100),
  "-1R": [(50, 85), (51, 85), (52, 85), (53, 85)],
  "fR0": [(27, 91), (26, 91), (28, 91)],
  "fR1": [(27, 83), (26, 83), (28, 83)],
  "fR2": [(27, 75), (26, 75), (28, 75)],
  "fR3": [(27, 67), (26, 67), (28, 67)],
  "fR4": [(27, 59), (26, 59), (28, 59)]
}

class APCState:
  """
  State representation for Aeroplane Chess
  """
  def __init__(self, player_num=4, isTerminal=False):
    self.player_num = player_num
    self.plane_num = PLANE_NUM
    self.players = {}
    for i in range(player_num):
      self.players[i] = PlayerState(self.plane_num)
    self.turn = 0
    self.isTerminal = False
    self.winner = -1
    self.dice_roll_res = random.randint(1, 6)

  def copy(self):
    copy = APCState(self.player_num)
    copy.players = {}
    for k, v in self.players.items():
      copy.players[k] = v.copy()
    copy.turn = self.turn
    copy.isTerminal = self.isTerminal
    copy.winner = self.winner
    copy.dice_roll_res = self.dice_roll_res
    return copy
    

class PlayerState:
  def __init__(self, plane_num):
    self.plane_num = plane_num
    # positions of each plane
    # position = None: plane has not taken off
    # position = -1: plane has taken off but not on track
    # position = [0, 49]: plane is on track
    # position = -2: plane is on final stretch
    self.plane_positions = [HOME] * self.plane_num
    self.plane_home = [False] * self.plane_num
    self.final_stretch = [-1] * self.plane_num

  def get_on_final_stretch(self, player_idx, plane, steps):
    """
    Given a plane number and steps to apply, check if the plane can get on final stretch.
    """
    range_start = ((player_idx - 1) % 4) * 13 + 5
    range_end = range_start + 5
    if self.plane_positions[plane] >= range_start and self.plane_positions[plane] <= range_end:
      return self.plane_positions[plane] + steps > range_end

  def copy(self):
    copy = PlayerState(self.plane_num)
    copy.plane_positions = self.plane_positions.copy()
    copy.plane_home = self.plane_home.copy()
    copy.final_stretch = self.final_stretch.copy()
    return copy


class APCEnv(gym.Env):
  metadata = {
    'render.modes': ['ascii']
  }

  def __init__(self):
    self.track_len = TRACK_LEN
    self.final_stretch_pos = [50, 11, 24, 37]  # first position on board to start final stretch for each player
    self.state = None
    self.empty_board = read_game_board()
    self.pos_to_board_pos = POS_TO_BOARDPOS

  def step(self, action):
    """
    Play the game for one round for one player.
    action: (player, plane) pair, where steps being 0 means that player choose to take off plane
    :return: copy of the state, reward for all players this round, boolean for termination, debug info
    debug info contains whether there will be another bonus round and a feature vector of the result of the action applied
    feature vector: [
      1 if get one plane out of home, 0 otherwise
      1 if get one plane to home, 0 otherwise
      1 if plane is blocked or overkills final stretch, 0 otherwise
      1 if plane gets on final stretch, 0 otherwise
      1 if plane big fly, 0 otherwise
      1 if plane small fly, 0 otherwise
      1 if plane kills opponents, 0 otherwise
      1 if plane sacrificed, 0 otherwise
      1 if plane moves normally, 0 otherwise
      1 if player won the game, 0 otherwise
    ]
    """
    feature_vector = [0] * FEATURES
    active_player_idx, plane = action
    steps = self.state.dice_roll_res
    bonus = steps == 6
    active_player = self.state.players[active_player_idx]
    self.state.turn += 1
    reward = [0] * 4
    # print information about the game
    # print(f"----------- Turn {self.state.turn} -----------")
    # print(f"Active Player: {PLAYER_TO_COLOR[active_player_idx]}")
    # print(f"Dice Roll: {self.state.dice_roll_res}")
    if plane == None:
      # print(f"No plane to move. PASS.")
      self.state.dice_roll_res = self._roll_dice()
      # print(f"Next Dice Roll: {self.state.dice_roll_res}")
      reward[active_player_idx] = PASS_REWARD
      feature_vector[NO_MOVE_IDX] = 1
      return self.state.copy(), reward, False, {"bonus": False, "feature": feature_vector}
    # print(f"Action: Plane {plane}")
    # check if selected plane has taken off
    if active_player.plane_positions[plane] == HOME:
      if not steps == 6:
        a = 2
      assert steps == 6
      active_player.plane_positions[plane] = TAKEN_OFF
      feature_vector[TAKE_OFF_IDX] = 1
    else:
      # plane has taken off

      # Step 1: Move the plane
      # first check if the plane is on final strech
      if active_player.plane_positions[plane] == FINAL_STRETCH:
        assert not active_player.final_stretch[plane] == -1
        cal_final_stretch = active_player.final_stretch[plane] + steps
        if cal_final_stretch > 5:
          reward[active_player_idx] = FINAL_STRETCH_OVERKILL_REWARD
          active_player.final_stretch[plane] = 5 - (cal_final_stretch - 5)
          feature_vector[BLOCKED_IDX]
        else:
          active_player.final_stretch[plane] = cal_final_stretch
        if active_player.final_stretch[plane] == 5:
          reward[active_player_idx] = BACK_HOME_REWARD
          active_player.plane_home[plane] = True
          active_player.plane_positions[plane] = BACK_HOME
          feature_vector[BACK_HOME_IDX] = 1
      else:
        # plane has taken off
        # if plane is not yet on track, put it on track
        if active_player.plane_positions[plane] == TAKEN_OFF:
          active_player.plane_positions[plane] = active_player_idx * 13
          steps -= 1
        # record old position
        old_pos = active_player.plane_positions[plane]
        # calculated new position, use this to calculate if fly, get on final stretch or blocked
        cal_new_pos = active_player.plane_positions[plane] + steps
        # first check if we're blocked
        block_pos = -1
        for pos in range(active_player.plane_positions[plane], cal_new_pos):
          planes_on_cur_pos, _ = self.planes_on_pos(pos, active_player_idx)
          if len(planes_on_cur_pos) > 1:
            block_pos = pos
            break
        # check if blocked
        if block_pos > 0:
          reward[active_player_idx] = BlOCKED_REWARD
          active_player.plane_positions[plane] = (block_pos - (cal_new_pos - block_pos)) % TRACK_LEN
          feature_vector[BLOCKED_IDX] = 1
        # check if we get on final stretch
        elif active_player.get_on_final_stretch(active_player_idx, plane, steps):
          reward[active_player_idx] = GET_ON_FINAL_STRETCH_REWARD
          active_player.plane_positions[plane] = FINAL_STRETCH
          active_player.final_stretch[plane] = cal_new_pos - self.final_stretch_pos[active_player_idx]
          feature_vector[GET_ON_FINAL_STRETCH_IDX] = 1
          if active_player.final_stretch[plane] == 5:
            reward[active_player_idx] = BACK_HOME_REWARD
            active_player.plane_home[plane] = True
            active_player.plane_positions[plane] = BACK_HOME
            feature_vector[BACK_HOME_IDX] = 1
        # check for big fly
        elif (cal_new_pos - active_player_idx * 13) % 52 == 17 or (cal_new_pos - active_player_idx * 13) % 52 == 13:
          reward[active_player_idx] = BIG_FLY_REWARD
          active_player.plane_positions[plane] = cal_new_pos + 16
          feature_vector[BIG_FLY_IDX] = 1
        # check for small fly
        elif (cal_new_pos - active_player_idx * 13 - 1) % 4 == 0:
          reward[active_player_idx] = SMALL_FLY_REWARD
          active_player.plane_positions[plane] = cal_new_pos + 4
          feature_vector[SMALL_FLY_IDX] = 1
        # just a normal move
        else:
          reward[active_player_idx] = NORMAL_REWARD
          active_player.plane_positions[plane] = cal_new_pos
          feature_vector[NORMAL_IDX] = 1

    if active_player.plane_positions[plane] >= 0:
      active_player.plane_positions[plane] = active_player.plane_positions[plane] % 52

    # Step 2: Check for collision
    planes_on, opponent = self.planes_on_pos(active_player.plane_positions[plane], active_player_idx)
    for opponent_plane in planes_on:
      reward[active_player_idx] += ATTACK_BONUS_REWARD
      reward[opponent] -= ATTACKED_PENALTY
      self.state.players[opponent].plane_positions[opponent_plane] = HOME
      feature_vector[ATTACK_IDX] = 1
    if len(planes_on) > 1:
      reward[active_player_idx] += SACRIFICE_PENALTY
      active_player.plane_positions[plane] = HOME
      feature_vector[SACRIFICE_IDX] = 1

    # Step 3: Check for plane arriving home
    for p in range(active_player.plane_num):
      if active_player.final_stretch[p] == 5:
        active_player.plane_home[p] = True

    # Step 4: Check for ternimation
    if all(active_player.plane_home):
      self.state.isTerminal = True
      self.state.winner = active_player_idx
      reward[active_player_idx] = WINNING_REWARD
      for i in range(self.state.player_num):
        if not i == active_player_idx:
          reward[i] = LOSING_PANELTY
      feature_vector[WINNING_IDX] = 1
      return self.state.copy(), reward, True, {"bonus": False, "feature": feature_vector}

    # Step 5: Roll dice for next round
    self.state.dice_roll_res = self._roll_dice()
    # print(f"Next Dice Roll: {self.state.dice_roll_res}")
    return self.state.copy(), reward, False, {"bonus": bonus, "feature": feature_vector}
      
  def reset(self):
    self.state = APCState()
    return self.state.copy()

  def get_actions(self, player):
    actions = []
    player_state = self.state.players[player]
    for plane in range(player_state.plane_num):
      if not player_state.plane_home[plane]:
        if not player_state.plane_positions[plane] == HOME:
          actions.append((player, plane))
        else:
          if self.state.dice_roll_res == 6:
            actions.append((player, plane))
    return actions

  def close(self):
    pass

  def copy(self):
    copy = APCEnv()
    copy.state = self.state.copy()
    return copy

  def render(self):
    game_board = self.empty_board.copy()
    pos_keys_seen = {}
    # render all planes
    for player in range(self.state.player_num):
      player_color = PLAYER_TO_COLOR[player]
      player_state = self.state.players[player]
      for plane in range(player_state.plane_num):
        plane_pos = player_state.plane_positions[plane]
        # print(f"Plane Pos: {plane_pos}")
        pos_key = "placeholder"
        if plane_pos == HOME:
          pos_key = player_color + player_color + str(plane)
        elif plane_pos == TAKEN_OFF:
          pos_key = f"-1{player_color}"
        elif plane_pos >= 0 and plane_pos <= 51:
          pos_key = str(plane_pos)
        elif plane_pos == BACK_HOME or player_state.plane_home[plane]:
          pos_key = player_color + player_color + str(plane)
          player_color = "*"
        elif plane_pos == FINAL_STRETCH:
          final_stretch_pos = player_state.final_stretch[plane]
          assert not final_stretch_pos == -1
          if final_stretch_pos == 5:
            pos_key = "WIN"
          else:
            pos_key = "f" + player_color + str(final_stretch_pos)
        assert not pos_key == "placeholder"
        if not pos_key in pos_keys_seen:
          pos_keys_seen[pos_key] = 0
        else:
          pos_keys_seen[pos_key] += 1
        # print(f"Pos_key: {pos_key}")
        pos_to_replace = self.pos_to_board_pos[pos_key]
        if isinstance(pos_to_replace, list):
          pos_to_replace = pos_to_replace[pos_keys_seen[pos_key]]
        # print(f"Pos_to_replace: {pos_to_replace}")
        temp_line = list(game_board[pos_to_replace[0]])
        temp_line[pos_to_replace[1]] = player_color
        temp_line[pos_to_replace[1] + 1] = str(plane)
        game_board[pos_to_replace[0]] = ''.join(temp_line)
        player_color = PLAYER_TO_COLOR[player]

    for line in game_board:
      print(line.rstrip())

  def _roll_dice(self):
    """
    Roll a dice.
    :return: A random integer between 1 and 6 (inclusive).
    """
    # if self.state.turn < 4:
    #   return 6
    # return 1
    return random.randint(1, 6)

  def planes_on_pos(self, pos, active_player):
    """
    Check how many planes are on the given position that does not belong to the given player.
    :return: Number of planes of the same opponent players on a given position
    """
    planes_on_pos = []
    opponent = -1
    if pos == HOME or pos == TAKEN_OFF or pos == BACK_HOME or pos == FINAL_STRETCH:
      return planes_on_pos, opponent
    for player, player_state in self.state.players.items():
      if not player == active_player:
        opponent_plane = 0
        for p in player_state.plane_positions:
          if p == pos:
            opponent = player
            planes_on_pos.append(opponent_plane)
          opponent_plane += 1
    return planes_on_pos, opponent
