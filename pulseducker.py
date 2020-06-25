#!/bin/python3 


PHONES=['Playback Stream'] # Voice to duck over when sink is created. It wil duck over the Play_voices. This is useful for thinkgs that are only create sinks when activated, like audios on telegram.
PLAY_VOICES=['AudioStream'] # Name of the Playback to give preference and start ducking all others when it starts playing
DUCKABLE=['RTP Stream (PulseAudio RTP Stream on Vostro)', 'Spotify']#, 'AudioStream'] # Streams to lower when something from the list above plays
FACTOR=0.35 # Factor to lower other sink's volumes


#########################################################################
#  Matheus Fillipe -- 23, June of 2020                                  #
#   DUMB_DUCKER/PULSEDUCKER  (not good or caring with names)            #
#########################################################################
#  Description: This is a simple and hacky audio ducker for PulseAudio  #
# that allows you to define ducking rules for certain streams by putting#
# their names on the lists above.                                       #
#                                                                       #
#########################################################################
#  Depends on: pulsectl (pip install pulsectl)                          #
#                                                                       #
#########################################################################
        

import pulsectl
from pulsectl.lookup import pulse_obj_lookup
import os, sys, pulsectl, signal, functools as ft
from sys import argv
import time

signal.signal(signal.SIGINT, lambda sig,frm: sys.exit(0))
verboseMode=False
last_event=0
event=0
ducking=[]
playing=[]

def verbose(*args):
    global verboseMode
    if verboseMode: print(*args)

def callback(pulse, ev):
    global event 
    if ev.t in [pulsectl.PulseEventTypeEnum.new,pulsectl.PulseEventTypeEnum.remove, pulsectl.PulseEventTypeEnum.change]:
        event=ev
        verbose("---------------------")
        raise pulsectl.PulseLoopStop
    
def get_sink(pulse, ev):
    sinks=pulse.sink_input_list()
    sink=[s for s in sinks if s.index==ev.index]
    if len(sink)==0:
        verbose("Mismatched event looking for sink")
        verbose("Event is: ",ev.t)
        verbose("Sinks", [s.name for s in sinks])
        verbose("Sink: ",sink)
    return sink[-1] if len(sink) else False

def check_playing(pulse, sink):
    global playing
    if sink and sink.name in PLAY_VOICES+PHONES:
        verbose("Checking!")
        isPlaying=pulse.get_peak_sample(pulse.sink_info(sink.sink).monitor_source, 0.3, sink.index)>0            
        if isPlaying and not sink.name in playing:
            playing.append(sink.name)
        elif sink.name in playing and not sink.name in PHONES:
            playing.remove(sink.name)
        return isPlaying

def update(pulse):
    global playing
    sinks=pulse.sink_input_list()
    newplaying=[]
    for sink in sinks:
        if sink.name in playing:
            newplaying.append(sink.name)
    playing=newplaying


def duck(ev, pulse): 
    global last_event
    global ducked
    global playing
    global ducking

    #Update Ducking and Playing
    if ev.t==pulsectl.PulseEventTypeEnum.remove: #Who was removed?
        verbose("Removed Stream")
        update(pulse)
    elif ev.t==pulsectl.PulseEventTypeEnum.new: 
        sinks=pulse.sink_input_list()
        for sink in sinks:
            if sink.name in PHONES:
                playing.append(sink.name)
    else:
        sink=get_sink(pulse, ev)
        verbose("Sink is: ", sink)
        if not sink:
            update(pulse)
        else:
            isPlaying=check_playing(pulse, sink)
            verbose("isPlaying: ",isPlaying)
            verbose("Playing is: ",playing)
            verbose("Ducking is: ",ducking)

            if isPlaying is None:
                update(pulse)

    #Manage Ducking
    sinks=pulse.sink_input_list()
    isPhone=len([p for p in playing if p in PHONES])>0
    for sink in sinks:
        if not sink.name in PLAY_VOICES+PHONES+DUCKABLE:
            continue
        #Undudking
        if sink.name in ducking:
            if len(playing)==0: 
                pulse.volume_change_all_chans(sink, FACTOR) 
                ducking.remove(sink.name)
            elif not isPhone and sink.name in PLAY_VOICES: # Make sure to raise PLAY_VOICES again
                pulse.volume_change_all_chans(sink, FACTOR) 
                ducking.remove(sink.name)            
       #Ducking
        else: 
            if isPhone:
                if sink.name in PLAY_VOICES+DUCKABLE:
                    pulse.volume_change_all_chans(sink, -FACTOR) 
                    ducking.append(sink.name)
            elif len(playing)>0:
                if sink.name in DUCKABLE: 
                    pulse.volume_change_all_chans(sink, -FACTOR) 
                    ducking.append(sink.name)



def pulse_loop():
    global event
    while True:
        try:
            with pulsectl.Pulse('ducker') as pulse: 
                pulse.event_mask_set("sink_input") 
                pulse.event_callback_set(ft.partial(callback, pulse))
                pulse.event_listen() 
                while True:
                    pulse.event_listen(timeout=1) 
                    duck(event, pulse)
        except pulsectl.pulsectl.PulseError:
            verbose("Failed to connect to PulseAudio: Trying again in 2 seconds")
            time.sleep(2)


if __name__=="__main__":
    if len(argv)>1:
        arg=argv[1]
        #Dumb opt parser
        
        if "-v" in argv: verboseMode=True
        if arg.startswith("-h") or arg.startswith("--h"):
            print("-h for this help\n-l for listing devices and events\n-v for verbose")
            sys.exit()
        elif arg.startswith("-l") or arg.startswith("--l"):
            print("Printing all sink_input events. Take a note of the currently playing streams names to configure on this python file\n\n")
            with pulsectl.Pulse('print') as pulse: 
                for sink in pulse.sink_input_list():
                    print(sink.name)
                pulse.event_mask_set("sink_input") 
                pulse.event_callback_set(ft.partial(print, pulse))
                pulse.event_listen() 
            sys.exit()
        elif arg!="-v":
            print(f"Unrecognized option '{arg}', use -h for help")

    print("Audio Ducker Started.")
    pulse_loop()
