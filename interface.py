import tkinter as tk
from tkinter import font as tkfont
from webdriverMethods import browser_window

#TODO: include the link to the post that explains how the class structure of tkinter works
#make text bigger if the screen is big enough

class window(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)

		#tk.Tk.iconbitmap(self, default='scroll.ico')

		self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold")
		container_of_frames = tk.Frame(self)
		container_of_frames.pack(side='top', fill='both', expand=True)
		container_of_frames.grid_rowconfigure(0, weight=1)
		container_of_frames.grid_columnconfigure(0, weight=1)

		self.all_selected_sessions = []

		self.frames = {}
		self.frames['StartPage'] = StartPage(parent=container_of_frames, controller=self)
		self.frames['ChooseClass'] = ChooseClass(parent=container_of_frames, controller=self)
		self.frames['ChooseOption'] = ChooseOption(parent=container_of_frames, controller=self)
		self.frames['StartPage'].grid(row=0, column=0, sticky="nsew")
		self.frames['ChooseClass'].grid(row=0, column=0, sticky="nsew")
		self.frames['ChooseOption'].grid(row=0, column=0, sticky="nsew")

		self.show_frame('StartPage')

	def show_frame(self, page_name):
		frame = self.frames[page_name]
		frame.tkraise()

	def get_frame(self, page_name):
		return self.frames[page_name]

class StartPage(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller

		header = tk.Label(self, text='Welcome to Schedule Creator', font=controller.title_font)
		header.pack(side='top', fill='x', pady=10)
		explanation = tk.Label(self, text='Please ignore the web browser which will pop up. It will be used along with the program, but you will not need to use it.', font=controller.title_font)
		explanation.pack(side='top', fill='x', pady=10)
		startbutton = tk.Button(self, text='Start', command=lambda:self.controller.show_frame('ChooseClass'))
		startbutton.pack()

class ChooseClass(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		self.browser = browser_window()

		term_names = self.browser.return_term_names()
		school_names = self.browser.return_school_names()

		term_box = tk.Listbox(self, listvariable=tk.StringVar(value=term_names), exportselection=0)
		school_box = tk.Listbox(self, listvariable=tk.StringVar(value=school_names), exportselection=0)
		class_box = tk.Listbox(self, exportselection=0, listvariable=tk.StringVar([]))
		session_box = tk.Listbox(self, exportselection=0, listvariable=tk.StringVar([]))
		add_button = tk.Button(self, text='Add selected class')
		selected_box = tk.Listbox(self, listvariable=tk.StringVar(value=self.controller.all_selected_sessions), exportselection=0)
		remove_button = tk.Button(self, text='Remove selected class')
		next_button = tk.Button(self, text='Next', command=lambda:self.controller.show_frame('ChooseOption'))

		term_label = tk.Label(self, text='Term')
		school_label = tk.Label(self, text='School')
		class_label = tk.Label(self, text='Class')
		session_label = tk.Label(self, text='Session')
		selected_label = tk.Label(self, text='Selected classes')

		term_label.grid(row=1, column=1, columnspan=2)
		term_box.grid(row=2, column=1, rowspan=2, columnspan=2, padx=5, sticky='nsew')
		school_label.grid(row=1, column=3, columnspan=2)
		school_box.grid(row=2, column=3, rowspan=2, columnspan=2, padx=5, sticky='nsew')
		class_label.grid(row=1, column=5, columnspan=2)
		class_box.grid(row=2, column=5, rowspan=2, columnspan=2, padx=5, sticky='nsew')
		session_label.grid(row=1, column=7, columnspan=2)
		session_box.grid(row=2, column=7, rowspan=2, columnspan=2, padx=5, sticky='nsew')
		add_button.grid(row=3, column=9, columnspan=2, sticky='ws')
		selected_label.grid(row=5, column=2, columnspan=7, pady=10)
		selected_box.grid(row=6, column=2, rowspan=2, columnspan=7, sticky='nsew')
		remove_button.grid(row=7, column=9, columnspan=2, sticky='ws')
		next_button.grid(row=8, column=4, columnspan=2, pady=10)

		for i in range(10):
			self.rowconfigure(i, weight=1)
		for i in range(11):
			self.columnconfigure(i, weight=1)

		term_box.bind('<<ListboxSelect>>', lambda event: self.select_term(event, term_box))
		school_box.bind('<<ListboxSelect>>', lambda event: self.select_school(event, class_box, school_box, session_box))
		class_box.bind('<<ListboxSelect>>', lambda event: self.select_class(event, class_box, session_box))
		add_button.bind('<Button-1>', lambda event: self.add_session(event, selected_box, session_box))
		remove_button.bind('<Button-1>', lambda event: self.remove_session(event, selected_box))

	def select_term(self, event, term_box):
		self.browser.select_term(term_box.get(term_box.curselection()))

	def select_school(self, event, class_box, school_box, session_box):
		self.browser.return_to_home_screen() #make sure you are back on the home page before selecting a new school
		self.browser.select_school(school_box.get(school_box.curselection()))
		class_box.delete(0, tk.END) #clear the class box
		session_box.delete(0, tk.END) #clear the session box
		self.populate_class(class_box)

	def populate_class(self, class_box):
		for _class in self.browser.return_class_names():
			class_box.insert(tk.END, _class)
		
	def select_class(self, event, class_box, session_box):
		if len(class_box.curselection()) != 0:
			try:
				self.browser.return_to_home_screen()
				self.browser.select_class(class_box.get(class_box.curselection()))
				session_box.delete(0, tk.END) #clear the session box
				self.populate_session(session_box)
			except:
				print('error occured in select_class')
				pass

	def populate_session(self, session_box):
		for _session in self.browser.return_session_names():
			session_box.insert(tk.END, _session)

	def add_session(self, event, selected_box, session_box):
		#check to avoid adding duplicate sessions.
		def not_yet_added(selected_box, session_box):
			for entry in selected_box.get(0, tk.END):
				if entry == session_box.get(session_box.curselection()):
					print('session is already selected. not adding duplicate')
					return False
			return True
	
		if len(session_box.curselection()) != 0:
			if (not_yet_added(selected_box, session_box)):
				selected_box.insert(tk.END, session_box.get(session_box.curselection()))

	def remove_session(self, event, selected_box):
		if len(selected_box.curselection()) != 0:
			selected_box.delete(selected_box.curselection()[0])
			#if the selected box is not empty afterwards deleting, highlight the last one. 
			if len(selected_box.curselection()) != 0:
				#selected_box.selection_set(selected_box.get(0))
				selected_box.activate(0)
				selected_box.focus_set()

class ChooseOption(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		
		header = tk.Label(self, text='To be implemented later...', font=controller.title_font)
		header.pack(side='top', fill='x', pady=10)
		
		#nextbutton = tk.Button(self, text='Next', command=lambda:controller.show_frame('LoadingPage'))
		#nextbutton.pack()
		backbutton = tk.Button(self, text='Back', command=lambda:controller.show_frame('ChooseClass'))

'''
class LoadingPage(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller

		header = tk.Label(self, text='To be implemented later...', font=controller.title_font)
		header.pack(side='top', fill='x', pady=10)

		nextbutton = tk.Button(self, text='Next', command=lambda: self.controller.show_frame('ShowResult'))
		nextbutton.pack()

class ShowResult(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller

		header = tk.Label(self, text='to be implemented later...', font=controller.title_font)
		header.pack(side='top', fill='x', pady=10)

		quitbutton = tk.Button(self, text='Quit', command=lambda: self.controller.destroy())
		quitbutton.pack()
'''

test = window()
test.mainloop()
input('Press ENTER to exit')