""""
This class represents an individual equity request.  The constructor takes in a single string to perform the parsing, 
and contains all necessary information for the equity program to perform an equity analysis, as well as the 
method to do so.
"""
from os import system

class EquityQuery:
	command_str = "holdem-eval/holdem-val"

	#Various error strings; INVALID_OPTION, RANGE_UNDERFLOW, and RANGE_OVERFLOW are detected before running 
	#the equity analysis; INVALID_RANGE and RANGE_CONFLICT AFTER
	error_prefix = "Error: "
	INVALID_OPTION = error_prefix + "cannot parse option: viable options are \"board\" (or \'b\') and \"dead\" (or \'d\')"
	INVALID_RANGE = error_prefix + "invalid range" #TODO: add ability to check which range was invalid (multiple queries?)
	RANGE_UNDERFLOW = error_prefix + "need at least 2 ranges to run analysis"
	RANGE_OVERFLOW = error_prefix + "can only process up to 6 ranges"
	RANGE_CONFLICT = error_prefix + "range conflict: 2 ranges (or board/dead cards) contain the same card"
	

	#The constructor takes in a string (pre-pruned/parsed, i.e. the whole string is relevant and no part is irrelevant)
	def __init__(self, input_substring):
		self.ranges = []
		self.opts = []
		self.processed = False
		self.reply = self.prog_output = "" #only the reply to the individual query, not the whole comment/post
		self.monte_carlo = False

		#go word by word through the input string; anything with a colon in it is interpreted as an option.
		#aAll other words are interpreted as ranges.
		for word in input_substring.lower().split():
			if len(word) == 0 or "u/" in word.lower():
				continue #skip potential username pings
			elif ':' in word:
				word_split = word.split(':')
				if len(word_split) >= 2:
					pre_colon, post_colon = word_split[0], word_split[1]
				
				#we immediately stop when encountering an invalid option
				if len(word_split) != 2 or pre_colon not in ('b', 'd', "board", "dead"):
					self.reply = INVALID_OPTION
					break

				self.opts.append(("-b " if pre_colon in ('b', "board") else "-d ") + word)
			else:
				self.ranges.append(word)

		#self.reply is instantiated to a non-empty string, so that when process() is called it immediately quits
		#Also note that build_reply is unnecessary if this occurs
		if len(ranges) <= 1: self.reply = RANGE_UNDERFLOW
		elif len(ranges) > 6: self.reply = RANGE_OVERFLOW

		if len(self.reply) > 0:
			self.processed = True

	#Method to actually run the equity analysis.  Called once per object
	def process(self):
		if self.processed: return

		command = [command_str]
		if self.monte_carlo:
			command += [" --mc -t 5"]
		else:
			command += [" -t 3"]

		for o in self.opts:
			command += [" ", o]
		for r in self.ranges:
			command += [" ", r]

		command.append([" 1>o.txt 2>e.txt"])

		exit_status = os.system("".join(command))
		if exit_status > 0:
			self.reply = RANGE_CONFLICT if exit_status == 8 else INVALID_RANGE
			return

		with open("o.txt", 'r') as out:
			self.prog_output = out.read()

		if "--mc" in prog_output:
			self.monte_carlo = True
			command[1] = " --mc -t 5"
			os.system("".join(command)) #would not produce an error not already seen
			with open("o.txt", 'r') as out:
				self.prog_output = out.read()

		self.processed = True
		self.build_reply()

	def build_reply(self):
		if len(self.reply) > 0: return
		if not self.processed: self.process()

		reply_words = ["Range|Equity\n:--|--:\n"]
		for player in self.prog_output.split("***")[1].strip().split('\n'):
			hand, equity = i.split(':')
			reply_words += [hand.strip(), '|', equity.strip(), '\n']

		if self.monte_carlo:
			reply_words += ["**Note:** Monte Carlo simulation used (original simulation exceeded 3 seconds)"]

		self.reply = "".join(reply_words)

"""
This class represents an individual comment which contains one or more requests for an equity analysis.
Requests must take one of the two following forms:

1. If enclosed curly braces are anywhere within the comment, the bot will assume that 
   the content enclosed within the braces are a query.  The rest of the comment will be ignored, and all of 
   the content within the braces is apart of the query.
2. Otherwise, the whole body of the post, minus any bot u/ mention, will count as the query.  
"""

class QueryCommentBody:
	#body is the content of the comment, message or post
	def __init__(self, body):
		self.queries = [] #may potentially be multiple queries per comment
		self.replies = [] #the reply to the whole comment/post

		brace_index = body.find('{')
		while brace_index != -1:
			stop_index = body.find('}', brace_index)
			if stop_index == -1: stop_index = len(body) #user forgot to close braces
			self.queries.append(EquityQuery(body[brace_index + 1:stop_index]))
			brace_index = body.find('{', stop_index)

		if len(self.queries) == 0:
			self.queries.append(EquityQuery(body)) #use whole comment

	def process(self):
		if len(self.reply) > 0: return

		for query in self.queries:
			query.process()
			self.replies.append(query.reply)

		self.reply = "\n***\n".join(self.replies)