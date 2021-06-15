#!/usr/bin/env python

import pymumble_py3 as pymumble
import json
import audioop
import subprocess as sp
import os
import time
from os import path

# Update: exception, error handling
f = open("benny.json")
config = json.load(f)
idle_min = float(config.get("idle_min"))
user_idle_data = {}
playing = False
running = True
volume = 0.4

def validate(filename):
    # A filename will have an extension, or it won't.
    # We'll check for both cases.

    # TODO: Iterate through directories, not just the current directory

    file_types = config.get("library").get("allowed_file_types")

    if filename.find(".") != -1:
        if path.exists(filename):
            return filename
        else:
            channel_message("Cannot locate " + filename + ".")
    else:
        for t in file_types:
            print(t)
            if path.exists(filename + t):
                return filename + t

        channel_message("Cannot locate " + filename + " under any of the supported file types.")
        return -1

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
    if filename == -1:
        return

    print(filename)

    command = ["ffmpeg", "-i", filename, "-acodec", "pcm_s16le", "-f", "s16le", "-ab", "192k", "-ac", "1", "-ar", "48000", "-"]
    sound = sp.Popen(command, stdout=sp.PIPE, stderr=sp.DEVNULL, bufsize=1024)

    if type(sound) is None:
        channel_message("Couldn't retrieve " + filename + " from sound library!")
        return -1

    channel_message("Playing.")

    playing = True
    # Change into callback?
    while playing:
        chunk = sound.stdout.read(1024)
        if not chunk:
            break
        mumble.sound_output.add_sound(audioop.mul(chunk, 2, volume))

        while mumble.sound_output.get_buffer_size() > 0.2:
            time.sleep(0.01)

def cmd_stop(msg, a):
    global playing

    channel_message("Stopping.")

    playing = False
    mumble.sound_output.clear_buffer()

# Take our directory listing and break it into
# chunks of 50 lines.
# Return a list of those chunks
def split_list(l):
    strings = []

    coll = []
    count = 0
    for elem in l:
        coll.append(elem)

        count += 1

        if count >= 50:
            strings.append(coll)
            coll = []
            count = 0

    return strings

# Print a list of the files in the sound library.
def cmd_list(msg, a):
    actor = mumble.users.get(msg.actor)

    library_path = config.get("library").get("path")

    l = []

    for root, dirs, files, in os.walk(library_path, topdown=True):
        for name in sorted(files):
            l.append(os.path.join(name))

        # NOTE: Not sure that we need to list directory names
        #for name in dirs:
        #    list_join(l, os.path.join(root, name))

    messages = split_list(l)
    print(messages)

    for elem in messages:
        chunk = []
        for string in elem:
            string = "<p>" + string + "</p>"
            chunk.append(string)

        s = "\n"
        for st in chunk:
            s += st

        actor.send_text_message(s)

def cmd_volume(msg, a):
    global volume

    if len(a) < 1:
        channel_message("Volume is set to " + str(volume * 100) + ".")
        return

    volume = float(a.pop(0))

    # clamp volume
    volume = max(0, min(volume, 100))
    volume = volume / 100

    channel_message("Volume is set to " + str(volume * 100) + ".")

def probe_users():
    global user_idle_data

    users = mumble.users
    current_channel = users.myself['channel_id']
    channel = mumble.channels.find_by_name(config.get("away_channel"))
    idle_ignore_names = config.get("idle_ignore_names")
    current_time = time.time()

    idle_data_tmp = user_idle_data.copy()

    # prune absent users from user_idle_data
    bad_keys = []
    for key in idle_data_tmp.keys():
        if key not in users.keys():
            bad_keys.append(key)

    for key in bad_keys:
        del idle_data_tmp[key]

    for i in users:
        user = users[i]

        # don't move the bot itself
        if user == users.myself:
            continue

        # don't move anyone not in the bot's current channel
        if current_channel != user['channel_id']:
            if i in idle_data_tmp:
                del idle_data_tmp[i]
            continue

        # don't move a user who is in the ignore list
        if user['name'] in idle_ignore_names:
            continue

        # if we have a new user, add them to our timer dict
        if i not in idle_data_tmp:
            idle_data_tmp[i] = current_time
            continue

        # check to see if the time elapsed since this user last spoke is past idle_min
        if current_time - idle_data_tmp[i] >= idle_min * 60:
            if i in idle_data_tmp:
                del idle_data_tmp[i]

            channel.move_in(user['session'])

    user_idle_data = idle_data_tmp.copy()

aliases = {
    'bp': cmd_play,
    'bs': cmd_stop,
    'bl': cmd_list,
    'bv': cmd_volume
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

def connect_check():
    print("PYMUMBLE_CLBK_CONNECTED: pass")

def disconnect_check():
    global running

    print("PYMUMBLE_CLBK_DISCONNECTED: pass")
    print("Client has disconnected. Exiting...")
    running = False

def voice_check(user, sound):
    # a user has spoken, so reset their idle timer
    user_idle_data[user['session']] = sound.time

mumble = pymumble.Mumble(config.get("server"), config.get("nick"), password=config.get("password"), certfile=config.get("certfile"), port=int(config.get("port")), reconnect=True)
mumble.callbacks.set_callback(pymumble.constants.PYMUMBLE_CLBK_TEXTMESSAGERECEIVED, process_message)
mumble.callbacks.set_callback(pymumble.constants.PYMUMBLE_CLBK_CONNECTED, connect_check)
mumble.callbacks.set_callback(pymumble.constants.PYMUMBLE_CLBK_DISCONNECTED, disconnect_check)
mumble.callbacks.set_callback(pymumble.constants.PYMUMBLE_CLBK_SOUNDRECEIVED, voice_check)
mumble.set_receive_sound(True)
mumble.start()
mumble.is_ready()

channel_name = config.get("channel")
if channel_name:
    channel = mumble.channels.find_by_name(channel_name)
    channel.move_in()

while running:
    #probe_users()
    time.sleep(1)
