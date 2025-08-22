import os
import functools
from typing import Dict, Any, Optional, List, Callable, Tuple
from abc import ABC, abstractmethod


class LLMTracker:
    """Centralized Langfuse tracking configuration"""

    def __init__(self):
        self.enabled = os.getenv("LANGFUSE_TRACKING_ENABLED", "false").lower() == "true"
        self.client = None
        self.observe = None
        self.tracker_available = self._initialize_langfuse()

    def _initialize_langfuse(self):
        """Initialize Langfuse client and observe decorator"""
        if not self.enabled:
            self.observe = lambda **kwargs: lambda func: func  # No-op decorator
            return False

        try:
            from langfuse import Langfuse, observe

            # Test connection first
            test_client = Langfuse(
                secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                host=os.getenv("LANGFUSE_HOST")
            )

            # Try a simple health check or ping
            try:
                # This will fail fast if connection is refused
                test_client.flush()  # Force any pending requests
            except Exception as conn_error:
                print(f"Langfuse connection failed: {conn_error}")
                print("Continuing without tracking...")
                self.enabled = False
                self.observe = lambda **kwargs: lambda func: func
                return False

            self.client = None
            self.observe = observe
            print("Langfuse tracking initialized successfully")
            return True
        except ImportError:
            print("Langfuse not installed - tracking disabled")
            self.enabled = False
            self.observe = lambda **kwargs: lambda func: func
            return False
        except Exception as e:
            print(f"Failed to initialize Langfuse: {e}")
            self.enabled = False
            self.observe = lambda **kwargs: lambda func: func
            return False

    def track_llm_call(self, name: str = None):
        """Decorator factory for tracking LLM calls"""

        def decorator(func: Callable) -> Callable:
            if not self.enabled or not self.tracker_available:
                return func

            @self.observe(
                name=name or func.__name__,
                as_type="generation"
            )
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    # Extract metadata before function call
                    model = kwargs.get('model', 'unknown')
                    max_tokens = kwargs.get('max_tokens')

                    # Call the actual function
                    result = func(*args, **kwargs)

                    # Extract usage information from result
                    # This needs to be adapted based on your specific LLM response format
                    usage_info = self._extract_usage_info(result, model, max_tokens)
                    if self.client:
                        self.client.update_current_generation(
                            usage_details=usage_info.get("usage_details"),
                            model=usage_info.get('model'),
                            model_parameters=usage_info.get('metadata')
                        )

                    return result
                except Exception as e:
                    raise

            return wrapper

        return decorator

    @staticmethod
    def _extract_usage_info(result, model: str, max_tokens: Optional[int]) -> Dict[str, Any]:
        """Extract usage information from LLM response - override in subclasses"""
        usage_info = {
            "model": model,
            "metadata": {
                "max_tokens": max_tokens,
            }
        }

        tokens_usage = result[-1] if result and len(result) > 1 else {}

        usage_info.update({
            "usage_details": {
                "input": tokens_usage.get('input_tokens', 0),
                "output": tokens_usage.get('output_tokens', 0),
                'cache_read_input_tokens': tokens_usage.get('cached_tokens', 0)
            }
        })

        return usage_info

    def manual_track(self, name: str, input_data: Any, model: str, **kwargs):
        """Manual tracking method for complex scenarios"""
        if not self.enabled or not self.tracker_available:
            return None

        generation = self.client.generation(
            name=name,
            model=model,
            input=input_data,
            **kwargs
        )
        return generation


class LLMConfig:
    def __init__(self, model: str, max_tokens: int, cached: bool):
        self.model = model
        self.max_tokens = max_tokens
        self.cached = cached


class LLMServiceBase(ABC):
    """Base class for LLM services - no decorators on abstract methods"""
    llm_tracker = LLMTracker()

    def __init__(self, api_key: str):
        self.client = self._initialize_client(api_key)
        self.async_client = self._initialize_async_client(api_key)


    @abstractmethod
    def get_function_call_response(
            self,
            prompt: str | List[Dict[str, Any]],
            model: str,
            max_tokens: int,
            function_definition: Dict,
            system_prompt: Optional[str] = None,
            cached: bool = False,
    ) -> Tuple[Dict[str, Any], Dict]:
        """Abstract method - implement with tracking decorator in subclasses"""
        pass

    @abstractmethod
    def get_stream_response(
            self,
            prompt: str,
            model: str,
            max_tokens: int,
            system_prompt: Optional[str] = None,
            cached: bool = False,
    ) -> Tuple:
        """Abstract method - implement with tracking decorator in subclasses"""
        pass

    @abstractmethod
    def get_response(
            self,
            prompt: str | List[Dict[str, Any]] | Any,
            model: str,
            max_tokens: int,
            system_prompt: Optional[str] = None,
            cached: bool = False,
    ) -> Tuple[str, Dict]:
        """Abstract method - implement with tracking decorator in subclasses"""
        pass

    @abstractmethod
    async def get_function_call_response_async(
            self,
            prompt: (
                    str | List[Dict[str, Any]]
            ),
            model: str,
            max_tokens: int,
            function_definition: Dict,
            system_prompt: Optional[str] = None,
            cached: bool = False,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        pass

    @abstractmethod
    def get_images_llm_message_content(self, images_data, prompt):
        pass

    @abstractmethod
    def get_pdfs_llm_message_content(self, pdfs_data, prompt):
        pass

    @abstractmethod
    def get_audios_llm_message_content(
            self, audios_data: List[str], prompt: str
    ):
        raise NotImplementedError

    @abstractmethod
    def _initialize_client(self, api_key: str):
        """Initialize the specific LLM client"""
        pass

    @abstractmethod
    def _initialize_async_client(self, api_key: str):
        pass

    @staticmethod
    def _create_messages(
            prompt: str | List[Dict[str, Any]] | Any,
            system_prompt: Optional[str] = None,
    ) -> list:
        """Helper method to create message format"""
        if isinstance(prompt, list):
            messages = prompt
        else:
            messages = [{"role": "user", "content": str(prompt)}]

        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})
        return messages

