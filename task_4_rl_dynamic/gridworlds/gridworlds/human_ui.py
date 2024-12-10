import time
import datetime

import pygame
import pycolab
import numpy as np
from IPython import display
#display.display(display.HTML("<style> .output_stdout pre {line-height: 1.0;} </style>"))

# simple time utiliy
def convert_timedelta(timedelta):
    hours   = timedelta.seconds // 3600
    minutes = timedelta.seconds // 60 % 60
    seconds = timedelta.seconds % 60
    return hours, minutes, seconds

# simple color scaling utility
def convert_curses_colors(color, reverse=False):

  from_scale = 999
  to_scale = 255
  if reverse: from_scale, to_scale = to_scale, from_scale

  r = int(color[0] / from_scale * to_scale)
  g = int(color[1] / from_scale * to_scale)
  b = int(color[2] / from_scale * to_scale)

  return (r,g,b)

class NotebookUi(object):

  def __init__(self, keycodes_to_actions={}, style="ASCII", colour_fg={}, colour_bg={}, game_fps=10, input_fps=100,  K_NOOP=-1, character_mapping=None):

    self._keycodes_to_actions = keycodes_to_actions

    # If keycodes are provided, set up for human game play,
    # ELSE: just use as a render proxy
    if self._keycodes_to_actions:
      self._game = None
      self._start_time = None
      self._total_return = None
      self._NOOP = self._keycodes_to_actions[K_NOOP]
      self._PygameInterface = PygameInterface(self._keycodes_to_actions, K_NOOP)
      self._game_fps = game_fps
      self._input_fps=input_fps
      self._key_repeat_limit= self._input_fps // self._game_fps
      self._style=style

    #self._COLOUR_FG = {key:("\x1b[38;2;%s;%s;%sm" % convert_curses_colors(value)) for key,value in colour_fg.items()}
    #self._COLOUR_BG = {key:("\x1b[48;2;%s;%s;%sm" % convert_curses_colors(value)) for key,value in colour_bg.items()}
    self._COLOUR_FG = {key:("rgb(%s,%s,%s)" % convert_curses_colors(value)) for key,value in colour_fg.items()}
    self._COLOUR_BG = {key:("rgb(%s,%s,%s)" % convert_curses_colors(value)) for key,value in colour_bg.items()}
    self._character_mapping = character_mapping

    for char in self._COLOUR_FG:
      if char not in self._COLOUR_BG:
        #self._COLOUR_BG[char] = "\x1b[48;2;%s;%s;%sm" % convert_curses_colors(colour_fg[char])
        self._COLOUR_BG[char] = "rgb(%s,%s,%s)" % convert_curses_colors(colour_fg[char])

  def render(self, observation, style="ASCII", total_return=None, elapsed=None, fps=None):

    # General Game Info
    game_info = []
    if total_return is not None: game_info.append("Score: %s " % total_return)
    if elapsed:      game_info.append("Time: %s:%s:%s " % (convert_timedelta(elapsed)))
    if fps:          game_info.append("FPS: %2.0f." % fps)
    if game_info: print(''.join(game_info))

    # Rendering options: ASCII, COLOR, ALL
    if isinstance(observation, pycolab.rendering.Observation):
      board = observation.board
    elif  isinstance(observation, np.ndarray):
      board = observation
    else:
      raise RuntimeError('NotebookUi can not render: %s. Use <numpy.ndarray> or <pycolab.rendering.Observation>.' % type(observation))

    # Color rendering imitating ncurses Terminal print
    if style == "COLOR" or style == "ALL":
      rows = ['<pre style="line-height:1.1;">']

      for row in board:
        row_chars = []

        last_c = ''
        for char in row:
          c = char.tostring().decode('ascii')
          if self._character_mapping is not None and c in self._character_mapping:
            c = self._character_mapping[c]

          if c != last_c:
            last_c = c
            if row_chars:
              row_chars.append('</span>')
            row_chars.append('<span style="')
            if c in self._COLOUR_FG: row_chars.append('color: %s;' % self._COLOUR_FG[c])
            if c in self._COLOUR_BG: row_chars.append('background-color: %s;' % self._COLOUR_BG[c])
            row_chars.append('">')
          row_chars.append(c)
        row_chars.append('</span>\n')
        #row_chars.append("\n")
        rows.append(''.join(row_chars))
        #rows.append("\x1b[0m")
      #print(''.join(rows))
      display.display(display.HTML(''.join(rows)))


    # ASCII rendering
    if style == "ASCII" or style == "ALL":
      rows = ['<pre style="line-height:1.1;">']
      for row in board:
        rows.append(row.tostring().decode('ascii'))
        rows.append("\n")
      #print(''.join(rows))
      display.display(display.HTML(''.join(rows)))
    display.clear_output(wait=True)


  def play(self, game):

    if not self._keycodes_to_actions:
      raise RuntimeError('NotebookUi was initialized without keycodes_to_actions!')

    if self._game is not None:
      raise RuntimeError('NotebookUi is not at all thread safe')

    pygame.init()
    pygame.display.set_caption("Exitgames")
    pygame.display.set_mode((200,200))
    self._clock = pygame.time.Clock()
    self._game = game
    self._start_time = datetime.datetime.now()
    self._last_action = None
    self._total_return = 0

    # initialize the game
    observation, reward, _ = self._game.its_showtime()
    self.last_observation = observation.board.copy()
    if reward is not None:
          self._total_return += reward
    self.render(observation, self._style, self._total_return, datetime.datetime.now() - self._start_time, self._game_fps)

    # start the game loop
    self._game_loop()

    # game is over now, print info and...
    duration = datetime.datetime.now() - self._start_time
    hours, minutes, seconds = convert_timedelta(duration)
    print('Great! You finished the game in %s:%s:%s with a score of %s.' % (hours, minutes, seconds, self._total_return))
    # clean up!
    pygame.quit()
    self._game = None
    self._start_time = None
    self._total_return = None
    self._last_action = None

  def _game_loop(self):

    self._key_repeat = 0

    # Run pygame at _input_fps (e.g. high framerate) for fast key detection.
    while not self._game.game_over:
      self._clock.tick(self._input_fps)
      action =  self._keycodes_to_actions[self._PygameInterface.get_key()]

      # Run the game logic only every key_repeat_limit frame so it is still "controllable" for humans and not to fast
      # Note that _last_action and current action are compared so that key changes are still detected fast!
      if (self._last_action == action) and (self._key_repeat < self._key_repeat_limit): #and (action is not self._NOOP):
        self._key_repeat += 1
      else:
        self._key_repeat = 0
        self._last_action = action
        observation, reward, _ = self._game.play(action)

        # Handle Reward
        if reward is not None:
          self._total_return += reward

      # render only if board is "dirty" (e.g. if something has changed)
      if np.array_equal(self.last_observation, observation.board):
        pass
      else:
        elapsed = datetime.datetime.now() - self._start_time
        self.render(observation, self._style, self._total_return, elapsed, self._game_fps)
        self.last_observation = observation.board.copy()

class PygameInterface(object):

  def __init__(self, keycodes_to_actions, K_NOOP=-1):

    self._K_NOOP = K_NOOP
    self._key_states = {key:False for key in keycodes_to_actions}

  def _update(self):

    keys = pygame.key.get_pressed()
    for key in  self._key_states:
      if keys[key]:
        self._key_states[key] = True
        break
      else:
        self._key_states[key] = False

    pygame.event.clear()
    '''
    # event based key detection
    for event in pygame.event.get():
      #pass
      if event.type == pygame.KEYUP:
        for key in self._key_states:
          if event.key == key:
            #return self._K_NOOP
            self._key_states[key] = False

      if event.type == pygame.KEYDOWN:
        for key in self._key_states:
          if event.key == key:
            #return key
            self._key_states[key] = True
    '''
  def get_key(self):
    self._update()

    key = self._K_NOOP # If no key was pressed, return NOOP key
    for k,pressed in self._key_states.items():
      if pressed:
        key = k
        break

    return key
