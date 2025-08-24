from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

@dataclass
class PerplexityMessage:
    role: str
    content: str

@dataclass
class PerplexityRequest:
    model: str
    messages: List[PerplexityMessage]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    stream: Optional[bool] = None
    return_citations: Optional[bool] = None
    return_related_questions: Optional[bool] = None
    return_images: Optional[bool] = None
    
    def to_dict(self):
        """Convert to dictionary for API call"""
        result = {}
        for key, value in asdict(self).items():
            if value is not None:
                if key == 'messages':
                    result[key] = [asdict(msg) for msg in self.messages]
                else:
                    result[key] = value
        return result

@dataclass
class PerplexityUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

@dataclass
class PerplexityChoice:
    index: int
    finish_reason: str
    message: PerplexityMessage

@dataclass
class PerplexitySearchResult:
    title: str
    url: str
    snippet: str

@dataclass
class PerplexityResponse:
    id: str
    object: str
    created: int
    model: str
    choices: List[PerplexityChoice]
    usage: PerplexityUsage
    search_results: Optional[List[PerplexitySearchResult]] = None
    related_questions: Optional[List[str]] = None
    citations: Optional[List[str]] = None

@dataclass
class ApiRequestLog:
    id: str
    timestamp: datetime
    model: str
    prompt: str
    request_json: str
    response_json: Optional[str] = None
    response_id: Optional[str] = None
    response_content: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    status: str = "pending"
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    search_results: List[PerplexitySearchResult] = field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        # Convert datetime to ISO format
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[Any, Any]):
        """Create instance from dictionary"""
        # Convert timestamp back to datetime
        if isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Convert search_results
        if 'search_results' in data and data['search_results']:
            data['search_results'] = [
                PerplexitySearchResult(**sr) for sr in data['search_results']
            ]
        
        return cls(**data)
