import itertools
from operator import mul
from functools import reduce
import matplotlib.pyplot as plt

LEAGUE_AVE_THREE_PERC = 0.362
LEAGUE_AVE_TWO_PERC = 0.510

class Team:

    def __init__(self, three_perc, two_perc, ft_perc, three_defen_perc, two_defen_perc):
        self.three_perc = three_perc
        self.two_perc = two_perc
        self.ft_perc = ft_perc
        self.three_defen_perc = three_defen_perc
        self.two_defen_perc = two_defen_perc

    def get_two_perc_against(self, team2):
        return self.two_perc * team2.two_defen_perc / LEAGUE_AVE_TWO_PERC

    def get_three_perc_against(self, team2):
        return self.three_perc * team2.three_defen_perc / LEAGUE_AVE_THREE_PERC

    def get_ft_perc_against(self, team2):
        return team2.ft_perc

class State:
    def __init__(self):
        self.probs = []
        self.states = []
        self.team1 = None
        self.team2 = None
        self.score_diff = -1
        self.time = -1
        self.pos = -1

    def is_chance_state(self):
        pass

    def is_gameover(self):
        return False

class ChanceState(State):
    def __init__(self, probs, states, last_move):
        self.probs = probs
        self.states = states
        self.pos = 0
        self.last_move = last_move

        self.team1 = 1
        self.team2 = 1
        self.score_diff = -1
        self.time = -1
        self.pos = -1

    def __str__(self):
        return str(self.last_move)

    def __eq__(self, other):
        return self.probs == other.probs and self.states == other.states and self.last_move == other.last_move

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return sum(map(lambda state: hash(state), self.states)) * 3 + int(sum(self.probs) * 5) + hash(self.last_move) * 7

    def is_chance_state(self):
        return True

    def is_gameover(self):
        return False

    def get_state_prob(self, index):
        return self.probs[index]

    def get_child_states(self):
        return  self.states

class Move:

    def __init__(self, game_state):
        self.pos_change = True
        self.time_consump = 0
        self.score_change = 0
        self.occ_count = 0
        self.prob_func = lambda x, y: x
        self.game_state = game_state

    def __str__(self):
        return "Take a " + self.__class__.__name__ + " in " + str(self.time_consump) + " seconds."

    def is_applyable(self):
        time = self.game_state.time - self.time_consump
        return time >= -4

    def get_chance_child(self):
        team1 = self.game_state.team1
        team2 = self.game_state.team2

        if self.pos_change:
            new_pos = 1 if self.game_state.pos == 2 else 2
        else:
            new_pos = self.game_state.pos

        time = self.game_state.time - self.time_consump

        score_diff = self.game_state.score_diff

        states = []
        probs = []

        if self.game_state.pos == 2:
            t1 = team2
            t2 = team2
        else:
            t1 = team1
            t2 = team2

        for make_comb in itertools.product([1, 0], repeat=self.occ_count):
            ## 1 - self.prob_func(t1, t2), self.prob_func(t1, t2)
            # Make
            if self.game_state.pos == 1:
                score_diff = self.game_state.score_diff + self.score_change * sum(make_comb)
            else:
                score_diff = self.game_state.score_diff - self.score_change * sum(make_comb)

            prec = self.prob_func(t1, t2)
            prob_comb = list(map(lambda score_chan: prec if score_chan == 1 else 1 - prec, make_comb))

            gs = GameState(team1, team2, score_diff, time, new_pos)
            states.append(gs)
            probs.append(reduce(mul, prob_comb, 1))


        return ChanceState(probs, states, self)


class TwoPointer(Move):

    def __init__(self, quick, game_state):
        self.pos_change = True
        self.time_consump = 4 if quick else 15
        self.score_change = 2
        self.occ_count = 1
        self.prob_func = Team.get_two_perc_against
        self.game_state = game_state


class ThreePointer(Move):

    def __init__(self, quick, game_state):
        self.pos_change = True
        self.time_consump = 4 if quick else 15
        self.score_change = 3
        self.occ_count = 1
        self.prob_func = Team.get_three_perc_against
        self.game_state = game_state

class Foul(Move):

    def __init__(self, game_state):
        self.pos_change = False
        self.time_consump =  2
        self.score_change = -1
        self.occ_count = 2
        self.prob_func = Team.get_ft_perc_against
        self.game_state = game_state



class GameState(State):

    def __init__(self, team1, team2, score_diff, time, pos):
        self.team1 = team1
        self.team2 = team2
        self.score_diff = score_diff
        self.time = time
        self.pos = pos
        self.probs = []
        self.states = []
        self.last_move = 1


    def __eq__(self, other):
        return self.team1 == other.team1 and self.team2 == other.team2 and self.score_diff == other.score_diff and self.time == other.time and self.pos == other.pos

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return str(self.time)

    def __hash__(self):
        return self.score_diff * 3 + self.time * 5 + self.pos * 7

    def get_heuristic_score(self):
        if self.score_diff <= 0:
            return 0
        else:
            return 1

    def is_gameover(self):
        return self.time <= 0

    def get_child_states(self):
        return list(map(lambda move: move.get_chance_child(), self.get_available_moves()))

    def get_available_moves(self):
        quick_three = ThreePointer(True, self)
        slow_three = ThreePointer(False, self)
        quick_two = TwoPointer(True, self)
        slow_two = TwoPointer(False, self)
        foul = Foul(self)
        moves = [quick_three, slow_three, quick_two, slow_two, foul]
        return list(filter(lambda move: move.is_applyable(), moves))

    def is_chance_state(self):
        return False



def run_expectiminimax(start_state, max_depth):

    dp = {}

    def expectiminimax(state, depth):

        if not state.is_chance_state() and (state.is_gameover() or depth == 0):
            return state.get_heuristic_score()

        if state.pos == 1:
            alpha = float('-inf')
            alpha_child = None
            for child in state.get_child_states():
                if child in dp:
                    val = dp[child]
                else:
                    val = expectiminimax(child, depth - 1)
                    dp[child] = val
                if val > alpha:
                    alpha = val
                    alpha_child = child
            if state == start_state:
                print(alpha_child)
        elif state.pos == 2:
            alpha = float('inf')
            for child in state.get_child_states():
                if child in dp:
                    val = dp[child]
                else:
                    val = expectiminimax(child, depth - 1)
                    dp[child] = val
                alpha = min(alpha, val)
        elif state.is_chance_state():
            alpha = 0
            for i, child in enumerate(state.get_child_states()):
                if child in dp:
                    val = dp[child]
                else:
                    val = expectiminimax(child, depth - 1)
                    dp[child] = val
                alpha += state.get_state_prob(i) * val
        else:
            print("SHOULDN'T BE HERE!")

        return alpha



    max_prob = expectiminimax(start_state, max_depth)
    return max_prob
