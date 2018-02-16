#!/usr/bin/env python3

import socket
import sys
import string
import time
import redis

rdb = redis.StrictRedis(host = "localhost", port = 6379, db = 1)

irc_port = 6667
irc_server = "chat.freenode.net"

nickname = "brobit"
channel = "#robittest"

s = socket.socket()
s.connect((irc_server, irc_port))

def irc_send(datas):
  datas = datas + "\r\n"
  print("> " + str.rstrip(datas))
  s.send(bytes(datas, "UTF-8"))

irc_send("NICK " + nickname)
irc_send("USER " + nickname + " host server :" + nickname)
irc_send("JOIN " + channel)

buf = ""

while 1:
  time.sleep(0.1)
  buf = buf + s.recv(1024).decode("UTF-8")
  lines = str.split(buf, "\n")
  buf = lines.pop()
  for line in lines:
    line = str.rstrip(line)
    print("< " + line)
    word = str.split(line)
    if (word[0] == "PING"):
      irc_send("PONG " + word[1])
    if (word[1] == "PRIVMSG"):
      message = str(" ".join(word[3:])[1:])
      if " is " in message:
        key, value = message.split(" is ")
        existing_values = rdb.lrange(key, 0, -1)
        if (value not in existing_values):
          rdb.rpush(key, value)
      elif message.endswith('?'):
        key = message[:-1]
        values = rdb.lrange(key, 0, -1)
        reply = key + " is " + (b" or ".join(values)).decode("UTF-8")
        irc_send("PRIVMSG " + channel + " :" + reply)
      elif message == nickname + ": stats":
        irc_send("PRIVMSG " + channel + " :" + "total factoids: " + str(rdb.dbsize()))
