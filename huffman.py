import os
import sys
import marshal
import array

try:
    import cPickle as pickle
except:
    import pickle

class Node:
    def __init__(self, char, weight, left = None, right = None):
        self.char = char
        self.weight = weight
        self.left = left
        self.right = right

    def __lt__(self):
        self.weight

    def __gt__(self):
        self.weight

    def __le__(self):
        self.weight

    def __ge__(self):
        self.weight

    def is_leaf(self):
        return not self.left and not self.right

def create_codes(root, codes = {}):
    if not root.is_leaf():
        create_codes(root.left, codes)
        create_codes(root.right, codes)
    return codes

def code(msg):
    # case should msg be an empty string
    if msg == '':
        return ('', [])

    # Invariant (init): unique characters and number of occurrences in msg
    chars = {}
    # Invariant (init): binary tree representation of msg
    f = []

    # take count of unique characters in msg
    for c in msg:
        if c not in chars:
            chars[c] = 1
        else:
            chars[c] += 1

    # build the initial forest
    for (char, weight) in chars.items():
        x = Node(char, weight)
        f.append(x)

    # merge the forest into single tree
    while len(f) > 1:
        # Invariant (maint): sort by frequency
        f.sort(key = lambda x: x.weight)
        # get node with lowest weight
        s = f[0]
        f.remove(s)
        # get node with second lowest weight
        t = f[0]
        f.remove(t)
        # make new root node with lowest and second lowest as children
        root = Node(s.char, s.weight + t.weight, s, t)
        f.append(root)

    nodes_walked = 0
    while nodes_walked < len(chars):
        pass

    codes = create_codes(f[0])

    print(chars) # TEMP
    print(f[0].char, f[0].weight) # TEMP

    # Invariant (init): binary representation of msg
    string = ''

    return (string, f[0])

def decode(str, decoderRing):
    msg = ''
    return msg

def compress(msg):
    raise NotImplementedError

def decompress(str, decoderRing):
    raise NotImplementedError

def usage():
    sys.stderr.write("Usage: {} [-c|-d|-v|-w] infile outfile\n".format(sys.argv[0]))
    exit(1)

if __name__=='__main__':
    if len(sys.argv) != 4:
        usage()
    opt = sys.argv[1]
    compressing = False
    decompressing = False
    encoding = False
    decoding = False
    if opt == "-c":
        compressing = True
    elif opt == "-d":
        decompressing = True
    elif opt == "-v":
        encoding = True
    elif opt == "-w":
        decoding = True
    else:
        usage()

    infile = sys.argv[2]
    outfile = sys.argv[3]
    assert os.path.exists(infile)

    if compressing or encoding:
        fp = open(infile, 'rb')
        str = fp.read()
        fp.close()
        if compressing:
            msg, tree = compress(str)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), msg), fcompressed)
            fcompressed.close()
        else:
            msg, tree = code(str)
            print(msg)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), msg), fcompressed)
            fcompressed.close()
    else:
        fp = open(infile, 'rb')
        pickleRick, msg = marshal.load(fp)
        tree = pickle.loads(pickleRick)
        fp.close()
        if decompressing:
            str = decompress(msg, tree)
        else:
            str = decode(msg, tree)
            print(str)
        fp = open(outfile, 'wb')
        fp.write(str)
        fp.close()
