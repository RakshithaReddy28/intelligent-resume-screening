import enum


class UserRole(enum.Enum):
    RECRUITER = "recruiter"
    CANDIDATE = "candidate"


class ResumeStatus(enum.Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSED = "parsed"
    FAILED = "failed"


class JobStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class MatchStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
