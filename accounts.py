import argparse
from database import Storage
import sys
import random
import string

parser = argparse.ArgumentParser(description='Instrument for creating new accounts for chat-parser.')
parser.add_argument('-n', help='Create N new accounts', type=int, required=True)
parser.add_argument('-f', help='Create accounts with number starting from given', type=int, default=0)



def main():
    args = vars(parser.parse_args())
    acc_num = args['n']
    start_num = args['f'] - 1

    # db object
    s = Storage()


    for i in range(start_num, acc_num + start_num):
        # generate random string of len 10
        password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

        # create login
        login = 'admin{}'.format(i + 1)

        # at first, username is the same as login, but it can be changed later
        if s.register_new_account({ 'login' : login, 'password' : password, 'username' : login }) != True:
            print ('{} is already taken'.format(login))
            continue

        print ('{} / {}'.format(login, password))


if __name__ == '__main__':
    main()
