def read_game_board():
  with open("empty_board.txt") as fp:
    res = fp.readlines()
  return res
  
def read_label_board():
  labeled_board = []
  with open("labeled_board.txt") as fp:
    labeled_board = fp.readlines()
  res = {}
  # all positions on track
  for i in range(52):
    line, pos = _find_pos(labeled_board, " " + str(i))
    res[i] = [(line, pos + 1), (line - 1, pos + 1), (line + 1, pos + 1)]
  colors = ["B", "Y", "G", "R"]
  for color in colors:
    # all home position
    for i in range(4):
      str_to_find = color + color + str(i)
      res[str_to_find] = _find_pos(labeled_board, str_to_find)
    # all starting position
    str_to_find = "-1" + color
    ine, pos = _find_pos(labeled_board, str_to_find)
    res[str_to_find] = [(line, pos), (line + 1, pos), (line + 2, pos), (line + 3, pos)]
    # all final strech positions
    for i in range(5):
      str_to_find = "f" + color + str(i)
      line, pos = _find_pos(labeled_board, str_to_find)
      res[str_to_find] = [(line, pos), (line - 1, pos), (line + 1, pos)]
  return res

def _find_pos(labeled_board, str_to_find):
  for j in range(len(labeled_board)):
      pos = labeled_board[j].find(str_to_find)
      if pos >= 0:
        return (j, pos)