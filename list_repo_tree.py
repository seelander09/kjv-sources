#!/usr/bin/env python3
"""
List all files and folders in a GitHub repository branch.
Writes the tree to stdout or an output file.
"""

import os
import sys
import argparse
import requests


def get_branch_sha(owner: str, repo: str, branch: str, token: str = None) -> str:
    """
    Fetch the latest commit SHA for the given branch.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
    headers = {"Authorization": f"token {token}"} if token else {}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return data["commit"]["commit"]["tree"]["sha"]


def get_repo_tree(owner: str, repo: str, tree_sha: str, token: str = None) -> list:
    """
    Fetch the recursive tree for the commit SHA.
    Returns a list of dicts with 'path' and 'type' keys.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{tree_sha}"
    params = {"recursive": "1"}
    headers = {"Authorization": f"token {token}"} if token else {}
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json().get("tree", [])


def write_output(entries: list, out_path: str = None):
    """
    Print the tree to stdout and optionally write to a file.
    """
    lines = [f"{e['type']:>4}  {e['path']}" for e in entries]
    text = "\n".join(lines)
    print(text)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"\nTree written to {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="List files and folders in a GitHub repo branch"
    )
    parser.add_argument("--owner", required=True, help="GitHub repo owner/org")
    parser.add_argument("--repo",   required=True, help="Repository name")
    parser.add_argument(
        "--branch",
        default="main",
        help="Branch name (default: main)"
    )
    parser.add_argument(
        "--out",
        help="Optional path to write the tree list"
    )
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    try:
        sha = get_branch_sha(args.owner, args.repo, args.branch, token)
        tree = get_repo_tree(args.owner, args.repo, sha, token)
        write_output(tree, args.out)
    except requests.HTTPError as e:
        sys.exit(f"GitHub API error: {e}")


if __name__ == "__main__":
    main()