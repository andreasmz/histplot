import os
import tkinter as tk
from tkinter import messagebox, filedialog, ttk, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
import configparser
import numpy as np
import math

class IntStringVar:
    def __init__(self, root, IntVar: tk.IntVar):
        self.IntVar = IntVar
        self.StringVar = tk.StringVar(root, value=self.IntVar.get())
        self.IntVar.trace_add("write", self._IntVarUpdate)
        self.StringVar.trace_add("write", self._StringVarUpdate)

    def _IntVarUpdate(self, val1, val2, val3):
        if (self.StringVar.get() != str(self.IntVar.get())):
            self.StringVar.set(str(int(self.IntVar.get())))
    
    def _StringVarUpdate(self, val1, val2, val3):
        if (self.StringVar.get() != str(self.IntVar.get())):
            if (self.StringVar.get().lstrip("-").isdigit()):
                self.IntVar.set(self.StringVar.get())


class GUI():
    _plotFigSize = (20,20)
    _exportFigSize = (6,4)
    def __init__(self):
        self.root = None
        self.data = None
        self.histData = None
        self.config = None

    def GUI(self):
        self.root = tk.Tk()
        self.root.iconbitmap(os.path.join(os.path.dirname(__file__), "histplot_icon.ico"))
        self.root.title("Histplot")
        self.root.geometry("600x600")
        self.root.protocol("WM_DELETE_WINDOW", self.On_closing)

        self.config = configparser.ConfigParser()
        self.config.read('histplot_settings.ini')
        if "SETTINGS" not in self.config.sections():
            self.config.add_section("SETTINGS")
        if not self.config.has_option("SETTINGS", "XAxisLabel"):
            self.config.set("SETTINGS", "XAxisLabel", "X Label")
        if not self.config.has_option("SETTINGS", "YAxisLabel"):
            self.config.set("SETTINGS", "YAxisLabel", "Y Label")
        if not self.config.has_option("SETTINGS", "TitleLabel"):
            self.config.set("SETTINGS", "TitleLabel", "Weighted Plot")
        if not self.config.has_option("SETTINGS", "AutoMinMax"):
            self.config.set("SETTINGS", "AutoMinMax", "1")
        if not self.config.has_option("SETTINGS", "ExportFigSizeWidth"):
            self.config.set("SETTINGS", "ExportFigSizeWidth", "4")
        if not self.config.has_option("SETTINGS", "ExportFigSizeHeight"):
            self.config.set("SETTINGS", "ExportFigSizeHeight", "3")

        GUI._exportFigSize = (int(self.config.get("SETTINGS", "ExportFigSizeWidth")), int(self.config.get("SETTINGS", "ExportFigSizeHeight")))

        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        self.menuFile = tk.Menu(self.menubar,tearoff=0)
        self.menubar.add_cascade(label="File",menu=self.menuFile)
        self.menuFile.add_command(label="Open File(s)", command=self.OpenFiles)
        self.menuFile.add_command(label="Open Folder", command=self.OpenFolder)
        self.menuOptions = tk.Menu(self.menubar,tearoff=0)
        self.menubar.add_cascade(label="Options",menu=self.menuOptions)
        self.checkAutoMinMaxVar = tk.IntVar(value=int(self.config.get("SETTINGS", "AutoMinMax")))
        self.menuOptions.add_checkbutton(label="Auto set min and max", variable=self.checkAutoMinMaxVar)
        self.menuOptions.add_command(label="Set standard figsize", command=self.DialogSetStandardFigsize)

        self.frameTools = tk.Frame(self.root)
        self.frameTools.pack(side=tk.LEFT, expand=True, fill="y")
        self.framePlot = tk.Frame(self.root)
        self.framePlot.pack(side=tk.LEFT, expand=True, fill="both")


        self.figure = plt.Figure(figsize=GUI._plotFigSize, dpi=100)
        self.figureExport = plt.Figure(figsize=GUI._exportFigSize, dpi=200)
        self.ax = self.figure.add_subplot() 
        self.axExport = self.figureExport.add_subplot() 
        self.canvas = FigureCanvasTkAgg(self.figure, self.framePlot)
        self.canvtoolbar = NavigationToolbar2Tk(self.canvas,self.framePlot)
        self.canvtoolbar.update()
        self.canvas.mpl_connect('resize_event', self._CanvasResize)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.draw()

        self.framePlotOptions = ttk.LabelFrame(self.frameTools, text="Plot Options")
        self.framePlotOptions.pack(anchor="nw", fill="x")
        tk.Grid.columnconfigure(self.framePlotOptions, 1, weight=1)
        tk.Label(self.framePlotOptions, text="Title").grid(row=0, column=0)
        tk.Label(self.framePlotOptions, text="X Axis Label").grid(row=1, column=0)
        tk.Label(self.framePlotOptions, text="Y Axis Label").grid(row=2, column=0)
        tk.Label(self.framePlotOptions, text="Bins").grid(row=3, column=0)
        tk.Label(self.framePlotOptions, text="Min").grid(row=4, column=0)
        tk.Label(self.framePlotOptions, text="Max").grid(row=5, column=0)
        tk.Label(self.framePlotOptions, text="Data column").grid(row=6, column=0)
        tk.Label(self.framePlotOptions, text="Weights").grid(row=7, column=0)
        self.txtTitleVar = tk.StringVar(value=self.config.get("SETTINGS", "TitleLabel"))
        self.txtXLabelVar = tk.StringVar(value=self.config.get("SETTINGS", "XAxisLabel"))
        self.txtYLabelVar = tk.StringVar(value=self.config.get("SETTINGS", "YAxisLabel"))
        self.txtTitleVar.trace_add("write", self._EntryUpdate)
        self.txtXLabelVar.trace_add("write", self._EntryUpdate)
        self.txtYLabelVar.trace_add("write", self._EntryUpdate)
        self.binsVar = IntStringVar(self.root, tk.IntVar(self.root, value=20))
        self.minVar = IntStringVar(self.root, tk.IntVar(self.root, value=0))
        self.maxVar = IntStringVar(self.root, tk.IntVar(self.root, value=1000))
        self.txtTitle = tk.Entry(self.framePlotOptions, textvariable=self.txtTitleVar)
        self.txtXLabel = tk.Entry(self.framePlotOptions, textvariable=self.txtXLabelVar)
        self.txtYLabel = tk.Entry(self.framePlotOptions, textvariable=self.txtYLabelVar)
        self.scaleIntBins = ttk.Scale(self.framePlotOptions, from_=1, to=100, variable=self.binsVar.IntVar,  command=self._WidgetUpdate)
        self.scaleIntMin = ttk.Scale(self.framePlotOptions, from_=0, to=5000, variable=self.minVar.IntVar,  command=self._WidgetUpdate)
        self.scaleIntMax = ttk.Scale(self.framePlotOptions, from_=0, to=5000, variable=self.maxVar.IntVar,  command=self._WidgetUpdate)
        self.numIntBins = tk.Spinbox(self.framePlotOptions, width=6, textvariable=self.binsVar.StringVar, from_=1, to=1000, command=self._SpinboxUpdate)
        self.numIntMin = tk.Spinbox(self.framePlotOptions, width=6, textvariable=self.minVar.StringVar, from_=-10000, to=10000, command=self._SpinboxUpdate)
        self.numIntMax = tk.Spinbox(self.framePlotOptions, width=6, textvariable=self.maxVar.StringVar, from_=-10000, to=10000, command=self._SpinboxUpdate)
        self.txtTitle.grid(row=0, column=1, columnspan=2, sticky="news")
        self.txtXLabel.grid(row=1, column=1, columnspan=2, sticky="news")
        self.txtYLabel.grid(row=2, column=1, columnspan=2, sticky="news")
        self.scaleIntBins.grid(row=3, column=1, sticky="news")
        self.scaleIntMin.grid(row=4, column=1, sticky="news")
        self.scaleIntMax.grid(row=5, column=1, sticky="news")
        self.numIntBins.grid(row=3, column=2)
        self.numIntMin.grid(row=4, column=2)
        self.numIntMax.grid(row=5, column=2)
        self.comboDataColumnVar = tk.StringVar() 
        self.comboDataColumnVar.trace_add("write", self.ComboColumnChanged)
        self.comboDataColumn = ttk.Combobox(self.framePlotOptions, textvariable = self.comboDataColumnVar, state="readonly")
        self.comboDataColumn.grid(row=6, column=1, columnspan=2, sticky="news") 
        self.comboWeightColumnVar = tk.StringVar() 
        self.comboWeightColumnVar.trace_add("write", self.ComboColumnChanged)
        self.comboWeightColumn = ttk.Combobox(self.framePlotOptions, textvariable = self.comboWeightColumnVar, state="readonly")
        self.comboWeightColumn.grid(row=7, column=1, columnspan=2, sticky="news") 

        self.frameFiles = ttk.LabelFrame(self.frameTools, text="Files")
        self.frameFiles.pack(anchor="nw", fill="x")
        self.listFiles = tk.Listbox(self.frameFiles)
        self.listFiles.pack(fill="x")

        self.frameExport = ttk.LabelFrame(self.frameTools, text="Export")
        self.frameExport.pack(anchor="nw", fill="x")
        self.frameExport1 = tk.Frame(self.frameExport)
        self.frameExport1.pack(anchor="nw")
        self.frameExport2 = tk.Frame(self.frameExport)
        self.frameExport2.pack(anchor="nw")
        self.btnExportCSV = tk.Button(self.frameExport1, text="Export Data (CSV)", command=self.ExportCSV)
        self.btnExportCSV.pack(side=tk.LEFT)
        self.btnExportFigure1 = tk.Button(self.frameExport1, text="Save figure as seen", command=self.SaveFigure)
        self.btnExportFigure1.pack(side=tk.LEFT)
        self.btnExportFigure2 = tk.Button(self.frameExport2, text="Save figure in standard size", command=self.SaveFigureFixed)
        self.btnExportFigure2.pack(side=tk.LEFT)

        self.root.mainloop()

    def On_closing(self):
        try:
            self.ConfigUpdate()
            with open('histplot_settings.ini', 'w') as configfile:
                self.config.write(configfile)
        except Exception as ex:
            print(str(ex))
            pass
        self.root.destroy()

    def OpenFiles(self):
        filepaths = filedialog.askopenfilename(parent=self.root, title="Swift Tools: Open csv files", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")), multiple=True)
        if filepaths is not None and filepaths != "" and len(filepaths) > 0:
            self.ReadData(filepaths)

    def OpenFolder(self):
        path = filedialog.askdirectory(parent=self.root, title="Swift Tools: Open csv files")
        if path is not None and path != "":
            files = [os.path.abspath(os.path.join(path, f)) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            if (len(files) > 0):
                self.ReadData(files)

    def ReadData(self, files):
        self.data = pd.DataFrame()
        self.listFiles.delete(0,tk.END)
        for file in files:
            try:
                _pd = pd.read_csv(file, sep=",", header=0)
            except Exception:
                continue
            _pd["file"] = os.path.basename(file)
            self.listFiles.insert(tk.END, os.path.basename(file))
            self.data = pd.concat([self.data, _pd], ignore_index=True)
        self.data = self.data.apply(pd.to_numeric, errors='coerce')
        self.comboDataColumn['values'] = [f"{x} ({self.data[x].count()})" for x in list(self.data.columns) if x != "file"]
        _weightsColumns = list([f"{x} ({self.data[x].count()})" for x in list(self.data.columns) if x != "file"])
        _weightsColumns.insert(0, "None ")
        self.comboWeightColumn['values'] = _weightsColumns
        if len(self.comboDataColumn["values"]) > 0:
            self.comboDataColumn.current(0)
        self.comboWeightColumn.current(0)
        self.ComboColumnChanged("", "", "")
        self.Update()

    def Update(self, updateExportFig=False):
        if updateExportFig:
            _ax = self.axExport
        else:
            _ax = self.ax
            self.histData = None
        _ax.clear()

        if self.data is None:
            self.canvas.draw()
            return
        _dataColumn = " ".join(self.comboDataColumnVar.get().split(" ")[:-1])
        _weightColumn = " ".join(self.comboWeightColumnVar.get().split(" ")[:-1])
        if _dataColumn not in self.data.columns or (_weightColumn not in self.data.columns and _weightColumn != "None"):
            self.canvas.draw()
            return
        _ax.set_title(self.txtTitleVar.get())
        _ax.set_ylabel(self.txtYLabelVar.get())
        _ax.set_xlabel(self.txtXLabelVar.get())
        range = (self.minVar.IntVar.get(), self.maxVar.IntVar.get())
        if range[0] > range[1]:
            range = (self.maxVar.IntVar.get(), self.minVar.IntVar.get())

        # plt.hist is Nan save as it is using np.histogram. Don't use df.dropna() as it will alter the shape messing of with the weights column
        _data = self.data[_dataColumn]
        _weights = None
        if _weightColumn != "None":
            _weights = self.data[_weightColumn].fillna(0) # If NaN weight column, set it to weight 0

        _histData = _ax.hist(_data, weights=_weights, bins=self.binsVar.IntVar.get(), range=range)
        if not updateExportFig:
            self.histData = _histData
            if self.framePlot.winfo_width() > 100:
                self.figure.tight_layout()
        else:
            self.figureExport.tight_layout()
        self.canvas.draw()

    def ExportCSV(self):
        if self.histData is None:
            self.root.bell()
            return
        _dataColumn = " ".join(self.comboDataColumnVar.get().split(" ")[:-1])
        _weightColumn = " ".join(self.comboWeightColumnVar.get().split(" ")[:-1])
        if _dataColumn not in self.data.columns or (_weightColumn not in self.data.columns and _weightColumn != "None"):
            self.root.bell()
            return
        save_file = filedialog.asksaveasfile(parent=self.root, mode="w", title="Save as csv", filetypes=[("Comma-separated values", "*.csv"), ("All files", "*.*")], defaultextension=".csv")
        if save_file is None:
            return
        save_file.write(f"'{_dataColumn}_left','{_dataColumn}_right','{_dataColumn} weighted by {_weightColumn}'\n")
        for i in range(len(self.histData[0])):
            save_file.write("%s,%s,%s\n" % (round(self.histData[1][i],3),round(self.histData[1][i+1],3), self.histData[0][i]))
        save_file.close()

    def SaveFigure(self, fixedSize=False):
        if self.histData is None:
            self.root.bell()
            return
        save_file = filedialog.asksaveasfile(parent=self.root, mode="w", title="Save as PNG", filetypes=[("PNG", "*.png"), ("All files", "*.*")], defaultextension=".png")
        if save_file is None:
            return
        _fname = save_file.name
        save_file.close()
        if fixedSize:
            self.Update(updateExportFig=True)
            self.figureExport.savefig(_fname, dpi=200)
        else:
            self.figure.savefig(_fname)

    def SaveFigureFixed(self):
        self.SaveFigure(fixedSize=True)

    def DialogSetStandardFigsize(self):
        _width = simpledialog.askinteger("HistPlot", "Width in inches (recommended: 6)", minvalue=1, maxvalue=20, initialvalue=self.config.get("SETTINGS", "ExportFigSizeWidth"))
        _height = simpledialog.askinteger("HistPlot", "Height in inches (recommended: 4)", minvalue=1, maxvalue=20, initialvalue=self.config.get("SETTINGS", "ExportFigSizeHeight"))
        if _width is None or _height is None:
            return
        GUI._exportFigSize = (_width, _height)
        self.figureExport.set_size_inches(GUI._exportFigSize)
        self.config.set("SETTINGS", "ExportFigSizeWidth", str(_width))
        self.config.set("SETTINGS", "ExportFigSizeHeight", str(_height))
        messagebox.showinfo("HistoPlot", f"Default plot size set to {_width}x{_height}")

    def ComboColumnChanged(self, val1, val2, val3):
        if self.data is None:
            self.Update()
            return
        if (self.checkAutoMinMaxVar.get() != 1):
            self.Update()
            return
        _dataColumn = " ".join(self.comboDataColumnVar.get().split(" ")[:-1])
        if _dataColumn not in self.data.columns:
            self.Update()
            return
        _min = np.min(self.data[_dataColumn])
        _max = np.max(self.data[_dataColumn])
        if math.isnan(_min) or math.isnan(_max):
            self.Update()
            return
        self.minVar.IntVar.set(np.min(self.data[_dataColumn]))
        self.maxVar.IntVar.set(np.max(self.data[_dataColumn]))
        self.Update()

    def _WidgetUpdate(self, val):
        self.Update()

    def _SpinboxUpdate(self):
        self.Update()

    def _EntryUpdate(self, val1, val2, val3):
        self.Update()

    def _CanvasResize(self, event):
        if self.framePlot.winfo_width() > 100:
            self.figure.tight_layout()
            self.canvas.draw()

    def ConfigUpdate(self):
        self.config.set("SETTINGS", "XAxisLabel", self.txtXLabelVar.get())
        self.config.set("SETTINGS", "YAxisLabel", self.txtYLabelVar.get())
        self.config.set("SETTINGS", "TitleLabel", self.txtTitleVar.get())
        self.config.set("SETTINGS", "AutoMinMax", str(self.checkAutoMinMaxVar.get()))