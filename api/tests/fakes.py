from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace

_UNSET: object = object()


def ns(**kwargs: object) -> SimpleNamespace:
    return SimpleNamespace(**kwargs)


@dataclass(slots=True)
class FakeScalarResult:
    values: list[object]

    def all(self) -> list[object]:
        return list(self.values)


@dataclass(slots=True)
class FakeResult:
    rows: list[object] | object = _UNSET
    scalars_list: list[object] | object = _UNSET
    one_or_none_row: object = _UNSET
    scalar_one_or_none_value: object = _UNSET

    def all(self) -> list[object]:
        if self.rows is _UNSET:
            raise AssertionError("FakeResult.all() called but no rows configured")
        if isinstance(self.rows, list):
            return list(self.rows)
        raise AssertionError("FakeResult.rows must be a list when using .all()")

    def one_or_none(self) -> object | None:
        if self.one_or_none_row is not _UNSET:
            return self.one_or_none_row
        rows = self.all()
        if not rows:
            return None
        if len(rows) > 1:
            raise AssertionError("Expected at most one row for one_or_none()")
        return rows[0]

    def scalar_one_or_none(self) -> object | None:
        if self.scalar_one_or_none_value is not _UNSET:
            return self.scalar_one_or_none_value
        if self.scalars_list is not _UNSET:
            if not isinstance(self.scalars_list, list):
                raise TypeError(
                    "FakeResult.scalars_list must be a list when using scalar_one_or_none()"
                )
            if not self.scalars_list:
                return None
            if len(self.scalars_list) > 1:
                raise AssertionError(
                    "Expected at most one scalar for scalar_one_or_none()"
                )
            return self.scalars_list[0]
        return self.one_or_none()

    def scalars(self) -> FakeScalarResult:
        if self.scalars_list is _UNSET:
            rows = self.all()
            derived: list[object] = []
            for row in rows:
                if isinstance(row, tuple) and len(row) == 1:
                    derived.append(row[0])
                else:
                    derived.append(row)
            return FakeScalarResult(values=derived)
        if not isinstance(self.scalars_list, list):
            raise TypeError(
                "FakeResult.scalars_list must be a list when using scalars()"
            )
        return FakeScalarResult(values=list(self.scalars_list))

    def unique(self) -> FakeResult:
        return self


@dataclass(slots=True)
class FakeSession:
    results: list[FakeResult]
    executed: list[object] = field(default_factory=list, init=False)

    def execute(self, statement: object) -> FakeResult:
        self.executed.append(statement)
        if not self.results:
            raise AssertionError("Unexpected session.execute() call (no results left)")
        return self.results.pop(0)

    def scalar(self, statement: object) -> object | None:
        return self.execute(statement).scalar_one_or_none()
