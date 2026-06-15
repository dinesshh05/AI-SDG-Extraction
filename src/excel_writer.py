import os

from openpyxl import Workbook  # type: ignore


def export_to_excel(
    initiatives,
    output_path="output/sustainability_report.xlsx"
):

    os.makedirs(
        "output",
        exist_ok=True
    )

    wb = Workbook()

    ws = wb.active

    ws.title = "Sustainability Initiatives"

    headers = [
        "Initiative Name",
        "Description",
        "Metric",
        "SDG IDs",
        "SDG Names",
        "Evidence",
        "Page Reference"
    ]

    ws.append(headers)

    for item in initiatives:

        ws.append(
            [
                item["initiative_name"],
                item["description"],
                item["metric"],
                ", ".join(
                    str(x)
                    for x in item["sdg_ids"]
                ),
                ", ".join(
                    item["sdg_names"]
                ),
                item["evidence"],
                item["page_reference"]
            ]
        )

    wb.save(
        output_path
    )

    print(
        f"\nExcel saved to: {output_path}"
    )

    return output_path