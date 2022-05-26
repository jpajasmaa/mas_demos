import argparse
import time
import numpy as np
import datetime
import random
import time

import os
os.environ['PYTHONASYNCIODEBUG'] = '1'
import asyncio

import aioxmpp
import click
from aioxmpp import PresenceType, Presence, JID, PresenceShow, MessageType
from aioxmpp.roster.xso import Item

from spade import agent, behaviour
from spade.behaviour import State
from spade.message import Message
from spade.template import Template
from spade import agent
from spade_bdi.bdi import BDIAgent
from spade.template import Template
from spade.behaviour import PeriodicBehaviour, OneShotBehaviour
from spade.behaviour import TimeoutBehaviour
from datetime import datetime
from datetime import timedelta


from PreferenceAgent import PreferenceAgent 
from bdiAgent import bdiPreferenceAgent


class BdiReceiverAgent(BDIAgent):
    class RecvBehav2(OneShotBehaviour):
        async def run(self):
            print("bdiRecvBehav running")

            msg = await self.receive(timeout=50)  # wait for a message for 10 seconds
            if msg:
                print("Message received with content: {}".format(msg.body))
                sols = ((0.5,0.5), (0.9, 0.1),(1.1, 0.2), (0.1, 0.8), (1.0 ,1.0))
                belief_types = ["obj1", "obj2"] # "refpoint" "nondom"
                a = bdiPreferenceAgent("bdiagent@localhost", "k", "bdi.asl")
                a.bdi.set_belief("type", belief_types[1])
                a.bdi.set_belief("sols", tuple(sols))

                await a.start()

            # stop agent from behaviour
            await self.agent.stop()


    async def setup(self):
        print("BdiReceiverAgent started")
        b = self.RecvBehav2()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)



class ReceiverAgent(agent.Agent):
    class RecvBehav(OneShotBehaviour):
        async def run(self):
            print("RecvBehav running")

            msg = await self.receive(timeout=50)  # wait for a message for 10 seconds
            if msg:
                print("Message received with content: {}".format(msg.body))
                # start serve behaviour
                arr = np.array([[0.5, 0.5], [0.9, 0.1], [1.1, 0.2], [0.1, 0.8], [1.0, 1.0]])
                pref_point = np.array([0.7, 0.0])
                pref_point = pref_point
                print("DM's pref point", pref_point)
                pp = PreferenceAgent("prefagent@localhost", "k")
                pp.set("sols", arr)
                if pref_point is not None:
                    pp.set("preference_point", pref_point)

                await pp.start()

            # stop agent from behaviour
            await self.agent.stop()

    class ServeBehav(OneShotBehaviour):
        async def run(self):
            print("ServeBehav running")
            #print(self.super())
            await self.agent.b.join()

            arr = np.array([[0.5, 0.5], [0.9, 0.1], [1.1, 0.2], [0.1, 0.8], [1.0, 1.0]])
            pref_point = np.array([0.7, 0.0])
            pref_point = pref_point
            print("DM's pref point", pref_point)
            pp = PreferenceAgent("prefagent@localhost", "k")
            pp.set("sols", arr)
            if pref_point is not None:
                pp.set("preference_point", pref_point)

            await pp.start()

    async def setup(self):
        print("ReceiverAgent started")
        b = self.RecvBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)
        #c = self.agent.ServeBehav()
        #self.add_behaviour(c)
        #self.c.join()

