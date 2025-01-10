from __future__ import annotations
import curses
import os
import sys
import json
import time

# UI elements using pycurses. 
# Implemented as a module for re-usability.

class ListView:
# Used before scan to display the hosts that will be scanned
    curses.update_lines_cols() 
    avail_lines=curses.LINES-2
    def __init__(self):
        pass

    def display(self,stdscr,lst):
        # lst represents a list to display on screen
        #TODO allow sublist view (indentated sub items)
        xpos=1
        ypos=2
        idx=0
        # TODO page_num = 1
        # XXX pages=[]
        for itm in lst:
            stdscr.addstr(ypos,xpos,str(idx)+" "+itm)
            ypos+=1
            idx+=1

class ScanView:
    # Used DURING scan to get a deeper look at the hosts and _ports_
    def __init__(self):

        pass
    

    def display(self,stdscr,lst):
        # hstate represents a dict (hosts statte
        xpos=1
        ypos=2
        idx=0
        subidx=0
         
        #page_num = 1
        for itm in lst:
            if ypos < curses.LINES-2:
                if type(itm) == "list" and subidx in itm:
                    stdscr.addstr(ypos,xpos,str(idx)+" LIST")
                    xpos+=2
                    for i in itm:
                        stdscr.addstr(ypos,xpos,str(subidx)+" "+i)
                        ypos+=1
                        subidx+=1
                        
                else:
                    stdscr.addstr(ypos,xpos,str(idx)+" "+itm)
                ypos+=1
                idx+=1
            else:
                break


class StatusBar:
    line_num=None
    text = ""

    def __init__(self):
        self.line_num=curses.LINES-1
        self.set_text("Placeholder")

    def draw(self,stdscr):
        stdscr.addstr(self.line_num,0,self.text,curses.A_REVERSE)
    
    def set_text(self,msg=None):
        if msg:
            self.text = msg.ljust(curses.COLS-2)
        else:
            self.text=" ".ljust(curses.COLS-2)

    def get_str(self,stdscr,msg):
        stdscr.addstr(self.line_num,0," ".ljust(curses.COLS-1),curses.A_REVERSE)
        stdscr.addstr(self.line_num,0,msg,curses.A_REVERSE)
        curses.echo()
        curses.flash()
        inp = stdscr.getstr()
        curses.noecho()
        return inp

class MenuBar:
    drop_width = {}
    drop_xpos = {} 
    keybinds={}
    color_selected=2
    def __init__(self,itemlst):
        self.menu_items=itemlst
        self.keybinds={it[0]: it for it in self.menu_items}
        self.main_items=list(self.menu_items)
        for mainitem in self.main_items:
            self.drop_width[mainitem] = 0
            self.drop_xpos[mainitem] = 0
        #Figure out the dropdown top-left corner position along the x Axis
        #(Done easily by checking the position of item's first letter in the following string:
        self.menu_str = "   ".join(self.main_items)
        for mainitem in self.main_items:
            self.drop_xpos[mainitem] = self.menu_str.find(mainitem)
            for subitem in self.menu_items[mainitem]:
                if len(subitem)+1 > self.drop_width[mainitem]:
                    self.drop_width[mainitem] = len(subitem)+1

    def draw(self,stdscr):
        stdscr.addstr(0,0,self.menu_str,curses.A_STANDOUT)
    
    def dropdown(self,stdscr,mainitem):
        menuctrl=True
        selection_ypos=1
        selected_item=None
        
        # Take care of drawing the dropdown
        while menuctrl:
            stdscr.addstr(0,0,self.menu_str,curses.A_STANDOUT)
            stdscr.addstr(0,self.drop_xpos[mainitem],mainitem)
            ypos=1
            for subitem in self.menu_items[mainitem]:
                if ypos != selection_ypos:
                    stdscr.addstr(ypos,self.drop_xpos[mainitem],subitem.ljust(self.drop_width[mainitem]),curses.A_REVERSE)
                elif ypos == selection_ypos:
                    stdscr.addstr(ypos,self.drop_xpos[mainitem],subitem.ljust(self.drop_width[mainitem]),curses.color_pair(self.color_selected))
                ypos=ypos+1
            # Key bindings to react to input below...
            inkey=stdscr.getch()
            if inkey == curses.KEY_UP and selection_ypos > 1:
                selection_ypos=selection_ypos-1
            elif inkey==curses.KEY_DOWN and selection_ypos < len(self.menu_items[mainitem]):
                selection_ypos=selection_ypos+1
            elif inkey == curses.KEY_LEFT and self.main_items.index(mainitem) >= 1 :
                stdscr.clear()
                mainitem = self.main_items[self.main_items.index(mainitem)-1]
            elif inkey == curses.KEY_RIGHT and self.main_items.index(mainitem) < len(self.main_items)-1:
                stdscr.clear()
                mainitem = self.main_items[self.main_items.index(mainitem)+1]
            elif inkey==10: # key : ENTER
                selected_item=self.menu_items[mainitem][selection_ypos-1] 
                return selected_item
            stdscr.refresh()

class ProgressMeterBar:
    def __init__(self,value,valuemax: 'value to track'):
        pass






class DialogBox_yesno:
    def __init__(self,msg,boxtype="input",bc="+",itemlist=None):
    # ypos and xpos represents top left corner
    # This class will return the input string IF it is an input dialog
        self.msg=msg
        self.boxtype=boxtype
        self.padding = 2
        self.borderchar = bc
        self.ypos=curses.LINES//3
        self.xpos=curses.COLS//3
        self.ylen=8
        self.xlen=21
        self.items=itemlist



    def display(self):
        self.win = curses.newwin(self.ylen,self.xlen,self.ypos,self.xpos)
        self.win.border()
        self.win.addstr(self.padding,self.padding,self.msg)
        if self.boxtype == "input":
            curses.echo()
            self.win.refresh()
            in_str=self.win.getstr(self.ylen-self.padding,self.padding) 
            curses.noecho()
            return str(in_str)

class DialogBox_input:
    def __init__(self,msg,bc="+"):
    # ypos and xpos represents top left corner
        self.msg=msg
        self.padding = 2
        self.borderchar = bc
        self.ypos=int(curses.LINES//3)
        self.xpos=int(curses.COLS//3)
        self.ylen=7
        self.xlen=19


    def display(self):
        self.win = curses.newwin(self.ylen,self.xlen,self.ypos,self.xpos)
        #self.win.attron(curses.A_REVERSE)
        self.win.addstr(self.padding,self.padding,str(self.msg))
        curses.echo()
        in_str=self.win.getstr(self.ylen-1,self.padding) 

        curses.noecho()
        # XXX Kill the window !!
        return in_str.decode()



