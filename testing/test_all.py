from os import listdir
import pytest
from scraper import Scraper
from filemanager import FileManager

def test_all():
	input_filenames = listdir(path='./testing/inputs')
	scraper = Scraper()
	filemanager = FileManager()
	for input_filename in input_filenames:
		input_data = filemanager.read_input_file( \
					'testing/inputs/' + input_filename)
		scraper_data = []
		for word in input_data[0]:
			scraper_data.append(scraper.scrape_word(word))
		for sentence_tuple in input_data[1]:
			scraper_data.append(scraper.scrape_sentence( \
						sentence_tuple[0]))
		output_data = []
		output_filename = 'output' + input_filename[5:]
		output_data = filemanager.read_output_file( \
					'testing/outputs/' + output_filename)
		for data in output_data:
			if '#####' in  data[1]:
				audio_bytes = b''
			else:
				audio_bytes = filemanager.read_audio_file('testing/audio/' + data[2] + '.mp3')
			data[1] = audio_bytes
		for i in range(len(scraper_data)):
			for j in range(4):
				if scraper_data[i][j] != output_data[i][j]:
					print()
					print(scraper_data[i][2])
					print()
				assert scraper_data[i][j] == output_data[i][j]

