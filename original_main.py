import argparse
import ftplib
import os
import tqdm
import time

"""
Example usage as a CLI:
```
python3 download_ftp_tree ftp.something.com /some/directory .
```
The code above will look for a directory called /some/directory/ on the ftp
host, and then duplicate the directory and its entire contents into the local
current working directory.
Additional options are available for authentication and more. See help:
```
python3 download_ftp_tree -h
```
"""




def _make_parent_dir(fpath):
    """ ensures the parent directory of a filepath exists """
    dirname = os.path.dirname(fpath)
    while not os.path.exists(dirname):
        try:
            os.mkdir(dirname)
            print("created {0}".format(dirname))
        except:
            _make_parent_dir(dirname)


def _download_ftp_file(ftp_handle, name, dest, overwrite):
    """ downloads a single file from an ftp server """
    _make_parent_dir(dest.lstrip("/"))
    if not os.path.exists(dest) or overwrite is True:
        try:
            with open(dest, 'wb') as f:
                ftp_handle.retrbinary("RETR {0}".format(name), f.write)
        except FileNotFoundError:
            print("FAILED: {0}".format(dest))
    else:
        print("already exists: {0}".format(dest))





def download(ftp_handle, files, overwrite, sleep=4):
    progress = tqdm.tqdm(total=sum(list(files.values())))
    for item, size in files.items():
        time.sleep(sleep)
        _download_ftp_file(ftp_handle, item, item, overwrite)
        progress.update(size)
    progress.close()





def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)



def main():
    parser = argparse.ArgumentParser(description='Bulk download over FTP.')
    parser.add_argument('host', type=str)
    parser.add_argument('remote_dir_ftp', type=str, help='source directory')
    parser.add_argument('local_dir', type=str, help='target directory')
    parser.add_argument('--username', type=str, help='username for login')
    parser.add_argument('--password', type=str, help='password for login')
    parser.add_argument('--sleep', type=str, default=4,
                        help=('delay between files to avoid hammering sever '
                              '(in seconds)'))
    args = parser.parse_args()
    ftp_handler = ftplib.FTP(args.host, args.username or None, args.password or None)
    ftp_handler.login()
    download_ftp_tree(ftp_handler, args.remote_dir_ftp, args.local_dir, args.sleep)


def download_ftp_tree(
        ftp_handler, remote_dir_ftp, local_dir, sleep=4, overwrite=False, guess_by_extension=True):

    remote_dir_ftp = remote_dir_ftp.lstrip("/")
    original_directory = os.getcwd()    # remember working directory before function is executed
    os.chdir(local_dir)               # change working directory to ftp mirror directory
    files = {}
    files_directory = _mirror_ftp_dir(ftp_handler, files, remote_dir_ftp, guess_by_extension)

    print(files_directory)

    #
    # download(ftp_handler, files, overwrite, sleep)
    # os.chdir(original_directory)        # reset working directory to what it was before function exec


def _mirror_ftp_dir(ftp_handler, files, remote_dir_ftp, guess_by_extension):

    # print(files)

    # print('cumulative size: {}  currently rescursing {}'.format(
	# 	sizeof_fmt(sum(list(files.values()))), remote_dir_ftp))

    for item_dir in ftp_handler.nlst(remote_dir_ftp):
        if _is_ftp_dir(ftp_handler, item_dir, guess_by_extension):
            print(guess_by_extension)
            _mirror_ftp_dir(ftp_handler, files, item_dir, guess_by_extension)
        else:
            try:
                size = ftp.size(item_dir)
                print("Hola Mundo")
            except Exception:
                size = 1  # FTP does not always implement size

            if ".bin" in item_dir:
                files[item_dir] = size
            else:
                print("No es un binario.")

    files_directory = files
    return files_directory


def _is_ftp_dir(ftp_handler, item_dir, guess_by_extension=True):
    """ simply determines if an item listed on the ftp server is a valid directory or not """

    # if the name has a "." in the fourth to last position, its probably a file extension
    # this is MUCH faster than trying to set every file to a working directory, and will work 99% of time.
    if guess_by_extension is True:
        if len(item_dir) >= 4:
            if item_dir[-4] == '.':
                return False

    original_cwd = ftp_handler.pwd()     # remember the current working directory
    try:
        ftp_handler.cwd(item_dir)            # try to set directory to new name
        ftp_handler.cwd(original_cwd)    # set it back to what it was
        return True
    except:
        return False





if __name__ == "__main__":
    main()
