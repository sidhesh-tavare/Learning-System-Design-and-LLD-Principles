# Complete ReportService — Python LLD

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Protocol
import csv
import io
import json


# Protocol: sinks need compatible capabilities, not shared inheritance.
class WritableSink(Protocol):
    def write(self, report: str) -> None:
        ...


# ISP: reading is a separate capability.
class ReadableSink(Protocol):
    def read_all(self) -> list[str]:
        ...

class ConsoleSink:
    def write(self, report: str) -> None:
        print(report)

#File Sink has both the protocols of read_all and write - ie both WritableSink and Readable Sink
class FileSink:
    def __init__(self, filepath: str) -> None:
        self.filepath = Path(filepath)

    def write(self, report: str) -> None:
        with self.filepath.open("a", encoding="utf-8") as file:
            file.write(report + "\n")

    def read_all(self) -> list[str]:
        if not self.filepath.exists():
            return []
        return self.filepath.read_text(
            encoding="utf-8"
        ).splitlines()


# Satisfies WritableSink and ReadableSink without inheritance.
class FakeSink:
    def __init__(self) -> None:
        self.reports: list[str] = []

    def write(self, report: str) -> None:
        self.reports.append(report)

    def read_all(self) -> list[str]:
        return self.reports.copy()


# ABC: formatters share an algorithm and validation logic and seequence so its an abc child classes have the smae flow with differnet formating methods 
class BaseFormatter(ABC):
    def format(self, data: dict[str, object]) -> str:
        self.validate(data)
        return self._format_data(data)

    def validate(self, data: dict[str, object]) -> None:
        if not isinstance(data, dict):
            raise ValueError("Report data must be a dictionary")
        if not data:
            raise ValueError("Report data cannot be empty")

    @abstractmethod
    def _format_data(self, data: dict[str, object]) -> str:
        pass


class CsvFormatter(BaseFormatter):
    def _format_data(self, data: dict[str, object]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(data.keys())
        writer.writerow(data.values())
        return output.getvalue().rstrip("\r\n")


class JsonFormatter(BaseFormatter):
    def _format_data(self, data: dict[str, object]) -> str:
        return json.dumps(data)


class ReportService:
    def __init__(
        self,
        sink: WritableSink,
        formatter: BaseFormatter,
    ) -> None:
        self.sink = sink
        self.formatter = formatter

    def send(self, data: dict[str, object]) -> str:
        report = self.formatter.format(data)
        self.sink.write(report)
        return report


def main() -> None:
    data: dict[str, object] = {
        "name": "Sid",
        "score": 90,
    }

    print("--- Console + CSV ---")
    service1 = ReportService(ConsoleSink(), CsvFormatter())
    service1.send(data)

    print("\n--- File + JSON ---")
    file_sink = FileSink("reports.txt")
    service2 = ReportService(file_sink, JsonFormatter())
    service2.send(data)
    print("Reports in file:", file_sink.read_all())

    print("\n--- FakeSink + JSON ---")
    fake_sink = FakeSink()
    service3 = ReportService(fake_sink, JsonFormatter())
    service3.send(data)
    print("Captured reports:", fake_sink.read_all())


if __name__ == "__main__":
    main()

