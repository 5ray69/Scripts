
class Tshiel(object):
    koef_circuit = 1.05
    def __init__(self, x):
        self.x = x

    @staticmethod
    def du(y):
        return y*y

    def first(self, z):
        return self.du(z)

    def second(self, a, b):
        return self.du(a) + b


w = Tshiel(1)
print(w.first(2))
print(w.second(2, 3))