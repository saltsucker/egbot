import unittest
from unittest import mock
from eg import EGbot, main

class TestUnitManager(unittest.TestCase):
    def setUp(self):
        self.eg = EGbot()

    def test_add_unit(self):
        """_initialize_variables
        probably needs to be called to set up the proper vars. 
        This normally gets called by `run_game` but since we're not running the game, we need to
        sharpy mockbot also calls this
        """
        # main()
        self.eg._initialize_variables()
        self.eg.state = mock.Mock()
        self.eg.state.game_loop = mock.Mock()
        self.eg._game_data = mock.Mock()
        