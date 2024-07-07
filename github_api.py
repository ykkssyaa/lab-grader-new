from github import Github
from github import Auth
from config_loader import GITHUB_TOKEN

auth = Auth.Token(GITHUB_TOKEN)


def is_user_exist(username: str) -> bool:
    g = Github(auth=auth)
    try:
        user = g.get_user(username)
        return user is not None
    except:
        return False


def main():
    g = Github(auth=auth)

    org_name = 'suai-os-2024'
    organization = g.get_organization(org_name)

    print("Название организации:", organization.name)
    print("Описание:", organization.description)
    print("Местоположение:", organization.location)
    print("Электронная почта:", organization.email)
    print("Блог:", organization.blog)
    print("Публичные репозитории:", organization.public_repos)
    print("Создана:", organization.created_at)

    for repo in organization.get_repos():
        print("---")
        print(repo.name)
        print(repo.description)
        print(repo.created_at)
        print(repo.stargazers_count)
        print(repo.language)

    # To close connections after use
    g.close()



