from github import Github
from github import Auth, Repository
from config_loader import GITHUB_TOKEN

auth = Auth.Token(GITHUB_TOKEN)


DEFAULT_JOBS = ["run-autograding-tests", "test", "build", "Autograding"]


def is_user_exist(username: str) -> bool:
    g = Github(auth=auth)
    try:
        user = g.get_user(username)
        g.close()
        return user is not None
    except:
        g.close()
        return False


def get_org_repo(org_name:str, repo_name:str) -> Repository:
    g = Github(auth=auth)
    try:
        org = g.get_organization(org_name)
        repo = org.get_repo(repo_name)

        g.close()
        return repo
    except:
        g.close()
        return None


def check_workflows_runs(repository: Repository, workflows_list: list):
    if len(workflows_list) == 0:
        workflows_list = DEFAULT_JOBS

    default_branch = repository.default_branch

    commits = repository.get_commits(sha=default_branch)
    latest_commit_sha = commits[0].sha

    workflow_runs = repository.get_workflow_runs(branch=default_branch)

    runs = []
    logs = []
    for workflow_run in workflow_runs:
        if workflow_run.head_sha == latest_commit_sha:
            if workflow_run.status == "completed":
                runs.append(workflow_run.updated_at)
                logs.append(workflow_run.logs_url)

            else:
                raise Exception("repository has unsuccessful jobs")

    return runs, logs
