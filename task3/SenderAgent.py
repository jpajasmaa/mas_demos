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







class SenderAgent(agent.Agent):
    class InformBehav(OneShotBehaviour):
        async def run(self):
            print("InformBehav running")
            #msg = Message(to="prefagent@localhost")  # Instantiate the message
            msg = Message(to="bdiagent@localhost")  # Instantiate the message
            #msg = Message(to=self.agent.recv_jid)  # Instantiate the message
            msg.set_metadata(
                "performative", "inform"
            )  # Set the "inform" FIPA performative
            msg.body = "Objective number to prefer is 1 from agent {}".format(
                self.agent.jid
                #self.agent.obj_prefer
            )  # Set the message content

            print("before msg sent")
            await self.send(msg)
            print("Message sent!")
            # create pref agent here?
            # stop agent from behaviour
            await self.agent.stop()

        #async def on_start(self):

    async def setup(self):
        print("SenderAgent started")
        #self.agent.obj_prefer = 1 # equal 0, -1 for not set, 1 for obj1 etc.
        b = self.InformBehav()
        self.add_behaviour(b)

    #def __init__(self, recv_jid, obj_prefer, *args, **kwargs):
    #    self.recv_jid = recv_jid
    #    self.obj_prefer = obj_prefer # equal 0, -1 for not set, 1 for obj1 etc.
    #    super().__init__(*args, **kwargs)


