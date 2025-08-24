import json
import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from models.api_models import ApiRequestLog, PerplexityRequest, PerplexityResponse, PerplexitySearchResult
import streamlit as st

class DataService:
    def __init__(self):
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        
        # File paths
        self.requests_file = self.data_dir / 'api_requests.json'
        self.prompts_file = self.data_dir / 'saved_prompts.json'
        self.responses_file = self.data_dir / 'saved_responses.json'
        self.config_file = self.data_dir / 'config.json'
        
        # Initialize files if they don't exist
        self._init_files()
    
    def _init_files(self):
        """Initialize JSON files if they don't exist"""
        if not self.requests_file.exists():
            self._save_json(self.requests_file, [])
        
        if not self.prompts_file.exists():
            self._save_json(self.prompts_file, self._get_default_prompts())
        
        if not self.responses_file.exists():
            self._save_json(self.responses_file, [])
        
        if not self.config_file.exists():
            self._save_json(self.config_file, {
                'api_key': '',
                'default_model': 'sonar-pro',
                'default_max_tokens': 1000,
                'default_temperature': 0.7
            })
    
    def _get_default_prompts(self) -> List[Dict]:
        """Get default prompt templates"""
        research_prompt = ("Provide a comprehensive analysis of the latest developments in artificial intelligence, focusing on:\n"
                          "1. Recent breakthroughs in large language models\n"
                          "2. Advances in computer vision and image generation\n"
                          "3. Progress in robotics and autonomous systems\n"
                          "4. Ethical considerations and regulatory developments\n"
                          "5. Industry applications and market trends\n\n"
                          "Please include specific examples, statistics, and cite recent sources from 2024-2025.")
        
        market_prompt = ("Analyze the current global stock market trends with particular focus on:\n"
                        "- Technology sector performance (FAANG stocks, AI companies, semiconductor industry)\n"
                        "- Economic indicators affecting market sentiment\n"
                        "- Geopolitical events impacting international markets\n"
                        "- Cryptocurrency market correlation with traditional assets\n"
                        "- Investment recommendations for the next 6 months\n\n"
                        "Provide specific data, charts references, and expert opinions from financial institutions.")
        
        news_prompt = ("Create a comprehensive news summary for today covering:\n"
                      "- Breaking news in technology and business\n"
                      "- Political developments worldwide\n"
                      "- Scientific discoveries and health updates\n"
                      "- Environmental and climate change news\n"
                      "- Sports highlights and entertainment updates\n\n"
                      "Organize by category and include source citations for each major story.")
        
        tech_prompt = ("Conduct a detailed technical analysis on a specific programming topic:\n"
                      "1. Current best practices and methodologies\n"
                      "2. Performance considerations and optimization techniques\n"
                      "3. Security implications and vulnerabilities\n"
                      "4. Integration with modern frameworks and tools\n"
                      "5. Future trends and evolution in this area\n\n"
                      "Include code examples, benchmarks, and industry adoption statistics.")
        
        return [
            {
                'id': str(uuid.uuid4()),
                'name': 'Research Analysis',
                'description': 'Comprehensive research analysis template',
                'content': research_prompt,
                'category': 'Research',
                'created_at': datetime.now().isoformat(),
                'last_used': None,
                'usage_count': 0
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Market Analysis',
                'description': 'Stock market and financial analysis template',
                'content': market_prompt,
                'category': 'Finance',
                'created_at': datetime.now().isoformat(),
                'last_used': None,
                'usage_count': 0
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'News Summary',
                'description': 'Daily news summary template',
                'content': news_prompt,
                'category': 'News',
                'created_at': datetime.now().isoformat(),
                'last_used': None,
                'usage_count': 0
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Technical Analysis',
                'description': 'Technical programming analysis template',
                'content': tech_prompt,
                'category': 'Technology',
                'created_at': datetime.now().isoformat(),
                'last_used': None,
                'usage_count': 0
            }
        ]
    
    def _load_json(self, file_path: Path) -> Any:
        """Load JSON from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading {file_path}: {e}")
            return [] if file_path != self.config_file else {}
    
    def _save_json(self, file_path: Path, data: Any):
        """Save data to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            st.error(f"Error saving {file_path}: {e}")
    
    # Request logging methods
    def log_request(self, request: PerplexityRequest, request_json: str) -> str:
        """Log API request and return request ID"""
        request_id = str(uuid.uuid4())
        
        log_entry = ApiRequestLog(
            id=request_id,
            timestamp=datetime.now(),
            model=request.model,
            prompt=request.messages[0].content if request.messages else '',
            request_json=request_json,
            status='sent'
        )
        
        requests = self._load_json(self.requests_file)
        requests.append(log_entry.to_dict())
        self._save_json(self.requests_file, requests)
        
        return request_id
    
    def update_response(self, request_id: str, response: PerplexityResponse, response_json: str, duration_ms: int):
        """Update request log with response data"""
        requests = self._load_json(self.requests_file)
        
        for request in requests:
            if request['id'] == request_id:
                request['response_json'] = response_json
                request['response_id'] = response.id
                request['response_content'] = response.choices[0].message.content if response.choices else ''
                request['prompt_tokens'] = response.usage.prompt_tokens
                request['completion_tokens'] = response.usage.completion_tokens
                request['total_tokens'] = response.usage.total_tokens
                request['status'] = 'completed'
                request['duration_ms'] = duration_ms
                
                # Add search results
                if response.search_results:
                    request['search_results'] = [
                        {
                            'title': sr.title,
                            'url': sr.url,
                            'snippet': sr.snippet
                        }
                        for sr in response.search_results
                    ]
                
                break
        
        self._save_json(self.requests_file, requests)
    
    def update_error(self, request_id: str, error_message: str, duration_ms: int):
        """Update request log with error"""
        requests = self._load_json(self.requests_file)
        
        for request in requests:
            if request['id'] == request_id:
                request['status'] = 'error'
                request['error_message'] = error_message
                request['duration_ms'] = duration_ms
                break
        
        self._save_json(self.requests_file, requests)
    
    # Query methods
    def get_recent_requests(self, limit: int = 10) -> List[Dict]:
        """Get recent API requests"""
        requests = self._load_json(self.requests_file)
        # Sort by timestamp (most recent first)
        requests.sort(key=lambda x: x['timestamp'], reverse=True)
        return requests[:limit]
    
    def get_requests_by_model(self, model: str, limit: int = 10) -> List[Dict]:
        """Get requests by model"""
        requests = self._load_json(self.requests_file)
        filtered = [r for r in requests if r['model'] == model]
        filtered.sort(key=lambda x: x['timestamp'], reverse=True)
        return filtered[:limit]
    
    def get_request_by_id(self, request_id: str) -> Optional[Dict]:
        """Get request by ID"""
        requests = self._load_json(self.requests_file)
        for request in requests:
            if request['id'] == request_id:
                return request
        return None
    
    def get_usage_statistics(self) -> Dict:
        """Get usage statistics"""
        requests = self._load_json(self.requests_file)
        
        total_requests = len(requests)
        completed_requests = len([r for r in requests if r['status'] == 'completed'])
        total_tokens = sum(r.get('total_tokens', 0) for r in requests if r.get('total_tokens'))
        success_rate = (completed_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Model usage
        model_usage = {}
        for request in requests:
            model = request['model']
            model_usage[model] = model_usage.get(model, 0) + 1
        
        # Recent activity (last 7 days)
        from datetime import timedelta
        recent_date = datetime.now() - timedelta(days=7)
        recent_requests = [
            r for r in requests 
            if datetime.fromisoformat(r['timestamp']) >= recent_date
        ]
        
        return {
            'total_requests': total_requests,
            'completed_requests': completed_requests,
            'total_tokens': total_tokens,
            'success_rate': success_rate,
            'model_usage': model_usage,
            'recent_requests': len(recent_requests),
            'avg_tokens_per_request': total_tokens / completed_requests if completed_requests > 0 else 0
        }
    
    # Prompt management
    def get_saved_prompts(self) -> List[Dict]:
        """Get all saved prompts"""
        return self._load_json(self.prompts_file)
    
    def save_prompt(self, name: str, content: str, description: str = '', category: str = 'Custom') -> str:
        """Save a new prompt"""
        prompts = self._load_json(self.prompts_file)
        
        prompt_id = str(uuid.uuid4())
        new_prompt = {
            'id': prompt_id,
            'name': name,
            'description': description,
            'content': content,
            'category': category,
            'created_at': datetime.now().isoformat(),
            'last_used': None,
            'usage_count': 0
        }
        
        prompts.append(new_prompt)
        self._save_json(self.prompts_file, prompts)
        
        return prompt_id
    
    def update_prompt_usage(self, prompt_id: str):
        """Update prompt usage statistics"""
        prompts = self._load_json(self.prompts_file)
        
        for prompt in prompts:
            if prompt['id'] == prompt_id:
                prompt['last_used'] = datetime.now().isoformat()
                prompt['usage_count'] = prompt.get('usage_count', 0) + 1
                break
        
        self._save_json(self.prompts_file, prompts)
    
    def delete_prompt(self, prompt_id: str):
        """Delete a saved prompt"""
        prompts = self._load_json(self.prompts_file)
        prompts = [p for p in prompts if p['id'] != prompt_id]
        self._save_json(self.prompts_file, prompts)
    
    # Response management
    def save_response(self, request_id: str, response_data: Dict, prompt_name: str = ''):
        """Save a response for later viewing"""
        responses = self._load_json(self.responses_file)
        
        response_entry = {
            'id': str(uuid.uuid4()),
            'request_id': request_id,
            'prompt_name': prompt_name,
            'saved_at': datetime.now().isoformat(),
            'response_data': response_data
        }
        
        responses.append(response_entry)
        self._save_json(self.responses_file, responses)
    
    def get_saved_responses(self) -> List[Dict]:
        """Get all saved responses"""
        responses = self._load_json(self.responses_file)
        responses.sort(key=lambda x: x['saved_at'], reverse=True)
        return responses
    
    def delete_response(self, response_id: str):
        """Delete a saved response"""
        responses = self._load_json(self.responses_file)
        responses = [r for r in responses if r['id'] != response_id]
        self._save_json(self.responses_file, responses)
