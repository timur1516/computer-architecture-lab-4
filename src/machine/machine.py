from __future__ import annotations

import logging
import sys

from src.constants import INTERRUPTS_HANDLER_ADDRESS
from src.isa.instructions.instruction import Instruction
from src.isa.util.data_translators import from_bytes_data, from_bytes_instructions
from src.machine.control_unit import ControlUnit
from src.machine.data_path import DataPath
from src.machine.exceptions.exceptions import SimulationError
from src.machine.util import int_list_to_str


def simulation(
    instructions: list[Instruction],
    data: list[int],
    input_timetable: dict[int, int],
    data_memory_size: int,
    limit: int,
) -> str:
    """Подготовка модели и запуск симуляции процессора.

    Выполняет:

    - инициализацию `ControlUnit` и `DataPath`

    - обработку исключений

    - контроль количества тактов

    - логирование
    """

    assert len(data) <= data_memory_size, "memory overflow"

    data_path = DataPath(data_memory_size, data)
    control_unit = ControlUnit(instructions, data_path, input_timetable, INTERRUPTS_HANDLER_ADDRESS)

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
    logging.info('output_buffer: "%s" | %s', int_list_to_str(data_path.output_buffer), data_path.output_buffer)

    return "output_buffer_str:\n{}\noutput_buffer_num:\n{}".format(
        int_list_to_str(data_path.output_buffer, True), data_path.output_buffer
    )


def main(instructions_file: str, data_file: str, input_timetable_file: str):
    """Функция запуска модели процессора. Параметры -- имена файлов с машинным
    кодом и расписанием прерываний с входными данными для симуляции.
    """

    with open(instructions_file, "rb") as file:
        binary_instructions = file.read()
    instructions = from_bytes_instructions(binary_instructions)

    with open(data_file, "rb") as file:
        binary_data = file.read()
    data = from_bytes_data(binary_data)

    input_timetable = {}
    with open(input_timetable_file, encoding="utf-8") as f:
        for line in f:
            num, value = line.strip().split()
            try:
                value = int(value)
            except ValueError:
                value = ord(value)
            input_timetable[int(num)] = value

    output = simulation(
        instructions,
        data,
        input_timetable,
        data_memory_size=1000,
        limit=20000,
    )

    print("".join(output))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    assert len(sys.argv) == 4, "Wrong arguments: machine.py <instructions_bin_file> <data_bin_file> <input_file>"
    _, instructions_bin_file, data_bin_file, input_file = sys.argv
    main(instructions_bin_file, data_bin_file, input_file)
