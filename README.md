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
* `seed` (mandatory): A short string which you believe is contained in the compressed data. In the CRIME attack, this seed is the name of the cookie, because it always directly precedes the actual cookie data.
* `alphabet`: The allowable charset of the secret information. This defaults to `string.printable`. It's a good idea to restrict the alphabet as much as possible, because it will cut down on attack time, but most importantly, the false-positive detection (Two-Tries Method) relies on characters from outside of the allowable alphabet to eliminate incorrect guesses.
* `max_threads`: The number of concurrent threads to start. Using more than one thread may cause problems if the server is keeping some kind of state that prevents multiple concurrent queries to be made. The number of threads running at once will never be greated than the size of the allowable alphabet.

You may also want to override the `CompressionOracle.prepare` and `CompressionOracle.cleanup` methods, which may be used to allocate any ressource you may need (for example, you 
may wish to retreive some kind of session token from a web server). The `prepare()` method is called just after entering the `run()` method but before any call to `oracle()`. 
The `cleanup()` method is called after all calls to `oracle()` just before the `run()` method returns.

More Ressources
---------------
1. CRIME: https://docs.google.com/presentation/d/11eBmGiHbYcHR9gL5nDyZChu_-lCa2GizeuOfaLU2HOU/edit
3. BREACH: [http://breachattack.com/resources/BREACH - BH 2013 - PRESENTATION.pdf](http://breachattack.com/resources/BREACH - BH 2013 - PRESENTATION.pdf)
2. BREACH: [http://breachattack.com/resources/BREACH - SSL, gone in 30 seconds.pdf](http://breachattack.com/resources/BREACH - SSL, gone in 30 seconds.pdf)
2. https://www.isecpartners.com/media/106031/ssl_attacks_survey.pdf
