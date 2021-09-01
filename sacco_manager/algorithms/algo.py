class FilterClass:
    # This is used to format entries
    def prepare_town_search(self,departure, destination):
        result = False
        alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                    'U', 'V', 'W', 'X', 'Y', 'Z']
        if alphabet.index(departure.upper()[0]) > alphabet.index(destination.upper()[0]):
            result = False
        elif alphabet.index(departure.upper()[0])== alphabet.index(destination.upper()[0]):
            #Check the next letter on index 1.
            if alphabet.index(departure.upper()[1]) > alphabet.index(destination.upper()[1]):
                result=False
                #The second letter is equal
            elif alphabet.index(departure.upper()[1]) == alphabet.index(destination.upper()[1]):
                #Check index 2.
                if alphabet.index(departure.upper()[2]) > alphabet.index(destination.upper()[2]):
                    result = False
                else:
                    result=True

            else:
                result=True

        else:
            result = True
        return result