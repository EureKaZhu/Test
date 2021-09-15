# -*- coding: utf-8 -*-
"""
human VS AI models
Input your move in the format: 2,3
"""

from __future__ import print_function
import pickle
from game import Board, Game
from vision import init, human_step,Who_first
from mcts_ZT import MCTSPlayer
from policy_value_net_numpy import PolicyValueNetNumpy


class Human(object):
    """
    human player
    """

    def __init__(self):
        self.player = None

    def set_player_ind(self, p):
        self.player = p

    def get_action(self, board):
        try:
            location = human_step()
            move = board.location_to_move(location)
        except Exception as e:
            move = -1
        if move == -1 or move not in board.availables:
            move = 0
        return move

    def __str__(self):
        return "Human {}".format(self.player)


def run():
    init()
    n = 5
    width, height = 8, 8
    model_file = 'best_policy_8_8_5.model'
    try:
        board = Board(width=width, height=height, n_in_row=n)
        game = Game(board)

        # load the provided model (trained in Theano/Lasagne) into a MCTS player written in pure numpy
        try:
            policy_param = pickle.load(open(model_file, 'rb'))
        except:
            policy_param = pickle.load(open(model_file, 'rb'),
                                       encoding='bytes')  # To support python3
        best_policy = PolicyValueNetNumpy(width, height, policy_param)
        mcts_player = MCTSPlayer(best_policy.policy_value_fn,
                                 c_puct=5,
                                 n_playout=400)  # set larger n_playout for better performance

        who_first = Who_first()

        human = Human()

        # set start_player=0 for human first

        if who_first == 1:
            game.start_play(human, mcts_player, start_player=0, is_shown=1)
        else:
            game.start_play(human, mcts_player, start_player=1, is_shown=1)
    except KeyboardInterrupt:
        print('\n\rquit')


if __name__ == '__main__':
    run()
