## OpenMaple API for Python

**OpenMaple for Python** provides an interface between the Maple evaluation engine and a Python program.  This is implemented using Python classes and standard interfaces.

### Instructions for use

OpenMaple for Python requires an installation of Maple 2023 or later on the same machine. To get this to work, set either an environment variable to specify the location of your Maple installation.

You can set the MAPLE environment variable to point at the root of your Maple installation, for example `C:\Program Files\Maple 2024` (on Windows) or `/Library/Frameworks/Maple.framework/Versions/2024` (on macOS).

Alternatively, you can set an environment variable to explicitly specify the Maple binary directory. Examples for specific platforms using default install locations:
* For Windows set **`PATH`** to include `C:\Program Files\Maple 2024\bin.X86_64_WINDOWS`
* For Linux set **`LD_LIBRARY_PATH`** to include `/opt/maple2024/bin.X86_64_LINUX`
* For macOS set **`DYLD_LIBRARY_PATH`** to include `/Library/Frameworks/Maple.framework/Versions/2024/bin.APPLE_UNIVERSAL_OSX`

Next, launch Python. If using a version of Python other than the one shipped with Maple, ensure it is Python 3.11 or later and that numpy is installed and working. 

If it not already in the Python module search path (`sys.path`), add the installed location of the OpenMaple for Python with
```
sys.path.append('C:\\Program Files\\Maple 2024\\Python.X86_64_WINDOWS\\lib')
```

Do a simple test to check everything is working with
```
import maple
import maple.namespace as mpl
print( mpl.int( mpl.x ** 2, mpl.x ) )
```
