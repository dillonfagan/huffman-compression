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
code dictionary containing a binary code for each unique character.
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
            # Invariant (init): init for each unique character
            chars[c] = 1
        else:
            # Invariant (maint): increment occurrences of character for each pass
            chars[c] += 1

    # Invariant (init): binary tree representation of msg
    tree = []

    # Invariant (maint): build the initial forest with each character as a tree
    for (char, count) in chars.items():
        x = (count, char) # tuple(frequency, subtree)
        tree.append(x)

    # Invariant (maint): sort forest by weight of each tree
    # Should be able to get the two subtrees with the lowest weight
    #   if the list is sorted.
    tree.sort(key = lambda s: s[0])

    # Invariant (maint): merge the forest into two subtrees
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

    # Invariant (init): build codebook for encoding message
    # Each character in the message should have been assigned a code
    #   in the codebook.
    codes = traverse(tree)

    # Invariant (init): empty string to hold the encoded message
    string = ''

    # Invariant (maint): append the code of each character to the encoded
    #   message using the codebook
    for c in msg:
        string += codes[c]

    return (string, tree)


def decode(string, decoderRing):
    # Invariant (init): will hold decoded message
    msg = ''

    # Invariant (init): codebook for bit codes
    codes = traverse(decoderRing)

    # Invariant (init): temporary storage to examine bit combinations in order
    #   to identify a character that matches the bitcode from codebook
    bincode = ''

    for bit in string:
        # Invariant (maint): append next bit to bincode and check whether
        #   there is a character assigned to a bitcode equal to bincode
        bincode += bit
        if bincode in codes.values():
            for (char, code) in codes.items():
                if code == bincode:
                    msg += char
            bincode = '' # (maint): reset

    return msg


def compress(msg):
    # Invariant (init): string of bits (the encoded message)
    # Invariant (init): huffman tree to later decompress message
    string, tree = code(msg)

    # Invariant (init): byte array to store compressed message
    bitstream = array.array('B')

    # Invariant (maint): for each block of eight bits in the encoded message,
    #   convert the eight bits into an integer and add it to bitstream. If the
    #   final block has fewer than eight bits, the disparity (number of bits lacking)
    #   is appended to bitstream to later assist with decompression.
    for i in range(0, len(string) - 1, 8):
        j = i + 8 # end of eight-bit block
        diff = 0 # bits missing in last block
        last = False # if true, exit loop

        if j > len(string):
            j = len(string)
            last = True
            for bit in string[i:j]:
                if bit == '0':
                    diff += 1
                else:
                    break

        byte = int(string[i:j], 2)
        bitstream.append(byte)

        if last:
            bitstream.append(diff)

    return (bitstream, tree)

'''
Returns a binary string given an integer s.
'''
def binary(s):
    return str(s) if s <= 1 else binary(s >> 1) + str(s & 1)


def decompress(bitstream, decoderRing):
    # cast bistream as byte array to ensure proper type
    bitstream = array.array('B', bitstream)

    # disparity of bits of last element relative to size of byte
    diff = bitstream.pop()

    # Invariant (init): decompressed bit string
    string = ''

    # Invariant (maint): convert each byte in bitstream back into blocks of bits
    #   and append them to string.
    for (i, byte) in enumerate(bitstream):
        bits = binary(byte)
        if i < len(bitstream) - 1:
            bits = ('0' * (8 - len(bits))) + bits
        else:
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
