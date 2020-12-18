from io import StringIO
from typing import Optional

from cleo.commands import Command
from cleo.io.buffered_io import BufferedIO
from cleo.io.inputs.string_input import StringInput
from cleo.io.outputs.output import Verbosity


class CommandTester(object):
    """
    Eases the testing of console commands.
    """

    def __init__(self, command: Command) -> None:
        self._command = command
        self._io = BufferedIO()
        self._inputs = []
        self._status_code = None

    @property
    def io(self) -> BufferedIO:
        return self._io

    @property
    def status_code(self):  # type: () -> int
        return self._status_code

    def execute(
        self,
        args: str,
        inputs: Optional[str] = None,
        interactive: Optional[bool] = None,
        verbosity: Optional[Verbosity] = None,
        decorated: Optional[bool] = None,
    ) -> int:
        """
        Executes the command
        """
        application = self._command.application
        if application is not None and application.definition.has_argument("command"):
            args = self._command.name + " " + args

        input = StringInput(args)
        self._io.set_input(input)

        if inputs is not None:
            self._io.input.set_stream(StringIO(inputs))

        if interactive is not None:
            self._io.interactive(interactive)

        if verbosity is not None:
            self._io.set_verbosity(verbosity)

        if decorated is not None:
            self._io.decorated(decorated)

        self._status_code = self._command.run(self._io)

        return self._status_code
