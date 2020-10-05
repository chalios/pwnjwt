#!/usr/bin/env python3
# ~*~ coding: utf-8 ~*~

import json
import jwt
import os
import random
import string
import subprocess as sp

from argparse import ArgumentParser

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


class JWToken(object):
    def __init__(self, token, key=None):
        try:
            self.header  = jwt.get_unverified_header(token)
            self.payload = jwt.decode(token, verify=False)
            self.encoded = token

            # Check if token is signed
            try:
                # If we can decode without key it's not signed.
                jwt.decode(token, '', verify=True)
                self.signed = False
                self.algo   = None
            except:
                self.signed = True
                self.algo   = self.header['alg']

            if key and self._is_valid(key):
                self.key = key
            else:
                self.key = ''
        except Exception as e:
            raise e

    def _is_valid(self, key):
        try:
            # Check that the key is the good one.
            jwt.decode(self.encoded, key, algorithms=[self.algo])
            return True
        except:
            return False

    def bruteforce(self, wordlist=None):
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

        def cracked_key():
            out = sp.check_output(['john', fname, '--show', format_arg()]).decode('utf-8')
            if '0 left' in out:
                print(out.split('\n')[0].replace('?:', ''))
                return out.split('\n')[0].replace('?:', '')
            return None

        fname   = f'jwt_{get_random_string(6)}.txt'

        with open(fname, 'w') as dst:
            dst.write(self.encoded)

        cmd = ['john', fname, format_arg()]

        if wordlist:
            cmd.append(f'--wordlist={wordlist}')

        sp.check_call(cmd, stdout=open(os.devnull, 'w'), stderr=sp.STDOUT)

        key = cracked_key()
        if key:
            if self._is_valid(key):
                self.key = key

        sp.check_call(['rm', fname])

    def forge(self, payload):
        if self.key:
            if type(payload) is str:
                payload = json.loads(payload)
            return jwt.encode(payload, self.key, algorithm=self.algo).decode('utf-8')
        else:
            print('Impossible to forge without key')
            return None

def main():
    parser = ArgumentParser(description='Crack and/or Forge JSON Web Tokens (JWT)',
                            epilog='Use it at your own risk. Do not do stupid or illegal stuff. You are responsible of what you do.')

    parser.add_argument('token', help='The token to crack or to forge from')
    parser.add_argument('-b', '--bruteforce', action='store_true',
                        help='Add this option to bruteforce the key using JohnTheRipper')
    parser.add_argument('-f', '--forge', help='JSON payload string of the new JTW to forge')
    parser.add_argument('-k', '--key', help='The key if you know it. (Will be verified)')
    parser.add_argument('-w', '--wordlist', help='The path of the wordlist JTR will use')

    args = parser.parse_args()


    if args.key:
        token = JWToken(args.token, key=args.key)
    else:
        token = JWToken(args.token)

    if args.bruteforce:
        if args.wordlist:
            print(f'Starting Bruteforce with John using {args.wordlist}.')
            token.bruteforce(wordlist=args.wordlist)
        else:
            print('Starting Bruteforce with John.')
            token.bruteforce()
        print('Done.')

    if args.forge:
        print('')
        print(f'New Token: {token.forge(args.forge)}')
        print('')

    print(f'''
    Token:     {token.encoded}
    Signed:    {token.signed}
    Algorithm: {token.algo}
    Key:       {token.key}
    Payload:   {token.payload}
    ''')

if __name__ == '__main__':
    main()
