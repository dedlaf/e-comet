from fastapi import HTTPException

"""
Три кастомных ошибки для RepoService, 
для более удобного отслеживания проблем,
а также сокращения строк кода.
"""


class RepoServiceExceptions:
    class RepoServiceException(HTTPException):
        def __init__(self, status_code: int, detail: str):
            super().__init__(status_code=status_code, detail=detail)

    class InternalRepoServiceException(RepoServiceException):
        def __init__(
            self, detail: str = "An error occurred while processing the request"
        ):
            super().__init__(status_code=500, detail=detail)

    class RateLimitExceededException(RepoServiceException):
        def __init__(self):
            super().__init__(
                status_code=403,
                detail="GitHub API rate limit exceeded. Please try again later.",
            )
