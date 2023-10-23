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
    
    def __init__(self, successes=(0,0,0), attempts=(0,0,0), hit_prob=NUM_HIT_PROB_STATES-1, length=10, target=(7,7,4),
                 cut_score_func=None):
        """
        sr: success rate
        """
        self.successes = list(successes)
        self.attempts = list(attempts)
        self.hit_prob = hit_prob

        self.length = length
        self.target = target
            

    def set_state(self, sr: int, successes: Tuple[int], attempts: Tuple[int]):
        return

    def record_success_on(self, index):
        successes = deepcopy(self.successes)
        successes[index] += 1
        
        attempts = deepcopy(self.attempts)
        attempts[index] += 1
        hit_prob = max(self.hit_prob-1, 0)

        return State(successes, attempts, hit_prob, length=self.length, target=self.target)

    def record_failure_on(self, index):
        successes = deepcopy(self.successes)
        successes[index] += 0
        
        attempts = deepcopy(self.attempts)
        attempts[index] += 1
        hit_prob = min(self.hit_prob+1, State.NUM_HIT_PROB_STATES-1)

        return State(successes, attempts, hit_prob, length=self.length, target=self.target)

    def get_state(self):
        return self.successes, self.attempts, self.hit_prob

    def reached_limit_index(self, index):
        return self.attempts[index] == self.length

    def is_terminal(self):
        attempts = self.attempts
        target = self.target
        
        # Possible to short circuit before 10/10/10 attempts, but not implemented
        return all(attempt == self.length for attempt in attempts) # or \
            # (attempts[-1] == self.length and attempts[0] >= target[0] and attempts[1] >= target[1])

    def terminal_state_value(self):
        attempts = self.attempts
        successes = self.successes
        target = self.target

        # 1 if meets target, 0 otherwise
        return int(sum(attempts) == 3*self.length and \
            successes[0] >= target[0] and successes[1] >= target[1] and successes[2] <= target[2]) 
            
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


def calculate(length=10, target=(9,7,4), cut_score_func=None):
    state = State(length=length, target=target)
    return calculate_(state)

def calculate_(state):
    if state in statehash:
        return statehash[state]
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
    statehash[state] = (optimal, optimal_move)
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

    # 9-7 either way
    def cut_score_func(attempts):
        return int(max(attempts[:2]) >= 9 and min(attempts[:2]) >= 7 and attempts[2] <= 4)

    optimal, optimal_move = calculate()
    print(optimal, optimal_move)
    print(len(statehash))

    # Denominator: 107374182400000000000000000000000000000

    with open('statehash.pkl', 'wb') as f:
        pickle.dump(statehash, f)

    # 774: 5169511470844657481170536432757040091/107374182400000000000000000000000000000
    # 974: 15193612562836429137779045907427203/21474836480000000000000000000000000000


