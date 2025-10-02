"""LLM service for intelligent query enhancement and recommendation"""

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-powered query understanding and recommendation enhancement"""

    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 150,
    ):
        """Initialize LLM service

        Args:
            provider: LLM provider ('openai', 'anthropic', or 'local')
            model: Model name/identifier
            api_key: API key for the provider
            temperature: Temperature for generation (0-1)
            max_tokens: Maximum tokens to generate
        """
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the LLM client based on provider"""
        try:
            if self.provider == "openai":
                self._init_openai()
            elif self.provider == "anthropic":
                self._init_anthropic()
            elif self.provider == "local":
                logger.info("Local LLM provider selected - no client initialization needed")
            else:
                logger.warning(f"Unknown provider: {self.provider}. LLM service disabled.")
                self.client = None
        except Exception as e:
            logger.warning(f"Failed to initialize LLM client: {e}. LLM service disabled.")
            self.client = None

    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            from openai import OpenAI

            if not self.api_key:
                logger.warning("OpenAI API key not found. LLM service disabled.")
                return

            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
        except ImportError:
            logger.warning("OpenAI package not installed. Install with: pip install openai")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None

    def _init_anthropic(self):
        """Initialize Anthropic client"""
        try:
            import anthropic

            if not self.api_key:
                logger.warning("Anthropic API key not found. LLM service disabled.")
                return

            self.client = anthropic.Anthropic(api_key=self.api_key)
            logger.info("Anthropic client initialized successfully")
        except ImportError:
            logger.warning("Anthropic package not installed. Install with: pip install anthropic")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            self.client = None

    def is_available(self) -> bool:
        """Check if LLM service is available

        Returns:
            True if LLM client is initialized, False otherwise
        """
        return self.client is not None

    def expand_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Expand a query into related search terms using LLM

        Args:
            query: User's original query
            context: Optional context information (user history, domain, etc.)

        Returns:
            List of expanded/related queries
        """
        if not self.is_available():
            return []

        try:
            prompt = self._build_query_expansion_prompt(query, context)
            
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a query expansion assistant for a business intelligence system. Generate semantically related queries."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                result = response.choices[0].message.content.strip()
            elif self.provider == "anthropic":
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                result = message.content[0].text.strip()
            else:
                return []

            # Parse the result - expect comma-separated or line-separated queries
            expanded_queries = self._parse_llm_response(result)
            logger.info(f"Expanded query '{query}' to {len(expanded_queries)} related queries")
            return expanded_queries

        except Exception as e:
            logger.error(f"Failed to expand query with LLM: {e}")
            return []

    def generate_related_queries(
        self,
        query: str,
        existing_results: Optional[List[str]] = None,
        limit: int = 5,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate related queries using LLM understanding

        Args:
            query: User's original query
            existing_results: Existing search results to avoid duplication
            limit: Maximum number of related queries to generate
            context: Optional context information

        Returns:
            List of related query dictionaries with text and metadata
        """
        if not self.is_available():
            return []

        try:
            prompt = self._build_related_queries_prompt(query, existing_results, limit, context)
            
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a business intelligence query assistant. Generate relevant follow-up queries."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                result = response.choices[0].message.content.strip()
            elif self.provider == "anthropic":
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                result = message.content[0].text.strip()
            else:
                return []

            # Parse and format results
            related_queries = []
            parsed_queries = self._parse_llm_response(result)
            
            for i, query_text in enumerate(parsed_queries[:limit]):
                related_queries.append({
                    "text": query_text,
                    "score": 0.95 - (i * 0.05),  # Decreasing score for each item
                    "source": "llm",
                    "keywords": [],
                    "metadata": {
                        "llm_generated": True,
                        "llm_provider": self.provider,
                        "llm_model": self.model
                    }
                })

            logger.info(f"Generated {len(related_queries)} LLM-based related queries for '{query}'")
            return related_queries

        except Exception as e:
            logger.error(f"Failed to generate related queries with LLM: {e}")
            return []

    def rewrite_query(self, query: str, intent: str = "clarify") -> Optional[str]:
        """Rewrite a query for better search results

        Args:
            query: Original query
            intent: Rewrite intent ('clarify', 'expand', 'formalize')

        Returns:
            Rewritten query or None if failed
        """
        if not self.is_available():
            return None

        try:
            prompt = self._build_query_rewrite_prompt(query, intent)
            
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a query optimization assistant. Rewrite queries to be more effective for search."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # Lower temperature for more deterministic rewrites
                    max_tokens=100,
                )
                rewritten = response.choices[0].message.content.strip()
            elif self.provider == "anthropic":
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=100,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                rewritten = message.content[0].text.strip()
            else:
                return None

            logger.info(f"Rewrote query '{query}' to '{rewritten}'")
            return rewritten

        except Exception as e:
            logger.error(f"Failed to rewrite query with LLM: {e}")
            return None

    def _build_query_expansion_prompt(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build prompt for query expansion"""
        prompt = f"Given the business intelligence query: '{query}'\n\n"
        
        if context:
            if "domain" in context:
                prompt += f"Domain: {context['domain']}\n"
            if "user_history" in context and context["user_history"]:
                prompt += f"Recent queries: {', '.join(context['user_history'][:3])}\n"
        
        prompt += "\nGenerate 5 semantically related queries that a user might also search for. "
        prompt += "Return only the queries, one per line, without numbering or explanation."
        
        return prompt

    def _build_related_queries_prompt(
        self,
        query: str,
        existing_results: Optional[List[str]] = None,
        limit: int = 5,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for related query generation"""
        prompt = f"Given the business intelligence query: '{query}'\n\n"
        
        if existing_results:
            prompt += f"Already suggested: {', '.join(existing_results[:5])}\n\n"
        
        if context:
            if "domain" in context:
                prompt += f"Domain: {context['domain']}\n"
        
        prompt += f"\nGenerate {limit} related follow-up queries that would naturally come after this query. "
        prompt += "Focus on logical next steps in analysis or exploration. "
        prompt += "Return only the queries, one per line, without numbering or explanation."
        
        return prompt

    def _build_query_rewrite_prompt(self, query: str, intent: str) -> str:
        """Build prompt for query rewriting"""
        intent_descriptions = {
            "clarify": "make it more specific and clear",
            "expand": "make it more comprehensive",
            "formalize": "make it more formal and professional"
        }
        
        description = intent_descriptions.get(intent, "improve it")
        prompt = f"Rewrite this business intelligence query to {description}: '{query}'\n\n"
        prompt += "Return only the rewritten query, without explanation."
        
        return prompt

    def _parse_llm_response(self, response: str) -> List[str]:
        """Parse LLM response into a list of queries

        Args:
            response: Raw LLM response text

        Returns:
            List of parsed queries
        """
        # Try to parse as line-separated
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        
        # If only one line, try comma-separated
        if len(lines) == 1:
            lines = [item.strip() for item in response.split(',') if item.strip()]
        
        # Clean up any numbering or bullets
        cleaned = []
        for line in lines:
            # Remove common prefixes like "1.", "- ", "* ", etc.
            cleaned_line = line
            for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '0.', '-', '*', '•', '·']:
                if cleaned_line.startswith(prefix):
                    cleaned_line = cleaned_line[len(prefix):].strip()
            
            # Remove quotes
            cleaned_line = cleaned_line.strip('"\'""''')
            
            if cleaned_line and len(cleaned_line) > 2:
                cleaned.append(cleaned_line)
        
        return cleaned
