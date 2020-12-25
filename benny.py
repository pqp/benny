#!/usr/bin/env python

import pymumble_py3 as pymumble
from pymumble_py3.callbacks import PYMUMBLE_CLBK_TEXTMESSAGERECEIVED as PCM
import json
import subprocess as sp
from os import path

# Update: exception, error handling
f = open("benny.json")
config = json.load(f)
global playing
playing = False

def audio_stream_process(data, frame_count, time_info, status):
    pass

def validate(filename):
    # A filename will have an extension, or it won't.
    # We'll check for both cases.
    #

    # TODO: Iterate through directories, not just the current directory

    file_types = [".wav", ".mp3", ".ogg"]

    if filename.find(".") != -1:
        if path.exists(filename):
            return filename
    else:
        for t in file_types:
            print(t)
            if path.exists(filename + t):
                return filename + t

def cmd_play(a):
    # Check that array is only one element
    # Check that element is a valid filename
    # Play it.

    filename = a.pop()
    filename = config.get("library") + filename
    filename = validate(filename)
    print(filename)

    command = ["ffmpeg", "-i", filename, "-acodec", "pcm_s16le", "-f", "s16le", "-ab", "192k", "-ac", "1", "-ar", "48000", "-"]
    sound = sp.Popen(command, stdout=sp.PIPE, stderr=sp.DEVNULL, bufsize=1024)

    playing = True
    # Change into callback?
    while playing:
        raw_music = sound.stdout.read(1024)
        if not raw_music:
            break
        mumble.sound_output.add_sound(raw_music)

    print(a)

def cmd_stop(a):
    # TODO: Print message
    pass

aliases = {
    'play': cmd_play,
    'p': cmd_play,
    'stop': cmd_stop,
    's': cmd_stop
}

def process_command(a):
    # There are two ways to input commands:
    # benny + <cmd> + <arg1> + <arg2>, benny stop...
    # or bp <arg1>, bs...

    cmd = a.pop()
    print("cmd: " + cmd)

    aliases[cmd](a)

def process_message(msg):
    actor = msg.actor
    channel_id = msg.channel_id
    message = msg.message

    a = message.split()
    a.reverse()
    call = a.pop()

    # If a user merely calls with 'benny', then
    # process the command and its arguments.
    if call == ("benny"):
        process_command(a)
    # but if a user uses an abbreviation, then
    # strip the beginning 'b' and see if the
    # rest is a command (the user might simply
    # be using a word that starts with 'b')
    elif call[0] == 'b':
        cmd = call.strip('b')
        a.append(cmd)
        process_command(a)
    else:
        return -1

mumble = pymumble.Mumble(config.get("server"), config.get("nick"), password=config.get("password"), port=int(config.get("port")))
mumble.callbacks.set_callback(PCM, process_message)
mumble.start()
mumble.is_ready()

while True:
    pass
