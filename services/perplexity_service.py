import streamlit as st
import requests
import json
import time
from typing import Optional, Dict, Any
from models.api_models import PerplexityRequest, PerplexityResponse, PerplexityMessage, PerplexityUsage, PerplexityChoice, PerplexitySearchResult

class PerplexityService:
    def __init__(self):
        self.base_url = self._get_base_url()
        self.api_key = self._get_api_key()
        self.timeout = 30
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _get_api_key(self) -> str:
        """Get API key from secrets or environment"""
        try:
            # Try Streamlit secrets first
            if hasattr(st, 'secrets') and 'perplexity' in st.secrets:
                return st.secrets.perplexity.api_key
            
            # Try environment variable
            import os
            api_key = os.getenv('PERPLEXITY_API_KEY')
            if api_key:
                return api_key
            
            # Fallback to local config
            try:
                with open('data/config.json', 'r') as f:
                    config = json.load(f)
                    return config.get('api_key', '')
            except FileNotFoundError:
                st.error("API key not found. Please configure your Perplexity API key.")
                return ''
                
        except Exception as e:
            st.error(f"Error loading API key: {e}")
            return ''
    
    def _get_base_url(self) -> str:
        """Get base URL from secrets or use default"""
        try:
            if hasattr(st, 'secrets') and 'perplexity' in st.secrets:
                return st.secrets.perplexity.get('base_url', 'https://api.perplexity.ai')
            return 'https://api.perplexity.ai'
        except:
            return 'https://api.perplexity.ai'
    
    def send_request(self, request: PerplexityRequest) -> Optional[PerplexityResponse]:
        """Send request to Perplexity API"""
        try:
            start_time = time.time()
            
            url = f"{self.base_url}/chat/completions"
            payload = request.to_dict()
            
            response = self.session.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                response_data = response.json()
                return self._parse_response(response_data)
            else:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                st.error(error_msg)
                return None
                
        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return None
    
    def _parse_response(self, response_data: Dict[Any, Any]) -> PerplexityResponse:
        """Parse API response into PerplexityResponse object"""
        try:
            # Parse usage
            usage_data = response_data.get('usage', {})
            usage = PerplexityUsage(
                prompt_tokens=usage_data.get('prompt_tokens', 0),
                completion_tokens=usage_data.get('completion_tokens', 0),
                total_tokens=usage_data.get('total_tokens', 0)
            )
            
            # Parse choices
            choices = []
            for choice_data in response_data.get('choices', []):
                message_data = choice_data.get('message', {})
                message = PerplexityMessage(
                    role=message_data.get('role', ''),
                    content=message_data.get('content', '')
                )
                choice = PerplexityChoice(
                    index=choice_data.get('index', 0),
                    finish_reason=choice_data.get('finish_reason', ''),
                    message=message
                )
                choices.append(choice)
            
            # Parse search results
            search_results = []
            if 'search_results' in response_data and response_data['search_results']:
                for sr_data in response_data['search_results']:
                    search_result = PerplexitySearchResult(
                        title=sr_data.get('title', ''),
                        url=sr_data.get('url', ''),
                        snippet=sr_data.get('snippet', '')
                    )
                    search_results.append(search_result)
            
            return PerplexityResponse(
                id=response_data.get('id', ''),
                object=response_data.get('object', ''),
                created=response_data.get('created', 0),
                model=response_data.get('model', ''),
                choices=choices,
                usage=usage,
                search_results=search_results if search_results else None,
                related_questions=response_data.get('related_questions'),
                citations=response_data.get('citations')
            )
        except Exception as e:
            st.error(f"Error parsing response: {str(e)}")
            raise
    
    def send_chat_request(self, prompt: str, model: str = "sonar-pro", **kwargs) -> Optional[PerplexityResponse]:
        """Send a simple chat request"""
        request = PerplexityRequest(
            model=model,
            messages=[PerplexityMessage(role="user", content=prompt)],
            max_tokens=kwargs.get('max_tokens', 1000),
            temperature=kwargs.get('temperature', 0.7),
            top_p=kwargs.get('top_p', 1.0),
            presence_penalty=kwargs.get('presence_penalty', 0.0),
            frequency_penalty=kwargs.get('frequency_penalty', 0.0),
            stream=False,
            return_citations=kwargs.get('return_citations', True),
            return_related_questions=kwargs.get('return_related_questions', True),
            return_images=kwargs.get('return_images', False)
        )
        
        return self.send_request(request)
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            response = self.send_chat_request(
                "Hello, this is a test message. Please respond with a simple confirmation.",
                max_tokens=50
            )
            return response is not None
        except Exception:
            return False
    
    def get_available_models(self) -> list:
        """Get list of available models"""
        return [
            "sonar",
            "sonar-pro", 
            "sonar-reasoning",
            "sonar-reasoning-pro"
        ]
