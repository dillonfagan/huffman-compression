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
        # append 0 or 1 to binary code
        bincode += str(i)
        if type(subtree[1]) is not list:
            # leaf reached
            codes[subtree[1]] = bincode
        else:
            traverse(subtree[1], bincode, codes)
        bincode = bincode[:-1]
    return codes


def code(msg):
    # case should msg be an empty string
    if msg == '':
        return ('', [])

    # Invariant (init): unique characters and number of occurrences in msg
    chars = {}
    # take count of unique characters in msg
    for c in msg:
        if c not in chars:
            chars[c] = 1
        else:
            # Invariant (maint): increment occurrences for each pass
            chars[c] += 1

    # Invariant (init): binary tree representation of msg
    tree = []
    # build the initial forest
    for (char, count) in chars.items():
        x = (count, char) # (frequency, subtree)
        tree.append(x)

    # Invariant (maint): sort forest by weight of each subtree
    tree.sort(key = lambda s: s[0])

    # merge the forest into two subtrees
    while len(tree) > 2:
        # get subtree with lowest weight
        s = tree[0]
        tree.remove(s)

        # get subtree with second lowest weight
        t = tree[0]
        tree.remove(t)

        weight = t[0] + s[0]
        subtree = [s, t]

        tree.append((weight, subtree))
        tree.sort(key = lambda s: s[0])

    # build codebook
    codes = traverse(tree)

    # assemble binary string from codebook
    string = ''
    for c in msg:
        string += codes[c]

    return (string, tree)


def decode(string, decoderRing):
    msg = ''
    codes = traverse(decoderRing)
    bincode = ''
    for bit in string:
        bincode += bit
        if bincode in codes.values():
            for (char, code) in codes.items():
                if code == bincode:
                    msg += char
            bincode = ''
    return msg


def compress(msg):
    string, tree = code(msg); print(string)

    bitstream = array.array('B')
    #buff = 0
    #count = 0

    for i in range(0, len(string) - 1, 8):
        j = i + 8
        diff = 0
        last = False
        if j > len(string):
            j = len(string)
            last = True
            diff = 8 - len(string[i:j])
        byte = int(string[i:j], 2)
        bitstream.append(byte)
        if last:
            bitstream.append(diff)

    # for bit in string:
    #     if bit == '0':
    #         buff = (buff << 1)
    #     else:
    #         buff = (buff << 1) | 0x01
    #     count += 1
    #     if count == 8:
    #         bitstream.append(buff)
    #         count = 0
    #         buff = 0
    #
    # if count != 0:
    #     bitstream.append(buff << (8 - count))
    return (bitstream, tree)


def binary(s):
    return str(s) if s <= 1 else binary(s >> 1) + str(s & 1)


# code >> (1) & 1 ?
def decompress(bitstream, decoderRing):
    bitstream = array.array('B', bitstream)

    diff = bitstream.pop() # disparity of bits of last element relative to byte

    string = ''
    for (i, byte) in enumerate(bitstream):
        bits = binary(byte)
        if i == len(bitstream) - 1:
            bits = ('0' * diff) + bits
        string += bits
    return decode(string, decoderRing)


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
