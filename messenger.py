#!/usr/bin/env python
import fbchat
import textwrap, re
import os, sys
import threading
from getpass import getpass

# rows, columns = os.popen('stty size', 'r').read().split()

# http://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux
color_self = '\033[1;34m '  # ligh blue
color_friend = '\033[0m '  # normal
color_normal = '\033[0m '  # don't change


def align(string, colomns, right=True):
    if right:
        output = color_self
    else:
        output = color_friend
    list_string = textwrap.wrap(string, round(colomns / 2))
    for i in list_string:
        if right:
            output += i.rjust(colomns - 2)
        else:
            output += i
        output += "\n"
    return output + color_normal


def print_color(message, color):
    pass


class Listing(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client

    def run(self):
        self.client.listen()

class DaemonChat(threading.Thread):
    class Listing(threading.Thread):
        def __init__(self, client):
            threading.Thread.__init__(self, daemon=True)
            self.client = client

        def run(self):
            self.client.listen()


class Client(fbchat.Client):
    def __init__(self, email=None, password=None, do_login=True, rows=70, columns=70, start_daemon=True):
        fbchat.Client.__init__(self, email, password, do_login=do_login, debug=False)
        self.daemon = Listing(self)
        if do_login:
            self.saveSession(".fb.txt")
        self.rows = rows
        self.columns = columns
        self.chat_id = 0

    def getName(self, id):
        return self.getThreadInfo(id)['name']

    def print_messages(self, friend, begin=0, end=None, print_url_photo=False):
        messages = self.getThreadInfo(friend.uid, begin, end)
        messages.reverse()
        for message in messages:
            id = re.findall('\d*', message.author_email)[0]
            if id != str(friend.uid):  # own message
                if message.has_attachment:
                    if print_url_photo:
                        output = "URL"
                    else:
                        output = "<PHOTO>"
                else:
                    output = message.body
                print(align(output, self.columns, True))

            else:  # friend's message
                if message.has_attachment:
                    if print_url_photo:
                        # TODO
                        output = "URL"
                    else:
                        output = "<PHOTO>"
                else:
                    output = message.body
                print(align(output, self.columns, False))

    def on_message(self, mid, author_id, author_name, message, metadata):
        self.markAsDelivered(author_id, mid)  # mark delivered
        if self.chat_id != 0:
            if author_id == str(self.chat_id):
                print(align(message, self.columns, False))
            elif author_id == str(self.uid):
                print(align(message, self.columns, True))
        else:
            print("\033[5m Message from %s \033[0m"  % author_id)

    def start_chat_with_person(self, friend):
        self.chat_id = friend.uid
        self.print_messages(friend, self.columns)
        li = Listing(self)
        li.start()
        exit = False
        while(exit == False):
            user_input = input()
            print( "\033[A                             \033[A")
            if user_input == 'exit':
                print("exit")
                self.chat_id = 0
                li.join(1)
                self.saveSession('.fb.txt')
                exit = True
            elif user_input == 'like':
                self.send(friend.uid, None, like='small')
            else:
                self.send(friend.uid, user_input)

    def make_session(self):
        pass


if __name__ == '__main__':
    argv = sys.argv[1:]
    client = Client(None, None, do_login=False, start_daemon=False)
    if(argv[0] == 'login'):
        paswd = getpass()
        client = Client(argv[1], paswd)
        print("Login Succesful")
    elif argv[0] == 'chat':
        client.loadSession(".fb.txt")
        friend = client.getUsers(argv[1])[0]
        client.start_chat_with_person(friend)
    elif argv[0] == 'send':
        client.loadSession('.fb.txt')
        friend = client.getUsers(argv[1])[0]
        if argv[2] == 'like':
            client.send(friend.uid, None, like='small')
        else:
            client.send(friend.uid, argv[2])
        print("Send Succesful")
    elif argv[0] == 'listen':
        client.loadSession(".fb.txt")
        print("\n Listening ... \n")
        client.listen()
    else:
        print("error")