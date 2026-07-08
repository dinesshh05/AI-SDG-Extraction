import os
 
from openpyxl import Workbook  # type: ignore
from openpyxl.styles import Font, Alignment  # type: ignore
 
 
SDG_TITLES = {
    1:  "SDG 1: No Poverty",
    2:  "SDG 2: End hunger, achieve food security and improved nutrition and promote sustainable agriculture",
    3:  "SDG 3: Good Health and Well-being",
    4:  "SDG 4: Quality Education",
    5:  "SDG 5: Gender Equality",
    6:  "SDG 6: Clean Water and Sanitation",
    7:  "SDG 7: Affordable and Clean Energy",
    8:  "SDG 8: Decent Work and Economic Growth",
    9:  "SDG 9: Industry, Innovation and Infrastructure",
    10: "SDG 10: Reduced Inequalities",
    11: "SDG 11: Sustainable Cities and Communities",
    12: "SDG 12: Responsible Consumption and Production",
    13: "SDG 13: Climate Action",
    14: "SDG 14: Life Below Water",
    15: "SDG 15: Life on Land",
    16: "SDG 16: Peace, Justice, and Strong Institutions",
    17: "SDG 17: Partnerships for the Goals",
}
 
HEADER_FONT = Font(bold=True, size=10)
BODY_FONT = Font(bold=False, size=10)
NO_ACTIVITY_TEXT = "No activity fetched"
 
 
def _group_by_sdg(initiatives):
    """One initiative can map to multiple SDGs, so it's repeated under each."""
 
    grouped = {sdg_no: [] for sdg_no in SDG_TITLES}
 
    for item in initiatives:
        for sdg_id in item.get("sdg_ids", []):
            if sdg_id in grouped:
                grouped[sdg_id].append(item)
 
    return grouped
 
 
def _format_activity_list(items):
 
    if not items:
        return NO_ACTIVITY_TEXT
 
    lines = []
 
    for i, item in enumerate(items, start=1):
        text = (item.get("description") or item.get("initiative_name", "")).strip()
        metric = item.get("metric", "")
        if metric:
            text = f"{text} ({metric})" if text else metric
        lines.append(f"{i}. {text}")
 
    return "\n".join(lines)
 
 
def export_to_excel(initiatives, output_path="output/sustainability_report.xlsx"):
 
    os.makedirs("output", exist_ok=True)
 
    wb = Workbook()
    ws = wb.active
    ws.title = "Sustainability Initiatives"
 
    grouped = _group_by_sdg(initiatives)
    row = 1
 
    for sdg_no in sorted(grouped):
 
        ws.cell(row=row, column=1, value=SDG_TITLES[sdg_no]).font = HEADER_FONT
        row += 1
 
        cell = ws.cell(row=row, column=1, value=_format_activity_list(grouped[sdg_no]))
        cell.font = BODY_FONT
        cell.alignment = Alignment(wrap_text=True)
        row += 2
 
    ws.column_dimensions["A"].width = 100
 
    wb.save(output_path)
    print(f"\nExcel saved to: {output_path}")
 
    return output_path
 