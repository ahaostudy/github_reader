from runtime import Args
from typings.readProjectStructure.readProjectStructure import Input, Output

import json
import requests
from enum import Enum
from typing import List, Optional

"""
Each file needs to export a function named `handler`. This function is the entrance to the Tool.

Parameters:
args: parameters of the entry function.
args.input - input parameters, you can get test input value by args.input.xxx.
args.logger - logger instance used to print logs, injected by runtime.

Remember to fill in input/output in Metadata, it helps LLM to recognize and use tool.

Return:
The return data of the function, which should match the declared output parameters.
"""


class FileType(Enum):
    FILE = "file"
    DIRECTORY = "dir"


class FileNode:
    def __init__(self, path: str = '', typ: FileType = FileType.DIRECTORY, size: Optional[int] = None):
        self.path = path
        self.type = typ
        self.size = size
        self.children = list()

    def add_child(self, child):
        self.children.append(child)

    def __str__(self):
        return ', '.join(['%s: %s' % item for item in self.__dict__.items()])


def json_serializer(obj):
    if isinstance(obj, FileNode):
        return obj.__dict__
    if isinstance(obj, FileType):
        return obj.value
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def join_path(pa, pb):
    return pa + ('/' if len(pa) else '') + pb


def get_default_branch(owner, repo):
    """
    Get the default branch of the repository
    """
    url = f'https://api.github.com/repos/{owner}/{repo}'
    resp = requests.get(url)

    if resp.status_code == 200:
        repo_info = resp.json()
        return repo_info['default_branch']
    else:
        raise Exception(f"Error: Unable to fetch repository info. Status code: {resp.status_code}")


def get_repo_tree(owner, repo, sha):
    """
    Get the directory tree of the specified branch
    """
    url = f'https://api.github.com/repos/{owner}/{repo}/git/trees/{sha}?recursive=1'
    resp = requests.get(url)

    if resp.status_code == 200:
        return resp.json()
    else:
        raise Exception(f"Error: Unable to fetch repository tree. Status code: {resp.status_code}")


def get_base_url(path: str) -> str:
    path = path.strip('/')
    i = len(path) - 1
    while i >= 0:
        if path[i] == '/':
            return path[:i]
        i -= 1
    return ''


def get_tree_by_path(owner: str, repo: str, path: str) -> List[FileNode]:
    """
    Get the directory tree under the specified path
    """
    default_branch = get_default_branch(owner, repo)
    tree = get_repo_tree(owner, repo, default_branch)

    nodes = {path: FileNode(path)}
    for child in tree.get('tree'):
        cpath: str = child.get('path', '')
        ctype = FileType.DIRECTORY if child.get('type') == 'tree' else FileType.FILE
        if len(cpath) > len(path) and cpath.startswith(path):
            node = FileNode(cpath, ctype, child.get('size'))
            nodes[cpath] = node
            nodes[get_base_url(cpath)].add_child(node)
    return nodes[path].children


def get_files_by_path(owner: str, repo: str, path: str) -> List[FileNode]:
    """
    Get all files under the specified path
    """
    get_repository_content_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
    resp = requests.get(get_repository_content_url)

    if resp.status_code == 200:
        children = list()
        for item in resp.json():
            child = FileNode(join_path(path, item.get('name')), item.get('type'), item.get('size'))
            children.append(child)
        return children
    else:
        raise Exception(f'Error: Unable to fetch repository tree. Status code: {resp.status_code}')


def handler(args: Args[Input]) -> Output:
    try:
        owner, repo, path = args.input.owner, args.input.repo, args.input.path.strip('/')
        if args.input.recursion:
            children = get_tree_by_path(owner, repo, path)
        else:
            children = get_files_by_path(owner, repo, path)
        return {"children": json.dumps(children, default=json_serializer), "status": True, "status_msg": "ok"}
    except Exception as e:
        return {"status": False, "status_msg": str(e)}
