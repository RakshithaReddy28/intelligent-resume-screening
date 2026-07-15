import re
from typing import List, Dict, Optional
from datetime import date, datetime


class ExperienceExtractor:
    """Extract work experience from resume text."""

    JOB_TITLE_PATTERNS = [
        r"(?:senior|junior|lead|principal|staff|chief)\s+(?:software|data|systems|network|cloud|devops)\s+(?:engineer|developer|architect|analyst)",
        r"(?:software|data|systems|network|cloud|devops)\s+(?:engineer|developer|architect|analyst)",
        r"(?:project|product|program)\s+(?:manager|director)",
        r"(?:frontend|backend|fullstack|full-stack|full stack)\s+(?:developer|engineer)",
        r"(?:machine learning|ml|ai)\s+(?:engineer|researcher|scientist)",
        r"(?:business|operations|financial|marketing)\s+(?:analyst|manager|director)",
    ]

    COMPANY_PATTERNS = [
        r"(?:at|@)\s+([A-Z][a-zA-Z0-9\s&.,]+?)(?:\s*,|\s*-\s*\d|\s*\n)",
        r"^([A-Z][a-zA-Z0-9&.,]+(?:\s+[A-Z][a-zA-Z0-9&.,]+)*)\s*$",
    ]

    DATE_RANGE_PATTERN = r"(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|present|current|\d{4})"

    def extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience entries from text."""
        experiences = []

        # Find experience section
        exp_section = self._find_experience_section(text)
        if not exp_section:
            return experiences

        # Split into individual job entries
        entries = self._split_into_entries(exp_section)

        for entry in entries:
            experience = self._parse_entry(entry)
            if experience:
                experiences.append(experience)

        return experiences

    def _find_experience_section(self, text: str) -> Optional[str]:
        """Find the experience/work history section."""
        section_headers = [
            r"(?:work\s+)?experience",
            r"employment\s+history",
            r"professional\s+experience",
            r"work\s+history",
            r"career\s+history",
        ]

        for header in section_headers:
            pattern = rf"(?:{header})[:\s]*(.*?)(?:\n\n|(?:education|skills|projects|certifications)[:\s])"
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()

        return None

    def _split_into_entries(self, text: str) -> List[str]:
        """Split experience section into individual job entries."""
        # Split by date patterns or bullet points
        entries = re.split(r"(?=\d{4}\s*[-–]\s*(?:\d{4}|present|current))", text)

        # Also split by bullet points if no dates found
        if len(entries) <= 1:
            entries = re.split(r"(?:^|\n)\s*[•\-\*]\s+", text)

        return [entry.strip() for entry in entries if entry.strip()]

    def _parse_entry(self, entry: str) -> Optional[Dict]:
        """Parse a single job entry."""
        experience = {
            "company": None,
            "title": None,
            "location": None,
            "start_date": None,
            "end_date": None,
            "is_current": False,
            "description": entry,
            "duration_months": None,
        }

        # Extract job title
        for pattern in self.JOB_TITLE_PATTERNS:
            match = re.search(pattern, entry, re.IGNORECASE)
            if match:
                experience["title"] = match.group(0).strip()
                break

        # Extract company
        for pattern in self.COMPANY_PATTERNS:
            match = re.search(pattern, entry, re.IGNORECASE)
            if match:
                experience["company"] = match.group(1).strip()
                break

        # Extract dates
        dates = self._extract_dates(entry)
        if dates:
            experience["start_date"] = dates[0]
            if len(dates) > 1:
                experience["end_date"] = dates[1]
                if dates[1] == date.today():
                    experience["is_current"] = True

        # Calculate duration
        experience["duration_months"] = self._calculate_duration(
            experience["start_date"],
            experience["end_date"],
            experience["is_current"],
        )

        # Extract location
        experience["location"] = self._extract_location(entry)

        return experience if experience["title"] or experience["company"] else None

    def _extract_dates(self, text: str) -> List[Optional[date]]:
        """Extract dates from text."""
        dates = []

        match = re.search(self.DATE_RANGE_PATTERN, text, re.IGNORECASE)
        if match:
            start_date = self._parse_date(match.group(1))
            end_str = match.group(2).lower()

            if end_str in ("present", "current"):
                end_date = date.today()
            else:
                end_date = self._parse_date(match.group(2))

            if start_date:
                dates.append(start_date)
            if end_date:
                dates.append(end_date)

        return dates

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse a date string into a date object."""
        date_str = date_str.strip().lower()

        if date_str in ("present", "current"):
            return date.today()

        # Try different date formats
        formats = [
            "%B %Y",  # January 2024
            "%b %Y",  # Jan 2024
            "%m/%Y",  # 01/2024
            "%Y",     # 2024
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        return None

    def _calculate_duration(
        self,
        start_date: Optional[date],
        end_date: Optional[date],
        is_current: bool,
    ) -> Optional[int]:
        """Calculate duration in months."""
        if not start_date:
            return None

        if is_current or end_date is None:
            end_date = date.today()

        if end_date < start_date:
            return None

        months = (end_date.year - start_date.year) * 12
        months += end_date.month - start_date.month

        return max(1, months)

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from text."""
        # Simple pattern for location (City, State or City, Country)
        location_pattern = r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2,})"
        match = re.search(location_pattern, text)
        return match.group(1) if match else None
