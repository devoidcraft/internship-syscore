import pandas as pd
import re
from .comment_extractor import extract_comment


def find_header_index(file_path: str, sheet_name: str) -> int:
    """Reads the first 20 rows to dynamically find where the true table headers start."""
    # Now reading from excel directly
    df_temp = pd.read_excel(
        file_path, sheet_name=sheet_name, header=None, nrows=20, engine="openpyxl"
    )
    for idx, row in df_temp.iterrows():
        row_str = " ".join([str(val).strip() for val in row.values if pd.notnull(val)])
        if "Part" in row_str and "Status" in row_str and "Review Comment" in row_str:
            return idx
    return 0


def clean_part_name(raw_part: str) -> str:
    """Extracts 'A01.1' from 'A01.1\nMeet Thresholds...'"""
    if not isinstance(raw_part, str):
        return ""
    match = re.search(r"^([A-Z0-9\.]+)", raw_part.strip())
    return match.group(1) if match else str(raw_part).strip()


def process_file(file_path: str, target_heading: str) -> list:
    sheet_name = "Review Comments"

    try:
        header_idx = find_header_index(file_path, sheet_name)
        # Read the specific sheet from the Excel file
        df = pd.read_excel(
            file_path, sheet_name=sheet_name, header=header_idx, engine="openpyxl"
        )
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

    df.columns = [str(col).strip() for col in df.columns]

    required_cols = ["Part", "Status", "Review Comment"]
    for col in required_cols:
        if col not in df.columns:
            print(f"Warning: Missing column '{col}' in {file_path}")
            return []

    points_col = next((c for c in df.columns if "Point" in c), None)

    results = []

    for _, row in df.iterrows():
        raw_part = row.get("Part", "")

        if pd.isna(raw_part) or not str(raw_part).strip():
            continue

        part_id = clean_part_name(str(raw_part))

        if "." not in part_id:
            continue

        raw_comment = str(row.get("Review Comment", ""))
        extracted_comment = extract_comment(raw_comment, target_heading)

        points = str(row.get(points_col, "0")) if points_col else "0"
        if pd.isna(row.get(points_col)):
            points = "0"

        status = str(row.get("Status", ""))

        results.append({
            "part": part_id,
            "points": points.strip(),
            "status": status.strip(),
            "review_comment": extracted_comment,
        })

    return results
