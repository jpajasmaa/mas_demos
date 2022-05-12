import argparse

from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade import quit_spade
from spade_bdi.bdi import BDIAgent
import time
import numpy as np
import agentspeak
from desdeo_tools.utilities import distance_to_reference_point, fast_non_dominated_sort_indices
import asyncio

from bdiAgent import bdiPreferenceAgent



def main():
    # crate agent
    #a = BDIAgent("temp@localhost", "k", "basic.asl")
    a = bdiPreferenceAgent("temp@localhost", "k", "bdi.asl")
    a.start()

    import time
    time.sleep(1)
    
    # give something to the beliefs
    #sols = np.array([[0.5,0.5], [0.9, 0.1],[1.1, 0.2], [0.1, 0.8], [1.0 ,1.0]])
    #sols = [[0.5,0.5], [0.9, 0.1],[1.1, 0.2], [0.1, 0.8], [1.0 ,1.0]]
    sols = ((0.5,0.5), (0.9, 0.1),(1.1, 0.2), (0.1, 0.8), (1.0 ,1.0))

    # make these beliefs change and add more..

    #a.bdi.set_belief("type", "obj1")
    a.bdi.set_belief("type", "obj2")
    a.bdi.set_belief("sols", tuple(sols))
    a.bdi.remove_belief("type")
    a.bdi.remove_belief("sols")

    # wait bit for reset
    time.sleep(5)

    a.bdi.set_belief("type", "obj1")
    a.bdi.set_belief("sols", tuple(sols))
    a.bdi.remove_belief("type")
    a.bdi.remove_belief("sols")

    time.sleep(5)


    rp = ((0.4,0.4))
    a.bdi.set_belief("type", "refpoint")
    #a.bdi.set_belief("sols", tuple(sols))
    a.bdi.set_belief("refpoint",tuple(rp), tuple(sols))
    #a.bdi.set_belief("sols", tuple(sols))

    #time.sleep(5)

    #a.bdi.set_belief("type", "nondom")
    #a.bdi.set_belief("sols", tuple(sols))
    #a.bdi.remove_belief("type")

    time.sleep(5) # why need to wait after ? agents computation should not take that long??

    #a.stop().result()


if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        quit_spade()
