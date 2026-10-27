from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Sequence
from xml.sax.saxutils import quoteattr
from zipfile import ZIP_STORED, ZipFile, ZipInfo

from reporting.deterministic_xlsx_model import (
    CONTENT_NS,
    FIXED_TIME,
    MAIN_NS,
    PKG_REL_NS,
    REL_NS,
    STYLE_IDS,
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


def _content_types(count: int) -> str:
    overrides = [
        ('/xl/workbook.xml', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml'),
        ('/xl/styles.xml', 'application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml'),
        ('/docProps/core.xml', 'application/vnd.openxmlformats-package.core-properties+xml'),
        ('/docProps/app.xml', 'application/vnd.openxmlformats-officedocument.extended-properties+xml'),
    ]
    overrides.extend(
        (f"/xl/worksheets/sheet{i}.xml", "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml")
        for i in range(1, count + 1)
    )
    items = "".join(
        f'<Override PartName={quoteattr(path)} ContentType={quoteattr(kind)}/>'
        for path, kind in overrides
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Types xmlns="{CONTENT_NS}">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        f"{items}</Types>"
    )


def _package_rels() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Relationships xmlns="{PKG_REL_NS}">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        '</Relationships>'
    )


def _workbook_xml(sheets: Sequence[Sheet]) -> str:
    items = "".join(
        f'<sheet name={quoteattr(sheet.name)} sheetId="{i}" r:id="rId{i}"/>'
        for i, sheet in enumerate(sheets, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<workbook xmlns="{MAIN_NS}" xmlns:r="{REL_NS}">'
        '<workbookPr date1904="0"/>'
        '<bookViews><workbookView activeTab="0" firstSheet="0"/></bookViews>'
        f'<sheets>{items}</sheets></workbook>'
    )


def _workbook_rels(count: int) -> str:
    items = "".join(
        f'<Relationship Id="rId{i}" Type="{REL_NS}/worksheet" '
        f'Target="worksheets/sheet{i}.xml"/>'
        for i in range(1, count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Relationships xmlns="{PKG_REL_NS}">{items}'
        f'<Relationship Id="rId{count + 1}" Type="{REL_NS}/styles" '
        'Target="styles.xml"/></Relationships>'
    )


def _styles_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<styleSheet xmlns="{MAIN_NS}">'
        '<numFmts count="1"><numFmt numFmtId="164" formatCode="yyyy-mm-dd"/></numFmts>'
        '<fonts count="2"><font><sz val="11"/><name val="Calibri"/>'
        '<family val="2"/></font><font><b/><sz val="11"/>'
        '<name val="Calibri"/><family val="2"/></font></fonts>'
        '<fills count="3"><fill><patternFill patternType="none"/></fill>'
        '<fill><patternFill patternType="gray125"/></fill>'
        '<fill><patternFill patternType="solid"><fgColor rgb="FFD9E2F3"/>'
        '<bgColor indexed="64"/></patternFill></fill></fills>'
        '<borders count="2"><border><left/><right/><top/><bottom/>'
        '<diagonal/></border><border><left style="thin"><color auto="1"/>'
        '</left><right style="thin"><color auto="1"/></right>'
        '<top style="thin"><color auto="1"/></top><bottom style="thin">'
        '<color auto="1"/></bottom><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" '
        'borderId="0"/></cellStyleXfs><cellXfs count="4">'
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
        '<xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" '
        'applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">'
        '<alignment vertical="top" wrapText="1"/></xf>'
        '<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" '
        'applyNumberFormat="1"/><xf numFmtId="0" fontId="0" fillId="0" '
        'borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" '
        'wrapText="1"/></xf></cellXfs><cellStyles count="1">'
        '<cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        '<dxfs count="0"/><tableStyles count="0" '
        'defaultTableStyle="TableStyleMedium2" '
        'defaultPivotStyle="PivotStyleLight16"/></styleSheet>'
    )


def _core_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        '<dc:title>Dacia Knowledge Base Comparison Workbook</dc:title>'
        '<dc:creator>Dacia Knowledge Base</dc:creator>'
        '<cp:lastModifiedBy>Dacia Knowledge Base</cp:lastModifiedBy>'
        f'<dcterms:created xsi:type="dcterms:W3CDTF">{FIXED_TIME}</dcterms:created>'
        f'<dcterms:modified xsi:type="dcterms:W3CDTF">{FIXED_TIME}</dcterms:modified>'
        '</cp:coreProperties>'
    )


def _app_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
        '<Application>Dacia Knowledge Base</Application>'
        '<AppVersion>1.0</AppVersion></Properties>'
    )


def _zip_info(name: str) -> ZipInfo:
    info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def write_workbook(path: Path, sheets: Sequence[Sheet]) -> None:
    if not sheets:
        raise WorkbookError("workbook requires at least one worksheet")
    names = [validate_sheet_name(sheet.name) for sheet in sheets]
    if len(names) != len(set(names)):
        raise WorkbookError("worksheet names must be unique")
    entries = [
        ("[Content_Types].xml", _content_types(len(sheets))),
        ("_rels/.rels", _package_rels()),
        ("docProps/app.xml", _app_xml()),
        ("docProps/core.xml", _core_xml()),
        ("xl/workbook.xml", _workbook_xml(sheets)),
        ("xl/_rels/workbook.xml.rels", _workbook_rels(len(sheets))),
        ("xl/styles.xml", _styles_xml()),
    ]
    entries.extend(
        (f"xl/worksheets/sheet{i}.xml", sheet_xml(sheet))
        for i, sheet in enumerate(sheets, start=1)
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(path, "w", compression=ZIP_STORED) as archive:
        for name, content in entries:
            archive.writestr(_zip_info(name), content.encode("utf-8"))


def _targets(archive: ZipFile) -> dict[str, str]:
    root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    return {
        item.attrib["Id"]: item.attrib["Target"]
        for item in root.findall(f"{{{PKG_REL_NS}}}Relationship")
    }


def read_workbook(path: Path) -> dict[str, list[list[Any]]]:
    output: dict[str, list[list[Any]]] = {}
    with ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        targets = _targets(archive)
        for sheet in workbook.findall(f".//{{{MAIN_NS}}}sheet"):
            name = sheet.attrib["name"]
            relation = sheet.attrib[f"{{{REL_NS}}}id"]
            root = ET.fromstring(archive.read(f"xl/{targets[relation]}"))
            parsed: list[list[Any]] = []
            for row in root.findall(f".//{{{MAIN_NS}}}row"):
                values: list[Any] = []
                for cell in row.findall(f"{{{MAIN_NS}}}c"):
                    reference = cell.attrib["r"]
                    letters = "".join(ch for ch in reference if ch.isalpha())
                    column = 0
                    for character in letters:
                        column = column * 26 + ord(character) - 64
                    while len(values) < column:
                        values.append(None)
                    kind = cell.attrib.get("t", "")
                    style = int(cell.attrib.get("s", "0"))
                    if kind == "inlineStr":
                        value = "".join(
                            node.text or ""
                            for node in cell.findall(f".//{{{MAIN_NS}}}t")
                        )
                    else:
                        node = cell.find(f"{{{MAIN_NS}}}v")
                        raw = node.text if node is not None and node.text else ""
                        if kind == "b":
                            value = raw == "1"
                        elif style == STYLE_IDS["date"] and raw:
                            value = date(1899, 12, 30) + timedelta(days=int(raw))
                        elif raw:
                            number = Decimal(raw)
                            value = int(number) if number == number.to_integral() else number
                        else:
                            value = None
                    values[column - 1] = value
                parsed.append(values)
            output[name] = parsed
    return output


def workbook_entries(path: Path) -> tuple[str, ...]:
    with ZipFile(path) as archive:
        return tuple(archive.namelist())
