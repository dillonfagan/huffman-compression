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
code dictionary.
'''
def traverse(tree, bincode = '', codes = {}):
    for (i, subtree) in enumerate(tree):
        if type(subtree[1]) is not list:
            # leaf reached
            bincode += str(i)
            codes[subtree[1]] = bincode
        else:
            bincode += str(i)
            traverse(subtree[1], bincode, codes)

        bincode = bincode[:-1]
    return codes

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
    while len(tree) > 2:
        s = tree[0]
        tree.remove(s)

        t = tree[0]
        tree.remove(t)

        weight = t[0] + s[0]
        subtree = [s, t]

        tree.append((weight, subtree))
        tree.sort(key = lambda s: s[0])

    codes = traverse(tree)

    string = ''
    for c in msg:
        string += codes[c]

    return (string, tree)

def decode(string, decoderRing):
    msg = ''
    codes = traverse(decoderRing)
    bincode = ''
    for d in string:
        bincode += d
        if bincode in codes.values():
            for (char, code) in codes.items():
                if code == bincode:
                    msg += char
            bincode = ''

    return msg

def compress(msg):
    raise NotImplementedError

def decompress(string, decoderRing):
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
        string = fp.read()
        fp.close()
        if compressing:
            msg, tree = compress(string)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), msg), fcompressed)
            fcompressed.close()
        else:
            msg, tree = code(string)
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
            string = decompress(msg, tree)
        else:
            string = decode(msg, tree)
            print(string)
        fp = open(outfile, 'wb')
        fp.write(string)
        fp.close()
