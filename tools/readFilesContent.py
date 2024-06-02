from runtime import Args
from typings.readFilesContent.readFilesContent import Input, Output
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


def get_github_file_content(owner, repo, filepath):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filepath}"
    headers = {
        "Accept": "application/vnd.github.v3.raw"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"unable to fetch file contents, HTTP status code is {response.status_code}")


def handler(args: Args[Input]) -> Output:
    owner, repo, paths = args.input.owner, args.input.repo, args.input.paths
    try:
        files = list()
        for path in paths:
            raw = get_github_file_content(owner, repo, path.strip('/'))
            files.append({"path": path, "content": raw})
        return {"files": files, "status": True, "status_msg": "ok"}
    except Exception as e:
        return {"status": False, "status_msg": str(e)}


if __name__ == "__main__":
    args = Args(Input(owner='ahaostudy', repo='github_reader', paths=['README.md', 'readFilesContent.py']))
    print(handler(args))
