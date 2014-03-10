compression-oracle
==================

Python framework for extracting secret data from compression oracles such as those exploited by the BEAST and CRIME attacks.

What does it do?
----------------

This is a python class that facilitates the exploitation of compression oracles. This project was created after 
the final round of CSAW CTF 2013. One of the challenge presented during the event was a compression oracle, which 
would have required a lot less effort to complete if this kind of project had existed.

Features
--------
* Multi-thread support
* Implements the 'Two-Tries Method' for false-positive detection (described [here](http://breachattack.com/resources/BREACH%20-%20SSL,%20gone%20in%2030%20seconds.pdf)).
* Support automatic retry with different Two-Tries complements chosen at random outside of the charset.
* Support lookaheads of arbitrary length in case the Two-Tries method fails to produce viable candidates.

How does it work?
-----------------

To be exploitable, a compression oracle requires that we be able to inject an arbitrary value that will be compressed along with a secret 
information (which we want to retreive). The vulnerable system then must *leak* the length of compressed data. This leak constitutes the
side-channel on which the attack is based.

In the sample vulnerable server `samples/oracle1-vulnerable-server.py`, the vulnerability is introduced here:

```python
msg = zlib.compress('user_data=%s;secret=%s' % (data, secret))
```

The attacker-provided `data` is compressed together with `secret` that we want to retreive, and the length of the compressed data is returned to the attacker.

To exploit this vulnerable server, all you have to do is create a subclass of `CompressionOracle` and override the `CompressionOracle.oracle` method.

```python
class Client(CompressionOracle):
	def oracle(self, guess_data):
		# Return the length of `guess_data` after the vulnerable server has compressed it.
```

In the `oracle` method, you should place the logic of sending the `guess_data` to the vulnerable server and 
return the length of the compressed data. The `CompressionOracle` class will take care of everything else.

Now, to begin the attack:
```python
c = Client(seed='secret=')
c.run()
print repr(c.retreived_guesses)
```

You may provide a few arguments to the `CompressionOracle` constructor:
* `seed` (mandatory): A short string which you believe is contained in the compressed data. In the CRIME attack, this seed is the name of the cookie, because it always directly precedes the actual cookie data. The recovery is performed left-to-right, with the prefix being on the left and new guesses being added on the right.
* `alphabet`: The allowable charset of the secret information. This defaults to `string.printable`. It's a good idea to restrict the alphabet as much as possible, because it will cut down on attack time, but most importantly, the false-positive detection (Two-Tries Method) relies on characters from outside of the allowable alphabet to eliminate incorrect guesses.
* `max_threads`: The number of concurrent threads to start. Using more than one thread may cause problems if the server is keeping some kind of state that prevents multiple concurrent queries to be made. The number of threads running at once will never be greated than the size of the allowable alphabet.
* `complement_size`: In order to perform false-positive detection, two characters from outside the allowed alphabet will be chosen. These two characters, repeated `complement_size` times, will be used as complement. This value can be a integer, or a tuple `(min, max)`, in which case a random size between the `min` and `max` bounds (inclusive) will be chosen. 
* `retries`: The number of times the complement will be changed at random before giving up and trying a lookahead method.
* `lookaheads`: The length of the lookahead to perform. When all 1-letter guesses fail, then 2-letter guesses will be tried next, up to `lookaheads+1`-letter guesses. The default is 1, which puts the limit at 2-letter guesses. Set to 0 to disable lookahead.

You may also want to override the `CompressionOracle.prepare` and `CompressionOracle.cleanup` methods, which may be used to allocate any ressource you may need (for example, you 
may wish to retreive some kind of session token from a web server). The `prepare()` method is called just after entering the `run()` method but before any call to `oracle()`. 
The `cleanup()` method is called after all calls to `oracle()` just before the `run()` method returns.

You may override the `prepare_complement()` method in order to implement your own algorithm to choose a complement. This method is called each time no candidate can be found.

Two-Tries and Lookahead
-----------------------

Let's look at an example run of the program to better explain the relation between Two-Tries method and Lookahead and what these two mechanism do for you.

Let's start setting up the context for this example. You start your program with the following arguments:
```
Client(seed='FLAG=', alphabet='abcdef0123456789', complement_size=[1,5], retries=5, lookaheads=1)
```
Lets see what they mean:
`seed`: means the string `FLAG=` directly precedes the secret you want to recover.
`alphabet`: means only hexadecimal characters (`abcdef0123456789`) can be part of the secret. If the secret contains any other characters, recovery will most likely fail.
`complement_size`: means each time a complement has to be chosen, a random number `n` between 1 to 5 will be chosen, as well as two random characters which will be repeated `n` times.
`lookaheads`: means at most 3-letter guesses will be generated.

So the recovery process will start. First, a complement will be chosen, which is made up of two letters outside the allowed alphabet, repeated a few times. Let's pretend %$ were chosen, and our random number in the range [1,5] was 3. Our complement is then `%$%$%$`. It's called a *complement* because it does not contain any characters from the alphabet.

Next, the very first guess will be made. Naively, we could send `FLAG=a, ..., FLAG=9` to the server, look at the compression ratio and keep the one letter which produces the smallest ratio. However, this method would produce false positives. What we actually do, is send `FLAG=a%$%$%$` as *possible-good* guess and `FLAG=%$%$%$a` as *known-bad* guess. In a nutshell, that's the *Two-Tries Method*.

Here's how we rate each guess in the Two-Tries method. We know this guess was a false positive if the compressed ratio of the known-bad guess is better than the other one, and we put it in the *discard pool*. If the compression ratio for the *possible-good* guess is better, then we keep that guess for the next round. If the ratios are equal, we don't discard the guess but we don't keep in either, we just put it in a *reserve pool* and keep it for later.

Let's pretend that a few characters are successfully recovered without problem. Let's pretend `FLAG=a39df238` was recovered, but the next guesses, `"FLAG=a39df238"+[a,b,...,9]` produce no candidates that we can keep. In other words, they produce only discarded guesses or reserve guesses. In that case, we'll simply pick a new complement (by calling `prepare_complement()`. We will do that up to `retries` times before giving up and performing a lookahead.

So let's pretend now that we checked all `"FLAG=a39df238"+[a,b,...,9]` guesses 5 times, with a different complement each time, and each time there were no candidates to keep, only *discarded* or *reserve* candidates. What we'll do in this case is increase the length of our guesses to 2 guessed letters. Before doing this, we throw out all guesses from our *discarded pool* and only keep the *reserve pool*. If our reserve pool contained `[a,d,9]`, then our guesses would become `[aa,ab,...,da,db,...,98,99]`. If none of these produce any guesses, we change the complement just as we did for our 1-letter guesses.

So, what if we try all 1-letter guesses with 5 complements, then increase to 2-letter guesses with another round of 5 complements, and nothing is produced? At that point the `CompressionOracle` class will return. It probably means the next letter wasn't in the allowed alphabet, which is ofter an indicator that the secret was fully recovered. Note that since compression oracles are highly dependant on the actual compressed data, it may also mean you should just retry the attack a few times.

More Ressources
---------------
1. CRIME: https://docs.google.com/presentation/d/11eBmGiHbYcHR9gL5nDyZChu_-lCa2GizeuOfaLU2HOU/edit
3. BREACH: [http://breachattack.com/resources/BREACH - BH 2013 - PRESENTATION.pdf](http://breachattack.com/resources/BREACH - BH 2013 - PRESENTATION.pdf)
2. BREACH: [http://breachattack.com/resources/BREACH - SSL, gone in 30 seconds.pdf](http://breachattack.com/resources/BREACH - SSL, gone in 30 seconds.pdf)
2. https://www.isecpartners.com/media/106031/ssl_attacks_survey.pdf
