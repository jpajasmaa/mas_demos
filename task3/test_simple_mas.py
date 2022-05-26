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


from SenderAgent import SenderAgent
from ReceiverAgent import ReceiverAgent, BdiReceiverAgent


"""
mas accounts:

main

a1
a2
a3
a4
a5

passes: a

Problems:

When something goes wrong inside other agents behaviour, subprocess etc
No debug info about to event. Makes it very hard find out what went wrong and why.


"""

## TODO:
# maybe need to use the .join() to combine behaviours?


#def fake_emo(sols, pref):
def fake_emo():
    time.sleep(3)
    print("fake emo")
    #for i in range(sols.shape[0]):
    #    sols[i] = perf
    #    i 
    return 0
 

def create_pref_agent(pref_point):
    arr = np.array([[0.5, 0.5], [0.9, 0.1], [1.1, 0.2], [0.1, 0.8], [1.0, 1.0]])
    pref_point = pref_point
    print("DM's pref point", pref_point)
    pp = PreferenceAgent("prefagent@{}localhost", "k")
    pp.set("sols", arr)
    if pref_point is not None:
        pp.set("preference_point", pref_point)

    return pp


def create_bdi_agent(idx):
    sols = ((0.5,0.5), (0.9, 0.1),(1.1, 0.2), (0.1, 0.8), (1.0 ,1.0))
    belief_types = ["obj1", "obj2"] # "refpoint" "nondom"
    a = bdiPreferenceAgent("bdiagent@localhost", "k", "bdi.asl")
    a.agent.bdi.set_belief("type", belief_types[idx])
    a.agent.bdi.set_belief("sols", tuple(sols))

    return a



class WebAgent(agent.Agent):
    class DummyBehav(behaviour.CyclicBehaviour):
        async def run(self):
            await asyncio.sleep(1)

        async def on_end(self):
            print("Ending behav.")


    class DummyPeriodBehav(behaviour.PeriodicBehaviour):
        async def run(self):
            print("i might work")
            await asyncio.sleep(1)

    class DummyTimeoutBehav(behaviour.TimeoutBehaviour):
        async def run(self):
            print("do i work")
            await asyncio.sleep(1)


    async def setup(self):
        #self.web.start(templates_path="examples")
        template1 = Template(sender="temp@localhost")
        template2 = Template(sender="a1@localhost")
        template3 = Template(sender="a2@localhost")

        print("WebAgent started")

        # Create some dummy behaviours
        dummybehav = self.DummyBehav()
        self.add_behaviour(dummybehav, template=template1)
        periodbehav = self.DummyPeriodBehav(period=12.7)
        self.add_behaviour(periodbehav, template=template2)
        timeoutbehav = self.DummyTimeoutBehav(start_at=datetime.now())
        self.add_behaviour(timeoutbehav, template=template3)

        #servebeh = self.ServeBehav()
        #template4 = Template()
        #template4.set_metadata("performative", "inform")
        #self.add_behaviour(servebeh, template4)
        behavs = [dummybehav, periodbehav, timeoutbehav]

        self.add_fake_contact("bdiagent@localhost", PresenceType.AVAILABLE)
        self.add_fake_contact("prefagent@localhost", PresenceType.AVAILABLE)
        # Create some fake contacts
        self.add_fake_contact("temp@localhost", PresenceType.AVAILABLE)
        self.add_fake_contact(
            "a1@localhost", PresenceType.AVAILABLE, show=PresenceShow.AWAY
            )
        self.add_fake_contact(
            "a2@localhost",
            PresenceType.AVAILABLE,
            show=PresenceShow.DO_NOT_DISTURB,
        )
        self.add_fake_contact("a3@localhost", PresenceType.UNAVAILABLE)
        self.add_fake_contact(
            "a4@localhost", PresenceType.AVAILABLE, show=PresenceShow.CHAT
        )

        await self.send_fake_mgs(behavs)
        print("here")


    async def send_fake_mgs(self, behavs):
        # Send and Receive some fake messages
        print("in fak")
        self.traces.reset()
        for i in range(5):
            number = random.randint(1, 4)
            from_ = JID.fromstr("a{}@localhost".format(number))
            msg = aioxmpp.Message(from_=from_, to=self.jid, type_=MessageType.CHAT)
            msg_table = [
                "Hello from {}! I prefer objective 1.",
                "Hello from {}! I prefer objective 2.",
                "Hello from {}! I want even solution.",
                "Hello from {}! I want more solutions.",
            #    "Hello from {}! I have preference point [0.7, 0.2]. Please give me the best result"
            ]
            rn_msg = random.randint(0,4)

            msg.body[None] = msg_table[rn_msg].format(
                from_.localpart
            )
            msg = Message.from_node(msg)
            msg.metadata = {"performative": "inform"}
            msg = msg.prepare()
            self._message_received(msg=msg)
            msg = Message(
                sender=str(self.jid), to=str(from_), body="Prefagent x will handle, dont worry."
            )
            msg.sent = True

            # could set bdi agent as rec agent. maybe it will work?
            if i == 0:
                rec_agent = BdiReceiverAgent("bdiagent@localhost", "k", "bdi.asl")
                await rec_agent.start()
            else:
                rec_agent = ReceiverAgent("prefagent@localhost", "k")
                await rec_agent.start()

            senderagent = SenderAgent("temp@localhost", "k")
            #senderagent = SenderAgent("prefagent@localhost", 1,"temp@localhost", "k")
            await senderagent.start()
            
            time.sleep(5)

            self.traces.append(msg, category=str(behavs[number]))

    def add_fake_contact(self, jid, presence, show=None):
        jid = JID.fromstr(jid)
        item = Item(jid=jid)
        item.approved = True
        self.presence.roster._update_entry(item)
        if show:
            stanza = Presence(from_=jid, type_=presence, show=show)
        else:
            stanza = Presence(from_=jid, type_=presence)
        self.presence.presenceclient.handle_presence(stanza)



"""
Whats even the point of the mas?
TODO:
simple mas plan
lets just give solutions
- create 

more complex plan
create agent
give it solutions
it gives it to agent it beliefs should handle it
that handles it

could also do simple mas adm
use interactive emo. 
couple agents with different preferences
handle conflict somehow
winner gets to give preference


WEB SPADE
one web agent
fake agents (DMs) give requests
web agent serves them creating PreferenceAgent for each request
Show requests and results etc

to demo the idea of using agents with spade for group dm.


"""
def main(server, password):
    #fake_emo()
    
    a = WebAgent("main@{}".format(server), password)
    future = a.start()
    a.web.start(hostname="127.0.0.1", port="10000")
    future.result()

    #time.sleep(50)
    #future.result()
    while a.is_alive():
        try:
            print("still alive")
            time.sleep(5)
        except KeyboardInterrupt:
            a.stop()
    #time.sleep(10)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='spade bdi master-server example')
    parser.add_argument('--server', type=str, default="localhost", help='XMPP server address.')
    parser.add_argument('--password', type=str, default="a", help='XMPP password for the agents.')
    args = parser.parse_args()

    try:
        main(args.server, args.password)
    except KeyboardInterrupt:
        print("Exiting...")

