import tkinter as tk
from tkinter import ttk
#pylint: disable=unused-wildcard-import
from tkinter.ttk import *
import shutil
import win32api
import win32file
import re
from PIL import Image, ImageTk

def convtostoragedict(inint, label=True):
    sd = {
        'Terabytes': "{:.2f}".format(round(inint/1000000000000, 2)),
        'Gigabytes': "{:.2f}".format(round(inint/1000000000, 2)),
        'Megabytes': "{:.2f}".format(round(inint/1000000, 2)),
        'Kilobytes': "{:.2f}".format(round(inint/1000, 2)),
        'Bytes': "{:.2f}".format(inint)
    }
    if label:
        sd = {
            'Terabytes': sd['Terabytes'] + 'TB',
            'Gigabytes': sd['Gigabytes'] + 'GB',
            'Megabytes': sd['Megabytes'] + 'MB',
            'Kilobytes': sd['Kilobytes'] + 'KB',
            'Bytes': sd['Bytes'] + 'B'
        }
    return sd

def getdrivesize(drive):
    ufdd = shutil.disk_usage(drive)
    dd = {
        'total': convtostoragedict(ufdd[0]),
        'used': convtostoragedict(ufdd[1]),
        'free': convtostoragedict(ufdd[2])
    }
    return(dd)

def getdrivetype(drive):
    DRIVE_TYPES = {
        0: 'Unknown',
        1: 'No Root Directory',
        2: 'Removable Disk',
        3: 'Local Disk',
        4: 'Network Drive',
        5: 'Compact Disc',
        6: 'RAM Disk'
    }
    return DRIVE_TYPES[win32file.GetDriveType(drive)]

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('LiveDisk')
        self.geometry('400x220')
        self.resizable(1, 0)
        self.minsize(width=350, height=220)
        self.style = ttk.Style(self)
        self.iconbitmap('icons/icon.ico')
        self.drivetype = tk.StringVar(self)
        self.style.theme_use('vista')

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.monitoring = 0
        self.monitorval = None

        title = Label(self, text="LiveDisk", font=("Agency FB bold", 25))
        title.grid(column=0, row=0, columnspan=3, pady=5)

        self.drivetypel = ttk.Label(self)
        self.drivetypel.grid(column=1, row=1, pady=10, sticky="nsew")
        self.drivetypel.configure(anchor="center")
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        self.seldrive = tk.StringVar(self)
        self.seldrive.set(drives[0])
        self.drivetype.set('(' + getdrivetype(drives[0]) + ')')
        self.seldrivem = OptionMenu(self, self.seldrive, drives[0], *drives, command=self.updatedrivetype)
        self.seldrivem.grid(column=0, row=1, padx=10, pady=10, sticky="ew")

        self.updatedrivetype(drives[0])
        self.diskdisp = tk.StringVar(self)
        self.diskdisp.set("Gigabytes")
        diskdispoptions = ['Bytes', 'Kilobytes', 'Megabytes', 'Gigabytes', 'Terabytes']
        self.seldiskdisp = OptionMenu(self, self.diskdisp, 'Gigabytes', *diskdispoptions)
        self.seldiskdisp.grid(column=2, row=1, padx=10, pady=10, sticky="ew")

        separator = Separator(self, orient='horizontal')
        separator.grid(column=0, row=2, columnspan=3, sticky='ew')

        self.totalsize = tk.StringVar(self)
        self.usedspace = tk.StringVar(self)
        self.freespace = tk.StringVar(self)

        totalsizel = Label(self, textvariable=self.totalsize)
        totalsizel.grid(column=0, row=7, pady=10)
        usedspacet = Label(self, text="Used Space")
        usedspacet.grid(column=2, row=5, padx=10, pady=10)
        usedspacet.configure(anchor="center")
        freespacet = Label(self, text="Free Space")
        freespacet.grid(column=0, row=5, padx=10, pady=10)
        freespacet.configure(anchor="center")
        usedspacel = Label(self, textvariable=self.usedspace)
        usedspacel.grid(column=2, row=6, padx=10, pady=10)
        freespacel = Label(self, textvariable=self.freespace)
        freespacel.grid(column=0, row=6, padx=10, pady=10)

        self.monitorsel = tk.StringVar()
        self.monitorselm = OptionMenu(self, self.monitorsel, "Monitor", "Free Space", "Used Space", command=self.monitorseld)
        self.monitorselm.grid(column=1, row=5)
        
        self.disksize = Progressbar(self, orient='horizontal', length=100, mode='determinate')
        self.disksize.grid(column=1, row=7, columnspan=2, sticky="ew", padx=10)

        self.monitordisp = tk.StringVar()
        self.monitordisp.set('Waiting...')
        self.monitordispl = Label(self, textvariable=self.monitordisp, foreground='gray')
        self.monitordispl.grid(column=1, row=6)

    def updatedrivetype(self, selecteddrive):
        img = Image.open("icons\\drives-disks\\" + getdrivetype(selecteddrive) + ".ico")
        img = img.resize((25, 25), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        self.drivetypel.configure(image=img, justify=tk.CENTER)
        self.drivetypel.image = img
        
    def updatesizes(self):
        drivesizeinfo = getdrivesize(self.seldrive.get())
        self.totalsize.set(drivesizeinfo['total'][self.diskdisp.get()])
        self.usedspace.set(drivesizeinfo['used'][self.diskdisp.get()])
        self.freespace.set(drivesizeinfo['free'][self.diskdisp.get()])
        ufdd = shutil.disk_usage(self.seldrive.get())
        self.disksize['value'] = round(100*(ufdd[1] / ufdd[0]))
        nfper = round(100*(ufdd[1] / ufdd[0]), 2)
        per = "{:.2f}".format(nfper)
        self.totalsize.set(self.totalsize.get() + " (" + per + r"% used)")
        if not self.monitoring==0:
            diskdispconv = {
                'Bytes': 'B',
                'Kilobytes': "KB",
                'Megabytes': "MB",
                'Gigabytes': "GB",
                'Terabytes': "TB"
            }
            suffix = diskdispconv[self.diskdisp.get()]
            if self.monitoring==1:
                sub = re.compile(r'[^\d.]+')
                tempv = float(sub.sub('', self.freespace.get()))
                if round(tempv - self.monitorval, 2)>0:
                    self.monitordispl.configure(foreground='green')
                    prefix = "+"
                elif round(tempv - self.monitorval, 2)<0:
                    self.monitordispl.configure(foreground='red')
                    prefix = "-"
                else:
                    self.monitordispl.configure(foreground='black')
                    prefix = ""
                self.monitordisp.set(prefix + "{:.2f}".format(round(tempv - self.monitorval, 2)) + suffix)
            elif self.monitoring==2:
                sub = re.compile(r'[^\d.]+')
                tempv = float(sub.sub('', self.usedspace.get()))
                if round(tempv - self.monitorval, 2)>0:
                    self.monitordispl.configure(foreground='green')
                    prefix = "+"
                elif round(tempv - self.monitorval, 2)<0:
                    self.monitordispl.configure(foreground='red')
                    prefix = "-"
                else:
                    self.monitordispl.configure(foreground='black')
                    prefix = ""
                self.monitordisp.set(prefix + "{:.2f}".format(round(tempv - self.monitorval, 2)) + suffix)
    
    def monitorseld(self, sel):
        self.monitorsel.set('Monitoring...')
        self.monitorselm.set_menu(None, "Stop")
        self.seldrivem.configure(state='disabled')
        self.seldiskdisp.configure(state='disabled')
        if sel=="Stop":
            self.monitoring=0
            self.monitorval=None
            self.monitorsel.set('Monitor')
            self.monitorselm.set_menu(None, "Free Space", "Used Space")
            self.seldrivem.configure(state='normal')
            self.seldiskdisp.configure(state='normal')
            self.monitordispl.configure(foreground='gray')
            self.monitordisp.set('Waiting...')
        else:
            print(sel)
            if sel=="Free Space":
                self.monitoring=1
                sub = re.compile(r'[^\d.]+')
                self.monitorval=float(sub.sub('', self.freespace.get()))
            else:
                self.monitoring=2
                sub = re.compile(r'[^\d.]+')
                self.monitorval=float(sub.sub('', self.usedspace.get()))

if __name__ == "__main__":
    app = App()
    def update():
        app.updatesizes()
        app.after(50, update)
    update()
    app.mainloop()