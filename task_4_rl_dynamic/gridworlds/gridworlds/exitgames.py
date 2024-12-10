import curses
import sys
import types

import numpy as np
from pycolab import ascii_art
from pycolab.prefab_parts import sprites as prefab_sprites

# Colors for curses ui
COLOUR_FG = {' ': (950, 950,950),
             'x': (848, 225, 268),
             'E': (225, 464, 542),
             '#': (610, 610, 610),
             'P': (97, 996, 0),
           }

COLOUR_BG = {'x': (950,950,950),
             'E': (225, 464, 542),
             'P': (97, 996, 0),
             }

MAZES_ART = [
    # Maze #1
    ['######',
     '#   E#',
     '# x  #',
     '#  x #',
     '#P   #',
     '######'],

    # Maze #1
    ['##################',
     '#   xx   x   x  E#',
     '# #  x x x x x # #',
     '# ## x x x x x #x#',
     '#  # x x x x x # #',
     '## # x x x x x #x#',
     '#  #   x   x   # #',
     '# ##############x#',
     '#P x   x   x   x #',
     '##################'],

     # Maze #2
    ['###########################################',
     '#   x     x      x   x    x  x   x   x   E#',
     '#  x     x    x  x       x        x    xxx#',
     '#     x     x      x  x   x  x  xx   x  x #',
     '#        x x   x   x   x    x  x  x x   x #',
     '#   x        x       x     x  x   x   xx x#',
     '#    x  x   xx   x     x    x   x  x  x x #',
     '#  x     xx    x   x        x   x  x  x   #',
     '#     x   x       xx  x x    x   x   x  x #',
     '#   x   x   xx     x      x xx      x   x #',
     '#  x   x       x      x    x    x x    x  #',
     '#     x    xxx     x    x x   xx   x  x x #',
     '# x    x  x    x          x     x    x    #',
     '#   x   x      x   x  xx       x   x  xx  #',
     '#  x     x   x  x    x    x       x   x  x#',
     '#    x     x  xx  x   x        x    x  x  #',
     '# x    x   xx  x   x   x x     x x x  x  x#',
     '#  x  x  xx      x x      xx        x    x#',
     '# x   x    x  x   x  x x     x   x  x  xxx#',
     '#    x  x    x   x    x     x     x  x  x #',
     '#P x   x  x       x   x   x    x   x   xx #',
     '###########################################',]
    ]

# additional convenience method that gets attached to an exitgame
def get_action_set(self):
    return self._action_set

# additional convenience method that gets attached to an exitgame
def print_action_meanings(self):
    print({0: "NORTH", 1: "SOUTH", 2: "WEST", 3: "EAST", 4: "STAY"})

def get_world_map(self):

  if self._map is None:
    map = "".join(MAZES_ART[self._level])
    map = np.array([ord(i) for i in map], dtype='uint8').reshape(self.rows, self.cols)
    map[map == ord("P")] = ord(" ")

    self._map = map

  return self._map

def allowed_actions(self, index):

  assert isinstance(index, tuple) and len(index) == 2, "Index must be a tuple and of length two: (row,col)."

  if self._map[index] == ord("E"):
    return {4: prefab_sprites.MazeWalker._STAY}

  if self._map[index] == ord("#"):
    return {}

  A = {}
  for key,action in self._action_set.items():
    next_state = tuple(np.add(index, action))

    if self._map[next_state] != ord("#"):
      A[key] = action
  return A

def make_game(level):

  # default pycolab setup
  game =  ascii_art.ascii_art_to_game(
      MAZES_ART[level],
      what_lies_beneath=' ',
      sprites={
          'P': ascii_art.Partial(PlayerSprite)
          },
      #drapes={},
      update_schedule=['P'],
      z_order='P')

  # add some convenience attributes and methods
  game._level = level
  game._map = None
  game.action_space = 5
  game.state_space = (game.rows - 2, game.cols - 2)
  game._action_set = {
    0: prefab_sprites.MazeWalker._NORTH,
    1: prefab_sprites.MazeWalker._SOUTH,
    2: prefab_sprites.MazeWalker._WEST,
    3: prefab_sprites.MazeWalker._EAST,
    4: prefab_sprites.MazeWalker._STAY
  }
  game.get_action_set = types.MethodType(get_action_set, game)
  game.print_action_meanings = types.MethodType(print_action_meanings, game)
  game.get_world_map = types.MethodType(get_world_map, game)
  game.allowed_actions = types.MethodType(allowed_actions, game)
  game._map = game.get_world_map()
  return game

class PlayerSprite(prefab_sprites.MazeWalker):

  def __init__(self, corner, position, character):
    super(PlayerSprite, self).__init__(
        corner, position, character, impassable='#')

  def update(self, actions, board, layers, backdrop, things, the_plot):
    del backdrop, things # Unused

    if actions == 0:    # go upward?
      self._north(board, the_plot)
    elif actions == 1:  # go downward?
      self._south(board, the_plot)
    elif actions == 2:  # go leftward?
      self._west(board, the_plot)
    elif actions == 3:  # go rightward?
      self._east(board, the_plot)
    elif actions == 4:  # do nothing?
      self._stay(board, the_plot)
    elif actions == 5:  # quit?
      the_plot.terminate_episode()

    if layers['E'][self.position]:
      the_plot.add_reward(1)
      the_plot.terminate_episode()

    if layers['x'][self.position]:
      the_plot.add_reward(-1)

# helper utility that returns a render proxy to be used in jupyter notebooks
def get_notebook_ui():
  from gridworlds import human_ui
  return human_ui.NotebookUi(style="COLOR", colour_fg=COLOUR_FG, colour_bg=COLOUR_BG)

# helper utility that returns a human playable version of exitgames in a jupyter notebook
def play_notebook(level=0, style="COLOR", game_fps=10, input_fps=100):
  import pygame
  from gridworlds import human_ui
  game = make_game(level)

  keys_to_actions =  {pygame.K_UP:    0,
                      pygame.K_DOWN:  1,
                      pygame.K_LEFT:  2,
                      pygame.K_RIGHT: 3,
                      -1: 4,
                      pygame.K_q: 5}

  ui = human_ui.NotebookUi(keys_to_actions,
                           colour_fg=COLOUR_FG,
                           colour_bg=COLOUR_BG,
                           style=style, game_fps=game_fps, input_fps=input_fps)
  ui.play(game)

def main(argv=()):
  from pycolab import human_ui
  game = make_game(int(argv[1]) if len(argv) > 1 else 0)

  # Make a CursesUi to play it with. (in Terminal mode)
  ui = human_ui.CursesUi(
      keys_to_actions={curses.KEY_UP: 0, curses.KEY_DOWN: 1,
                       curses.KEY_LEFT: 2, curses.KEY_RIGHT: 3,
                       -1: 4,
                       'q': 5, 'Q': 5},
      delay=50, colour_fg=COLOUR_FG, colour_bg=COLOUR_BG)

  ui.play(game)

if __name__ == '__main__':
  main(sys.argv)
