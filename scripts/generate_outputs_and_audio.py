import sys
from scraper import Scraper
from filemanager import FileManager

def main():
	input_filename = sys.argv[1]
	output_filename = 'output' + input_filename[5:]
	filemanager = FileManager()
	input_data = filemanager.read_input_file('testing/inputs/' + input_filename)
	scraper = Scraper()
	scraper_data = []
	for word in input_data[0]:
		scraper_data.append(scraper.scrape_word(word))
	for sentence_tuple in input_data[1]:
		scraper_data.append(scraper.scrape_sentence( \
					sentence_tuple[0], sentence_tuple[1]))
	for data in scraper_data:
		if data[1]:
			audio_filename = 'testing/audio/' + data[2][:30] + '.mp3'
			filemanager.write_audio_file(audio_filename, data[1])
	filemanager.write_output_file('testing/outputs/' + output_filename, scraper_data)

if __name__ == '__main__':
	main()
