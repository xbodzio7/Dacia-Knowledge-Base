from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Sequence
from xml.sax.saxutils import escape, quoteattr

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
FIXED_TIME = "2000-01-01T00:00:00Z"
INVALID_XML = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
FORBIDDEN_SHEET = re.compile(r"[\\/*?:\[\]]")
STYLE_IDS = {"normal": 0, "header": 1, "date": 2, "wrap": 3}


class WorkbookError(ValueError):
    """Raised when the fixed XLSX contract cannot be processed."""


@dataclass(frozen=True)
class Cell:
    value: object = None
    style: str = "normal"


@dataclass(frozen=True)
class Sheet:
    name: str
    rows: Sequence[Sequence[object]]
    widths: Sequence[float] = ()
    freeze_header: bool = True
    auto_filter: bool = True


def clean_text(value: object) -> str:
    return INVALID_XML.sub("", str(value))


def column_name(index: int) -> str:
    if index < 1:
        raise WorkbookError("column indexes are one-based")
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def validate_sheet_name(value: str) -> str:
    if not value or len(value) > 31 or FORBIDDEN_SHEET.search(value):
        raise WorkbookError(f"invalid worksheet name: {value!r}")
    return value


def decimal_text(value: Decimal) -> str:
    if not value.is_finite():
        raise WorkbookError("workbook numeric values must be finite")
    rendered = format(value, "f")
    return "0" if rendered in {"-0", ""} else rendered


def cell_xml(reference: str, item: object, default_style: str) -> str:
    cell = item if isinstance(item, Cell) else Cell(item, default_style)
    style = cell.style or default_style
    if style not in STYLE_IDS:
        raise WorkbookError(f"unsupported cell style: {style!r}")
    value = cell.value
    if value is None:
        return ""
    attributes = [f"r={quoteattr(reference)}"]
    style_id = STYLE_IDS["date"] if isinstance(value, date) else STYLE_IDS[style]
    if style_id:
        attributes.append(f"s={quoteattr(str(style_id))}")
    if isinstance(value, bool):
        attributes.append('t="b"')
        return f"<c {' '.join(attributes)}><v>{1 if value else 0}</v></c>"
    if isinstance(value, int):
        return f"<c {' '.join(attributes)}><v>{value}</v></c>"
    if isinstance(value, Decimal):
        return f"<c {' '.join(attributes)}><v>{decimal_text(value)}</v></c>"
    if isinstance(value, date):
        serial = (value - date(1899, 12, 30)).days
        return f"<c {' '.join(attributes)}><v>{serial}</v></c>"
    if isinstance(value, float):
        raise WorkbookError("float cells are unsupported; use Decimal")
    attributes.append('t="inlineStr"')
    text = clean_text(value)
    preserve = bool(text) and (text[0].isspace() or text[-1].isspace())
    space = ' xml:space="preserve"' if preserve else ""
    return f"<c {' '.join(attributes)}><is><t{space}>{escape(text)}</t></is></c>"
