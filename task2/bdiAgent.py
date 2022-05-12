import argparse

from spade.behaviour import OneShotBehaviour, CyclicBehaviour, PeriodicBehaviour, TimeoutBehaviour
from spade import quit_spade
from spade_bdi.bdi import BDIAgent
import time
import numpy as np
import agentspeak
from desdeo_tools.utilities import distance_to_reference_point, fast_non_dominated_sort_indices
import asyncio
from datetime import datetime
from datetime import timedelta


# HOW to use/handle variables between having basic spade agents set and get methods
# bdi agents set beliefs, python self. variables and also agentspeak variables ?? 

# seems like BDIAgent does not actually implement all of spade agent things OR it is buggy OR im using it wrong.
# but using their end and start and params and attributes seems sometimes to work and sometimes not, even though
# sometimes i can read it is there sometimes it is maybe not?


class bdiPreferenceAgent(BDIAgent):
    async def setup(self):
        # why adding stuff here breaks all? no idea..
        #self.set_belief("solution", 3)
        self.stop = False
        self.add_behaviour(self.startBehav())
        self.add_behaviour(self.overrideBehav(start_at=datetime.now() + timedelta(seconds=10)))
        self.add_behaviour(self.timeoutBehav(start_at=datetime.now() + timedelta(seconds=15)))
        
        #self.set_belief('selected_sol', None)
        #self.set('selected_sol', None)
        #self.set_belief('ref_point', None)
        #self.set('ref_point', None)



    def add_custom_actions(self, actions):
        @actions.add_function(".selector", (int, tuple,))
        def _selector(i,x):
            print("in selector")
            x_arr = np.asarray(x)
            # get belief to select the solution from x.
            idx = np.argmin(x_arr[:,i])
            res = x[idx] 
            return res

        # i is for how many solutions to return from rank 0
        @actions.add_function(".non_dom", (int, tuple,))
        def _non_dom(i,x):
            print("in non dom")
            x_arr = np.asarray(x)
            # get belief to select the solution from x.
            res = self.select_sols(x_arr)  # just pick first for now.
            return tuple(res)

        @actions.add_function(".refpoint", (tuple, tuple,))
        def _refpoint(p,x):
            print("in refpoint")
            p_arr = np.asarray(p)
            x_arr = np.asarray(x)
            _, idx = distance_to_reference_point(x_arr, p_arr)
            selected_sol = x[idx]
            return selected_sol


        @actions.add(".result", 1)
        def _result(agent, term, intention):
            arg = agentspeak.grounded(term.args[0], intention.scope)
            print("result in plan",arg)
            yield

    async def select_sols(self, x_arr):
        await asyncio.sleep(2)
        non_dom = fast_non_dominated_sort_indices(x_arr)

        await asyncio.sleep(2)
        print("in sel sols",non_dom)
        res = x_arr[non_dom[0][0][0]]  
        return res


    class startBehav(OneShotBehaviour):
        async def on_start(self):
            print("starting behaviour")

        async def run(self):
            print("Giving solutions")
            self.agent.add_behaviour(self.agent.SelectSolutionBehav(period=5, start_at=datetime.now()))
            
            #self.agent.bdi.set_belief("sols", self.sols)

    class SelectSolutionBehav(PeriodicBehaviour):
        async def on_start(self):
            print("Starting result behaviour . . .")

        async def run(self):
            # put sols somehow to agent knowledge etc    
            sols = ((0.5,0.5), (0.9, 0.1),(1.1, 0.2), (0.1, 0.8), (1.0 ,1.0))
            belief_types = ["obj1", "obj2"] # "refpoint" "nondom"

            if self.agent.bdi.get_belief("refpoint") is not None:
                self.agent.bdi.remove_belief("type")
                self.agent.bdi.remove_belief("sols")

                # add refpoint belief
                self.agent.bdi.set_belief("type", "refpoint")
            else:
                #if self.agent.get("ref_point"):
                import random

                self.agent.bdi.set_belief("type", random.choice(belief_types))
                self.agent.bdi.set_belief("sols", tuple(sols))
                #self.agent.bdi.set_belief("type", "obj1")
                self.agent.bdi.remove_belief("type")
                self.agent.bdi.remove_belief("sols")

            if self.agent.stop:
                self._done = True
                #self.agent.stop().result()
                self.kill()

            if self.agent.bdi.get_belief("stop"):
                self.kill()

        async def on_end(self):
            # stop agent from behaviour
            await self.agent.stop()

    class overrideBehav(TimeoutBehaviour):
        async def run(self):
            self.agent.bdi.remove_belief("type")
            self.agent.bdi.remove_belief("sols")

            # they are removed above, but still exist below...
            #tt =  self.agent.bdi.get_belief("type")
            #ss =  self.agent.bdi.get_belief("sols")
            #print("ttt",tt)
            #print("sss",ss)
            sols = ((0.5,0.5), (0.9, 0.1),(1.1, 0.2), (0.1, 0.8), (1.0 ,1.0))
            rp = ((0.4, 0.4))
            
            self.agent.bdi.set_belief("type", "refpoint")
            self.agent.bdi.set_belief("refpoint",tuple(rp), tuple(sols))
            #self.agent.bdi.remove_belief("refpoint")

        #async def on_end(self):
            # stop agent from behaviour
            #await self.agent.stop()


    class timeoutBehav(TimeoutBehaviour):
        async def run(self):
            print("on timeoutBehav")
            self.agent.bdi.remove_belief("type")
            self.agent.bdi.remove_belief("sols")
            self.agent.remove_behaviour(self)
            self.agent.bdi.set_belief("stop", True)
            self.agent.bdi.set_belief("satisfied", True)
            #self.agent.pause_bdi()
            self.agent.stop = True
            self.kill()

        async def on_end(self):
            # stop agent from behaviour
            self.agent.pause_bdi()
            #await self.agent.stop()


if __name__=="__main__":

    a = bdiPreferenceAgent("temp@localhost", "k", "bdi.asl")
    a.start()

    #t = time.time()
    while a.bdi_enabled:
        try:
            print("BDI agent working")
            time.sleep(5)
            print("Current status :", a.bdi_enabled)

        except KeyboardInterrupt:
            print("Exiting...")
            quit_spade()
   # print(time.time()-t)
