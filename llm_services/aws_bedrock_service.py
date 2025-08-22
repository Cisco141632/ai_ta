import base64
from typing import Dict, Any, List, Optional, Generator, Tuple

import boto3
from botocore.exceptions import ClientError

from llm_services.llm_service import LLMServiceBase


class AWSBedrockModelConfig:
    """Configuration constants for AWS Bedrock models"""

    CLAUDE_3_7_SONNET = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    MAX_OUTPUT_TOKENS_FOR_SONNET_3_7 = 64000


class AWSBedrockService(LLMServiceBase):
    """
    AWS Bedrock service implementation for Claude models using AnthropicBedrock library

    This implementation doesn't require an API key as it uses AWS credentials
    from the environment or configuration files.
    """

    def __init__(self, region_name: str = "us-east-1"):
        """
        Initialize the AWS Bedrock service

        Args:
            region_name: AWS region name where Bedrock is available
        """
        self.region_name = region_name

        # API key not used but required by base class
        super().__init__(api_key=None)
        self.client = self._initialize_client(api_key=None)

    def _initialize_client(self, api_key: str = None):
        """
        Initialize the AnthropicBedrock client

        Args:
            api_key: Not used for AWS Bedrock, included for compatibility with base class

        Returns:
            AnthropicBedrock client that uses AWS credentials
        """
        return boto3.Session().client(
            service_name="bedrock-runtime",
            region_name=self.region_name,
            # Uses AWS credentials from environment or ~/.aws/credentials
        )

    def _initialize_async_client(self, api_key: str):
        pass

    def get_function_call_response(
        self,
        prompt: str | List[Dict[str, Any]],
        model: str,
        max_tokens: int,
        function_definition: Dict,
        system_prompt: Optional[str] = None,
        cached: bool = False,
    ) -> Dict[str, Any]:
        """
        Get a function call response from the model (Claude via Bedrock)
        Args:
            prompt: User prompt or list of message objects
            model: Model ID to use
            max_tokens: Maximum tokens to generate
            function_definition: Tool/function definition dict
            system_prompt: Optional system prompt
        Returns:
            Function call arguments as a dictionary
        """
        try:
            function_defs = self._transform_function_definition(
                [function_definition]
            )
            prompt = self._validate_and_update_the_prompt_structure(prompt)
            messages = self._create_messages(
                prompt=prompt, system_prompt=system_prompt
            )

            response = self.client.converse(
                modelId=model,
                inferenceConfig={
                    "maxTokens": max_tokens,
                },
                messages=messages,
                toolConfig=function_defs,
            )
            return self._extract_function_call_arguments(response)
        except Exception as e:
            print(f"Error in get_function_call_response: {e}")
            raise

    def get_stream_response(
        self,
        prompt: Any,
        model: str,
        max_tokens: int,
        system_prompt: Optional[str] = None,
        cached: bool = False,
    ) -> Generator[str, None, None]:
        """
        Get a streaming response from the model

        Args:
            prompt: User prompt or list of message objects
            model: Model ID to use
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            cached: Whether to use prompt caching

        Yields:
            Text chunks from the streaming response
        """
        try:
            # Convert to messages format if needed
            messages = self._create_messages(
                prompt=prompt, system_prompt=system_prompt
            )

            # Set up extra headers for caching if needed
            extra_headers = None
            if cached:
                extra_headers = {"anthropic-beta": "prompt-caching-2024-07-31"}

            # Use the AnthropicBedrock client to stream the response
            with self.client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                messages=messages,
                extra_headers=extra_headers,
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except ClientError as e:
            print(f"Error communicating with Bedrock Converse API: {e}")
            return None
        except Exception as e:
            print(f"Error in get_stream_response: {e}")
            raise

    def get_response(
        self,
        prompt: str | List[Dict[str, Any]] | Any,
        model: str,
        max_tokens: int,
        system_prompt: Optional[str] = None,
        cached: bool = False,
    ) -> str:
        """
        Get a complete response from the model

        Args:
            prompt: User prompt or list of message objects
            model: Model ID to use
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            cached: Whether to use prompt caching

        Returns:
            Complete text response from the model
        """
        try:
            # Convert to messages format if needed
            messages = self._create_messages(
                prompt=prompt, system_prompt=system_prompt
            )

            # Use the AnthropicBedrock client to create a message
            response = self.client.converse(
                modelId=model,
                inferenceConfig={
                    "maxTokens": max_tokens,
                },
                messages=messages,
            )
            print("response: ", response)
            # Extract the generated text
            return response["output"]["message"]["content"][0]["text"]
        except ClientError as e:
            print(f"Error communicating with Bedrock Converse API: {e}")
            raise
        except Exception as e:
            print(f"Error in get_response: {e}")
            raise


    async def get_function_call_response_async(self, prompt: (
            str | List[Dict[str, Any]]
    ), model: str, max_tokens: int, function_definition: Dict, system_prompt: Optional[str] = None,
                                               cached: bool = False) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        raise NotImplemented

    def get_audios_llm_message_content(self, audios_data: List[str], prompt: str):
        raise NotImplemented

    @staticmethod
    def _extract_function_call_arguments(response) -> Dict[str, Any]:
        """
        Extract function call arguments from the response

        Args:
            response: Response from AnthropicBedrock client

        Returns:
            Function call arguments as a dictionary
        """
        try:
            # Bedrock/Anthropic response: response["output"]["message"]["content"] is a list of dicts
            content_blocks = (
                response.get("output", {})
                .get("message", {})
                .get("content", [])
            )
            for block in content_blocks:
                if isinstance(block, dict) and "toolUse" in block:
                    return block["toolUse"].get("input", {})
            raise ValueError(
                "Failed to extract function call arguments from response"
            )
        except Exception as e:
            print(f"Error extracting function call arguments: {e}")
            return {}

    @staticmethod
    def _transform_function_definition(function_definitions: List):
        """
        Transform the function definition to a format compatible with AnthropicBedrock.
        Args:
            function_definition: Function definition dict.
        """
        bedrock_function_defs = []
        for function_def in function_definitions:
            bedrock_function_defs.append(
                {
                    "toolSpec": {
                        "name": function_def["name"],
                        "description": function_def["description"],
                        "inputSchema": {"json": function_def["input_schema"]},
                    }
                }
            )

        return {"tools": bedrock_function_defs}

    def get_images_llm_message_content(self, images_data, prompt):
        """
        Create message content with images for Claude (Anthropic Bedrock API).
        Args:
            images_data: List of dicts with keys 'image_data' (bytes) and 'image_type' (e.g., 'jpeg', 'png').
            prompt: Text prompt for the model.
        Returns:
            Dict: Message content ready for Claude API.
        """
        contents = []
        for image_data in images_data:
            contents.append(
                {
                    "image": {
                        "format": image_data["image_type"],
                        "source": {"bytes": image_data["image_data"]},
                    }
                }
            )
        contents.append({"text": prompt})
        return contents

    def get_pdfs_llm_message_content(self, pdfs_data, prompt):
        """
        Create message content with PDFs for Claude (Anthropic Bedrock API).
        Args:
            pdfs_data: List of bytes objects (raw PDF content).
            prompt: Text prompt for the model.
        Returns:
            List[Dict]: Message content list, as expected by Bedrock Claude API.
        """
        documents = []
        for idx, pdf_data in enumerate(pdfs_data):
            pdf_name = f"sample_pdf-{idx}"
            updated_file_name = "".join(pdf_name.split(" "))
            bytes_data = base64.b64decode(pdf_data)

            documents.append(
                {
                    "document": {
                        "name": updated_file_name,
                        "format": "pdf",
                        "source": {"bytes": bytes_data},
                    }
                }
            )
        documents.append({"text": prompt})
        return documents

    @staticmethod
    def _validate_and_update_the_prompt_structure(prompt):
        if type(prompt) == str:
            print(f"type of prompt: {type(prompt)}")
            return [{"text": prompt}]
        else:
            return prompt
