from __future__ import annotations
import curses
import os
import sys
from curses import wrapper
import json
import time
from UI_Classes import *
from helper import *
import socket

#REMEMBER THAT SCREEN COORDS ARE PASSED AS y,x
#### XXX XXX XXX USE decode to remove b"<-this"

#TODO TODO TODO TODO TODO TODO

# TODO-> make a dirbuster like tool (enumerate directories)
# TODO-> Random Hosts

MENU_ITEMS={"Scan": ["Configure ports","Begin Scan","Exit",],
        "Hosts": ["Add Host to queue (By IP address)","Edit Host","Remove from list"],
        "Tools": ["Enumerate HTTPs dirs","Ping ","Get Hostname from IP","Traceroute"],
        "Debug": ["test x"] }
# TODO change subLIST to a dict with callback func name

def main(stdscr):
    #Initialisation 
    PS=PyScan()

    stdscr.nodelay(False) 
    inkey = 0
    stdscr.clear()
    stdscr.immedok(True)
    stdscr.leaveok(True)
    while inkey != ord("Q"):
    # Main loop begins here
        PS.update_scr(stdscr)
        inkey=PS.handle_inkey(stdscr)


class PyScan:
    """This class is meant to serve as a container for the general execution of the program.
        it takes care of handling UI, saving to DB and Etc."""
    def __init__(self):
        # Curses Init. ============
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2,curses.COLOR_BLACK, curses.COLOR_BLUE) #Menu Selected
        # List/Dict Init. ------------
        self.ip_to_scan=[]
        self.ports_to_scan=[]
        # var below is a seq of seq with all ports states for that host
        # i.e. it contains the scan results
        self.hosts_state={h:False for h in self.ip_to_scan}
        # -------- Instantiate UI elements ----------
        self.status_bar=StatusBar()
        self.menu_bar=MenuBar(MENU_ITEMS)
        self.iplistview=ListView()
        self.scanview=ScanView()

    def update_scr(self,stdscr):
        stdscr.clear()
        self.iplistview.display(stdscr,self.ip_to_scan)
        self.status_bar.draw(stdscr) 
        self.menu_bar.draw(stdscr)
        

        stdscr.refresh()

    def handle_inkey(self,stdscr):
        inkey=stdscr.getch()
        # bindings for keys
        if chr(inkey) in self.menu_bar.keybinds:
            menu_select=self.menu_bar.dropdown(stdscr,self.menu_bar.keybinds[chr(inkey)])
        else:
            menu_select=False
        # Below is the binding for menu bar
        if menu_select:
            self.handle_menu_selection(stdscr,menu_select)
        else:
            return inkey

    def handle_menu_selection(self,stdscr,sel_item):
        if sel_item == "Exit":
            sys.exit("Goodbye...") 
        elif sel_item == "Add Host to queue (By IP address)":
            input_ip=DialogBox_input("Enter IP address:").display()
            self.ip_to_scan.append(input_ip)
            self.update_scr(stdscr)
        elif sel_item == "Remove from list":
            idx=DialogBox_input("Enter List *index*").display()
            if idx.isdigit(): idx=int(idx)
            if self.ip_to_scan[idx]:
                del self.ip_to_scan[idx] 
            else:
               self.status_bar.set_text("Item not in list... (index error) ->"+str(idx))
        elif sel_item == "Configure ports": 
            pass
        elif sel_item == "Begin Scan":
            self.do_scan()
        elif sel_item == "Enumerate HTTPs dirs":
            #dirbust
            pass

    def do_scan(self):
        for ip in self.ip_to_scan:
            #IP LOOP XXXXXXXXXXXXXXXXXXXXXX
            #becomes true If we get a reply from ANY PORT of host 
            host_reachable=False
            curr_ports_state={p: False for p in self.ports_to_scan}
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sx:
                probe=ProbeSocket(sx)
                for prt in self.ports_to_scan:
                    if probe.connect(ip,prt):
                        if probe.send_stress(self.payloadmsg):
                            host_reachable=True
                            #TODO get reply 

                            #probe.recv()
                        else:
                            pass
                    else:
                         #If we cant connect and send something skip to next port in the list.
                        continue
            
            if not host_reachable:
                pass
            elif host_reachable:   
                self.hosts_state[ip]=curr_ports_state
        #end ip loop                


        



curses.wrapper(main)

