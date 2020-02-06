import sys
import time
import random
import multiprocessing as mp
import numpy as np

# Define the required load function
def myfun(j):
    k = []

    for i in range(j):
        k.append(sum([sum(range(x)) for x in range(1000)]))

    return(k)

if __name__ == '__main__':
   
    start = time.time()
    with mp.Pool(processes=16) as p:
        res = p.map(myfun, [100]*32)
    print("Total time it took for parallel {}. Res size {}".format(time.time() - start, np.array(res).shape))

    # Applying the same function using python map
    start = time.time()
    res = list(map(myfun, [100]*32))
    print("Total time it took for sequential {}. Res size {}".format(time.time() - start, np.array(res).shape))