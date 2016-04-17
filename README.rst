Library for working with Electron's ASAR archive files.
Electron (formely known as Atom Shell) uses it's own archive format to
compress files into a single file. The format is somewhat similar to TAR
files. There's a Node.JS package for working with ASAR files:

::

    https://github.com/electron/asar

The URL above also contains the format documentation. Code was written for Python >3.4.

Example usage
-------------

::

    from asar import AsarArchive

    with AsarArchive.open('myasarfile.asar') as archive:
        archive.extract('/home/mydir')

At the moment that is all what it can do ;)


Disclaimer / License
--------------------
This is no way associated with Github, Electron or Atom. This is free,
and open-source (free as in beer) for fun and profit. Licensed under the
*Do What the Fuck You want Public License*:

::

    http://www.wtfpl.net/
