#!/usr/bin/env python3
# ~*~ coding: utf-8 ~*~

import json
import jwt
import os
import random
import string
import subprocess as sp

from argparse import ArgumentParser
from pathlib import Path

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


class JWToken(object):
    def __init__(self, token, key=None):
        try:
            self.header  = jwt.get_unverified_header(token)
            self.payload = jwt.decode(token, verify=False)
            self.encoded = token
            self.encoded_header, self.encoded_payload, self.signature = token.split('.')

            # Check if token is signed
            try:
                # If we can decode without key it's not signed.
                jwt.decode(token, '', verify=True)
                self.signed = False
                self.algo   = None
            except:
                self.signed = True
                self.algo   = self.header['alg']

            if key:
                self.set_key(key)
            else:
                self.key = ''

        except Exception as e:
            raise e

    def set_key(self, key):
        if self._is_valid(key):
            self.key = key
        else:
            print(f'Invalid key: {key}')

    def _is_valid(self, key):
        try:
            # Check that the key is the good one.
            jwt.decode(self.encoded, key)
            return True
        except:
            return False

    def bruteforce(self, wordlist=None):
        '''This function uses JohnTheRipper. It must be installed and on $PATH.
        Why to use it ? Because I'm lazy and because of it's performances!
        '''

        if not self.signed or not self.algo:
            print('Token not signed. Nothing to crack...')
            return

        def format_arg():
            arg = '--format='

            if self.algo == 'HS256':
                arg += 'HMAC-SHA256'
            elif self.algo == 'HS512':
                arg += 'HMAC-SHA512'

            return arg

        # To get the cracked key from JTR output
        def cracked_key():
            out = sp.check_output(['john', fname, '--show', format_arg()]).decode('utf-8')
            if '0 left' in out:
                print(out.split('\n')[0].replace('?:', ''))
                return out.split('\n')[0].replace('?:', '')
            return None

        # Create a random file name
        fname   = f'jwt_{get_random_string(6)}.txt'

        # Write token in the temporary random file
        with open(fname, 'w') as dst:
            dst.write(self.encoded)

        # Create the cmd list to execute as subprocess
        cmd = ['john', fname, format_arg()]

        if wordlist:
            cmd.append(f'--wordlist={wordlist}')

        # And run it silently
        sp.check_call(cmd, stdout=open(os.devnull, 'w'), stderr=sp.STDOUT)

        # Get the result, verify, and set self.key if it's good
        key = cracked_key()
        if key:
            self.set_key(key)

        # Remove the temporary file
        sp.check_call(['rm', fname])

    def forge(self, payload, algo=None):

        # Ensure payload is an object.
        if type(payload) is str:
            payload = json.loads(payload)

        # Particular case of no signing. Doesn't need a key.
        if algo == 'None':
            return jwt.encode(payload, None, algorithm=None).decode('utf-8')

        # Any other case we need a key
        if self.key:
            if algo and not algo == 'None':
                return jwt.encode(payload, self.key, algorithm=algo).decode('utf-8')
            return jwt.encode(payload, self.key, algorithm=self.algo).decode('utf-8')
        else:
            print('Impossible to forge without key')
            return None

def main():
    parser = ArgumentParser(description='Crack and/or Forge JSON Web Tokens (JWT)',
                            epilog='Use it at your own risk. Do not do stupid or illegal stuff. You are responsible of what you do.')

    parser.add_argument('token', help='The token to crack or to forge from')
    parser.add_argument('-a', '--algorithm', help='The algorithm to use. (HS256, HS512, RS256, None)')
    parser.add_argument('-b', '--bruteforce', action='store_true',
                        help='Add this option to bruteforce the key using JohnTheRipper')
    parser.add_argument('-f', '--forge', help='JSON payload string of the new JTW to forge')
    parser.add_argument('-k', '--key', help='The key if you know it. (Will be verified)')
    parser.add_argument('-w', '--wordlist', help='The path of the wordlist JTR will use')

    args = parser.parse_args()

    def get_token():
        if args.key:
            if os.path.exists(args.key): # If argument value is a file
                return JWToken(args.token, key=open(args.key, 'r').read())
            return JWToken(args.token, key=args.key)
        return JWToken(args.token)

    def bruteforce(token):
        if args.wordlist:
            print(f'[*] Starting Bruteforce with John using {args.wordlist}.')
            token.bruteforce(wordlist=args.wordlist)
        else:
            print('[*] Starting Bruteforce with John without wordlist.')
            token.bruteforce()
        if token.key:
            print(f'[+] Key found: {token.key}')
        else:
            print('[-] Key not found.')

    def forge(token):
        if args.algorithm:
            if args.algorithm in ('HS256', 'HS512', 'RS256', 'None'):
                print('')
                print(f'[+] New Token: {token.forge(args.forge, algo=args.algorithm)}')
                print('')
            else:
                print('Algorithm is not valid. Must be one of (HS256, HS512, RS256, None).')
                print(f'Using token\'s : {token.algo}')
                print('')
                print(f'[+] New Token: {token.forge(args.forge)}')
                print('')
        else:
            print('')
            print(f'[+] New Token: {token.forge(args.forge)}')
            print('')

    def show_details(token):
        print(f'''
        Token:     {token.encoded}
        Payload:   {token.payload}
        Algorithm: {token.algo}
        Key:       {token.key}
        ''')

    token = get_token()

    if not token.key and args.bruteforce:
        bruteforce(token)

    show_details(token)

    if args.forge:
        forge(token)



if __name__ == '__main__':
    main()
