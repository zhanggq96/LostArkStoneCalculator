# Based on: https://github.com/nwtnni/facet

import sys
import math
import pickle
from typing import Tuple
from fractions import Fraction
from copy import deepcopy


statehash = {} # records (optimal move, prob_success)
class State:
    NUM_HIT_PROB_STATES = 6
    PROB_MAP = {i: Fraction(25+10*i, 100) for i in range(NUM_HIT_PROB_STATES)} # 25, 35, ..., 75 
    
    def __init__(self, successes=(0,0,0), attempts=(0,0,0), hit_prob=NUM_HIT_PROB_STATES-1, length=10, target=None,
                 stone_scoring_func=None):
        """
        successes
        """
        self.successes = list(successes)
        self.attempts = list(attempts)
        self.hit_prob = hit_prob

        self.length = length
        
        if stone_scoring_func is None:
            assert target is not None 
            stone_scoring_func = \
                lambda successes: successes[0] >= target[0] and \
                successes[1] >= target[1] and successes[2] <= target[2] 
        self.stone_scoring_func = stone_scoring_func

    def set_state(self, sr: int, successes: Tuple[int], attempts: Tuple[int]):
        return

    def record_success_on(self, index):
        successes = deepcopy(self.successes)
        successes[index] += 1
        
        attempts = deepcopy(self.attempts)
        attempts[index] += 1
        hit_prob = max(self.hit_prob-1, 0)

        return State(successes, attempts, hit_prob, length=self.length, stone_scoring_func=self.stone_scoring_func)

    def record_failure_on(self, index):
        successes = deepcopy(self.successes)
        successes[index] += 0
        
        attempts = deepcopy(self.attempts)
        attempts[index] += 1
        hit_prob = min(self.hit_prob+1, State.NUM_HIT_PROB_STATES-1)

        return State(successes, attempts, hit_prob, length=self.length, stone_scoring_func=self.stone_scoring_func)

    def get_state(self):
        return self.successes, self.attempts, self.hit_prob

    def reached_limit_index(self, index):
        return self.attempts[index] == self.length

    def is_terminal(self):
        attempts = self.attempts
        
        # Possible to short circuit before 10/10/10 attempts, but not implemented
        return all(attempt == self.length for attempt in attempts) # or \
            # (attempts[-1] == self.length and attempts[0] >= target[0] and attempts[1] >= target[1])

    def terminal_state_value(self):
        attempts = self.attempts
        successes = self.successes

        # 1 if meets target, 0 otherwise
        return int(sum(attempts) == 3*self.length and self.stone_scoring_func(successes)) 
            
    def __eq__(self, other):
        if isinstance(other, State):
            return (self.successes, self.attempts, self.hit_prob) == (other.successes, other.attempts, other.hit_prob)
        return False
    
    def __hash__(self):
        successes, attempts, hit_prob = self.get_state()
        return hash((*tuple(successes), *tuple(attempts), hit_prob))

    def __str__(self):
        successes, attempts, hit_prob = self.get_state()
        return f'{successes} {attempts} {hit_prob}'


def calculate(length=10, target=None, stone_scoring_func=None):
    assert target is not None or stone_scoring_func is not None 
    if target is not None:
        state = State(length=length, target=target)
    else:
        state = State(length=length, stone_scoring_func=stone_scoring_func)
    
    return calculate_(state)

def calculate_(state):
    if state.__hash__() in statehash:
        return statehash[state.__hash__()]
    if state.is_terminal():
        # make sure not to stop early even if not at 10 attempts. 
        # can leave like this if can calculate number of remaining combinations
        # if len(statehash) % 10000 == 0:
        #     print(len(statehash), sys.getsizeof(statehash), state.length)
        #     print(state, state in statehash)
        #     print(state.successes, state.attempts, state.hit_prob, state.length, state.terminal_state_value())
        # statehash[state] = (state.terminal_state_value(), -1)
        return (state.terminal_state_value(), -1)

    optimal = 0
    optimal_move = -1
    hit_prob = state.PROB_MAP[state.hit_prob] # maps {0, ..., 5} -> {0.25, ..., 0.75}
    for i in range(3):
        if state.reached_limit_index(i):
            continue
        s_hit = state.record_success_on(i)
        prob_if_hit, _ = calculate_(s_hit)
        s_fail = state.record_failure_on(i)
        prob_if_fail, _ = calculate_(s_fail)
        
        prob_reach_target = hit_prob*prob_if_hit + (1-hit_prob)*prob_if_fail
        if prob_reach_target >= optimal:  
            optimal = prob_reach_target
            optimal_move = i 

    if len(statehash) % 10000 == 0:
        print(state, len(statehash))
    statehash[state.__hash__()] = (optimal, optimal_move)
    return optimal, optimal_move


if __name__ == '__main__':
    # size_of_ulonglong = np.dtype(np.uint64).itemsize
    # print(f'Size of ulonglong on your machine: {size_of_ulonglong} bytes')
    # 8 bytes

    # s1 = State(successes=(0,0,0), attempts=(0,0,0), hit_prob=3)
    # s2 = State(successes=(0,0,0), attempts=(0,0,0), hit_prob=3)

    # statehash[s1] = (0,0)
    # print(s2 in statehash)
    # print(hash(s1), hash(s2))

    def stone_scoring_func_97either(successes: Tuple[int]):
        """
        9-7 either way
        """
        return max(successes[:2]) >= 9 and min(successes[:2]) >= 7 and successes[2] <= 4

    def stone_scoring_func_77(successes: Tuple[int]):
        """
        7-7
        """
        return successes[0] >= 7 and successes[1] >= 7 and successes[2] <= 4

    def stone_scoring_func_97or610(successes: Tuple[int]):
        """
        Either 9-7 or 6-10 to get +2 on the second engraving
        """
        return ((successes[0] >= 9 and successes[1] >= 7) or (successes[0] >= 6 and successes[1] >= 10)) \
            and successes[2] <= 4

    optimal, optimal_move = calculate(length=10, stone_scoring_func=stone_scoring_func_97or610)
    print(optimal, optimal_move)
    print(len(statehash))

    with open('statehash.pkl', 'wb') as f:
        pickle.dump(statehash, f)

    # Probabilities of achieving stone cut
    # 774: 5169511470844657481170536432757040091/107374182400000000000000000000000000000 (0.04814482732)
    # 974: 15193612562836429137779045907427203/21474836480000000000000000000000000000 (0.00070750771)
    # 974 either way: 127303313351678582209888888318703619/107374182400000000000000000000000000000 (0.00118560449)


