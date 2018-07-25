#Golay´s encoding
import binascii
import numpy as np

def TransformTextToBits(txt):
    """
    Transform the text to bits.
    :param txt: The text to transform in bits.
    :return: The text transformed in bits.
    """
    bits = bin(int(binascii.hexlify(txt.encode('utf-8', 'surrogatepass')), 16))[2:]
    bitsToInt = [int(x) for x in bits]
    while len(bitsToInt) is not 12:
        bitsToInt.insert(0,0)
    return ''.join(map(str, bitsToInt))

def TransformBitsToText(txt):
    """
    Transform the bits to text.
    :param text: The text in bits to transform.
    :return: The bits transformed in text.
    """
    return chr(int(txt, base=2))

class Golay:
    def __init__(self):
        self.__matrixGenerator = self.__matrixGenerator()
        self.__identityMatrix = self.__identity()
        self.__decoder = np.array(self.__decoderMatrix())

    def __matrixGenerator (self):
        """
        Generates de generator matrix of Golay´s code 12
        :return: The generator matrix.
        """
        toret = []
        firstVector = "011111111111"
        mainVector = "11011100010"
        toret.append(list(int(x) for x in firstVector))
        toret.append(list(int(x) for x in ("1" + mainVector)))
        for i in range(10):
            row = mainVector[1:len(mainVector)]
            row = row + mainVector[0]
            toret.append(list(int(x) for x in ("1" + row)))
            mainVector = row

        return toret

    def __identity(self):
        """
        Generates the entity matrix of the Golay´s code.
        :return: The entity matrix.
        """
        canonicalVector = "100000000000"
        toret = []
        toret.append([int(x) for x in canonicalVector])
        for i in range(11):
            row = "0" + canonicalVector[0:-1]
            toret.append([int(x) for x in row])
            canonicalVector = row

        return toret

    def __decoderMatrix(self):
        """
        Generates the matrix (AI^tr)
        :return: The matrix to use in the encoding.
        """
        toret = []
        for row in range(12):
            aux = self.__identityMatrix[row]
            aux.extend(self.__matrixGenerator[row])
            toret.append(aux)

        return toret

    def encode(self, word):
        """
        Encode the text to binary.
        :param word: The text to encoding.
        :return: The text in binary.
        """
        wordToBin = [int(x) for x in word]
        wordToBin = np.array(wordToBin)
        toret = np.dot(wordToBin, self.__decoder) % 2

        return toret

    def decode(self, word):
        wordToBin = [int(x) for x in word]
        wordToBin = np.array(wordToBin)
        syn = np.dot(wordToBin, self.__decoder.T) % 2
        synWeight = self.__weight(syn)

        error = list()

        if synWeight <= 3:
            error = [int(bit) for bit in syn]
            for i in range(12):
                error.append(0)

        else:
            flag = 0
            i = 0
            indexA = 0

            while i < 12 and flag is 0:
                toret = (syn + self.__matrixGenerator[i]) % 2
                toret_weight = self.__weight(toret)

                if toret_weight <= 2:
                    flag = 1
                    indexA = i

                i += 1

            if flag is 1:
                error = [int(bit) for bit in toret]
                for i in range(12):
                    if i is not indexA:
                        error.append(0)
                    else:
                        error.append(1)

            else:
                syn2 = np.dot(syn, self.__matrixGenerator) % 2
                synWeight2 = self.__weight(syn2)

                if synWeight2 <= 3:
                    error = [int(bit) for bit in syn2]
                    for i in range(12):
                        error.insert(0, 0)
                else:
                    flag = 0
                    i = 0
                    indexA = 0

                    while i < 12 and flag is 0:
                        toret = (syn2 + self.__matrixGenerator[i]) % 2

                        toretWeight = self.__weight(toret)

                        if toretWeight <= 2:
                            flag = 1
                            indexA = i
                        i += 1

                    if flag is 1:
                        for i in range(12):
                            if i is not indexA:
                                error.append(0)
                            else:
                                error.append(1)

                        for i in range(12):
                            error.append(toret[i])
                    else:
                        print("There was an error in the message, please send it again.")
                        pass

        if len(error) is 24:

            decodedWord = (wordToBin + error) % 2
            return decodedWord[:12]
        else:
            error = [0,0,0,0,0,0,1,0,0,0,1,1]
            error = np.array(error)
            return error

    def __weight(self, word):
        """
        Return the weight of a vector.
        :param word: The vector.
        :return: The weigth of the vector.
        """
        weight = 0
        for bit in word:
            if int(bit) is 1:
                weight += 1

        return weight

if __name__ == "__main__":
    c = Golay()
    encoded = open('GolayEncoded.txt', 'w+')

    with open("quijote.txt", 'r+') as f:
        for line in f:
            for letter in line:
                encoded.write(''.join(map(str, c.encode(TransformTextToBits(letter)))))

    encoded.close()
    print("Encoded finish.")
    encodedText = open("GolayEncoded.txt", "r+").read()
    decodedText = open("GolayDecoded.txt", "w+")
    numChar = len(encodedText)

    for i in range(0,int(numChar/24)):
        decodedText.write(TransformBitsToText(''.join(map(str,c.decode(encodedText[i*24:((i+1)*24)])))))

    print("Decoded finish")
    decodedText.close()