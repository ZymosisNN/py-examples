from argparse import ArgumentParser
from typing import Optional, IO, Text, NoReturn


class CommandArgParser(ArgumentParser):
    def __init__(self, *args, internal=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.internal = internal
        self.add_argument('-all', action='store_true')
        self.add_argument('-thread', action='store_true')

    def print_usage(self, file: Optional[IO[str]] = ...) -> None:
        pass

    def print_help(self, file: Optional[IO[str]] = ...) -> None:
        pass

    def exit(self, status: int = ..., message: Optional[Text] = ...) -> NoReturn:
        pass

    def error(self, message: Text) -> NoReturn:
        raise CommandArgParserError(message)


class CommandArgParserError(Exception):
    pass
