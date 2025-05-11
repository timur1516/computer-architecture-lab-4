import contextlib
import io
import logging
import os
import shutil
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
        input_timetable = os.path.join(tmpdirname, "input_timetable.txt")
        target_instructions = os.path.join(tmpdirname, "target_instructions.bin")
        target_instructions_hex = os.path.join(tmpdirname, "target_instructions.bin.hex")
        target_data = os.path.join(tmpdirname, "target_data.bin")
        target_data_hex = os.path.join(tmpdirname, "target_data.bin.hex")

        stdlib_dir = "examples/stdlib"
        shutil.copytree(stdlib_dir, os.path.join(tmpdirname, "stdlib"))

        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["in_source"])
        with open(input_timetable, "w", encoding="utf-8") as file:
            file.write(golden["in_stdin"])

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main(source, target_instructions, target_data)
            print("============================================================")
            machine.main(target_instructions, target_data, input_timetable)

        with open(target_instructions, "rb") as file:
            instructions = file.read()
        with open(target_instructions_hex, encoding="utf-8") as file:
            instructions_hex = file.read()
        with open(target_data, "rb") as file:
            data = file.read()
        with open(target_data_hex, encoding="utf-8") as file:
            data_hex = file.read()

        assert instructions == golden.out["out_instructions"]
        assert instructions_hex == golden.out["out_instructions_hex"]
        assert data == golden.out["out_data"]
        assert data_hex == golden.out["out_data_hex"]
        assert stdout.getvalue() == golden.out["out_stdout"]
        assert caplog.text[0:MAX_LOG] + "EOF" == golden.out["out_log"]
