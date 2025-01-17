from enum import Enum

""""
Энамы, чтобы мы могли быть уверены, в корректности
запросов, а также, чтобы менять их в одном месте, вместо
изменения в других файлах
"""


class GitHubURL(str, Enum):
    BASE_URL = "https://api.github.com/"
    REPOS_URL = "https://api.github.com/search/repositories?q=stars:%3E50000&sort=stars&order=desc&per_page=100"


class SQLQueries(Enum):
    UPDATE_REPO = """
        UPDATE top100
        SET owner = %s,
            stars = %s,
            watchers = %s,
            forks = %s,
            open_issues = %s,
            language = %s,
            position_prev = position_cur,
            position_cur = %s
        WHERE repo = %s
        RETURNING repo
    """

    UPDATE_POSITIONS = """
        WITH ranked_repos AS (
            SELECT repo, ROW_NUMBER() OVER (ORDER BY stars DESC) AS rank
            FROM top100
        )
        UPDATE top100 SET
            position_prev = position_cur,
            position_cur = ranked_repos.rank
        FROM ranked_repos
        WHERE top100.repo = ranked_repos.repo;
    """

    INSERT_REPO = """
        INSERT INTO top100 (repo, owner, stars, watchers, forks, open_issues, language, position_prev, position_cur)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
