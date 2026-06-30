"""
Week 2 - Day 2: Pydantic v2 Models Practice
Building 5 complex Pydantic models for AI output schemas
"""

from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, date
from pydantic import BaseModel, Field, validator, field_validator, model_validator, EmailStr, HttpUrl

# ─── Model 1: User Profile ───

class Address(BaseModel):
    """User address model"""
    street: str
    city: str
    state: str
    postal_code: str
    country: str

class UserProfile(BaseModel):
    """Model 1: User profile with nested models"""
    
    user_id: str = Field(..., description="Unique user identifier")
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr = Field(..., description="Valid email address")
    age: Optional[int] = Field(None, ge=18, le=120, description="User age")
    addresses: List[Address] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)
    last_login: Optional[datetime] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30,
                "addresses": [
                    {
                        "street": "123 Main St",
                        "city": "New York",
                        "state": "NY",
                        "postal_code": "10001",
                        "country": "USA"
                    }
                ],
                "preferences": {"theme": "dark", "notifications": True},
                "is_active": True
            }
        }

# ─── Model 2: Sentiment Analysis ───

class SentimentResult(BaseModel):
    """Model 2: Sentiment analysis result"""
    
    text: str = Field(..., description="Original text analyzed")
    sentiment: Literal["positive", "negative", "neutral"] = Field(..., description="Predicted sentiment")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    scores: Dict[str, float] = Field(..., description="Individual sentiment scores")
    key_phrases: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=datetime.now)
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "This product is amazing!",
                "sentiment": "positive",
                "confidence": 0.95,
                "scores": {"positive": 0.92, "negative": 0.03, "neutral": 0.05},
                "key_phrases": ["product", "amazing"],
                "topics": ["product_review"]
            }
        }

# ─── Model 3: Financial Transaction ───

class FinancialTransaction(BaseModel):
    """Model 3: Financial transaction model"""
    
    transaction_id: str = Field(..., description="Unique transaction identifier")
    amount: float = Field(..., gt=0, description="Transaction amount")
    currency: Literal["USD", "EUR", "GBP", "PKR"] = Field("USD", description="Currency code")
    sender: str = Field(..., min_length=1, description="Sender account")
    recipient: str = Field(..., min_length=1, description="Recipient account")
    description: Optional[str] = Field(None, max_length=500)
    category: str = Field(..., description="Transaction category")
    timestamp: datetime = Field(default_factory=datetime.now)
    status: Literal["pending", "completed", "failed", "reversed"] = Field("pending")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return round(v, 2)

# ─── Model 4: Job Posting (Extended) ───

class CompanyInfo(BaseModel):
    """Company information"""
    name: str
    industry: Optional[str] = None
    website: Optional[HttpUrl] = None
    headquarters: Optional[str] = None

class JobPostingExtended(BaseModel):
    """Model 4: Extended job posting"""
    
    title: str = Field(..., description="Job title")
    company: CompanyInfo = Field(..., description="Company information")
    description: str = Field(..., description="Full job description")
    location: str = Field(..., description="Job location")
    remote_status: Literal["Remote", "Hybrid", "On-site"] = Field("On-site")
    salary_min: Optional[float] = Field(None, ge=0)
    salary_max: Optional[float] = Field(None, ge=0)
    salary_currency: Literal["USD", "EUR", "GBP", "PKR"] = "USD"
    required_skills: List[str] = Field(..., min_length=1)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_required: Optional[float] = Field(None, ge=0)
    education_required: Optional[str] = None
    posted_date: date = Field(default_factory=date.today)
    application_deadline: Optional[date] = None
    benefits: List[str] = Field(default_factory=list)
    job_type: Literal["Full-time", "Part-time", "Contract", "Internship"] = "Full-time"
    
    @model_validator(mode='after')
    def validate_salary_range(self):
        if self.salary_min is not None and self.salary_max is not None:
            if self.salary_max < self.salary_min:
                raise ValueError("Salary max cannot be less than salary min")
        return self

# ─── Model 5: Research Paper ───

class Author(BaseModel):
    """Research paper author"""
    name: str
    affiliation: Optional[str] = None
    email: Optional[EmailStr] = None
    orcid: Optional[str] = None

class Citation(BaseModel):
    """Research paper citation"""
    title: str
    authors: List[str]
    year: int
    journal: Optional[str] = None
    doi: Optional[str] = None

class ResearchPaper(BaseModel):
    """Model 5: Research paper model"""
    
    title: str = Field(..., min_length=5, description="Paper title")
    authors: List[Author] = Field(..., min_length=1, description="Paper authors")
    abstract: str = Field(..., min_length=10, description="Paper abstract")
    keywords: List[str] = Field(..., min_length=1)
    categories: List[str] = Field(default_factory=list)
    date: date = Field(default_factory=date.today)
    citations: List[Citation] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    doi: Optional[str] = None
    url: Optional[HttpUrl] = None
    file_size: Optional[int] = Field(None, ge=0)
    version: str = Field("1.0", pattern=r"^\d+\.\d+$")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()
    
    @field_validator('abstract')
    @classmethod
    def validate_abstract(cls, v):
        if not v.strip():
            raise ValueError("Abstract cannot be empty")
        return v.strip()

# ─── Demo ───

def main():
    """Demonstrate all 5 models"""
    
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    
    console.print(Panel.fit(
        "[bold white]Week 2 - Day 2: 5 Pydantic Models[/bold white]",
        border_style="cyan"
    ))
    
    models = [
        ("UserProfile", UserProfile, "User profile with nested address model"),
        ("SentimentResult", SentimentResult, "Sentiment analysis with confidence scores"),
        ("FinancialTransaction", FinancialTransaction, "Financial transaction with validation"),
        ("JobPostingExtended", JobPostingExtended, "Extended job posting with company info"),
        ("ResearchPaper", ResearchPaper, "Research paper with authors and citations")
    ]
    
    for name, model, description in models:
        console.print(f"\n[bold cyan]{name}[/bold cyan]")
        console.print(f"[dim]{description}[/dim]")
        console.print(f"Fields: {', '.join(model.model_fields.keys())}")
        console.print("")
        
        # Show JSON schema
        console.print(f"JSON Schema (first 100 chars):")
        schema = str(model.model_json_schema())[:100] + "..."
        console.print(f"  {schema}")
        console.print("-"*50)
    
    console.print("\n[bold green]All 5 models ready for use![/bold green]")

if __name__ == "__main__":
    main()
