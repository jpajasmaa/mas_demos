from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour, PeriodicBehaviour
import asyncio
import numpy as np
import time

from desdeo_tools.utilities import distance_to_reference_point

from PreferenceAgent import PreferenceAgent


if __name__ == "__main__":
    # represent the solutions
    # 0.5, 0.5 balanced
    # 0.9 0.1 prefer 2nd obj
    arr = np.array([[0.5,0.5], [0.9, 0.1],[1.1, 0.2], [0.1, 0.8], [1.0 ,1.0]])
    print("sols", arr)
    pref_point = np.array([0.7, 0.0])
    print("DM's pref point", pref_point)

    pref_agent = PreferenceAgent("temp@localhost", "k")
    pref_agent.set("sols", arr)
    pref_agent.set("preference_point", pref_point)    


    future = pref_agent.start()
    future.result()  # Wait until the start method is finished

    # print("Finished")
    #result = pref_agent.get('selected_sol')
    #print(result)
    # wait until the behaviour is finished to quit spade.
    while pref_agent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            pref_agent.stop()
            break
    print("Agent finished")
    quit_spade()
