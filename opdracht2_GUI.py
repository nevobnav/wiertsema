# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 21:54:12 2019

@author: ericv
"""

"""
GUI maken middels de volgende stappen:
    1. Main frame maken
    2. Zorgen dat geprogrameerde functies geimporteerd kunnen worden
    3. Zorgen voor een knop voor het importeren van 1 of meerdere csv bestanden (eerst 1) (moeten meerdere csv bestanden gemerged worden naar 1 shapefile?)
    4. Zorgen dat reduce data parameters duidelijk ingevoerd kunnen worden
    5. Zorgen dat het programma uitgevoerd kan worden op basis van 1 csv bestand
    6. als output opties op dit moment alleen een shapefile met punten
"""

from EM_Tomo_viz_tools import *
import tkinter as tk
from tkinter import filedialog,messagebox

def expand_GUI(master, self):
    if self.EC_min_bar.winfo_ismapped() == False:
        #show bars
        self.EC_min_bar.grid(row = 6, column = 1, sticky = tk.W)
        self.EC_max_bar.grid(row = 7, column = 1, sticky = tk.W)
        self.EC_resolution_bar.grid(row = 8, column = 1, sticky = tk.W)
        self.reduction_bar.grid(row = 9, column = 1, sticky = tk.W)

        #show labels
        self.min_EC_label.grid(row = 6, column = 0, sticky = tk.W)
        self.max_EC_label.grid(row = 7, column = 0, sticky = tk.W)
        self.EC_resolution_label.grid(row = 8, column = 0, sticky = tk.W)
        self.reduction_label.grid(row = 9, column = 0, sticky = tk.W)
    else:   
        #remove bars
        self.EC_min_bar.grid_remove()
        self.EC_max_bar.grid_remove()
        self.EC_resolution_bar.grid_remove()
        self.reduction_bar.grid_remove()
        
        #remove labels
        self.min_EC_label.grid_remove()
        self.max_EC_label.grid_remove()
        self.EC_resolution_label.grid_remove()
        self.reduction_label.grid_remove()

def is_float(x):
    try:
        x = float(x)
        return True
    except:
        return False
    
def setNumber(self):
    self.min_EC.set(self.min_EC.get())
    self.max_EC.set(self.max_EC.get())
    self.EC_resolution.set(self.EC_resolution.get())
    self.reduction_factor.set(self.reduction_factor.get())
    
#class Window(tk.Frame):
class Window:       
    def __init__(self, master):
        self.filename= tk.StringVar()
        self.filetext = tk.StringVar()
        self.output_filename = tk.StringVar()
        self.output_filetext = tk.StringVar()
        self.status_msg = tk.StringVar()
        self.succesmsg = tk.StringVar()
        self.final_msg = tk.StringVar()
        self.status_msg.set("Idle...")
        self.input_data_type = tk.StringVar()
        self.input_data_type.set("2D")
        self.reduce = tk.BooleanVar()
        self.reduce.set(False)
        self.min_EC = tk.DoubleVar()
        self.min_EC.set(10)        
        self.max_EC = tk.DoubleVar()
        self.max_EC.set(500)
        self.EC_resolution = tk.DoubleVar()
        self.EC_resolution.set(2)
        self.reduction_factor = tk.DoubleVar()
        self.reduction_factor.set(1.5)

        #Markup
               
        #Labels
        csvfile_label = tk.Label(root, text = "CSV files", bg="white").grid(row = 1, column = 0, sticky = tk.W)
        output_label = tk.Label(root, text = "Output folder", bg="white").grid(row = 2, column = 0, sticky = tk.W)
        Data_type_label = tk.Label(root, text = "2D or 3D data CSV files?", bg="white").grid(row = 4, column = 0, sticky = tk.W)
        Data_reduction_label = tk.Label(root, text = "Compress data for faster visualisation", bg="white").grid(row = 5, column = 0, sticky = tk.W)

        self.min_EC_label = tk.Label(root, text = "Minimum EC value:")
        self.max_EC_label = tk.Label(root, text = "Maximum EC value:")
        self.EC_resolution_label = tk.Label(root, text = "EC resolution:")
        self.reduction_label = tk.Label(root, text = "Data reduction factor:")

        self.status_frame = tk.Frame(root)
        self.status = tk.Label(self.status_frame, textvariable = self.status_msg, bg="white",bd = 1,relief=tk.SUNKEN, anchor=tk.W).pack(fill = "both", expand = True)
        self.status_frame.grid(row=10, column=0, columnspan=4, sticky=tk.E+tk.W+tk.S)

        #Buttons
        
        # creating the buttons for browsing to files
        self.browseButton = tk.Button(root, text = "Browse", command = self.browsefile)
        self.browseButton2 = tk.Button(root, text = "Browse", command = self.outputfilename)
        # placing the button on my window
        self.browseButton.grid(row = 1, column = 3, sticky = tk.E, padx=10, ipadx = 25)
        self.browseButton2.grid(row= 2, column = 3, sticky = tk.E, padx=10, ipadx = 25)
        #Go button
        self.cbutton = tk.Button(root, text = "Go!", bg="white",foreground = 'black',command = self.process)
        self.cbutton.grid(row = 9, column = 3, sticky = tk.E, padx = 10, ipadx = 35)
        
        #inputs  
        #input and output files
        input_bar = tk.Entry(master, textvariable = self.filetext).grid(row = 1, column = 1, padx=10)
        output_bar = tk.Entry(master, textvariable = self.output_filetext).grid(row = 2, column = 1, padx=10)
        
        #reduce data input fields
        self.EC_min_bar = tk.Entry(master, textvariable = self.min_EC)
        self.EC_max_bar = tk.Entry(master, textvariable = self.max_EC)
        self.EC_resolution_bar = tk.Entry(master, textvariable = self.EC_resolution)
        self.reduction_bar = tk.Entry(master, textvariable = self.reduction_factor)

        #2D or 3D data?
        data_button_2D = tk.Radiobutton(master, text = "2D Data", bg="white", variable = self.input_data_type, value = "2D").grid(row = 4, column = 1, padx = 10)
        data_button_3D = tk.Radiobutton(master, text = "3D Data", bg="white", variable = self.input_data_type, value = "3D").grid(row = 4, column =3, sticky = tk.E, padx = 10)
        
        #reduce data checkbox
        self.reduceDataCheck = tk.Checkbutton(master, text = "Yes/No", variable = self.reduce, command = lambda: expand_GUI(master, self))
        self.reduceDataCheck.grid(row = 5, column = 3, sticky = tk.E, padx=10)
           
    def client_exit(self):
        exit()
        
    def browsefile(self):
        self.filename = tk.filedialog.askopenfilenames(initialdir = "~/", title = "Select CSV file", filetypes = [("CSV files","*.CSV")])
        self.filetext.set(self.filename)

    def outputfilename(self):
        self.output_filename = tk.filedialog.asksaveasfilename(initialdir = "~/", title = "Give shapefile filename", filetypes = (("shp files","*.shp"),("all files","*.*")))
        self.output_filetext.set(self.output_filename)
        
    def process(self):
        try:
            setNumber(self)
        except:
            messagebox.showinfo("Result", "Only numbers as input for the data reduction parameters please")
            return
        input_files = self.filename
        output_file = self.output_filename
        #check if data reduction is required
        reduce = self.reduce.get()
        input_data_type = self.input_data_type.get()
        finished = False
        root.update()
        params = tuple()
        self.succesmsg.set("Running program....")
        self.status_msg.set("Running program...")
        root.update()
        if isinstance(input_files, tuple) == True and isinstance(output_file, str) == True:
            if input_data_type == "2D":
                if reduce == True:
                    if is_float(self.min_EC.get()) & is_float(self.max_EC.get()) & is_float(self.EC_resolution.get()) & is_float(self.reduction_factor.get()):
                        EC_min = self.min_EC.get()
                        EC_max = self.max_EC.get()
                        resolution = self.EC_resolution.get()
                        data_reduction_factor = self.reduction_factor.get()
                        params = (EC_min, EC_max, resolution, data_reduction_factor)
                    else:
                        messagebox.showinfo("Report", "Only numbers as input please")
                        return
                if len(input_files) > 1:    
                    input_files = list(input_files)
                    self.final_msg.set(str(Processing_2D(input_files, output_file, reduce, params)))            
                else:
                    self.final_msg.set(str(Processing_2D(input_files, output_file, reduce, params)))            
                self.succesmsg.set("Finished")
                self.status_msg.set("Idle...")
                finished = True
                if finished:
                    messagebox.showinfo("Result", str(self.final_msg.get()))
            else:
                if reduce == True:
                    if is_float(self.min_EC.get()) & is_float(self.max_EC.get()) & is_float(self.EC_resolution.get()) & is_float(self.reduction_factor.get()):
                        EC_min = self.min_EC.get()
                        EC_max = self.max_EC.get()
                        resolution = self.EC_resolution.get()
                        data_reduction_factor = self.reduction_factor.get()
                        params = (EC_min, EC_max, resolution, data_reduction_factor)
                    else:
                        messagebox.showinfo("Report","Only numbers as input please")
                if len(input_files) > 1:    
                    input_files = list(input_files)
                    self.final_msg.set(str(Processing_3D(input_files, output_file, reduce, params)))            
                else:
                    self.final_msg.set(str(Processing_3D(input_files, output_file, reduce, params)))            
                self.succesmsg.set("Finished")
                self.status_msg.set("Idle...")
                finished = True
                if finished:
                    print(self.final_msg.get())
                    messagebox.showinfo("Result", str(self.final_msg.get()))
        else:
            messagebox.showinfo("Report","Please specify input and output file(s)")
            
#main                
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.title("Inversion data convertor v1.0")    
root.lift()
root.configure(background = "white")
window = Window(root)
wiertsema_bs64="""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"""

icon = tk.PhotoImage(data=wiertsema_bs64)
tk.Label(root, image=icon, bg="white").grid(row=0, column = 0, sticky = tk.W)

window = Window(root)
root.mainloop()

