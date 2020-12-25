#!/usr/bin/env python

import pymumble_py3 as pymumble
from pymumble_py3.callbacks import PYMUMBLE_CLBK_TEXTMESSAGERECEIVED as PCM
import json
import subprocess as sp
import os
from os import path

# Update: exception, error handling
f = open("benny.json")
config = json.load(f)
playing = False
volume = 1.0

def validate(filename):
    # A filename will have an extension, or it won't.
    # We'll check for both cases.

    # TODO: Iterate through directories, not just the current directory

    file_types = config.get("library").get("allowed_file_types")

    if filename.find(".") != -1:
        if path.exists(filename):
            return filename
    else:
        for t in file_types:
            print(t)
            if path.exists(filename + t):
                return filename + t

def actor_message(actor, message):
    actor.send_text_message(message)

# Send a message into the active channel.
def channel_message(message):
    mumble.my_channel().send_text_message(message)

# Play a sound file.
def cmd_play(msg, a):
    # Check that array is only one element
    # Check that element is a valid filename
    # Play it.

    global playing
    global volume

    if len(a) <= 0:
        print("empty cmd")
        return -1

    # If we're already sending audio, stop, then clear the buffer
    if playing:
        playing = False
        mumble.sound_output.clear_buffer()

    filename = a.pop(0)
    filename = config.get("library").get("path") + filename
    filename = validate(filename)
    print(filename)

    command = ["ffmpeg", "-i", filename, "-filter:a", "volume=" + str(volume), "-acodec", "pcm_s16le", "-f", "s16le", "-ab", "192k", "-ac", "1", "-ar", "48000", "-"]
    sound = sp.Popen(command, stdout=sp.PIPE, stderr=sp.DEVNULL, bufsize=1024)

    channel_message("Playing.")

    playing = True
    # Change into callback?
    while playing:
        raw_music = sound.stdout.read(1024)
        if not raw_music:
            break
        mumble.sound_output.add_sound(raw_music)

def cmd_stop(msg, a):
    global playing

    channel_message("Stopping.")

    playing = False
    mumble.sound_output.clear_buffer()


# List pushing with limit testing
def list_join(l, elem):
    # FIXME: list max magic number
    if len(l) >= 50:
        return

    l.append(elem)

# Print a list of the files in the sound library.
def cmd_list(msg, a):
    actor = mumble.users.get(msg.actor)

    library_path = config.get("library").get("path")

    l = []

    for root, dirs, files, in os.walk(library_path, topdown=True):
        for name in files:
            list_join(l, os.path.join(root, name))

        # NOTE: Not sure that we need to list directory names
        #for name in dirs:
        #    list_join(l, os.path.join(root, name))

    s = "\n"
    for name in l:
        s += "<p>" + name + "</p>"

    actor.send_text_message(s)
    print(l)


aliases = {
    'bp': cmd_play,
    'bs': cmd_stop,
    'bl': cmd_list,
}

def process_command(msg, a):
    # There are two ways to input commands:
    # benny + <cmd> + <arg1> + <arg2>, benny stop...
    # or bp <arg1>, bs...

    cmd = a.pop(0)
    print("cmd: " + cmd)

    found = False
    for alias in aliases:
       if cmd == alias:
           found = True
           aliases[cmd](msg, a)

    if not found:
        print("Tried to find command " + cmd + " but couldn't find it")

    return

# TODO: add optional silent flag
def process_message(msg):
    actor = msg.actor
    channel_id = msg.channel_id
    message = msg.message

    a = message.split()
    process_command(msg, a)

mumble = pymumble.Mumble(config.get("server"), config.get("nick"), password=config.get("password"), port=int(config.get("port")))
mumble.callbacks.set_callback(PCM, process_message)
mumble.start()
mumble.is_ready()

while True:
    pass
