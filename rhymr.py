import json, urllib2, re, string, random, sys, nltk
from bs4 import BeautifulSoup
from nltk.corpus import cmudict

username = sys.argv[1] #script takes a tumblr username as its only argument
clean_posts = [] #list of tumblr text posts, with html removed, etc.
lines = [] #list of ten-syllable lines derived from tumblr text posts
rhymes = [] #list of rhyming couplets
discards = [] #list of lines that have already been used in rhymes
transcr = cmudict.dict() #carnegie mellon university's pronunciation dictionary
space = " "
WORD_RE = re.compile(r"\b[\w']+\b")

#1. get user's text posts and remove html tags, replace smart quotes, remove URLs
tumblr_key = ""
offsets = ["0", "20", "40", "60", "80"]

for offset in offsets:
	response = urllib2.urlopen("http://api.tumblr.com/v2/blog/" + username + ".tumblr.com/posts/text?api_key=" + tumblr_key + "&offset=" + offset)
	json_data = response.read()
	json_data = json.loads(json_data)

	posts = []

	for item in json_data['response']['posts']:
		if not 'reblog' in item:
			posts.append(item['body'])

	for post in posts:
		post = BeautifulSoup(post)
		for quote in post.findAll('blockquote'):
			quote.replaceWith("")
		post = post.get_text(separator=" ")
		post = post.replace(u"\u2018", "\'").replace(u"\u2019", "\'")
		post = post.replace(u"\u201c", "\"").replace(u"\u201d", "\"")
		post = re.sub('http\S*', "", post)
		post = re.sub('www\S*', "", post)
		clean_posts.append(post)

#cuts a list into two lists; the first is roughly ten syllables, the second is what remains
#returns false if the given list is less than ten syllables long
def chop(list_of_words):
	syllables = 0
	first = []
	second = []
	for word in list_of_words:
		lowercase_word = word.lower()
		if syllables >= 10:
			second.append(word)
		elif lowercase_word in transcr:
			phonemes = transcr[lowercase_word][0]
			for phoneme in phonemes:
				if phoneme[-1].isdigit():
					syllables += 1
			first.append(word)
		else:
			first.append(word)
			syllables += 2
	if syllables < 10:
		return False
	else:
		return (first, second)

#2. get a list of ten-syllable lines, derived from the tumblr posts
for item in clean_posts:
	words = string.split(item)
	while len(words) > 2:
		chopped_words = chop(words)
		if chopped_words:
			line = chopped_words[0]
			line = space.join(line)
			lines.append(line)
			words = chopped_words[1]
		else:
			break
random.shuffle(lines)

#takes a string, returns the last word of that string
#returns false if there are no words in the string
def get_last_word(line):
	words = WORD_RE.findall(line)
	if len(words) < 1:
		return False
	else:
		return words[-1]

#takes two words, tells whether they rhyme
def rhyming_words(a, b):
	a = a.lower()
	b = b.lower()
	if a in transcr and b in transcr:
		a_btntr = get_btntr(a)
		b_btntr = get_btntr(b)
		if a_btntr and b_btntr:
			if a_btntr[1] == b_btntr[1] and a_btntr[0] != b_btntr[0]:
				return True
	return False

#helper function for rhyming_words
def get_btntr(word):
	if word in transcr:
		phonemes = enumerate(transcr[word][0])
		accented = False
		accented2 = -1
		btntr = ""
		btsr = []
		for i, phoneme in phonemes:
			if phoneme[-1] == "1":
				accented = i
		if accented is not False:
			phonemes = transcr[word][0]
			following = phonemes[accented:]
			for phoneme in following:
				if not phoneme[-1].isdigit():
					btntr += phoneme
				else:
					btntr += phoneme[:-1]
			if accented != 0:
				preceding = phonemes[:accented]
				for i, phoneme in enumerate(preceding):
					if phoneme[-1].isdigit():
						accented2 = i
				preceding = phonemes[accented2+1:accented]
				for phoneme in preceding:
					if not phoneme[-1].isdigit():
						btsr.append(phoneme)
					else:
						btsr.append(phoneme[:-1])
			return (btsr, btntr)
	return False

#takes a line and a list of lines
#returns the given line as well as a rhyming line
#returns false if no rhyming lines can be found
def get_couplet(line, lines):
	word = get_last_word(line)
	if word and len(word) >= 4:
		for item in lines:
			if item not in discards:
				last_word = get_last_word(item)
				if last_word:
					if rhyming_words(word, last_word):
						return [line, item]
	return False

#3. find rhyming couplets and append to rhymes
for line in lines:
	if line not in discards:
		couplet = get_couplet(line, lines)
		if couplet:
			rhymes.append(couplet)
			discards.append(couplet[0])
			discards.append(couplet[1])
	if len(rhymes) > 7:
		break

#4. print output
print "~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~"
num = len(rhymes)
if num == 0:
	print "Sorry, no rhymes were found SADFACE"
elif num < 7:
	print "You didn't have enough rhymes for a sonnet, but here's a couplet:\n"
	index = random.randint(0, num - 1)
	print rhymes[index][0]
	print rhymes[index][1]
else:
	print rhymes[0][0]
	print rhymes[1][0]
	print rhymes[0][1]
	print rhymes[1][1] + "\n"
	print rhymes[2][0]
	print rhymes[3][0]
	print rhymes[2][1]
	print rhymes[3][1] + "\n"
	print rhymes[4][0]
	print rhymes[5][0]
	print rhymes[4][1]
	print rhymes[5][1] + "\n"
	print rhymes[6][0]
	print rhymes[6][1]
print "~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~"
