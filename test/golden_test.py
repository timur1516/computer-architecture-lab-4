import contextlib
import io
import logging
import os
import tempfile

import pytest
import src.machine.machine as machine
import src.translator.translator as translator

MAX_LOG = 4000


@pytest.mark.golden_test("golden/*.yml")
def test_translator_and_machine(golden, caplog):
    caplog.set_level(logging.DEBUG)

    with tempfile.TemporaryDirectory() as tmpdirname:
        source = os.path.join(tmpdirname, "source.fs")
        input_stream = os.path.join(tmpdirname, "input.txt")
        target = os.path.join(tmpdirname, "target.bin")
        target_hex = os.path.join(tmpdirname, "target.bin.hex")

        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["in_source"])
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["in_stdin"])

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main(source, target)
            print("============================================================")
            machine.main(target, input_stream)

        with open(target, "rb") as file:
            code = file.read()
        with open(target_hex, encoding="utf-8") as file:
            code_hex = file.read()

        assert code == golden.out["out_code"]
        assert code_hex == golden.out["out_code_hex"]
        assert stdout.getvalue() == golden.out["out_stdout"]
        assert caplog.text[0:MAX_LOG] + "EOF" == golden.out["out_log"]
