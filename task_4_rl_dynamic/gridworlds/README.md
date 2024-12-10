# Gridworld Games for Reinforcement Learning

This is a collection of simple gridworld games for teaching reinforcement learning. The package is based on the [pycolab](https://github.com/deepmind/pycolab) engine. It also extends the pycolab functionality with an HTML render mode to play pycolab in a jupyter notebook. The pygame library is used to handle human input.

## Install

```
git clone https://github.com/deepmind/pycolab.git
pip install -e pycolab

git clone https://gitlab.mi.hdm-stuttgart.de/theodoridis/gridworlds.git
pip install -e gridworlds
```

- WINDOWS ONLY: `pycolab` requires the `curses` package which is not available by default. To install a compatible binary, [download the corresponding version from here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#curses). For instance, choose **"curses‑2.2.1+utf8‑cp38‑cp38‑win_amd64.whl"** for python 3.8 on a 64 bit system. Then install with:

```
pip install curses‑2.2.1+utf8‑cp38‑cp38‑win_amd64.whl
```

## Examples

**Human gameplay in a terminal**:

```bash
# Adjust path to the exitgames.py file, choose level: 0 (default),1,2
# See the main method for code details.
python ./gridworlds/gridworlds/exitgames.py 0 
```

**Human gameplay in a jupyter notebook**:
```python
from gridworlds import exitgames

# Goal: Find the exit and avoid the traps
# Actions: Arrow Keys to move, q to quit
# Style Options: "COLOR", "ASCII", "ALL" (will render both)

exitgames.play_notebook(level=0, style="COLOR")
```

**Programmatical gameplay in jupyter notebook**:

```python
from gridworlds import exitgame

# create a new game
game = exitgames.make_game(level=0)

# initialize the game, this will return an observation, the first reward and 
# some additional information (_).
observation, reward, _ = game.its_showtime()

# You can get a more human friendly "rendering" of the board by
# printing the ASCII codes of the board as actual characters. For starters, simply use the notebook_ui utility.
ui = exitgames.get_notebook_ui()

# Style Options: "COLOR", "ASCII", "ALL" (will render both)
ui.render(observation.board, "ASCII")

# Print the actin space
print(game.action_space)

# Get the action set, action keys
actions = game.get_action_set()
print(actions)

# Print the action meanings for the key codes
game.print_action_meanings()

# Execute a step in the environment using the key codes. This should be used in a loop.
observation, reward, _ = game.play(0)

# Check if the game is over, if so, create a new game
if game.game_over:
    game = exitgames.make_game(level=0)

# ENJOY :)
