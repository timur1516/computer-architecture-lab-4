import sys
from typing import List

from src.isa.isa import from_bytes, Instruction
from src.machine.control_unit import ControlUnit
from src.machine.data_path import DataPath


def simulation(code: List[Instruction],
               input_timetable: List[tuple[int, chr]],
               init_data_memory: List[int],
               interrupt_vectors: List[int],
               is_interrupts_enabled: bool,
               data_memory_size: int,
               limit: int) -> List[chr]:
    assert len(init_data_memory) <= data_memory_size, 'memory overflow'

    data_path = DataPath(data_memory_size, init_data_memory, interrupt_vectors)
    control_unit = ControlUnit(code, data_path, input_timetable, is_interrupts_enabled)

    print(control_unit)
    try:
        while control_unit.get_tick() < limit:
            control_unit.process_next_tick()
            print(control_unit)
    except EOFError:
        print('Input buffer is empty!')
    except StopIteration:
        pass

    if control_unit.get_tick() >= limit:
        print('Ticks limit exceeded!')

    return data_path.output_buffer


def main(code_file: str, input_file: str):
    with open(code_file, "rb") as file:
        binary_code = file.read()
    code, data_memory, interrupt_vectors, is_interrupts_enabled = from_bytes(binary_code)

    input_timetable = []
    with open(input_file, 'r', encoding="utf-8") as f:
        for line in f:
            num, char = line.strip().split()
            input_timetable.append((int(num), char))

    output = simulation(
        code,
        input_timetable,
        data_memory,
        interrupt_vectors,
        is_interrupts_enabled,
        data_memory_size=100,
        limit=2000,
    )

    print("".join(output))


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: machine.py <code_file> <input_file>"
    _, code_file, input_file = sys.argv
    main(code_file, input_file)
