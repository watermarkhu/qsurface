

# opensurfacesim.decoders.mwpm.get_blossom5.run()

# %%
import opensurfacesim
pf = opensurfacesim.codes.toric.plot.FaultyMeasurements(3, figure3d=True)
pf.initialize("pauli")

dc = opensurfacesim.decoders.mwpm.plot.Toric(pf, use_blossom5=True)

#%%

pf.random_errors(p_bitflip=0.1, pm_bitflip=0.05)
pf.state_icons()


# dc.decode()
dc.decode()
pf.show_corrected()


print(pf.logical_state, pf.no_error)


# # %%
# pf.figure.close()
# %%
pf.figure.focus()

# %%
dc.figure.focus()
# %%
# Using meta class

from inspect import isfunction

class Metaclass(type):
    def __new__(cls, clsname, bases, attrs, show=False):
        cls.show = show
        for attr, value in attrs.items():
            if isfunction(value):
                attrs[attr] = cls.get_function(cls, attrs, attr, value)
        return super(Metaclass, cls).__new__(
            cls, clsname, bases, attrs)

    def get_function(cls, attrs, attr, value):
        if cls.show and "show_" + attr in attrs:
            def function(*args, **kwargs):
                ret = value(*args, **kwargs)
                attrs["show_" + attr](*args, **kwargs)
            return function
        else:
            return value



def get_class(show):
    class Test(object, metaclass=Metaclass, show=show):
        attr = 0
        class Nested(object):
            pass

        def test(self, txt ="hello"):
            print(txt)

        def show_test(*args, **kwargs):
            print("world")
    return Test()

Aclass = get_class(True)
Bclass = get_class(False)
# %%
# Monkey patching 

class DecoratorClass(object):
    def __init__(self, cls):
        self._cls = cls
        
    def __call__(self, *args, show=False, **kwargs):
        if show:
            self._cls._test = self._cls.test
            self._cls.test = self.get_wrapped()
        
        return self._cls(*args, **kwargs)
    
    def get_wrapped(self):
        def function(*args, **kwargs):
            self._cls._test(*args, **kwargs)
            self._cls._show_test(*args, **kwargs)
        return function


@DecoratorClass
class Test(object):
    def test(self, txt ="hello"):
        print(txt)

    def _show_test(self):
        print("world")
# %%
