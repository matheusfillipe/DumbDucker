# What is this

## Brief description

This is just a hacky and dumb audio ducker for linuxe's pulseaudio that is far from being optmized and
stable enough. Is more like a personal experiment for my own purposes. 

## What the heck is an audio Ducker?

It will lower the volume of other audio streams/sinks/playbacks while you want
to give priority on what you want to hear. You can configure this by setting
some variables on the code. 

## Usage

Use -h for help and take a look on the source code. Is very simple and uses
pulsectl python library. This code is at "just worked on my computer" stage but
I would interested in any contribution.

## Why I did this?

Because the default pulseaudio ducking module that you could use is first not
flexible enough and hard to setup and other problems I had with it. This one
will just match streams names and change volumes in real time. 
