import pytest
from scraper import Scraper

def test_scraper_init():
	s = Scraper()

def test_get_google_pinyin():
	s = Scraper()
	pinyin = s.get_google_pinyin('朴实')
	assert pinyin == 'Pǔshí'

def test_get_word_pinyin_and_translation():
	s = Scraper()
	retval = s.get_word_pinyin_and_translation('比如')
	assert retval[0] == 'bǐ rú'
	assert retval[1] == 'for example, for instance, such as'

def test_get_word_audio():
	s = Scraper()
	audio_bytes = s.get_word_audio('比如')
	assert audio_bytes

def test_get_sentence_translation_and_audio():
	sentence = '他会说很多种语言，比如汉语，日语，德语。'
	word = '比如'
	s = Scraper()
	retval = s.get_sentence_translation_and_audio(sentence, word)
	assert retval[0] == \
		'He can speak many languages, such as Chinese, Japanese and German.'
	assert retval[1] # (is nonempty)

