"""The game cerver: its game types, its lobbies with their players and their objects, and the scoreboards."""

from . import games, gametypes, lobbies, players, scores

from .games import *
from .gametypes import *
from .lobbies import *
from .players import *
from .scores import *

__all__ = games.__all__ + gametypes.__all__ + lobbies.__all__ + players.__all__ + scores.__all__
