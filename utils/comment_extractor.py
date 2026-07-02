def extract_comment(cell_text: str, target_heading: str) -> str:
    """
    Extracts the review comment for a specific phase from a multi-section cell.
    Follows exact rules from extract-comment-algorithm.md.
    """
    if not isinstance(cell_text, str) or not cell_text.strip():
        return ""

    lines = cell_text.split("\n")
    is_capturing = False
    captured_lines = []

    for line in lines:
        if not is_capturing:
            # Heading match must be EXACT
            if line == target_heading:
                is_capturing = True
        else:
            # Stop capturing if we hit another REVIEW: section
            if "REVIEW:" in line:
                break
            # Blank lines ARE included
            captured_lines.append(line)

    if is_capturing:
        # Join lines and trim extreme whitespace from the final block
        return "\n".join(captured_lines).strip()

    return ""  # Heading not found or no content
