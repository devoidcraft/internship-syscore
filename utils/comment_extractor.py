def extract_comment(cell_text: str, target_heading: str) -> str:
    """
    Extracts the review comment for a specific phase.
    Updated to handle whitespace mismatches and false-positive 'REVIEW:' stops.
    """
    if not isinstance(cell_text, str) or not cell_text.strip():
        return ""

    lines = cell_text.split("\n")
    is_capturing = False
    captured_lines = []

    # Clean the target heading to fix Issue 3 (exact heading mismatch/spaces)
    target_heading_clean = target_heading.strip().upper()

    for line in lines:
        line_clean = line.strip().upper()

        if not is_capturing:
            # Compare cleaned versions to bypass extra spaces
            if line_clean == target_heading_clean:
                is_capturing = True
        else:
            # Fix Issue 4: Stop ONLY if it looks like a real section header.
            # Real headers end with "REVIEW:" (e.g., "PRELIMINARY PERFORMANCE REVIEW:")
            if line_clean.endswith("REVIEW:"):
                break
            captured_lines.append(line)

    if is_capturing:
        return "\n".join(captured_lines).strip()

    return ""
