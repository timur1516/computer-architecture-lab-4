from __future__ import annotations

import os
import re

from src.translator.exceptions.exceptions import IncludeFileNotFoundError, IncludeFileReadingError


class IncludePreprocessor:
    """Выполняет обработку директив, начинающихся с символа `#`

    Поддерживаемые директивы:

    - ``#include "path-to-file"`` -- выполняется подстановка содержимого файла вместо директивы
    """

    src_file_text = None
    "Исходный код"

    src_file_name = None
    "Директория, в которой находится обрабатываемый файл"

    include_history: set[str] = None
    "Множество для хранения подключённых файлов. Используется для выявления циклических и повторяющихся зависимостей"

    def __init__(self, text: str, file_name: str):
        self.src_file_text = text
        self.src_file_name = file_name
        self.include_history = set()

    def preprocess(self):
        return self.include_preprocessor(self.src_file_text, self.src_file_name)

    def include_preprocessor(self, src_file_text: str, src_file_name: str) -> str:
        """Выполняет обработку директивы `include`"""

        if src_file_name in self.include_history:
            return ""

        self.include_history.add(src_file_name)
        src_file_dir = os.path.dirname(os.path.abspath(src_file_name))

        def replacement_function(match):
            included_file_path = match.group(1)
            included_file_full_path = os.path.join(src_file_dir, included_file_path)

            try:
                with open(included_file_full_path, encoding="utf-8") as file:
                    included_file_text = file.read()
                    return f"\n{self.include_preprocessor(included_file_text, included_file_full_path)}\n"
            except FileNotFoundError as e:
                raise IncludeFileNotFoundError(included_file_path) from e
            except Exception as e:
                raise IncludeFileReadingError(included_file_path) from e

        return re.sub(r'#include\s*"(.*?)"', replacement_function, src_file_text)
