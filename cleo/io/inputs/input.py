import re

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import TextIO
from typing import Union

from cleo._compat import shell_quote
from cleo.exceptions import RuntimeException
from cleo.exceptions import ValueException

from .definition import Definition


class Input:
    """
    This class is the base class for concrete Input implementations.
    """

    def __init__(self, definition: Optional[Definition] = None) -> None:
        self._definition = None
        self._stream = None
        self._options = {}
        self._arguments = {}
        self._interactive = True

        if definition is None:
            self._definition = Definition()
        else:
            self.bind(definition)
            self.validate()

    @property
    def arguments(self) -> Dict[str, Any]:
        return {**self._definition.argument_defaults, **self._arguments}

    @property
    def options(self) -> Dict[str, Any]:
        return {**self._definition.option_defaults, **self._options}

    @property
    def stream(self) -> TextIO:
        return self._stream

    @property
    def first_argument(self) -> Optional[str]:
        """
        Returns the first argument from the raw parameters (not parsed).
        """
        raise NotImplementedError()

    @property
    def script_name(self) -> Optional[str]:
        raise NotImplementedError()

    def read(self, length: int, default: Optional[str] = None) -> str:
        """
        Reads the given amount of characters from the input stream.
        """
        if not self._interactive:
            return default

        return self._stream.read(length)

    def read_line(
        self, length: Optional[int] = None, default: Optional[str] = None
    ) -> str:
        """
        Reads a line from the input stream.
        """
        if not self._interactive:
            return default

        return self._stream.readline(length)

    def close(self) -> None:
        """
        Closes the input.
        """
        self._stream.close()

    def is_closed(self) -> bool:
        """
        Returns whether the input is closed.
        """
        return self._stream.is_closed()

    def is_interactive(self) -> bool:
        return self._interactive

    def interactive(self, interactive: bool = True) -> None:
        self._interactive = interactive

    def bind(self, definition: Definition) -> None:
        """
        Binds the current Input instance with
        the given definition's arguments and options.
        """
        self._arguments = {}
        self._options = {}
        self._definition = definition

        self._parse()

    def validate(self) -> None:
        missing_arguments = []

        for argument in self._definition.arguments:
            if argument.name not in self._arguments and argument.is_required():
                missing_arguments.append(argument.name)

        if missing_arguments:
            raise RuntimeException(
                'Not enough arguments (missing: "{}")'.format(
                    ", ".join(missing_arguments)
                )
            )

    def argument(self, name: str) -> Any:
        if not self._definition.has_argument(name):
            raise ValueException(f'The argument "{name}" does not exist')

        if name in self._arguments:
            return self._arguments[name]

        return self._definition.argument(name).default

    def set_argument(self, name: str, value: Any) -> None:
        if not self._definition.has_argument(name):
            raise ValueException(f'The argument "{name}" does not exist')

        self._arguments[name] = value

    def has_argument(self, name: str) -> bool:
        return self._definition.has_argument(name)

    def option(self, name: str) -> Any:
        if not self._definition.has_option(name):
            raise ValueException(f'The option "--{name}" does not exist')

        if name in self._options:
            return self._options[name]

        return self._definition.option(name).default

    def set_option(self, name: str, value: Any) -> None:
        if not self._definition.has_option(name):
            raise ValueException(f'The option "--{name}" does not exist')

        self._options[name] = value

    def has_option(self, name: str) -> bool:
        return self._definition.has_option(name)

    def escape_token(self, token: str) -> str:
        if re.match("^[\w-]+$"):
            return token

        return shell_quote(token)

    def set_stream(self, stream: TextIO) -> None:
        self._stream = stream

    def has_parameter_option(
        self, values: Union[str, List[str]], only_params: bool = False
    ) -> bool:
        """
        Returns true if the raw parameters (not parsed) contain a value.
        """
        raise NotImplementedError()

    def parameter_option(
        self,
        values: Union[str, List[str]],
        only_params: bool = False,
        default: Any = False,
    ) -> Any:
        """
        Returns the value of a raw option (not parsed).
        """
        raise NotImplementedError()

    def _parse(self) -> None:
        raise NotImplementedError()
