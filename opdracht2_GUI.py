# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 21:54:12 2019

@author: ericv
"""

import tkinter as tk

class Window(tk.Frame):
    
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.init_window()
        
    #Creation of init_window
    def init_window(self):
        
        #changing the title of the widget
        self.master.title("Data transformatie tool")
        
        #allowing the widget to take the full space in the frame
        self.pack(fill=tk.BOTH, expand=1)
        
        # creating a button instance
        quitButton = tk.Button(self, text = "Quit", command = self.client_exit)
        
        #placing the button on my window
        quitButton.place(x=0, y=0)
        
    def client_exit(self):
        exit()
        
        
root = tk.Tk()

#size of the window
root.geometry("400x300")

app = Window(root)
root.mainloop()


