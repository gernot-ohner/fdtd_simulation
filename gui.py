import tkinter as tk
import shelve
from noc import FDTD

class Application(tk.Frame):

    def create_widgets(self):
        """Create most of the GUI"""
        self.bt_plot = tk.Button(self, text="compute", command = self.compute).grid(row = 11, column = 0)
        self.bt_plot = tk.Button(self, text="plot", command = self.plot).grid(row = 11, column = 1)

        self.lab_nt = tk.Label(self, text = "Number of timesteps: ").grid(row = 0, column = 0)
        self.lab_f = tk.Label(self, text = "Frequency: ").grid(row = 1, column = 0)
        self.lab_x = tk.Label(self, text = "x: ").grid(row = 2, column = 0)
        self.lab_y = tk.Label(self, text = "y: ").grid(row = 3, column = 0)
        self.lab_p = tk.Label(self, text = "p: ").grid(row = 4, column = 0)
        self.lab_q = tk.Label(self, text = "q: ").grid(row = 5, column = 0)

        self.lab_R = tk.Label(self, text = "R: ").grid(row = 10, column = 0)

        self.ent_nt = tk.Entry(self)
        self.ent_nt.insert(0, '500')
        self.ent_nt.grid(row = 0, column = 1)

        self.ent_f = tk.Entry(self)
        self.ent_f.insert(0, '1e9')
        self.ent_f.grid(row = 1, column = 1)

        self.ent_xmin = tk.Entry(self)
        self.ent_xmin.insert(0, '-2')
        self.ent_xmin.grid(row = 2, column = 1)

        self.ent_xmax = tk.Entry(self)
        self.ent_xmax.insert(0, '2')
        self.ent_xmax.grid(row = 2, column = 2)

        self.ent_ymin = tk.Entry(self)
        self.ent_ymin.insert(0, '-2')
        self.ent_ymin.grid(row = 3, column = 1)

        self.ent_ymax = tk.Entry(self)
        self.ent_ymax.insert(0, '2')
        self.ent_ymax.grid(row = 3, column = 2)

        self.ent_p = tk.Entry(self)
        self.ent_p.insert(0, '1')
        self.ent_p.grid(row = 4, column = 1)

        self.ent_q = tk.Entry(self)
        self.ent_q.insert(0, '1.5')
        self.ent_q.grid(row = 5, column = 1)

        self.ent_R = tk.Entry(self)
        self.ent_R.insert(0, '50')
        self.ent_R.grid(row = 10, column = 1)

        self.var_src = tk.StringVar(self)
        self.var_src.set("pulse_gauss")
        self.opt_src = tk.OptionMenu(self, self.var_src,'pulse_gauss', 'cont_gauss', 'point')
        self.opt_src.grid(row = 1, column = 2)



    def compute(self):
        """Acquire Values for various parameters. Create an FDTD object with these parameters
        Call the Function to compute the simulation. Call the function to plot the computed values"""

        xmin, xmax = int(self.ent_xmin.get()), int(self.ent_xmax.get())
        ymin, ymax = int(self.ent_ymin.get()), int(self.ent_ymax.get())
        p, q = float(self.ent_p.get()), float(self.ent_q.get())
        nt = int(self.ent_nt.get())
        f = float(self.ent_f.get())
        R = int(self.ent_R.get())
        src = self.var_src.get()
        shape = (xmin, xmax, ymin, ymax)
        self.fd = FDTD(f, shape, nt, src, p, q, R)
        self.fd.compute()

    def plot(self):
        self.fd.fdplot()

    def create_menu(self):
        """Create the menu entries in the GUI"""
        self.menubar = tk.Menu(root)

        self.filemenu = tk.Menu(self.menubar, tearoff = 0)
        self.filemenu.add_command(label = "Open", command = root.quit) # need to update command
        self.filemenu.add_command(label = "Save", command = root.quit) # need to update command
        self.filemenu.add_separator()
        self.filemenu.add_command(label = "Exit", command = root.quit) 

        self.configmenu = tk.Menu(self.menubar, tearoff = 0)
        self.configmenu.add_command(label = "Save Config", command = self.save_conf)
        self.configmenu.add_command(label = "Load Config", command = self.load_conf)

        self.menubar.add_cascade(label = "File", menu = self.filemenu)
        self.menubar.add_cascade(label = "Config", menu = self.configmenu)
        self.menubar.add_command(label = "Help", command = root.quit) # need to update command

    def save_conf(self):
        """Save the entries of the text fields (the simulation parameters)
        to a binary file."""
        xmin, xmax = int(self.ent_xmin.get()), int(self.ent_xmax.get())
        ymin, ymax = int(self.ent_ymin.get()), int(self.ent_ymax.get())
        p, q = float(self.ent_p.get()), float(self.ent_q.get())
        nt = int(self.ent_nt.get())
        f = float(self.ent_f.get())

        shelf_file = shelve.open('fdtd_data')
        conf = [xmin, xmax, ymin, ymax, f, nt, p, q]
        shelf_file['conf'] = conf
        shelf_file.close()
        print("Config saved.")

    def load_conf(self):
        """Load a binary configuration file created by the function "save_conf()" 
        and fill the text fields with the corresponding values"""
        shelf_file = shelve.open('fdtdconf')
        conf = shelf_file['conf']
        
        self.ent_xmin.delete(0, tk.END)
        self.ent_xmin.insert(0, conf[0])

        self.ent_xmax.delete(0, tk.END)
        self.ent_xmax.insert(0, conf[1])

        self.ent_ymin.delete(0, tk.END)
        self.ent_ymin.insert(0, conf[2])

        self.ent_ymax.delete(0, tk.END)
        self.ent_ymax.insert(0, conf[3])

        self.ent_f.delete(0, tk.END)
        self.ent_f.insert(0, conf[4])

        self.ent_nt.delete(0, tk.END)
        self.ent_nt.insert(0, conf[5])

        self.ent_p.delete(0, tk.END)
        self.ent_p.insert(0, conf[6])

        self.ent_q.delete(0, tk.END)
        self.ent_q.insert(0, conf[7])

        print('Config loaded')

    def __init__(self, master=None):
        """Initialize the Application object"""
        super().__init__(master)
        root.wm_title("FDTD")
        self.grid()
        self.create_menu()
        self.create_widgets()
        root.config(menu = self.menubar)

root = tk.Tk()
app = Application(master = root)
app.mainloop()
app.destroy()
