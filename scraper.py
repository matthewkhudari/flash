import os

import json
import urllib
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Scraper:
	def __init__(self, headless=True, credentials=None):
		options = Options()
		if headless:
			options.add_argument('--headless')
			options.add_argument('--disable-gpu')
			options.add_argument('--no-sandbox')
		chrome_path = os.getenv('GOOGLE_CHROME_PATH')
		if chrome_path:
			options.binary_location = chrome_path
		chromedriver_path = os.getenv('CHROMEDRIVER_PATH')
		if chromedriver_path:
		    self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
		else:
		    self.driver=webdriver.Chrome(options=options)
		self._logged_in = False
		if credentials:
			self.chinesepod_username = credentials[0]
			self.chinesepod_password = credentials[1]
		else:
			credentials = get_chinesepod_credentials()
			self.chinesepod_username = credentials['username']
			self.chinesepod_password = credentials['password']

	def verify_chinesepod_credentials(self):
		self.goto_chinesepod_page('拿手菜')
		return len(self.driver.find_elements_by_link_text('Log In')) == 0


	def scrape_word(self, word):
		pinyin_and_translation = self.get_word_pinyin_and_translation(word)
		audio = self.get_word_audio(word)
		return (pinyin_and_translation[0], audio, word, pinyin_and_translation[1])

	def scrape_sentence(self, sentence):
		pinyin = self.get_google_pinyin(sentence)
		translation_and_audio = self.get_sentence_translation_and_audio( \
					sentence)
		return (pinyin, translation_and_audio[1], sentence, translation_and_audio[0])


	def get_google_pinyin(self, phrase):
		url = 'https://translate.google.com/#zh-CN/en/{}'.format(urllib.parse.quote(phrase))
		self.driver.get(url)
		CLASSNAME = 'tlid-transliteration-content transliteration-content full'
		elements = self.driver.find_elements_by_xpath('//div[@class="{}"]'.format(CLASSNAME))
		for element in elements:
			if not element.text:
				elements.remove(element)
		assert len(elements) == 1, 'expected 1 nonempty element but got {}'.format(len(elements))
		return elements[0].text

	def get_word_pinyin_and_translation(self, word):
		url = 'https://chinese.yabla.com/chinese-english-pinyin-dictionary' \
			+ '.php?define={}'.format(urllib.parse.quote(word))
		self.driver.get(url)

		# Find elements that match word
		all_elements = self.driver.find_elements_by_xpath('//ul[@id="search_results"]/li')
		matching_elements = []
		for element in all_elements:
			descendants = element.find_elements_by_xpath('./div[1]/span[1]/a')
			character_string = ''
			for descendant in descendants:
				character_string += descendant.text
			if character_string == word:
				matching_elements.append(element)

		# Construct translation and pinyin
		pinyin = ''
		translation = ''
		for element in matching_elements:
			if pinyin != '':
				pinyin += ' OR '
				translation += ' OR '
			pinyin += element.find_element_by_xpath('.//span[@class="pinyin"]').text
			translation += element.find_element_by_xpath('.//div[@class="meaning"]').text.replace('\n', ', ')
		return (pinyin, translation)

	def get_word_audio(self, word):
		self.goto_chinesepod_page(word)
		try:
			element = self.driver.find_element_by_xpath( \
						'//div[@id="myTable"]//a[text()="Download"]')
		except:
			return b''
		session = requests.Session()
		cookies = self.driver.get_cookies()
		for cookie in cookies:
			session.cookies.set(cookie['name'], cookie['value'])
		audio_bytes = session.get(element.get_attribute('href')).content
		return audio_bytes

	def get_sentence_translation_and_audio(self, sentence):
		self.goto_chinesepod_page(sentence)
		parent = self.find_sentence_element(sentence)
		element = parent.find_element_by_xpath('./td[1]')
		translation = element.text[element.text.rindex('\n') + 1:]
		element = parent.find_element_by_xpath('.//a[text()="Download"]')
		session = requests.Session()
		cookies = self.driver.get_cookies()
		for cookie in cookies:
			session.cookies.set(cookie['name'], cookie['value'])
		audio_bytes = session.get(element.get_attribute('href')).content
		return (translation, audio_bytes)

	def goto_chinesepod_page(self, word):
		if not self._logged_in:
			self.driver.get('https://chinesepod.com/accounts/signin')
			email_input = self.driver.find_element_by_id('email')
			password_input = self.driver.find_element_by_id('password')
			email_input.send_keys(self.chinesepod_username)
			password_input.send_keys(self.chinesepod_password)
			self.driver.find_element_by_xpath('//button[text()="Log In"]').click()
			self._logged_in = True
		url = 'https://chinesepod.com/tools/glossary/entry/{}'.format( \
					urllib.parse.quote(word))
		self.driver.get(url)

	def find_sentence_element(self, sentence):
		# Must be logged in to chinesepod and in correct page
		return self.driver.find_element_by_xpath( \
					'//table[@class="table table-striped table-grossary"]/tbody/tr')

def get_chinesepod_credentials():
	with open('chinesepod_credentials.json') as f:
		return json.load(f)
