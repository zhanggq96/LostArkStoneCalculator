# Lost Ark Stone Probability Calculator
Based on the algorithm described here: https://github.com/nwtnni/facet/tree/main

Python implementation. You can create a custom scoring function to determine what constitutes a success. For example, most calculators implement a mode in which you can find the probability/optimal strategy to cut a 9/7 stone, but the 9 and 7 lines have to be specified. This makes sense when going for certain builds (e.g. Adrenaline level 2, in which case Adrenaline must be the +7) but if for some reason you do not care which is the 9 and which is the 7, you can conveniently use a custom scoring function:
```
def stone_scoring_func_97either(successes: Tuple[int]):
    """
    9-7 either way 
    """
    return max(successes[:2]) >= 9 and min(successes[:2]) >= 7 and successes[2] <= 4

prob_success, optimal_move = calculate(length=10, stone_scoring_func=stone_scoring_func_97either)
```
The `successes` line is in the format of a tuple `(a,b,c)` where `a` and `b` are the number of successful facets on the two engravings and `c` is the number of successful facets on the malice.
