import os
import sys
import marshal
import array

try:
    import cPickle as pickle
except:
    import pickle

'''
Traverses a given huffman tree and returns the binary
string representation.
'''
def traverse(root, string = [], top = 0):
    if len(root[1]) > 1:
        s = string
        s.append('0')

        t = string
        t.append('1')

        # traverse left and right
        return traverse(root[1][1], s, top + 1) + \
        traverse(root[1][0], t, top + 1)

    # check if root is a leaf
    if root[1] is not list:
        return string

def code(msg):
    # case should msg be an empty string
    if msg == '':
        return ('', [])

    # Invariant (init): unique characters and number of occurrences in msg
    chars = {}
    # Invariant (init): binary tree representation of msg
    tree = []

    # take count of unique characters in msg
    for c in msg:
        if c not in chars:
            chars[c] = 1
        else:
            chars[c] += 1

    # build the initial forest
    for (char, count) in chars.items():
        x = (count, char) # (frequency, subtree)
        tree.append(x)

    # Invariant (maint): sort by frequency
    # This sorting by frequency will only occur once.
    tree.sort(key = lambda s: s[0])

    # merge the forest into single tree
    while len(tree) > 1:
        for (i, s) in enumerate(tree):
            next_i = (i + 1) % len(tree)
            t = tree[next_i]
            weight = t[0] + s[0]
            subtree = None
            if t[1] is list:
                subtree = s[1] + t[1]
            else:
                subtree = [s, t]
            subtree.sort(key = lambda s: s[0])
            tree[next_i] = (weight, subtree)
            tree.remove(s)

    print(tree) # TEMP

    # Invariant (init): binary representation of msg
    string = ''.join(traverse(tree[0]))
    #print(string) # TEMP

    return (string, tree)

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
