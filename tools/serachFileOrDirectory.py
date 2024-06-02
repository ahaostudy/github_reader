from runtime import Args
from typings.searchFileOrDirectory.searchFileOrDirectory import Input, Output

import requests

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


def handler(args: Args[Input]) -> Output:
    owner, repo, name = args.input.owner, args.input.repo, args.input.name

    try:
        default_branch = get_default_branch(owner, repo)
        nodes = get_repo_tree(owner, repo, default_branch)
        result = list()
        for node in nodes.get('tree'):
            path, typ = node.get('path'), 'dir' if node.get('type') == 'tree' else 'file'
            if name in path:
                result.append({"type": typ, "path": path})
        return {"result": result, "status": True, "status_msg": "ok"}
    except Exception as e:
        return {"status": False, "status_msg": str(e)}
