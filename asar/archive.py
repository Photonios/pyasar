import struct
import json
import shutil
import os.path
import logging

LOGGER = logging.getLogger(__name__)


class AsarArchive:
    """Represents a single *.asar file."""

    def __init__(self, filename, asarfile, files, baseoffset):
        """Initializes a new instance of the :see AsarArchive class.

        Args:
            filename (str):
                The path to the *.asar file to read/write from/to.

            asarfile (File):
                A open *.asar file object.

            files (dict):
                Dictionary of files contained in the archive.
                (The header that was read from the file).

            baseoffset (int):
                Base offset, indicates where in the file the header ends.
        """

        self.filename = filename
        self.asarfile = asarfile
        self.files = files
        self.baseoffset = baseoffset

    def extract(self, destination):
        """Extracts the contents of the archive to the specifed directory.

        Args:
            destination (str):
                Path to an empty directory to extract the files to.
        """

        if os.path.exists(destination):
            raise OSError(20, 'Destination exists', destination)

        self.__extract_directory(
            '.',
            self.files['files'],
            destination
        )

    def __extract_directory(self, path, files, destination):
        """Extracts a single directory to the specified directory on disk.

        Args:
            path (str):
                Relative (to the root of the archive) path of the directory
                to extract.

            files (dict):
                A dictionary of files from a *.asar file header.

            destination (str):
                The path to extract the files to.
        """

        # assures the destination directory exists
        destination_path = os.path.join(destination, path)
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

        for name, contents in files.items():
            item_path = os.path.join(path, name)

            # objects that have a 'files' member are directories,
            # recurse into them
            if 'files' in contents:
                self.__extract_directory(
                    item_path,
                    contents['files'],
                    destination
                )

                continue

            self.__extract_file(item_path, contents, destination)

    def __extract_file(self, path, fileinfo, destination):
        """Extracts the specified file to the specified destination.

        Args:
            path (str):
                Relative (to the root of the archive) path of the
                file to extract.

            fileinfo (dict):
                Dictionary containing the offset and size of the file
                (Extracted from the header).

            destination (str):
                Directory to extract the archive to.
        """

        if 'offset' not in fileinfo:
            self.__copy_extracted(path, destination)
            return

        self.asarfile.seek(
            self.__absolute_offset(fileinfo['offset'])
        )

        # TODO: read in chunks, ain't going to read multiple GB's in memory
        contents = self.asarfile.read(
            self.__absolute_offset(fileinfo['size'])
        )

        destination_path = os.path.join(destination, path)

        with open(destination_path, 'wb') as fp:
            fp.write(contents)

        LOGGER.debug('Extracted %s to %s', path, destination_path)

    def __copy_extracted(self, path, destination):
        """Copies a file that was already extracted to the destination directory.

        Args:
            path (str):
                Relative (to the root of the archive) of the file to copy.

            destination (str):
                Directory to extract the archive to.
        """

        unpacked_dir = self.filename + '.unpacked'
        if not os.path.isdir(unpacked_dir):
            LOGGER.warn(
                'Failed to copy extracted file %s, no extracted dir',
                path
            )

            return

        source_path = os.path.join(unpacked_dir, path)

        if not os.path.exists(source_path):
            LOGGER.warn(
                'Failed to copy extracted file %s, does not exist',
                path
            )

            return

        destination_path = os.path.join(destination, path)
        shutil.copyfile(source_path, destination_path)

    def __absolute_offset(self, offset):
        """Converts the specified relative offset into an absolute offset.

        Offsets specified in the header are relative to the end of the header.

        Args:
            offset (int):
                The relative offset to convert to an absolute offset.

        Returns (int):
            The specified relative offset as an absolute offset.
        """

        return int(offset) + self.baseoffset

    def __enter__(self):
        """When the `with` statements opens."""

        return self

    def __exit__(self, type, value, traceback):
        """When the `with` statement ends."""

        if not self.asarfile:
            return

        self.asarfile.close()
        self.asarfile = None

    @classmethod
    def open(cls, filename):
        """Opens a *.asar file and constructs a new :see AsarArchive instance.

        Args:
            filename (str):
                Path to the *.asar file to open for reading.

        Returns (AsarArchive):
            An insance of of the :AsarArchive class or None if reading failed.
        """

        asarfile = open(filename, 'rb')

        # uses google's pickle format, which prefixes each field
        # with its total length, the first field is a 32-bit unsigned
        # integer, thus 4 bytes, we know that, so we skip it
        asarfile.seek(4)

        header_size = struct.unpack('I', asarfile.read(4))
        if len(header_size) <= 0:
            raise IndexError()

        # substract 8 bytes from the header size, again because google's
        # pickle format uses some padding here
        header_size = header_size[0] - 8

        # read the actual header, which is a json string, again skip 8
        # bytes because of pickle padding
        asarfile.seek(asarfile.tell() + 8)
        header = asarfile.read(header_size).decode('utf-8')

        files = json.loads(header)
        return cls(filename, asarfile, files, asarfile.tell())
