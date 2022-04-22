from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour, PeriodicBehaviour
import asyncio
import numpy as np
import time

from desdeo_tools.utilities import distance_to_reference_point, fast_non_dominated_sort_indices


"""
select_solutions and select_solutions2. Which way to use, async sub tasks where agent can get and set
or call non async functions and return the values. Then agent sets them.

"""


class PreferenceAgent(Agent):
    async def setup(self):
        print(f'{self.jid} created.')
        self.report_behav = ReportBehav()
        self.add_behaviour(self.report_behav)
        self.sol_behav = SelectSolutionBehav()
        self.add_behaviour(self.sol_behav)
        self.set('selected_sol', None)
        #self.set('preference_point', None) # overrides the set from main



class SelectSolutionBehav(OneShotBehaviour):
    async def on_start(self):
        print("Starting result behaviour . . .")

    async def run(self):
        sols = self.get("sols")
        pref_point = self.get("preference_point")

        # wait agent to select the solution
        time.sleep(5) # lets pretend this takes longer
        await self.select_solutions(sols, pref_point)
        #sol = select_solutions2(sols, pref_point)
        #self.set('selected_sol', sol)

        # get from the selected sol
        sol = self.get('selected_sol')
        print("AGENT selected solution :", sol)


    # asynchronosity problems with these
    # ok so the idea works, just need to handle the asynchronosity
    async def select_solutions(self, sols, pref_point):
        # here do the formalisation how to pick solution
        selected_sol = None
        if pref_point is None:
            # fast 
            non_dom = fast_non_dominated_sort_indices(sols)
            print(non_dom)
            selected_sol = sols[non_dom[0][0][0]] # just pick first for now. 
            # use BDI here to pick, or plotting to let DM decide
        else:
            _, idx = distance_to_reference_point(sols, pref_point)
            selected_sol = sols[idx]

        # need to set for the agents selected_sol spot.
        self.set('selected_sol', selected_sol)


    async def on_end(self):
        print("Solution selection behaviour finished with exit code {}.".format(self.exit_code))
        #self.kill()
        await self.agent.stop()


class ReportBehav(CyclicBehaviour):
    async def on_start(self):
        print("Starting reporting behaviour . . .")

    async def run(self):
        if self.get('selected_sol') is not None:
            print(f"reporter: DM's selected solution is {self.get('selected_sol')}")
            time.sleep(2)
            self.kill()
        else:
            print(f"reporter waiting for solution selection . . .")
        time.sleep(5)



def select_solutions2(sols, pref_point):
    # here do the formalisation how to pick solution
    _, idx = distance_to_reference_point(sols, pref_point)
    selected_sol = sols[idx]
    # need to set for the agents selected_sol spot.
    return selected_sol

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
