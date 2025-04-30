from __future__ import annotations

import logging
import sys

from src.isa.instructions.instruction import Instruction
from src.isa.util.data_translators import from_bytes
from src.machine.control_unit import ControlUnit
from src.machine.data_path import DataPath
from src.machine.exceptions.exceptions import SimulationError


def simulation(
    code: list[Instruction],
    input_timetable: list[tuple[int, chr]],
    init_data_memory: list[int],
    interrupt_handler_address: int,
    is_interrupts_enabled: bool,
    data_memory_size: int,
    limit: int,
) -> str:
    assert len(init_data_memory) <= data_memory_size, "memory overflow"

    data_path = DataPath(data_memory_size, init_data_memory)
    control_unit = ControlUnit(code, data_path, input_timetable, is_interrupts_enabled, interrupt_handler_address)

    logging.debug("%s", control_unit)
    try:
        while control_unit.get_tick() < limit:
            control_unit.process_next_tick()
            logging.debug("%s", control_unit)
    except SimulationError as e:
        logging.warning(e)
    except StopIteration:
        pass

    if control_unit.get_tick() >= limit:
        logging.warning("Limit exceeded!")
    logging.info("output_buffer: %s", repr("".join(data_path.output_buffer)))
    return "".join(data_path.output_buffer)


def main(code_file: str, input_file: str):
    with open(code_file, "rb") as file:
        binary_code = file.read()
    code, data_memory, interrupt_handler_address, is_interrupts_enabled = from_bytes(binary_code)

    input_timetable = []
    if is_interrupts_enabled:
        with open(input_file, encoding="utf-8") as f:
            for line in f:
                num, char = line.strip().split()
                input_timetable.append((int(num), char))

    output = simulation(
        code,
        input_timetable,
        data_memory,
        interrupt_handler_address,
        is_interrupts_enabled,
        data_memory_size=100,
        limit=2000,
    )

    print("".join(output))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    assert len(sys.argv) == 3, "Wrong arguments: machine.py <code_file> <input_file>"
    _, code_file, input_file = sys.argv
    main(code_file, input_file)
