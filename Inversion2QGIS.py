# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 21:54:12 2019
@author: ericv
"""

"""
Verbeter punten voor versie 1.1:
    1. Output folder vervangen voor output file(s)
    2. Optie voor wel of niet mergen van input bestanden
    3. Optie om zowel de normale als de gereduceerde data als output te genereren

"""
from EM_Tomo_viz_tools import *
import tkinter as tk
from tkinter import filedialog,messagebox, ttk
import sys
import base64


#initiate layer dictionary

layer_dict = {}
criteria = []
elevations = []

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
class Window1:
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
        csvfile_label = tk.Label(page1, text = "CSV files", bg="light grey").grid(row = 1, column = 0, sticky = tk.W)
        output_label = tk.Label(page1, text = "Output folder", bg="light grey").grid(row = 2, column = 0, sticky = tk.W)
        Data_type_label = tk.Label(page1, text = "2D or 3D data CSV files?", bg="light grey").grid(row = 4, column = 0, sticky = tk.W)
        Data_reduction_label = tk.Label(page1, text = "Compress data for faster visualisation", bg="light grey").grid(row = 5, column = 0, sticky = tk.W)

        self.min_EC_label = tk.Label(page1, text = "Minimum EC value:", bg="light grey")
        self.max_EC_label = tk.Label(page1, text = "Maximum EC value:", bg="light grey")
        self.EC_resolution_label = tk.Label(page1, text = "EC resolution:", bg="light grey")
        self.reduction_label = tk.Label(page1, text = "Data reduction factor:", bg="light grey")

        self.status_frame = tk.Frame(page1)
        self.status = tk.Label(self.status_frame, textvariable = self.status_msg, bg="white",bd = 1,relief=tk.SUNKEN, anchor=tk.W).pack(fill = "both", expand = True)

        self.status_frame.grid(row=10, column=0, columnspan=3, sticky=tk.E+tk.W+tk.S, pady = 15)
        #Buttons

        # creating the buttons for browsing to files
        self.browseButton = tk.Button(page1, text = "Browse", command = self.browsefile, bg = "light grey")
        self.browseButton2 = tk.Button(page1, text = "Browse", command = self.outputfilename, bg = "light grey")
        # placing the button on my window
        self.browseButton.grid(row = 1, column = 3, sticky = tk.E, padx=10, ipadx = 25)
        self.browseButton2.grid(row= 2, column = 3, sticky = tk.E, padx=10, ipadx = 25)
        #Go button
        self.cbutton = tk.Button(page1, text = "Go!", bg="light grey",foreground = 'black',command = self.process)
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
        data_button_2D = tk.Radiobutton(master, text = "2D Data", bg="light grey", variable = self.input_data_type, value = "2D").grid(row = 4, column = 1, padx = 10)
        data_button_3D = tk.Radiobutton(master, text = "3D Data", bg="light grey", variable = self.input_data_type, value = "3D").grid(row = 4, column =3, sticky = tk.E, padx = 10)

        #reduce data checkbox
        self.reduceDataCheck = tk.Checkbutton(master, text = "Yes/No", bg="light grey", variable = self.reduce, command = lambda: expand_GUI(master, self))
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
        page1.update()
        params = tuple()
        self.succesmsg.set("Running program....")
        self.status_msg.set("Running program...")
        page1.update()
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

class Window2:
    def __init__(self, master):
        self.layer_name = tk.StringVar()
        self.layer_id = tk.IntVar(0)
        self.filetext2 = tk.StringVar()
        self.filetext3 = tk.StringVar()
        self.filetext4 = tk.StringVar()
        self.filetext5 = tk.StringVar()
        self.filetext6 = tk.StringVar()
        self.status_msg2 = tk.StringVar()
        self.status_msg2.set("No criteria specified...")
        self.filename2 = tk.StringVar()
        #self.filename2.set('')
        self.output_filename2 = tk.StringVar()
        #self.output_filename2.set('')
        self.output_filetext2 = tk.StringVar()
        self.status_msg3 = tk.StringVar()
        self.status_msg3.set("Idle...")
        self.final_msg3 = tk.StringVar()
        self.succesmsg3 = tk.StringVar()


        #labels
        input_shp_label = tk.Label(page2, text = "Select input shape file", background = 'light grey').grid(row = 1, column = 0, sticky = tk.W)
        output_shp_label = tk.Label(page2, text = "Select output file name location", background = 'light grey').grid(row = 2, column = 0, sticky = tk.W)
        addcriteria_label1 = tk.Label(page2, text = "EC greater than:", background = 'light grey').grid(row = 4, column = 0, sticky = tk.W)
        addcriteria_label2 = tk.Label(page2, text = "EC smaller than:", background = 'light grey').grid(row = 5, column = 0, sticky = tk.W)
        addcriteria_label3 = tk.Label(page2, text = "Elev. greater than:", background = 'light grey').grid(row = 6, column = 0, sticky = tk.W)
        addcriteria_label4 = tk.Label(page2, text = "Elev. smaller than:", background = 'light grey').grid(row = 7, column = 0, sticky = tk.W)
        explanation_label1 = tk.Label(page2, text = 'Add selection criteria with the input fields below:', background = 'light grey')
        explanation_label1.grid(row = 3 , column = 0, columnspan = 3, sticky = tk.W, pady = 15)

        #status label
        self.status_frame2 = tk.Frame(page2)
        self.status2 = tk.Label(self.status_frame2, textvariable = self.status_msg2, bg="white",bd = 1,relief=tk.SUNKEN, anchor=tk.W).pack(fill = "both", expand = True)
        self.status_frame2.grid(row=8, column=0, columnspan=3, sticky=tk.E+tk.W+tk.S, pady = 15)
        self.status_frame3 = tk.Frame(page2)
        self.status3 = tk.Label(self.status_frame3, textvariable = self.status_msg3, bg="white",bd = 1,relief=tk.SUNKEN, anchor=tk.W).pack(fill = "both", expand = True)
        self.status_frame3.grid(row=10, column=0, columnspan=3, sticky=tk.E+tk.W+tk.S)

        #input fields
        output_shp_name_field = tk.Entry(master, textvariable = self.output_filetext2).grid(row = 2, column = 1, padx=10)
        input_bar2 = tk.Entry(master, textvariable = self.filetext2).grid(row = 1, column = 1, padx=10)
        input_bar3 = tk.Entry(master, textvariable = self.filetext3).grid(row = 4, column = 1, padx=10)
        input_bar4 = tk.Entry(master, textvariable = self.filetext4).grid(row = 5, column = 1, padx=10)
        input_bar5 = tk.Entry(master, textvariable = self.filetext5).grid(row = 6, column = 1, padx=10)
        input_bar6 = tk.Entry(master, textvariable = self.filetext6).grid(row = 7, column = 1, padx=10)

        #buttons
        self.addlayer_button = tk.Button(master, text = "Browse",command = self.outputfilename2, background = "light grey")
        self.addlayer_button.grid(row = 2, column = 2, sticky = tk.E, padx=10, ipadx = 25)
        self.addcriteria_button = tk.Button(master, text = "Add criterium to layer definition",command = self.add_criteria, background = "light grey")
        self.addcriteria_button.grid(row = 7, column = 2, padx=10, ipadx = 25, sticky = tk.E)
        self.browseButton3 = tk.Button(master, text = "Browse", command = self.browsefile2, background = "light grey").grid(row = 1, column = 2, padx = 10, ipadx = 25, sticky = tk.E)
        self.goButton2 = tk.Button(master, text = "Go!", command = self.process2, background = "light grey").grid(row = 9, column = 2, ipadx = 35,sticky = tk.E)

    def add_criteria(self):
        ec_greater = self.filetext3.get()
        ec_smaller = self.filetext4.get()
        elev_greater = self.filetext5.get()
        elev_smaller = self.filetext6.get()
        criteria.append([ec_greater, ec_smaller, elev_greater, elev_smaller])
        self.filetext3.set('')
        self.filetext4.set('')
        self.filetext5.set('')
        self.filetext6.set('')
        for crit in criteria:
            if crit == ['','','','']:
                messagebox.showinfo("Report", "No criteria specified")
                criteria.remove(crit)
                self.status_msg2.set('Total number of criteria defined = '+str(len(criteria)))
                break
            else:
                for i in crit:
                    if i != '':
                        try:
                            float(i)
                        except:
                            messagebox.showinfo("Report", "Input is not a valid number, please use numbers with . as decimal separator")
                            criteria.remove(crit)
                            self.status_msg2.set('Total number of criteria defined = '+str(len(criteria)))
                            break
            self.status_msg2.set('Total number of criteria defined = '+str(len(criteria)))

    def browsefile2(self):
        self.filename2 = tk.filedialog.askopenfilename(initialdir = "~/", title = "Select shapefile", filetypes = [("shapefiles", "*.shp")])
        self.filetext2.set(self.filename2)

    def outputfilename2(self):
        self.output_filename2 = tk.filedialog.asksaveasfilename(initialdir = "~/", title = "Give shapefile filename and location", filetypes = (("shp files","*.shp"),("all files","*.*")))
        self.output_filetext2.set(self.output_filename2)

    def process2(self):
        input_file2 = self.filename2
        output_file2 = self.output_filename2
        if isinstance(input_file2, str) == True & isinstance(output_file2, str) == True:
            if len(criteria) < 1:
                messagebox.showinfo("Report", "No criteria specified, operation aborted")
                return
            self.succesmsg3.set("Running program....")
            self.status_msg3.set("Running program...")
            page2.update()
            try:
                self.final_msg3.set(str(create_filtered_layer(input_file2, output_file2, criteria)))
            except:
                messagebox.showinfo("Report", "Something went wrong, contact the authors if it keeps happening")
            self.succesmsg3.set("Finished!")
            self.status_msg3.set("Idle...")
            page2.update()
            messagebox.showinfo("Result", str(self.final_msg3.get()))
            criteria.clear()
            self.status_msg2.set('Total number of criteria defined = '+str(len(criteria)))
        else:
            messagebox.showinfo("Report", "Please specify input and output file with the browse button")
            return


class Window3:
    def __init__(self, master):
        self.filetext = tk.StringVar()
        self.output_foldertext = tk.StringVar()
        self.status_msg = tk.StringVar()
        self.elevnum = tk.DoubleVar()
        self.elevnum.set(-1)
        self.grid_size = tk.DoubleVar()
        self.grid_size.set(0)
        self.autoGrid = tk.BooleanVar()
        self.autoGrid.set(True)


        #Markup

        #Labels
        input_file_label = tk.Label(master, text = "Select input shape file", bg="light grey").grid(row = 1, column = 0, sticky = tk.W)
        output_label = tk.Label(master, text = "Output folder", bg="light grey").grid(row = 2, column = 0, sticky = tk.W)
        input_height_label = tk.Label(master, text = "Elevation level (m)", bg="light grey").grid(row = 4, column = 0, sticky = tk.W)
        explainer_info = "Enter elevation level against NAP for which to generate the XY plane. Add multiple levels using the button."
        explainer_label = tk.Label(master, text = explainer_info, bg="light grey"). grid (row = 3, column = 0, columnspan=4, pady = 15, sticky=tk.W )
        self.grid_size_label = tk.Label(master, text = "Grid size (m)", bg="light grey")
        # self.grid_size_info_label = tk.Label(master, text = grid_info, bg="light grey")

        self.status_frame = tk.Frame(master)
        self.status = tk.Label(self.status_frame, textvariable = self.status_msg, bg="white",bd = 1,relief=tk.SUNKEN, anchor=tk.W).pack(fill = "both", expand = True)
        self.status_frame.grid(row=100, column=0, columnspan=7, sticky=tk.W+tk.E+tk.S)
        #Buttons

        # creating the buttons for browsing to files
        self.browseButton = tk.Button(master, text = "Browse", command = self.browsefile, bg = "light grey")
        self.browseButton2 = tk.Button(master, text = "Browse", command = self.browsefolder, bg = "light grey")
        # placing the button on my window
        self.browseButton.grid(row = 1, column = 3, sticky = tk.E, padx=10, ipadx = 25)
        self.browseButton2.grid(row= 2, column = 3, sticky = tk.E, padx=10, ipadx = 25)
        # add elevation buttons
        self.ElevationButton = tk.Button(master, text ="Add", command = self.addelevation, bg= "light grey")
        self.ElevationButton.grid(row= 4, column = 3, sticky = tk.E, padx=10, ipadx = 25)
        #Add option to specify raster size by oneself:
        self.autoGridCheck = tk.Checkbutton(master, text = "Automatic grid size", bg="light grey", variable = self.autoGrid, command = self.expand_manual_grid)
        self.autoGridCheck.grid(row = 5, column = 3, sticky = tk.E, padx=10)

        #Go button
        self.cbutton = tk.Button(master, text = "Go!", bg="light grey",foreground = 'black',command = self.process)
        self.cbutton.grid(row = 6, column = 3, ipadx = 35,sticky = tk.E, pady = 20)

        #inputs
        self.grid_size_field = tk.Entry(master, textvariable = self.grid_size)
        input_file_field = tk.Entry(master, textvariable = self.filetext).grid(row = 1, column = 1, padx=10)
        output_file_field = tk.Entry(master, textvariable = self.output_foldertext).grid(row = 2, column = 1, padx=10)
        input_height_field = tk.Entry(master, textvariable = self.elevnum).grid(row = 4, column = 1, padx = 10)

    def client_exit(self):
        exit()

    def browsefile(self):
        self.filename = tk.filedialog.askopenfilename(initialdir = "~/", title = "Select CSV file", filetypes = [("Shape files","*.shp")])
        self.filetext.set(self.filename)

    def browsefolder(self):
        self.output_folder = tk.filedialog.askdirectory(initialdir = "~/", title = "Select output folder")
        self.output_foldertext.set(self.output_folder)

    def addelevation(self):
        try:
            new_elevation = self.elevnum.get()
            float(new_elevation)
            elevations.append(float(new_elevation))
        except:
            messagebox.showinfo("Invalid number","Input is not a valid number. Only numbers with decimal points are allowed.")
            self.elevnum.set('')
        self.status_msg.set('Selected elevations: {}'.format(', '.join(map(str,elevations))))
        self.elevnum.set(-1)



    def expand_manual_grid(self):
        if self.grid_size_field.winfo_ismapped() == False:
            #show input field
            self.grid_size_field.grid(row = 5, column = 1, padx=10)
            #show labels
            self.grid_size_label.grid(row = 5, column = 0, sticky = tk.W)
            # self.grid_size_info_label.grid(row = 5, column = 0, sticky  = tk.W)
            messagebox.showinfo("Info","Please specify the grid width in meters")
        else:
            #remove bars
            self.grid_size_field.grid_remove()
            #remove labels
            self.grid_size_label.grid_remove()
            # self.grid_size_info_label.grid_remove()



    def process(self):
        #check manual grid button

        input_file = self.filetext.get()
        output_folder = self.output_foldertext.get()
        auto_grid_size = self.autoGrid.get()

        try:
            grid_size = self.grid_size.get()
            float(grid_size)
            if not(auto_grid_size) and grid_size<0:
                raise ValueError('grid_size is minus')
        except:
            messagebox.showinfo("Invalid number","Grid size is not a valid number. Only positive numbers with decimal points are allowed.")
            self.grid_size.set(0)


        if auto_grid_size:
            grid_size = 0
            #default value 0 will trigger automatic grid sizing.

        if input_file == '' or output_folder == '':
            messagebox.showinfo("Report", "Please specify input and output using the browse buttons.")
            return

        if len(elevations) == 0:
            messagebox.showinfo("Report", "No elevation levels specified. Please add levels using the Add button.")
            return

        output_msg = create_cross_section(self, input_file, output_folder, elevations, grid_size = grid_size)
        messagebox.showinfo("Report", output_msg)
        self.status_msg.set('Finished')
        elevations.clear()


#main
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
style = ttk.Style(root)

# set ttk theme to "clam" which support the fieldbackground option
style.theme_use("default")
style.configure('test.TNotebook', background = 'light grey')
style.configure('newstyle.TFrame', background = 'light grey')

#root.geometry('500x500')
root.title("Inversion2QGIS v4.0 - build 1")
root.lift()
root.configure(background = "light grey")
#window = Window(root)
wiertsema_bs64="""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"""

icon = tk.PhotoImage(data=wiertsema_bs64)
tk.Label(root, image=icon, bg="white").grid(row=0, column = 0, sticky = tk.W)


#define Notebook tabs
nb = ttk.Notebook(root, style = 'test.TNotebook')
nb.grid(row = 1, column = 0, sticky = 'NESW')

page1 = ttk.Frame(nb, style = 'newstyle.TFrame')
nb.add(page1, text='CSV to shp converter')


page2 = ttk.Frame(nb, style = 'newstyle.TFrame')
nb.add(page2, text = "Layer Selection")

page3 = ttk.Frame(nb, style = 'newstyle.TFrame')
nb.add(page3, text = "XY Plane")

window = Window1(page1)
window2 = Window2(page2)
window3 = Window3(page3)

imgicon = tk.PhotoImage(file='logo.gif')
root.tk.call('wm', 'iconphoto', root._w, imgicon)  
root.mainloop()
