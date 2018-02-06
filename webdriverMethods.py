from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import re
import os

class browser_window:
	def __init__(self):
		self.browser = webdriver.Chrome(executable_path=os.path.dirname(os.path.realpath(__file__))+"\chromedriver.exe")
		self.browser.set_window_position(0, 0)
		self.browser.set_window_size(0, 0)
		self.browser.get('http://albert.nyu.edu/albert_index.html')
		WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.textBox")))
		self.browser.find_element_by_xpath("//*[contains(text(), 'Public Course Search')]").click()

	def return_term_names(self):
		WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, "win0divNYU_CLS_WRK_")))
		term_names = [term.text for term in self.browser.find_element_by_id("win0divNYU_CLS_WRK_TERMS_LBL").find_elements_by_tag_name('label')]
		return term_names

	def select_term(self, term_name):
		#check that all checkboxes are empty
		checkbox_list = self.browser.find_elements_by_xpath("//input[@type='checkbox']")
		i = 0
		while i < len(checkbox_list):
			if checkbox_list[i].is_selected():
				checkbox_list[i].click()
				WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='WAIT_win0'][contains(@style, 'display: none')]")));
				i = 0
				checkbox_list = self.browser.find_elements_by_xpath("//input[@type='checkbox']")
			else:
				i = i+1

		name = "'"+term_name+"'"
		self.browser.find_element_by_xpath("//*[contains(text(), "+name+")]").click()
		WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='WAIT_win0'][contains(@style, 'display: none')]")));

	def return_school_names(self):
		list_of_school_ids = re.findall(r"win0divNYU_CLS_GRP_VW_DESCR254GP\$\d+", self.browser.find_element_by_id("ACE_GROUP$0").get_attribute("innerHTML"))
		school_names = []
		for _id in list_of_school_ids:
			school_names.append(self.browser.find_element_by_id(_id).text.replace('\n', ' ').strip())
		return school_names

	def select_school(self, school_name):
		selection = Select(self.browser.find_element_by_id('NYU_CLS_WRK2_DESCR254$33$'))
		selection.select_by_visible_text(school_name)
		WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='WAIT_win0'][contains(@style, 'display: none')]")));

	def return_class_names(self):
		class_links = self.browser.find_element_by_id('ACE_GROUP$0').find_elements_by_tag_name("a")
		class_names = []
		for link in class_links:
			class_names.append(link.text)
		return class_names[1:]

	def select_class(self, class_name):
		print('chosen class: ', class_name)
		try:
			for _class in self.browser.find_elements_by_xpath("//a[@ptlinktgt='pt_peoplecode']"):
				if _class.text == class_name:
					print('found match!')
					_class.click()
					WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='WAIT_win0'][contains(@style, 'display: none')]")));
					break;	#break out after selecting the class
		except:
			print('Unable to find class')
			pass

	def return_session_names(self):
		WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, "ACE_$ICField3$0")))
		list_of_class_block_ids = re.findall(r"ACE_NYU_CLS_SBDTLVW_CRSE_ID\$\d+", self.browser.find_element_by_id("ACE_$ICField3$0").get_attribute("innerHTML"))
		class_names = []
		for block_id in list_of_class_block_ids:
			class_block = self.browser.find_element_by_id(block_id)
			try:
				class_names.append(class_block.find_element_by_tag_name("b").text)
			except:
				pass
		return class_names

	def return_session_info(self, arrow_link):
		arrow_name = arrow_link.get_attribute("id")
		arrow_link.click()
		WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='WAIT_win0'][contains(@style, 'display: none')]")))
		all_class_info_elements = self.browser.find_elements_by_xpath("//td[@style='background-color: white; font-family: arial; font-size: 12px;']")
		for class_info_element in all_class_info_elements:
			block = class_info_element.get_attribute("innerHTML")
			status = re.search(r'<span style="color: \w+; font-weight: bold;">([a-zA-Z\s\(\)0-9]+)</span>', block).group(1)
			if status is not "Open":
				print('this class is closed')
				continue
			print('class name:\t', re.search(r'<b>([a-zA-Z0-9\s-]+)</b>', block).group(1))
			print('# credits:\t', re.search(r'</b> \| (\d*)', block).group(1))
			print('class #:\t', re.search(r'Class#\:</span> (\d+) \|', block).group(1))
			print('class section:\t', re.search(r'Section:</span>\s([a-zA-Z0-9]+)', block).group(1))
			print(status)
			print('class location:\t', re.search(r'Course Location: </b></span>([a-zA-z\s]+)', block).group(1))
			print('component:\t', re.search(r'Component\: </b>(\w+)', block).group(1))
				
			sessions = re.findall(r'<br>(\d\d/\d\d/\d\d\d\d - \d\d/\d\d/\d\d\d\d)', block)
			weekdays = re.findall(r'/\d\d\d\d ([\w,]+) \d', block)
			class_time = re.findall(r'[a-z] (.*) at', block)
			class_room = re.findall(r'at(.*)with', block)                     
			professor = re.findall(r"with ([a-zA-Z\s,;']+)", block)
	
			#check if no weekday dates or time or room are given
			for i in range(len(sessions)):
				print('\tclass session date: ', sessions[i])
				if len(weekdays)!=0:
					print('\tclass weekday: ', weekdays[i])
				if len(class_time)!=0:
					print('\tclass time: ', class_time[i])
				if len(class_room)!=0:
					print('\tclass room: ', class_room[i])
				if len(professor)!=0:
					print('\tprofessor: ', professor[i])
		self.browser.find_element_by_id(arrow_name).click()
		WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='WAIT_win0'][contains(@style, 'display: none')]")))

	def return_to_home_screen(self):
		try:
			self.browser.find_element_by_id('NYU_CLS_DERIVED_BACK').click()
			WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='WAIT_win0'][contains(@style, 'display: none')]")));
		except:
			print('already on hoem screen')
			pass
'''
t = browser_window()
#print(t.return_term_names())
#print('####')
#print(t.return_school_names())
t.select_school('College of Arts and Science')
print(t.return_class_names()[2])
print('###')
print(t.browser.find_element_by_id('LINK1$2').text)
'''
