class StorageError(Exception):
    pass


class NoFreeResource(StorageError):
    pass


class UserNotFound(StorageError):
    pass
