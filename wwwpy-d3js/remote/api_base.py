from typing import Callable, Coroutine, Awaitable

from pydantic import BaseModel


class ApiBase(BaseModel):
    class Config:
        validate_assignment = True

    async def send(self, transport: 'ApiTransportType' = None):
        if transport is None:
            transport = _global_transport
        return await transport(self)

    @classmethod
    def check_request_completeness(cls, request_type):
        if not hasattr(request_type, 'response_type'):
            name = request_type.__name__
            raise Exception(f'Request type `{name}` must have a static '
                            f'property `response_type` to designate the response type')


async def _no_send(request):
    raise Exception('no send was configured. Use `api_send_set(...)`.')


ApiTransportType = Callable[[ApiBase], Awaitable[BaseModel]]
_global_transport: ApiTransportType = _no_send


def global_transport_set(send: ApiTransportType):
    global _global_transport
    _global_transport = send
