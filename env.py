class Environment:
    def __init__(self, table=None, prev=None):
        self.table = {} if table is None else table
        self.prev = prev

    def __iter__(self):
        for key in self.table:
            yield key

    def __setitem__(self, key, value):
        """Attempts to find an ancestor environment frame containing the
        variable and sets the value there. If not found it will set it at the top frame."""
        currentframe = self
        while currentframe is not None:
            if key in currentframe.table:
                currentframe.table[key] = value
                break
            else:
                currentframe = currentframe.prev
        else:
            self.table[key] = value

    def __getitem__(self, key):
        try:
            return self.table[key]
        except KeyError:
            if self.prev is not None:
                return self.prev[key]
            else:
                raise NameError('Undefined name {}'.format(key))

if __name__ == '__main__':
    E1 = Environment()
    E1['thing'] = 1
    print('Can we access items in our environment?', E1['thing'])
    print('Looking good.')
    E2 = Environment(prev=E1)
    print('Let\'s try to access variables in E1 from E2.', E2['thing'])
    print('Annnnnd, we\'re good.')
    E2['stuff'] = 2
    print('Let\'s just make sure E2 isn\'t broken.', E2['stuff'])
    print('Goooood.')
    try:
        print('And this variable is undefined.', E2['junk'])
    except NameError:
        print('Undefined variable.')
        
