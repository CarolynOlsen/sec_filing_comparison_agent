"""Data models for SEC filing information using Pydantic."""

from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator


class CompanyInfo(BaseModel):
    """Company information from SEC filings."""
    cik: str = Field(..., description="Central Index Key")
    name: str = Field(..., description="Company name")
    ticker: Optional[str] = Field(None, description="Stock ticker symbol")
    sic: Optional[str] = Field(None, description="Standard Industrial Classification")
    state_of_incorporation: Optional[str] = Field(None, description="State of incorporation")
    fiscal_year_end: Optional[str] = Field(None, description="Fiscal year end")


class FilingDocument(BaseModel):
    """Individual document within a filing."""
    sequence: Optional[str] = Field(None, description="Document sequence number")
    description: Optional[str] = Field(None, description="Document description")
    document_url: str = Field(..., description="URL to the document")
    type: Optional[str] = Field(None, description="Document type")
    size: Optional[int] = Field(None, description="Document size in bytes")


class Filing(BaseModel):
    """SEC filing information."""
    accession_number: str = Field(..., description="SEC accession number")
    form_type: str = Field(..., description="Form type (e.g., 10-K, 10-Q)")
    filing_date: Union[datetime, str] = Field(..., description="Date filing was submitted")
    period_of_report: Optional[Union[datetime, str]] = Field(None, description="Period end date")
    company_info: CompanyInfo = Field(..., description="Company information")
    documents: List[FilingDocument] = Field(default_factory=list, description="Filing documents")
    filing_url: Optional[str] = Field(None, description="URL to the main filing document")
    
    @validator('filing_date', pre=True)
    def parse_filing_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d")
        return v
    
    @validator('period_of_report', pre=True)
    def parse_period_date(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d")
        return v


class CompanySearchResult(BaseModel):
    """Result from company search."""
    cik: str = Field(..., description="Central Index Key")
    name: str = Field(..., description="Company name")
    ticker: Optional[str] = Field(None, description="Stock ticker symbol")
    exchange: Optional[str] = Field(None, description="Stock exchange")


class FilingSearchParams(BaseModel):
    """Parameters for filing search."""
    company_name: Optional[str] = Field(None, description="Company name to search")
    cik: Optional[str] = Field(None, description="Central Index Key")
    ticker: Optional[str] = Field(None, description="Stock ticker symbol")
    form_type: str = Field("10-K", description="Form type to search for")
    limit: int = Field(10, description="Maximum number of results")
    before_date: Optional[datetime] = Field(None, description="Search before this date")
    after_date: Optional[datetime] = Field(None, description="Search after this date") 