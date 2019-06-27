class minbidict(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inverse = {}
        self.seclist = {}
        self.minlist = []
        self.min_ind = -1

        for key, value in self.items():
            self.inverse.setdefault(value, []).append(key)
            self.seclist.__setitem__(key, True)
            if self.minlist != []:
                self.insert_value(value)
            else:
                self.minlist = [value]

    def __setitem__(self, key, value):
        if key in self:
            if self[key] == self.minlist[-1]:
                self.minlist.pop()
            else:
                print("Not minimal value selected")
            self.inverse[self[key]].remove(key)
            if self.inverse[self[key]] == []:
                del self.inverse[self[key]]

        self.insert_value(value)

        super().__setitem__(key, value)
        self.inverse.setdefault(value, []).append(key)

    def __delitem__(self, key):
        value = self[key]
        if value == self.minlist[-1]:
            self.minlist.pop()
        else:
            print("Not minimal value selected")

        self.inverse.setdefault(self[key], []).remove(key)
        if self[key] in self.inverse and not self.inverse[self[key]]:
            del self.inverse[self[key]]
        super().__delitem__(key)

    def min_keys(self):


        min_val = self.minlist[self.min_ind]
        while min_val not in self.inverse:
            self.minlist.pop(self.min_ind)
            min_val = self.minlist[self.min_ind]

        return self.inverse[min_val]

        5//2

    def insert_value(self, value):
        if value <= self.minlist[-1]:
            self.minlist.append(value)
        elif value >= self.minlist[0]:
            self.minlist.insert(0, value)
        else:
            ma = self.minlist[0]
            mi = self.minlist[-1]
            pos_ind = len(self.minlist) - 1

            ind = pos_ind - round((value - mi + 1)/(ma - mi)*pos_ind) + 1
            self.minlist.insert(ind, value)
