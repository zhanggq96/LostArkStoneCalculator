# Lost Ark Stone Probability Calculator
Based on the algorithm described here: https://github.com/nwtnni/facet/tree/main

Python implementation. You can create a custom scoring function to determine what constitutes a success. For example, most calculators implement a mode in which you can find the probability/optimal strategy to cut a 9/7 stone, but the 9 and 7 lines have to be specified. This makes sense when going for certain builds (e.g. Adrenaline level 2, in which case Adrenaline must be the +7). But if for some reason you do not care which is the 9 and which is the 7, there is no way to create such a setting.

In this calculator, it is possible to create a custom scoring function:
```
def stone_scoring_func_97either(successes: Tuple[int]):
    """
    9-7 either way 
    """
    return max(successes[:2]) >= 9 and min(successes[:2]) >= 7 and successes[2] <= 4

prob_success, optimal_move = calculate(length=10, stone_scoring_func=stone_scoring_func_97either)
```
Here's another example of a use case. Recall that a 5x3+2 build (with the 2 specified) can also be achieved with a 6/10 stone. Hence, we can be satisfied with a result of either 9/7 or 6/10. 
```
def stone_scoring_func_97or610(successes: Tuple[int]):
    """
    Either 9-7 or 6-10 to get +2 on the second engraving
    """
    return ((successes[0] >= 9 and successes[1] >= 7) or (successes[0] >= 6 and successes[1] >= 10)) \
        and successes[2] <= 4
```

The `successes` line is in the format of a tuple `(a,b,c)` where `a` and `b` are the number of successful facets on the two engravings and `c` is the number of successful facets on the malice.

```
Probabilities:
7/7: 5169511470844657481170536432757040091/107374182400000000000000000000000000000 (0.04814482732)
9/7: 15193612562836429137779045907427203/21474836480000000000000000000000000000 (0.00070750771)
9/7 either way: 127303313351678582209888888318703619/107374182400000000000000000000000000000 (0.00118560449)
9/7 or 6/10: 1319605689012779037584690617051839/1677721600000000000000000000000000000 (0.00078654628) # Not much higher than 9/7, but still better!
```