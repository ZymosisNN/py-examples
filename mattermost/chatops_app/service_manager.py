from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict

from chatops_app.abstracts import AbstractService, ServiceRequest, ServiceResult, LogMixin, ChatOpsError


class ServiceManagerError(ChatOpsError):
    pass


class ServiceManager(LogMixin):
    def __init__(self, threads_count: int):
        super().__init__()
        self._executor = ThreadPoolExecutor(max_workers=threads_count)
        self._services: Dict[str, AbstractService] = {}

    def register_service(self, service: AbstractService):
        """
        This must be used to register services which will be used to handle requests
        A service must inherit AbstractService
        """
        if service.name in self._services:
            raise ServiceManagerError(f'Service "{service.name}" has already been registered')
        self._services[service.name] = service
        self._log.debug(f'Service "{service.name}" registered')

    def request(self, request: ServiceRequest) -> ServiceResult:
        """
        Blocking call: service processes data in the caller's thread
        response_service_name and response_data are ignored
        """
        service = self._get_service(request.service_name)
        return service.exec(request.data)

    def request_in_thread(self, request: ServiceRequest) -> Future:
        """
        Non-blocking call: service processes data in a separate thread
        The result can be sent to response_service if response_service_name is not None
        A future is returned to a caller
        """
        service = self._get_service(request.service_name)
        if not request.response_service_name:
            return self._make_task(service.exec, request.data)

        def do():
            result: ServiceResult = service.exec(request.data)
            if result.error:
                raise ServiceManagerError(f'Service "{request.service_name}" failed: {result.error}')

            data = request.response_data
            data.update(result.content)

            rsp_service = self._get_service(request.response_service_name)
            rsp_service.exec(data)

        return self._make_task(do)

    def _get_service(self, srv_name: str):
        try:
            return self._services[srv_name]
        except KeyError:
            raise ServiceManagerError(f'Service "{srv_name}" is not registered')

    def _make_task(self, func, *args, **kwargs) -> Future:
        self._log.debug('Starting a task thread')
        future = self._executor.submit(func, *args, **kwargs)

        def log_exceptions(done_future: Future):
            try:
                done_future.result()
            except Exception as ex:
                self._log.error(f'EXCEPTION in task thread: {ex}')
                raise ServiceManagerError(ex) from ex

        future.add_done_callback(log_exceptions)
        return future
