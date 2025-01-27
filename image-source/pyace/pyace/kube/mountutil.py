import os

from werkzeug.security import generate_password_hash


def subdirs_file_content_to_dict(root_dir, split_by_line: bool = True, subdict_by_path: bool = False,
                                 file_filter=lambda x: True, path_filter=lambda x: True):
    """Function to generate a dictionary with file paths as keys and the file content as value. Options exist to create
    sub-dictionaries for subdirectories, or to create the file content as lines array instead of string. File and path
    filters also applicable.

    :param root_dir: directory to build the dictionary from
    :type root_dir: string
    :param split_by_line: indication whether to create the file content as line array instead of string
    :type split_by_line: boolean
    :param subdict_by_path: indication whether to create sub-dictionaries for subdirectories
    :type subdict_by_path: boolean
    :param file_filter: file filter for the inclusion to the result dictionary
    :type file_filter: function
    :param path_filter: path filter for the inclusion to the result dictionary
    :type path_filter: function
    :returns: dictionary"""
    def post_process(open_file):
        res = open_file.read()
        if split_by_line:
            res = res.splitlines()
        return res

    result = dict()
    for root, dirs, files in filter(lambda x: len(x[2]) > 0, os.walk(root_dir)):
        subdir = root.removeprefix(root_dir).removeprefix(os.path.sep)
        if path_filter(subdir) and not subdir.startswith(".."):
            if subdir != "":
                subdir += os.path.sep
            result.update(tuple(
                (f"{subdir}{file}", post_process(open(f"{root.rstrip(os.path.sep)}{os.path.sep}{file}", "r"))) for file
                in filter(file_filter, files)))
    if not subdict_by_path:
        return result
    else:
        subdicted_result = dict()
        for path, content in result.items():
            temp = subdicted_result
            for dir in path.split(os.path.sep)[:-1]:
                if dir not in temp.keys():
                    temp[dir] = dict()
                temp = temp[dir]
            temp[path.split(os.path.sep)[-1]] = content
        return subdicted_result


def hash_dict_values(input_dict):
    """Generates password hashes for a user-pw dictionary

    :param input_dict: user-password values
    :type input_dict: dictionary"""
    input_dict.update(dict((x, generate_password_hash(y)) for x, y in input_dict.items()))


def create_dir_if_not_exists(path):
    """Creates a directory (and sub-directories) on disk if the path does not exist

    :param path: desired path to be created if not readily available
    :type path: string"""
    if not os.path.exists(path):
        os.makedirs(path)
