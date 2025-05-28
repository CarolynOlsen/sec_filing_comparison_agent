"""Tests for the EDGAR client."""

import asyncio
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from src.filing_agent.data.edgar_client import EdgarClient
from src.filing_agent.data.models import CompanySearchResult, Filing, CompanyInfo


class TestEdgarClient:
    """Test cases for EdgarClient."""
    
    @pytest.fixture
    def client(self):
        """Create an EdgarClient instance for testing."""
        return EdgarClient()
    
    @pytest.fixture
    def mock_company_tickers_response(self):
        """Mock response for company tickers API."""
        return {
            "0": {
                "cik_str": 320193,
                "ticker": "AAPL",
                "title": "Apple Inc."
            },
            "1": {
                "cik_str": 1318605,
                "ticker": "TSLA", 
                "title": "Tesla, Inc."
            },
            "2": {
                "cik_str": 1067983,
                "ticker": "BRK-B",
                "title": "Berkshire Hathaway Inc"
            },
            "3": {
                "cik_str": 1000228,
                "ticker": "HIG",
                "title": "Hartford Financial Services Group Inc"
            }
        }
    
    @pytest.fixture
    def mock_submissions_response(self):
        """Mock response for company submissions API."""
        return {
            "cik": "0001000228",
            "entityType": "operating",
            "sic": "6331",
            "sicDescription": "Fire, Marine & Casualty Insurance",
            "name": "Hartford Financial Services Group Inc",
            "tickers": ["HIG"],
            "exchanges": ["NYSE"],
            "ein": "061478200",
            "description": "Insurance",
            "website": "https://www.thehartford.com",
            "investorWebsite": "https://ir.thehartford.com",
            "category": "Large accelerated filer",
            "fiscalYearEnd": "1231",
            "stateOfIncorporation": "DE",
            "stateOfIncorporationDescription": "DE",
            "addresses": {
                "mailing": {
                    "street1": "HARTFORD PLAZA",
                    "street2": "690 ASYLUM AVENUE",
                    "city": "HARTFORD",
                    "stateOrCountry": "CT",
                    "zipCode": "06155",
                    "stateOrCountryDescription": "CT"
                },
                "business": {
                    "street1": "HARTFORD PLAZA",
                    "street2": "690 ASYLUM AVENUE", 
                    "city": "HARTFORD",
                    "stateOrCountry": "CT",
                    "zipCode": "06155",
                    "stateOrCountryDescription": "CT"
                }
            },
            "phone": "8605475000",
            "flags": "",
            "formerNames": [],
            "filings": {
                "recent": {
                    "accessionNumber": [
                        "0001000228-24-000008",
                        "0001000228-24-000007"
                    ],
                    "filingDate": [
                        "2024-02-08",
                        "2024-01-25"
                    ],
                    "reportDate": [
                        "2023-12-31",
                        "2023-12-31"
                    ],
                    "acceptanceDateTime": [
                        "2024-02-08T16:30:15.000Z",
                        "2024-01-25T16:30:10.000Z"
                    ],
                    "act": ["34", "34"],
                    "form": ["10-K", "8-K"],
                    "fileNumber": ["001-13958", "001-13958"],
                    "filmNumber": ["24631234", "24567890"],
                    "items": ["", "5.02"],
                    "size": [1234567, 234567],
                    "isXBRL": [1, 0],
                    "isInlineXBRL": [1, 0],
                    "primaryDocument": ["hig-20231231.htm", "hig-8k_20240125.htm"],
                    "primaryDocDescription": ["10-K", "8-K"]
                },
                "files": []
            }
        }
    
    @pytest.mark.asyncio
    async def test_search_companies_success(self, client, mock_company_tickers_response):
        """Test successful company search."""
        with patch.object(client, '_make_request') as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_company_tickers_response
            mock_request.return_value = mock_response
            
            results = await client.search_companies("Hartford")
            
            assert len(results) == 1
            assert results[0].name == "Hartford Financial Services Group Inc"
            assert results[0].ticker == "HIG"
            assert results[0].cik == "0001000228"
    
    @pytest.mark.asyncio
    async def test_search_companies_no_results(self, client, mock_company_tickers_response):
        """Test company search with no results."""
        with patch.object(client, '_make_request') as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_company_tickers_response
            mock_request.return_value = mock_response
            
            results = await client.search_companies("NonexistentCompany")
            
            assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_get_company_filings_success(self, client, mock_submissions_response):
        """Test successful retrieval of company filings."""
        with patch.object(client, '_make_request') as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_submissions_response
            mock_request.return_value = mock_response
            
            filings = await client.get_company_filings("1000228", "10-K", limit=1)
            
            assert len(filings) == 1
            filing = filings[0]
            assert filing.form_type == "10-K"
            assert filing.accession_number == "0001000228-24-000008"
            assert filing.company_info.name == "Hartford Financial Services Group Inc"
            assert filing.company_info.ticker == "HIG"
    
    @pytest.mark.asyncio
    async def test_download_filing_success(self, client):
        """Test successful filing download."""
        # Create a mock filing
        company_info = CompanyInfo(
            cik="0001000228",
            name="Hartford Financial Services Group Inc",
            ticker="HIG"
        )
        
        filing = Filing(
            accession_number="0001000228-24-000008",
            form_type="10-K",
            filing_date="2024-02-08",
            company_info=company_info,
            filing_url="https://www.sec.gov/Archives/edgar/data/1000228/000100022824000008/000100022824000008.txt"
        )
        
        mock_content = "MOCK FILING CONTENT\n\nThis is a test 10-K filing..."
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = MagicMock()
            mock_response.text = mock_content
            mock_request.return_value = mock_response
            
            content = await client.download_filing(filing)
            
            assert content == mock_content
            mock_request.assert_called_once_with(filing.filing_url)
    
    @pytest.mark.asyncio
    async def test_search_and_download_filing_success(self, client, mock_company_tickers_response, mock_submissions_response):
        """Test the complete workflow of searching and downloading a filing."""
        mock_filing_content = "MOCK 10-K FILING CONTENT FOR HARTFORD"
        
        with patch.object(client, '_make_request') as mock_request:
            # Mock the company search response
            mock_tickers_response = MagicMock()
            mock_tickers_response.json.return_value = mock_company_tickers_response
            
            # Mock the submissions response
            mock_submissions_resp = MagicMock()
            mock_submissions_resp.json.return_value = mock_submissions_response
            
            # Mock the filing download response
            mock_filing_resp = MagicMock()
            mock_filing_resp.text = mock_filing_content
            
            # Set up the mock to return different responses for different calls
            mock_request.side_effect = [
                mock_tickers_response,  # Company search
                mock_submissions_resp,  # Company filings
                mock_filing_resp        # Filing download
            ]
            
            filing, content = await client.search_and_download_filing("Hartford", "10-K")
            
            assert filing.company_info.name == "Hartford Financial Services Group Inc"
            assert filing.form_type == "10-K"
            assert content == mock_filing_content
            assert mock_request.call_count == 3
    
    @pytest.mark.asyncio
    async def test_search_and_download_filing_company_not_found(self, client):
        """Test error handling when company is not found."""
        with patch.object(client, '_make_request') as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {}  # Empty response
            mock_request.return_value = mock_response
            
            with pytest.raises(ValueError, match="No companies found matching"):
                await client.search_and_download_filing("NonexistentCompany", "10-K")
    
    def test_normalize_cik(self, client):
        """Test CIK normalization."""
        assert client._normalize_cik("1000228") == "0001000228"
        assert client._normalize_cik("000320193") == "0000320193"
        assert client._normalize_cik("123") == "0000000123"


# Integration test (requires network access)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_edgar_api():
    """Integration test with real EDGAR API (requires network)."""
    async with EdgarClient() as client:
        # Test company search
        companies = await client.search_companies("Apple")
        assert len(companies) > 0
        
        apple = None
        for company in companies:
            if "APPLE INC" in company.name.upper():
                apple = company
                break
        
        assert apple is not None
        
        # Test getting filings
        filings = await client.get_company_filings(apple.cik, "10-K", limit=1)
        assert len(filings) > 0
        
        filing = filings[0]
        assert filing.form_type == "10-K"
        assert "APPLE" in filing.company_info.name.upper()


if __name__ == "__main__":
    # Run a simple test
    async def main():
        async with EdgarClient() as client:
            try:
                filing, content = await client.search_and_download_filing("Hartford", "10-K")
                print(f"Downloaded {filing.form_type} for {filing.company_info.name}")
                print(f"Filing date: {filing.filing_date}")
                print(f"Content length: {len(content)} characters")
                print(f"First 500 characters:\n{content[:500]}...")
            except Exception as e:
                print(f"Error: {e}")
    
    asyncio.run(main()) 