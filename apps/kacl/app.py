#!/usr/bin/env python3

# changelog_linter.py
import re
from datetime import datetime

class ChangelogLinter:
    VERSION_HEADER_REGEX = re.compile(
        r'^## \[(?P<version>.+?)\](?: - (?P<date>\d{4}-\d{2}-\d{2}))?$'
    )
    OPTIONAL_SECTION_REGEX = re.compile(r'^###\s+(Added|Changed|Deprecated|Removed|Fixed|Security)\s*$')

    def __init__(self, filepath):
        self.filepath = filepath
        self.errors = []
        self.content_lines = []

    def load_file(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.content_lines = f.readlines()
        except Exception as e:
            self.errors.append(f"Failed to load file: {e}")
            return False
        return True

    def lint(self):
        if not self.load_file():
            return self.errors

        # Check that the first non-empty line is "# Changelog"
        for line in self.content_lines:
            if line.strip():
                if line.strip() != "# Changelog":
                    self.errors.append("File must start with '# Changelog' as the first non-empty line.")
                break

        version_headers = []
        for idx, line in enumerate(self.content_lines):
            if line.startswith("## "):
                match = self.VERSION_HEADER_REGEX.match(line.strip())
                if not match:
                    self.errors.append(f"Line {idx+1}: Version header does not match required format.")
                else:
                    version = match.group("version")
                    date = match.group("date")
                    if version != "Unreleased":
                        if not date:
                            self.errors.append(f"Line {idx+1}: Version '{version}' must have a date.")
                        else:
                            try:
                                datetime.strptime(date, '%Y-%m-%d')
                            except ValueError:
                                self.errors.append(f"Line {idx+1}: Date '{date}' is not in YYYY-MM-DD format.")
                    else:
                        if date:
                            self.errors.append(f"Line {idx+1}: 'Unreleased' version should not have a date.")
                    version_headers.append((idx, version))
        if not version_headers:
            self.errors.append("No version headers found in the file.")

        # Verify that each version block has at least one optional section header
        for i, (start_idx, version) in enumerate(version_headers):
            end_idx = version_headers[i+1][0] if i+1 < len(version_headers) else len(self.content_lines)
            block = self.content_lines[start_idx+1:end_idx]
            if not any(self.OPTIONAL_SECTION_REGEX.match(line.strip()) for line in block):
                self.errors.append(
                    f"Version '{version}' (line {start_idx+1}) must include at least one optional section (e.g., Added, Changed, etc)."
                )
        return self.errors

def main(filepath):
    linter = ChangelogLinter(filepath)
    errors = linter.lint()
    if errors:
        print("Changelog lint errors:")
        for err in errors:
            print(f"- {err}")
        return 1
    else:
        print("Changelog is valid.")
        return 0

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python changelog_linter.py <path to CHANGELOG.md>")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
