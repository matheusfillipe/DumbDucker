# What is this

## Brief description

This is just a hacky and dumb audio ducker for linuxe's pulseaudio that is far from being optmized and
stable enough. Is more like a personal experiment for my own purposes. 

## What the heck is an Audio Ducker?

It will lower the volume of other audio streams/sinks/playbacks while you want
to give priority on something else what you want to hear, only when this prefered stream is playing.
You can configure this by setting some strings inside the lists on the begining
of this code. 

## Usage

Use -h for help and take a look on the source code. Is very simple and uses
pulsectl python library. This code is at "just worked on my computer" stage. 

Use -l to list your currently stream names. The name will be either the
application name if it exists or the pulseaudio stream name. Use -l to confirm
and configure.

Basically the PHONES list is going to duck over the VOICES list. Whenever
a phone stream is created all the others are ducked including Voices. This an
attempt to create a 3 level ducking. 

I would interested in any contribution.

## Why I did this?

Because the default pulseaudio ducking module that you could use is first not
flexible enough and hard to setup and other problems I had with it. This one
will just match streams names and change volumes in real time. 

## What does this still lack (But I am too lazy to do)

1. The ducking effect can produce so glitching sound because the  sudden and
   instant volume change. Gradual and linear volume change would be cool.

2. Better naming conventions and better control for the streams.

3. Better way for writing the ducking rules in a separate file. 
