import random
import threading
import time

class TwoTriesGuess(object):

	def __init__(self, oracle, prefix, letter, complement):
		""" Create Guess object.
		`prefix` is a known prefix to prepend with the guessed letter.
		`letter` is the new guessed letter.
		`complement` the alphabet complement to use for detecting false-positives.
		"""
		self.oracle = oracle
		self.prefix = prefix
		self.letter = letter
		self.complement = complement

		self.good_length = None # length of the presumed good guess
		self.bad_length = None # length of the presumed bad guess

		return

	def __len__(self):
		return self.good_length

	def __str__(self):
		return self.prefix+self.letter

	def __repr__(self):
		return '%s(%s+%s->%s)' % (self.__class__.__name__, repr(self.prefix), repr(self.letter), 'unknown length' if self.good_length is None else '%u,%u' % (self.good_length, self.bad_length))

	def keep(self):
		""" return True if this guess resulted in a false positive. """
		return self.good_length < self.bad_length

	def run(self):
		""" implement the logic behind determining the length of this guess """

		# run it!
		self.good_length = self.oracle.oracle(self.prefix+self.letter+self.complement)
		self.bad_length = self.oracle.oracle(self.prefix+self.complement+self.letter)

		return

class CompressionOracleRunner(threading.Thread):

	def __init__(self, guess):
		threading.Thread.__init__(self)
		self.guess = guess
		return

	def run(self):
		return self.guess.run()

class CompressionOracle(object):

	def __init__(self, seed, alphabet, max_threads=1):
		assert max_threads>0, 'max_threads cannot be <= 0'
		self.seed = seed
		self.max_threads = max_threads
		self.alphabet = alphabet

		self.__tries = []
		self.__complement_size = 10

		self.retreived_guesses = None
		return

	def oracle(self):
		""" Must be overriden by subclasses and implement the logic to query the compression oracle. """
		raise NotImplemented('oracle() must be overriden')

	def prepare(self):
		""" May be overriden by subclasses and make any initialization before running the attack. """
		return
	
	def cleanup(self):
		""" May be overriden by subclasses and cleanup any ressources after running the attack. """
		return

	def __prepare_complement(self):
		""" Prepare an alphabet complement for the Two-Tries method. """
		possible_complement = bytearray([chr(i) for i in range(256)])
		possible_complement.translate(possible_complement, self.alphabet)
		if len(possible_complement) != 0:
			return bytearray(random.sample(possible_complement, self.__complement_size))

		return [chr(random.randint(0, 0xff)) for _ in range(self.__complement_size)]

	def __run_all(self, guesses):

		threads = []
		queue = guesses[:]

		while len(queue) > 0:
			# start as many threads as permitted
			for i in range(self.max_threads-len(threads)):
				g = queue.pop(0)

				t = CompressionOracleRunner(g)
				t.start()
				threads.append(t)

				if len(queue) == 0:
					break
			print 'currently %u threads' % (len(threads), )
			# wait for some threads to finish
			while True:
				threads = [t for t in threads if t.is_alive()]
				if len(threads) < self.max_threads:
					break
				time.sleep(0.1)
		# wait for remaining threads to finish
		while len(threads) > 0:
			threads = [t for t in threads if t.is_alive()]

		kept = [g for g in guesses if g.keep()]
		return kept

	def run(self):
		""" run the attack against the comression oracle. """

		complement = self.__prepare_complement()
		guesses = [self.seed]

		self.prepare()

		round = 0
		while True:

			# append each letter in the keyspace to our current tries.
			oldguesses, guesses = guesses, []
			for guess in oldguesses:
				for letter in self.alphabet:
					guesses.append(TwoTriesGuess(self, str(guess), letter, complement))

			starttime = time.time()

			# testing phase
			kept = self.__run_all(guesses)

			print 'in round %u, ran all %u guesses in %u seconds' % (round, len(guesses), time.time()-starttime)

			print repr(kept)
			if len(kept) == 0:
				print "couldn't guess the next letter after %s" % (repr([str(g) for g in oldguesses]), )
				break

			_min = min([len(g) for g in kept])
			print 'keeping guesses with minimal length: %u' % (_min, )

			# switch over the new guesses
			guesses = [g for g in kept if len(g) == _min]
			print 'after round #%u, kept: %s' % (round, repr(guesses))

			round += 1

		self.retreived_guesses = guesses
		self.cleanup()

		return guesses

