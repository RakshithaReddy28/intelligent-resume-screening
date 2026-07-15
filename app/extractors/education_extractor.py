import re
from typing import List, Dict, Optional
from datetime import date


class EducationExtractor:
    """Extract education information from resume text."""

    DEGREE_PATTERNS = [
        r"\b(?:bachelor|b\.?s\.?|b\.?a\.?|undergraduate)\b",
        r"\b(?:master|m\.?s\.?|m\.?a\.?|mba|graduate)\b",
        r"\b(?:ph\.?d|doctorate|doctoral|phd)\b",
        r"\b(?:associate|a\.?s\.?|a\.?a\.?|diploma)\b",
        r"\b(?:high school|secondary)\b",
    ]

    FIELD_PATTERNS = [
        r"(?:in|of)\s+([A-Z][a-zA-Z\s]+?)(?:\s*,|\s*from|\s*at|\s*\n)",
        r"(?:degree|major|field)[:\s]*([A-Z][a-zA-Z\s]+?)(?:\s*,|\s*from|\s*at|\s*\n)",
    ]

    INSTITUTION_PATTERNS = [
        r"(?:university|college|institute|school|academy)\s+of\s+[A-Z][a-zA-Z\s]+",
        r"[A-Z][a-zA-Z\s]+(?:university|college|institute|school)",
    ]

    DATE_PATTERNS = [
        r"(\d{4})\s*[-–]\s*(\d{4}|present|current)",
        r"(\d{4})\s*[-–]\s*(\d{2})",
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+(\d{4})",
    ]

    def extract_education(self, text: str) -> List[Dict]:
        """Extract education entries from text."""
        educations = []

        # Split text into sections
        sections = self._split_into_sections(text)

        for section in sections:
            if self._is_education_section(section):
                education = self._parse_education_section(section)
                if education:
                    educations.append(education)

        # If no structured sections found, try line-by-line extraction
        if not educations:
            educations = self._extract_from_lines(text)

        return educations

    def _split_into_sections(self, text: str) -> List[str]:
        """Split resume into logical sections."""
        section_headers = [
            r"(?:education|academic|qualification)",
            r"(?:experience|employment|work history)",
            r"(?:skills|technologies)",
            r"(?:projects|portfolio)",
            r"(?:certifications|licenses)",
        ]

        pattern = "|".join(f"({h})" for h in section_headers)
        sections = re.split(f"(?={pattern})", text, flags=re.IGNORECASE)

        return [s.strip() for s in sections if s and s.strip()]

    def _is_education_section(self, text: str) -> bool:
        """Check if text is an education section."""
        education_indicators = [
            "education", "academic", "qualification", "degree",
            "university", "college", "bachelor", "master", "phd",
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in education_indicators)

    def _parse_education_section(self, text: str) -> Optional[Dict]:
        """Parse an education section."""
        education = {
            "institution": None,
            "degree": None,
            "field_of_study": None,
            "start_date": None,
            "end_date": None,
            "description": text,
        }

        # Extract degree
        for pattern in self.DEGREE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                education["degree"] = match.group(0)
                break

        # Extract field of study
        for pattern in self.FIELD_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                education["field_of_study"] = match.group(1).strip()
                break

        # Extract institution
        for pattern in self.INSTITUTION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                education["institution"] = match.group(0).strip()
                break

        # Extract dates
        dates = self._extract_dates(text)
        if dates:
            education["start_date"] = dates[0]
            if len(dates) > 1:
                education["end_date"] = dates[1]

        return education if education["institution"] or education["degree"] else None

    def _extract_from_lines(self, text: str) -> List[Dict]:
        """Extract education from individual lines."""
        educations = []
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line contains education-related keywords
            if any(keyword in line.lower() for keyword in ["university", "college", "bachelor", "master"]):
                education = {
                    "institution": None,
                    "degree": None,
                    "field_of_study": None,
                    "start_date": None,
                    "end_date": None,
                    "description": line,
                }

                # Try to extract components
                for pattern in self.INSTITUTION_PATTERNS:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        education["institution"] = match.group(0).strip()
                        break

                for pattern in self.DEGREE_PATTERNS:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        education["degree"] = match.group(0)
                        break

                if education["institution"] or education["degree"]:
                    educations.append(education)

        return educations

    def _extract_dates(self, text: str) -> List[Optional[date]]:
        """Extract dates from text."""
        dates = []

        for pattern in self.DATE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if len(match.groups()) == 2:
                        year1 = int(match.group(1))
                        year2_str = match.group(2).lower()

                        if year2_str in ("present", "current"):
                            dates.append(date(year1, 1, 1))
                        else:
                            year2 = int(year2_str)
                            dates.append(date(year1, 1, 1))
                            dates.append(date(year2, 1, 1))
                except (ValueError, IndexError):
                    continue

        return dates
