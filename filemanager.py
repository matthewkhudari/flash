class FileManager:
	def write_output_file(self, filename, scraper_data):
		with open(filename, 'w+') as f:
			for data in scraper_data:
				if data[1]:
					audio_filename = data[2][:30] + '.mp3'
				else:
					audio_filename = '#####.mp3'
				f.write(data[0] + '\t' \
							+ '[sound:' + audio_filename  + ']\t' \
							+ data[2] + '\t' \
							+ data[3] + '\n')

	def write_audio_file(self, filename, audio_bytes):
		with open(filename, 'wb') as f:
			f.write(audio_bytes)
		
	def read_input_file(self, filename):
		with open(filename, 'r') as f:
			lines = f.readlines()
			words = [line[1:-1] for line in lines if line[0] == 'w']
			sentence_tuples = []
			for sentence in (line[1:-1] for line in lines if line[0] == 's'):
				for word in words:
					if word in sentence:
						sentence_tuples.append((sentence, word))
						break
				else:
					raise NoMatchingWordError( \
						'no matching word for sentence: "{}"'.format(sentence))
		return (words, sentence_tuples)
	
	def read_audio_file(self, filename):
		with open(filename, 'rb') as f:
			return f.read()
	
	def read_output_file(self, filename):
		output_data = []
		with open(filename, 'r') as f:
			lines = f.readlines()
			for line in lines:
				output_data.append(line[:-1].split('\t'))
		return output_data


			
class NoMatchingWordError(Exception):
	pass
