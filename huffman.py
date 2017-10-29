import os
import sys
import marshal
import array

try:
    import cPickle as pickle
except:
    import pickle

def code(msg):
    # unique characters and number of occurrences in msg
    chars = {}
    # binary representation of msg
    string = ''
    # binary tree representation of msg
    tree = []

    # take count of unique characters in msg
    for c in msg:
        if c not in chars:
            chars[c] = 1
        else:
            chars[c] += 1

    # build the initial forest
    for c in chars:
        x = (c[1], [c[0]]) # (frequency, subtree)
        tree.append(x)

    # sort by frequency
    tree.sort(key = lambda t: t[0])

    # combine the trees
    while len(tree) > 1:
        for t in tree:
            for z in tree:
                if t == z:
                    continue
                z[0] += t[0]
                z[1] += t[1]
                tree.remove(t)

    print(chars) # TEMP print out chars to verify
    print(tree) # TEMP pring out tree to verify

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
