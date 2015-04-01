import base64
import os, sys, inspect

 # realpath() will make your script run, even if you symlink it :)
_abspath = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
#if _abspath not in sys.path:
#    sys.path.insert(0, _abspath)

     
#_abspath = os.path.abspath(os.path.dirname(__file__))


def load_image(filename):
#    # Geht nicht mit PY2EXE:
#    import pkgutil
#    return  base64.encodestring(pkgutil.get_data(__package__, filename))
    #print os.path.join(_abspath, filename)
    with open(os.path.join(_abspath, filename), 'rb') as fid:
        gif = base64.encodestring(fid.read())
    return gif
