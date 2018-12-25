import os
import json
import pickle


def loadIfJson(_input: str) -> bool:
    if isinstance(_input, bytes):
        _input = _input.decode()
    try:
        return json.loads(_input)
    except Exception:
        return False


def fastPickle(arg=None, ind=None):
    '''
    print('if pass int, will always used as indicator not filename!')
    '''
    objs = os.listdir('debug')
    objs = [int(i.split('.')[0]) for i in objs]
    objs.sort()
    if not arg:
        return objs
    elif isinstance(arg, int):
        fastPickle(ind=arg)
    elif ind and not obj:
        file_name = f'{objs[ind]}.pickle'
        with open(file_name, 'rb') as f:
            return pickle.load(f)
    else:
        try:
            file_name = f'debug/{objs[-1] + 1}.pickle'
            with open(f'{file_name}', 'wb') as f:
                pickle.dump(arg, f)
            return f'{arg} dumped as {file_name}'
        except Exception:
            print('failed')


def asciiBigSuccess():
    print('''                                                                      /$$
                                                                     | $$
  /$$$$$$$ /$$   /$$  /$$$$$$$  /$$$$$$$  /$$$$$$   /$$$$$$$ /$$$$$$$| $$
 /$$_____/| $$  | $$ /$$_____/ /$$_____/ /$$__  $$ /$$_____//$$_____/| $$
|  $$$$$$ | $$  | $$| $$      | $$      | $$$$$$$$|  $$$$$$|  $$$$$$ |__/
 \____  $$| $$  | $$| $$      | $$      | $$_____/ \____  $$\____  $$
 /$$$$$$$/|  $$$$$$/|  $$$$$$$|  $$$$$$$|  $$$$$$$ /$$$$$$$//$$$$$$$/ /$$
|_______/  \______/  \_______/ \_______/ \_______/|_______/|_______/ |__/
''')


def is_url(_input):
    flag = False
    if isinstance(_input, str):
        if _input.startswith('http'):
            flag = True
    return flag
