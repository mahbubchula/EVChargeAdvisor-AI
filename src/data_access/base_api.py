"""
🔧 Base API Client
==================

Foundation class for all API clients with retry logic,
error handling, and caching.

Author: MAHBUB
Date: December 25, 2024
"""

import requests
import time
import json
import os
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Add parent directory to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.settings import API_SETTINGS, PATHS


class BaseAPIClient(ABC):
    """
    Abstract base class for all API clients.
    
    Provides:
    - HTTP request handling
    - Automatic retry logic
    - Response caching
    - Error handling
    - Logging
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for the API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = API_SETTINGS["timeout"]
        self.max_retries = API_SETTINGS["max_retries"]
        self.retry_delay = API_SETTINGS["retry_delay"]
        self.cache_duration = API_SETTINGS["cache_duration"]
        self.cache_dir = PATHS["data_cache"]
        
        # Session for connection pooling
        self.session = requests.Session()
        
        # Request statistics
        self.stats = {
            "requests": 0,
            "cache_hits": 0,
            "errors": 0
        }
    
    # =========================================================================
    # CORE REQUEST METHODS
    # =========================================================================
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic and caching.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            headers: Additional headers
            use_cache: Whether to use caching
            
        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}" if endpoint else self.base_url
        
        # Check cache for GET requests
        if method.upper() == "GET" and use_cache:
            cached = self._get_cached_response(url, params)
            if cached is not None:
                self.stats["cache_hits"] += 1
                return cached
        
        # Prepare headers
        request_headers = self._get_default_headers()
        if headers:
            request_headers.update(headers)
        
        # Make request with retries
        last_error = None
        for attempt in range(self.max_retries):
            try:
                self.stats["requests"] += 1
                
                response = self.session.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=data,
                    headers=request_headers,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                
                # Cache successful GET responses
                if method.upper() == "GET" and use_cache:
                    self._cache_response(url, params, result)
                
                return result
                
            except requests.exceptions.Timeout:
                last_error = f"Request timeout after {self.timeout}s"
                print(f"⚠️ Attempt {attempt + 1}/{self.max_retries}: {last_error}")
                
            except requests.exceptions.HTTPError as e:
                last_error = f"HTTP Error: {e.response.status_code} - {e.response.text[:200]}"
                self.stats["errors"] += 1
                
                # Don't retry on client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    raise APIError(last_error, e.response.status_code)
                    
                print(f"⚠️ Attempt {attempt + 1}/{self.max_retries}: {last_error}")
                
            except requests.exceptions.RequestException as e:
                last_error = f"Request failed: {str(e)}"
                self.stats["errors"] += 1
                print(f"⚠️ Attempt {attempt + 1}/{self.max_retries}: {last_error}")
            
            # Wait before retry
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (attempt + 1))
        
        raise APIError(f"All {self.max_retries} attempts failed. Last error: {last_error}")
    
    def get(self, endpoint: str = "", params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make GET request."""
        return self._make_request("GET", endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str = "", data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make POST request."""
        return self._make_request("POST", endpoint, data=data, **kwargs)
    
    # =========================================================================
    # HEADERS & AUTHENTICATION
    # =========================================================================
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for requests."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "EVChargeAdvisor-AI/1.0"
        }
        return headers
    
    @abstractmethod
    def _add_auth_params(self, params: Dict) -> Dict:
        """Add authentication parameters. Must be implemented by subclasses."""
        pass
    
    # =========================================================================
    # CACHING
    # =========================================================================
    
    def _get_cache_key(self, url: str, params: Optional[Dict]) -> str:
        """Generate unique cache key for request."""
        cache_data = f"{url}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get file path for cached response."""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _get_cached_response(self, url: str, params: Optional[Dict]) -> Optional[Dict]:
        """Get cached response if valid."""
        cache_key = self._get_cache_key(url, params)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached = json.load(f)
            
            # Check if cache is still valid
            cached_time = datetime.fromisoformat(cached["timestamp"])
            if datetime.now() - cached_time < timedelta(seconds=self.cache_duration):
                return cached["data"]
            
            # Cache expired, remove file
            os.remove(cache_path)
            return None
            
        except (json.JSONDecodeError, KeyError, ValueError):
            return None
    
    def _cache_response(self, url: str, params: Optional[Dict], data: Dict) -> None:
        """Cache response data."""
        cache_key = self._get_cache_key(url, params)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            cache_data = {
                "timestamp": datetime.now().isoformat(),
                "url": url,
                "params": params,
                "data": data
            }
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            print(f"⚠️ Cache write failed: {e}")
    
    def clear_cache(self) -> int:
        """Clear all cached responses. Returns number of files deleted."""
        count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                os.remove(os.path.join(self.cache_dir, filename))
                count += 1
        return count
    
    # =========================================================================
    # STATISTICS & INFO
    # =========================================================================
    
    def get_stats(self) -> Dict[str, int]:
        """Get request statistics."""
        return self.stats.copy()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(base_url='{self.base_url}')"


class APIError(Exception):
    """Custom exception for API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("🔧 Base API Client Module")
    print("=" * 60)
    print("✅ Base API client loaded successfully!")
    print("\nThis is an abstract base class.")
    print("It will be inherited by specific API clients:")
    print("  - OpenChargeMapClient")
    print("  - CensusAPIClient")
    print("  - OverpassAPIClient")
    print("  - WeatherAPIClient")
    print("  - GroqAPIClient")