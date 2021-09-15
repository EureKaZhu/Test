"""
@author:ZhuTian
"""

import numpy as np
import copy
from vision import AI_step


def softmax(x):
    probs = np.exp(x - np.max(x))
    probs /= np.sum(probs)
    return probs

class TreeNode(object):
    """
    MCTS里面的结点，每个节点保存自身的价值Q，先验概率P和得分U
    """
    def __init__(self, parent, prior_p):
        self._parent = parent
        self._children = {} #初始化孩子节点
        self._n_visits = 0
        self._Q = 0
        self._u = 0
        self._P = prior_p

    def expand(self, action_priors):
        """
        树的扩展
        action_priors:由策略函数生成可能的动作和他们的先验概率组成的列表
        """
        for action,prob in action_priors:
            if action not in self._children:
                self._children[action] = TreeNode(self, prob)
            #如果该动作不在孩子节点中，添加到孩子节点中去

    def select(self, c_puct):
        """
        从孩子中挑选Q+U(P)最大的的结点
        """
        return max(self._children.items(),key=lambda act_node:act_node[1].get_value(c_puct))

    def update(self, leaf_value):
        """
        从叶子节点的评估更新根节点的值
        leaf_value:从当前玩家的角度，子树评估的价值
        """
        #Count visit
        self._n_visits += 1
        #从所有访问中更新Q
        self._Q += 1.0*(leaf_value - self._Q) / self._n_visits

    def update_recursive(self, leaf_value):
        """
        回溯阶段
        """
        #如果不是根节点，先更新该节点的父结点
        if self._parent:
            self._parent.update_recursive(-leaf_value)

        self.update(leaf_value)

    def get_value(self, c_puct):
        """
        计算并返回结点的价值
        c_cupt:一个正实数，控制Q，P在节点得分上的相关影响
        """
        self._u = (c_puct * self._P * np.sqrt(self._parent._n_visits) / (1 + self._n_visits))
        return self._Q + self._u

    def is_leaf(self):
        """
        检查是否为叶子节点
        """
        return self._children == {}

    def is_root(self):
        return self._parent is None


class MCTS(object):
    """
    蒙特卡洛树搜索主程序
    """

    def __init__(self,policy_value_fn,c_puct = 5, n_playout = 10000):
        """
        :param policy_value_fn: 一个为当前的玩家输入现有状态，然后输出一个(action,probability)元组，和一个[-1,1]之间的分数
        """
        self._root = TreeNode(None, 1.0)
        self._policy = policy_value_fn
        self._c_puct = c_puct
        self._n_playout = n_playout

    def _playout(self, state):
        """
        从根节点到叶结点跑一轮，然后给叶子节点一个价值，反向传播到父结点上
        """
        node = self._root
        while(1):
            if node.is_leaf():
                break
            action, node = node.select(self._c_puct)
            state.do_move(action)

        action_probs, leaf_value = self._policy(state)
        end, winner = state.game_end()
        if not end:
            node.expand(action_probs)
        else:
            if winner == -1:
                leaf_value = 0.0
            else:
                leaf_value = (1.0 if winner == state.get_current_player() else -1.0)

        node.update_recursive(-leaf_value)


    def get_move_probs(self, state, temp = 1e-3):
        """
        跑遍所有可能，返回可能的行动和他们对应的概率
        :param state:当前游戏状态
        :param temp:控制exploration的临时参数
        """
        for n in range(self._n_playout):
            state_copy = copy.deepcopy(state)
            self._playout(state_copy)

        act_visits = [(act, node._n_visits) for act, node in self._root._children.items()]
        acts, visits = zip(*act_visits)
        act_probs = softmax(1.0/temp * np.log(np.array(visits) + 1e-10))

        return acts, act_probs

    def update_with_move(self,last_move):
        """
        在树中向前进行，保持所有子树已知的消息
        """
        if last_move in self._root._children:
            self._root = self._root._children[last_move]
            self._root._parent = None
        else:
            self._root = TreeNode(None, 1.0)

    def __str__(self):
        return "MCTS"


class MCTSPlayer(object):
    """
    MCTS生成的人工智能
    """
    def __init__(self, policy_value_function, c_puct=5, n_playout = 2000, is_selfplay = 0):
        self.mcts = MCTS(policy_value_function,c_puct,n_playout)
        self._is_selfplay = is_selfplay

    def set_player_ind(self,p):
        self.player = p

    def reset_player(self):
        self.mcts.update_with_move(-1)

    def get_action(self,board,temp = 1e-3,return_prob = 0):
        sensible_moves = board.availables
        move_probs = np.zeros(board.width*board.height)
        if len(sensible_moves) > 0:
            acts, probs = self.mcts.get_move_probs(board,temp)
            move_probs[list(acts)] = probs
            if self._is_selfplay:
                #为了自我对抗阶段的训练需要添加随机因素
                move = np.random.choice(acts, p = 0.75*probs+0.25*np.random.dirichlet(0.3*np.ones(len(probs))))
                self.mcts.update_with_move(move)
            else:
                move = np.random.choice(acts,p= probs)
                self.mcts.update_with_move(-1)
                location = board.move_to_location(move)
                AI_step(location[0], location[1])
                #print("AI move: %d,%d\n" %(location[0],location[1]))

            if return_prob:
                return move, move
            else:
                return move
        else:
            print("WARNING:the board is full")

    def __str__(self):
        return "MCTS {}".format(self.player)

