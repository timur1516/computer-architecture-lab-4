import sys

from src.isa.isa import from_bytes
from src.machine.control_unit import ControlUnit
from src.machine.data_path import DataPath


def simulation(code, data_memory_size, limit):
    data_path = DataPath(data_memory_size)
    control_unit = ControlUnit(code, data_path)

    print(control_unit)
    try:
        while control_unit.get_tick() < limit:
            control_unit.process_next_tick()
            print(control_unit)
    except StopIteration:
        pass

    if control_unit.get_tick() >= limit:
        print('Ticks limit exceeded!')


def main(code_file: str):
    with open(code_file, "rb") as file:
        binary_code = file.read()
    code = from_bytes(binary_code)

    simulation(
        code,
        data_memory_size=100,
        limit=2000,
    )


if __name__ == "__main__":
    assert len(sys.argv) == 2, "Wrong arguments: machine.py <code_file>"
    _, code_file = sys.argv
    main(code_file)
