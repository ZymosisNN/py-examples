from ..common import LogMixin, SlashService, ServiceResult


class ServiceTools(SlashService, LogMixin):
    def __init__(self, name: str):
        super().__init__()
        self._name = name

    async def exec(self, cmd: str) -> ServiceResult:
        self.log.info(f'Execute cmd: {cmd}')
        result = ServiceResult()

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return f'Dummy implementation of "/{self.name}"'
