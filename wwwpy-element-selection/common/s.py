from __future__ import annotations
from typing import TypeVar, Generic, Protocol, Any, Type, runtime_checkable
import json
import unittest

T = TypeVar('T')
TypeHint = Any


class Encoder(Protocol):
    def encode_none(self) -> None: ...
    def encode_bool(self, value: bool) -> None: ...
    def encode_int(self, value: int) -> None: ...
    def encode_float(self, value: float) -> None: ...
    def encode_str(self, value: str) -> None: ...
    def begin_list(self, size: int | None = None) -> None: ...
    def end_list(self) -> None: ...
    def begin_object(self) -> None: ...
    def end_object(self) -> None: ...
    def encode_key(self, key: str) -> None: ...


class Decoder(Protocol):
    def decode_none(self) -> None: ...
    def decode_bool(self) -> bool: ...
    def decode_int(self) -> int: ...
    def decode_float(self) -> float: ...
    def decode_str(self) -> str: ...
    def begin_list(self) -> int | None: ...
    def end_list(self) -> None: ...
    def begin_object(self) -> None: ...
    def end_object(self) -> None: ...
    def decode_key(self) -> str: ...


class Serializer(Generic[T]):
    def serialize(self, encoder: Encoder, value: T, type_hint: TypeHint = None) -> None:
        raise NotImplementedError

    def deserialize(self, decoder: Decoder, type_hint: TypeHint) -> T:
        raise NotImplementedError


class SerializersRegistry:
    def __init__(self):
        self._registry: dict[Any, Serializer[Any]] = {}

    def register(self, type_: Any, serializer: Serializer[Any]) -> None:
        self._registry[type_] = serializer

    def get(self, type_hint: TypeHint) -> Serializer[Any]:
        if type_hint in self._registry:
            return self._registry[type_hint]
        raise TypeError(f"No serializer registered for type: {type_hint}")


class JsonEncoder:
    def __init__(self):
        self._stack = []
        self._current = None

    def encode_none(self) -> None:
        self._append(None)

    def encode_bool(self, value: bool) -> None:
        self._append(value)

    def encode_int(self, value: int) -> None:
        self._append(value)

    def encode_float(self, value: float) -> None:
        self._append(value)

    def encode_str(self, value: str) -> None:
        self._append(value)

    def begin_list(self, size: int | None = None) -> None:
        self._stack.append([])

    def end_list(self) -> None:
        lst = self._stack.pop()
        self._append(lst)

    def begin_object(self) -> None:
        self._stack.append({})

    def end_object(self) -> None:
        obj = self._stack.pop()
        self._append(obj)

    def encode_key(self, key: str) -> None:
        self._key = key

    def _append(self, value: Any) -> None:
        if not self._stack:
            self._current = value
        else:
            top = self._stack[-1]
            if isinstance(top, list):
                top.append(value)
            elif isinstance(top, dict):
                top[self._key] = value

    def finalize(self) -> str:
        return json.dumps(self._current)


class JsonDecoder:
    def __init__(self, data: str):
        self._root = json.loads(data)
        self._stack = [self._root]
        self._iterator = None

    def decode_none(self) -> None:
        return None

    def decode_bool(self) -> bool:
        return self._stack.pop()

    def decode_int(self) -> int:
        return self._stack.pop()

    def decode_float(self) -> float:
        return self._stack.pop()

    def decode_str(self) -> str:
        return self._stack.pop()

    def begin_list(self) -> int | None:
        lst = self._stack.pop()
        self._stack.append(lst)
        self._iterator = iter(lst)
        return len(lst)

    def end_list(self) -> None:
        self._stack.pop()

    def begin_object(self) -> None:
        obj = self._stack.pop()
        self._stack.append(obj)
        self._iterator = iter(obj.items())

    def end_object(self) -> None:
        self._stack.pop()

    def decode_key(self) -> str:
        key, value = next(self._iterator)
        self._stack.append(value)
        return key


class JsonFormat:
    def __init__(self, registry: SerializersRegistry):
        self.registry = registry

    def dumps(self, value: Any, type_hint: TypeHint = None) -> str:
        encoder = JsonEncoder()
        serializer = self.registry.get(type_hint or type(value))
        serializer.serialize(encoder, value, type_hint)
        return encoder.finalize()

    def loads(self, data: str, type_hint: TypeHint) -> Any:
        decoder = JsonDecoder(data)
        serializer = self.registry.get(type_hint)
        return serializer.deserialize(decoder, type_hint)


class IntSerializer(Serializer[int]):
    def serialize(self, encoder: Encoder, value: int, type_hint: TypeHint = None) -> None:
        encoder.encode_int(value)

    def deserialize(self, decoder: Decoder, type_hint: TypeHint) -> int:
        return decoder.decode_int()


class TestJsonFormat(unittest.TestCase):
    def test_int_serialization(self):
        registry = SerializersRegistry()
        registry.register(int, IntSerializer())
        json_format = JsonFormat(registry)

        original = 42
        json_str = json_format.dumps(original, int)
        restored = json_format.loads(json_str, int)

        self.assertEqual(original, restored)


if __name__ == '__main__':
    unittest.main()
