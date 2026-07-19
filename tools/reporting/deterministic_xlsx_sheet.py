from __future__ import annotations

from reporting.deterministic_xlsx_model import (
    MAIN_NS,
    Sheet,
    WorkbookError,
    cell_xml,
    column_name,
    validate_sheet_name,
)


def sheet_xml(sheet: Sheet) -> str:
    validate_sheet_name(sheet.name)
    rows = [tuple(row) for row in sheet.rows]
    columns = max((len(row) for row in rows), default=1)
    row_count = max(len(rows), 1)
    dimension = f"A1:{column_name(columns)}{row_count}"
    parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<worksheet xmlns="{MAIN_NS}">',
        f'<dimension ref="{dimension}"/>',
        '<sheetViews><sheetView workbookViewId="0">',
    ]
    if sheet.freeze_header and rows:
        parts.append(
            '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" '
            'state="frozen"/>'
        )
    parts.extend(
        ['</sheetView></sheetViews>', '<sheetFormatPr defaultRowHeight="15"/>']
    )
    if sheet.widths:
        parts.append("<cols>")
        for index, width in enumerate(sheet.widths, start=1):
            if width <= 0:
                raise WorkbookError("column widths must be positive")
            parts.append(
                f'<col min="{index}" max="{index}" width="{width:g}" '
                'customWidth="1"/>'
            )
        parts.append("</cols>")
    parts.append("<sheetData>")
    for row_number, row in enumerate(rows, start=1):
        parts.append(f'<row r="{row_number}">')
        default_style = "header" if row_number == 1 else "normal"
        for column_number, value in enumerate(row, start=1):
            rendered = cell_xml(
                f"{column_name(column_number)}{row_number}",
                value,
                default_style,
            )
            if rendered:
                parts.append(rendered)
        parts.append("</row>")
    parts.append("</sheetData>")
    if sheet.auto_filter and rows:
        parts.append(f'<autoFilter ref="{dimension}"/>')
    parts.append("</worksheet>")
    return "".join(parts)
