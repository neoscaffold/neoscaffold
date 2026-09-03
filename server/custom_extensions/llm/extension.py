import json
import os

version = "0.0.1"


def serialize_object(obj):
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [serialize_object(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: serialize_object(v) for k, v in obj.items()}
    else:
        return str(obj)  # Fallback to string representation


class OpenAI_LLM:
    CATEGORY = "utilities"
    SUBCATEGORY = "ai_inference"
    DESCRIPTION = "Requests text and multimodal responses from the OpenAI API"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "prompt": {
                "kind": "string",
                "name": "prompt",
                "widget": {"kind": "string", "name": "prompt", "default": ""},
            },
        },
        "optional_inputs": {
            "model": {
                "kind": "*",
                "name": "model",
                "widget": {
                    "kind": "string",
                    "name": "model",
                    "default": "gpt-4.1-mini",
                },
            },
            "system_prompt": {
                "kind": "*",
                "name": "system_prompt",
                "widget": {
                    "kind": "string",
                    "name": "system_prompt",
                    "default": "",
                },
            },
            "developer_prompt": {
                "kind": "*",
                "name": "developer_prompt",
                "widget": {
                    "kind": "string",
                    "name": "developer_prompt",
                    "default": "",
                },
            },
            "image_urls": {
                "kind": "*",
                "name": "image_urls",
                "widget": {
                    "kind": "string",
                    "name": "image_urls",
                    "default": "",
                },
            },
            "image_base64": {
                "kind": "*",
                "name": "image_base64",
                "widget": {
                    "kind": "string",
                    "name": "image_base64",
                    "default": "",
                },
            },
            "image_file_ids": {
                "kind": "*",
                "name": "image_file_ids",
                "widget": {
                    "kind": "string",
                    "name": "image_file_ids",
                    "default": "",
                },
            },
            "image_detail": {
                "kind": "*",
                "name": "image_detail",
                "widget": {
                    "kind": "string",
                    "name": "image_detail",
                    "default": "auto",
                },
            },
            "max_output_tokens": {
                "kind": "*",
                "name": "max_output_tokens",
                "widget": {
                    "kind": "number",
                    "name": "max_output_tokens",
                    "default": 1024,
                },
            },
            "temperature": {
                "kind": "*",
                "name": "temperature",
                "widget": {
                    "kind": "number",
                    "name": "temperature",
                    "default": "",
                },
            },
            "top_p": {
                "kind": "*",
                "name": "top_p",
                "widget": {
                    "kind": "number",
                    "name": "top_p",
                    "default": "",
                },
            },
            "previous_response_id": {
                "kind": "*",
                "name": "previous_response_id",
                "widget": {
                    "kind": "string",
                    "name": "previous_response_id",
                    "default": "",
                },
            },
            "tools": {
                "kind": "*",
                "name": "tools",
                "widget": {
                    "kind": "string",
                    "name": "tools",
                    "default": "",
                },
            },
        },
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": False,
    }

    def _input_value(self, inputs, name, default=None):
        return inputs.get(name, {}).get("values", default)

    def _split_values(self, value):
        if not value:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if not isinstance(value, str):
            return [value]

        value = value.strip()
        if not value:
            return []
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
            return [parsed]
        except json.JSONDecodeError:
            if "data:image/" in value:
                return [item.strip() for item in value.splitlines() if item.strip()]
            return [
                item.strip()
                for item in value.replace(",", "\n").splitlines()
                if item.strip()
            ]

    def _parse_tools(self, value):
        if not value:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            return [value]
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError(
                "OpenAI_LLM tools must be JSON, e.g. "
                "'[{\"type\": \"web_search_preview\"}]'"
            ) from error

        if isinstance(parsed, dict):
            return [parsed]
        return parsed

    def _set_optional_number(self, request, optional_inputs, name, default_value=None):
        value = self._input_value(optional_inputs, name, "")
        if value in ("", None):
            return

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            numeric_value = value

        if default_value is not None and numeric_value == default_value:
            return

        request[name] = numeric_value

    def _get_image_value(self, image):
        if not isinstance(image, dict):
            return image

        return (
            image.get("image_url")
            or image.get("url")
            or image.get("data_url")
            or image.get("base64")
            or image.get("b64_json")
            or image.get("image_path")
            or image.get("path")
            or ""
        )

    def _build_image_url(self, image, default_mime_type="image/png"):
        import base64
        import mimetypes
        import os

        image = self._get_image_value(image)
        if isinstance(image, (bytes, bytearray)):
            encoded_image = base64.b64encode(image).decode()
            return f"data:{default_mime_type};base64,{encoded_image}"

        if not isinstance(image, str):
            raise ValueError(
                "image input must be a URL, data URL, Base64 string, file path, or bytes"
            )

        image = image.strip()
        if image.startswith("http://") or image.startswith("https://"):
            return image
        if image.startswith("data:image/"):
            if "," not in image:
                raise ValueError("image data URLs must include a comma before the Base64 payload")
            return image
        if os.path.exists(image):
            mime_type = mimetypes.guess_type(image)[0] or default_mime_type
            with open(image, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode()
            return f"data:{mime_type};base64,{encoded_image}"

        return f"data:{default_mime_type};base64,{image}"

    def _build_input(self, prompt, optional_inputs):
        content = [{"type": "input_text", "text": prompt}]
        image_detail = self._input_value(optional_inputs, "image_detail", "auto")

        for image_url in self._split_values(
            self._input_value(optional_inputs, "image_urls", "")
        ):
            image_part = {
                "type": "input_image",
                "image_url": self._build_image_url(image_url),
            }
            if image_detail:
                image_part["detail"] = image_detail
            content.append(image_part)

        for image_base64 in self._split_values(
            self._input_value(optional_inputs, "image_base64", "")
        ):
            image_part = {
                "type": "input_image",
                "image_url": self._build_image_url(image_base64),
            }
            if image_detail:
                image_part["detail"] = image_detail
            content.append(image_part)

        for file_id in self._split_values(
            self._input_value(optional_inputs, "image_file_ids", "")
        ):
            image_part = {"type": "input_image", "file_id": file_id}
            if image_detail:
                image_part["detail"] = image_detail
            content.append(image_part)

        return [{"role": "user", "content": content}]

    def evaluate(self, node_inputs):
        required_inputs = node_inputs.get("required_inputs", {})
        optional_inputs = node_inputs.get("optional_inputs", {})

        prompt = self._input_value(required_inputs, "prompt", "")
        model = self._input_value(optional_inputs, "model", "gpt-4.1-mini")

        request = {
            "model": model,
            "input": self._build_input(prompt, optional_inputs),
            "instructions": self._input_value(optional_inputs, "system_prompt", ""),
            "max_output_tokens": self._input_value(
                optional_inputs, "max_output_tokens", 1024
            ),
            "previous_response_id": self._input_value(
                optional_inputs, "previous_response_id", ""
            ),
        }
        self._set_optional_number(request, optional_inputs, "temperature", 1)
        self._set_optional_number(request, optional_inputs, "top_p", 1)

        developer_prompt = self._input_value(optional_inputs, "developer_prompt", "")
        if developer_prompt:
            request["input"].insert(
                0,
                {
                    "role": "developer",
                    "content": [{"type": "input_text", "text": developer_prompt}],
                },
            )

        tools = self._parse_tools(self._input_value(optional_inputs, "tools", ""))
        if tools:
            request["tools"] = tools

        request = {
            key: value for key, value in request.items() if value not in ("", None)
        }

        from openai import OpenAI

        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = client.responses.create(**request)
        return serialize_object(response)


class OpenAI_Image:
    CATEGORY = "utilities"
    SUBCATEGORY = "ai_inference"
    DESCRIPTION = "Generates images with the OpenAI Images API"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "prompt": {
                "kind": "string",
                "name": "prompt",
                "widget": {"kind": "string", "name": "prompt", "default": ""},
            },
        },
        "optional_inputs": {
            "model": {
                "kind": "*",
                "name": "model",
                "widget": {
                    "kind": "string",
                    "name": "model",
                    "default": "gpt-image-2",
                },
            },
            "size": {
                "kind": "*",
                "name": "size",
                "widget": {
                    "kind": "string",
                    "name": "size",
                    "default": "1024x1024",
                },
            },
            "quality": {
                "kind": "*",
                "name": "quality",
                "widget": {
                    "kind": "string",
                    "name": "quality",
                    "default": "auto",
                },
            },
            "background": {
                "kind": "*",
                "name": "background",
                "widget": {
                    "kind": "string",
                    "name": "background",
                    "default": "auto",
                },
            },
            "output_format": {
                "kind": "*",
                "name": "output_format",
                "widget": {
                    "kind": "string",
                    "name": "output_format",
                    "default": "png",
                },
            },
            "n": {
                "kind": "*",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 1},
            },
            "timeout": {
                "kind": "*",
                "name": "timeout",
                "widget": {"kind": "number", "name": "timeout", "default": 120},
            },
        },
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": False,
    }

    def evaluate(self, node_inputs):
        required_inputs = node_inputs.get("required_inputs", {})
        optional_inputs = node_inputs.get("optional_inputs", {})

        prompt = required_inputs.get("prompt", {}).get("values", "")
        image_count = optional_inputs.get("n", {}).get("values", 1)
        image_count = int(image_count or 1)
        timeout = optional_inputs.get("timeout", {}).get("values", 120)
        timeout = float(timeout or 120)
        request = {
            "model": optional_inputs.get("model", {}).get("values", "gpt-image-2"),
            "prompt": prompt,
            "size": optional_inputs.get("size", {}).get("values", "1024x1024"),
            "quality": optional_inputs.get("quality", {}).get("values", "auto"),
            "background": optional_inputs.get("background", {}).get("values", "auto"),
            "output_format": optional_inputs.get("output_format", {}).get(
                "values", "png"
            ),
            "n": image_count,
        }

        # Avoid sending empty optional values when widgets are cleared.
        request = {key: value for key, value in request.items() if value not in ("", None)}

        from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI

        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), timeout=timeout)
        try:
            image_response = client.images.generate(**request)
        except APITimeoutError as exc:
            raise RuntimeError(
                f"OpenAI image generation timed out after {timeout:g} seconds"
            ) from exc
        except APIStatusError as exc:
            raise RuntimeError(
                "OpenAI image generation failed with "
                f"status {exc.status_code}: {exc.response.text}"
            ) from exc
        except APIConnectionError as exc:
            raise RuntimeError(
                f"OpenAI image generation connection failed: {exc}"
            ) from exc

        return serialize_object(image_response)


class Anthropic_LLM:
    CATEGORY = "utilities"
    SUBCATEGORY = "ai_inference"
    DESCRIPTION = "Requests from the Anthropic API"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "prompt": {
                "kind": "string",
                "name": "prompt",
                "widget": {"kind": "string", "name": "prompt", "default": ""},
            },
        },
        "optional_inputs": {
            "model": {
                "kind": "*",
                "name": "model",
                "widget": {
                    "kind": "string",
                    "name": "model",
                    "default": "claude-3-5-sonnet-20240620",
                },
            },
        },
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": False,
    }

    def evaluate(self, node_inputs):
        self.client = None

        # load the node_inputs
        if node_inputs.get("required_inputs"):
            if "prompt" in node_inputs.get("required_inputs"):
                self.prompt = (
                    node_inputs.get("required_inputs").get("prompt").get("values")
                )

            if "model" in node_inputs.get("optional_inputs"):
                self.model = (
                    node_inputs.get("optional_inputs").get("model").get("values")
                )

        if not self.client:
            from anthropic import Anthropic

            self.client = Anthropic(
                # This is the default and can be omitted
                api_key=os.environ.get("ANTHROPIC_API_KEY"),
            )

        message = self.client.messages.create(
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": self.prompt,
                }
            ],
            model=self.model,
        )
        return serialize_object(message)


class Perplexity_LLM:
    CATEGORY = "utilities"
    SUBCATEGORY = "ai_inference"
    DESCRIPTION = "Requests from the Perplexity LLM"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "prompt": {
                "kind": "string",
                "name": "prompt",
                "widget": {"kind": "string", "name": "prompt", "default": ""},
            },
        },
        "optional_inputs": {
            "model": {
                "kind": "*",
                "name": "model",
                "widget": {
                    "kind": "string",
                    "name": "model",
                    "default": "llama-3.1-sonar-small-128k-online",
                },
            },
        },
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": False,
    }

    def evaluate(self, node_inputs):
        self.client = None

        # load the node_inputs
        if node_inputs.get("required_inputs"):
            if "prompt" in node_inputs.get("required_inputs"):
                self.prompt = (
                    node_inputs.get("required_inputs").get("prompt").get("values")
                )

            if "model" in node_inputs.get("optional_inputs"):
                self.model = (
                    node_inputs.get("optional_inputs").get("model").get("values")
                )

        if not self.client:
            from openai import OpenAI

            self.client = OpenAI(
                # This is the default and can be omitted
                api_key=os.environ.get("PPL_API_KEY"),
                base_url="https://api.perplexity.ai",
            )

        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": self.prompt,
                }
            ],
            model=self.model,
        )

        response = {
            "id": chat_completion.id,
            "created": chat_completion.created,
            "model": chat_completion.model,
            "choices": [
                {
                    "index": choice.index,
                    "message": {
                        "role": choice.message.role,
                        "content": choice.message.content,
                    },
                    "finish_reason": choice.finish_reason,
                }
                for choice in chat_completion.choices
            ],
            "usage": {
                "prompt_tokens": chat_completion.usage.prompt_tokens,
                "completion_tokens": chat_completion.usage.completion_tokens,
                "total_tokens": chat_completion.usage.total_tokens,
            },
        }
        return response


class Cohere_LLM:
    CATEGORY = "utilities"
    SUBCATEGORY = "ai_inference"
    DESCRIPTION = "Requests from the Cophere LLM"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "prompt": {
                "kind": "string",
                "name": "prompt",
                "widget": {"kind": "string", "name": "prompt", "default": ""},
            },
        },
        "optional_inputs": {
            "model": {
                "kind": "*",
                "name": "model",
                "widget": {"kind": "string", "name": "model", "default": "command"},
            },
        },
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": False,
    }

    def evaluate(self, node_inputs):
        self.client = None

        # load the node_inputs
        if node_inputs.get("required_inputs"):
            if "prompt" in node_inputs.get("required_inputs"):
                self.prompt = (
                    node_inputs.get("required_inputs").get("prompt").get("values")
                )

            if "model" in node_inputs.get("optional_inputs"):
                self.model = (
                    node_inputs.get("optional_inputs").get("model").get("values")
                )

        if not self.client:
            import cohere

            self.client = cohere.Client(
                api_key=os.environ.get("CO_API_KEY"),
            )

        chat = self.client.chat(message=self.prompt, model="command")

        resp = {
            "text": chat.text,
            "generation_id": chat.generation_id,
            "citations": serialize_object(chat.citations),
            "documents": serialize_object(chat.documents),
            "is_search_required": chat.is_search_required,
            "search_queries": serialize_object(chat.search_queries),
            "search_results": serialize_object(chat.search_results),
            "finish_reason": chat.finish_reason,
            "tool_calls": serialize_object(chat.tool_calls),
            "chat_history": serialize_object(chat.chat_history),
            "prompt": chat.prompt,
            "meta": serialize_object(chat.meta),
        }
        return resp


class Cerebras_LLM:
    CATEGORY = "utilities"
    SUBCATEGORY = "ai_inference"
    DESCRIPTION = "Requests from the Cerebras Cloud API"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "prompt": {
                "kind": "string",
                "name": "prompt",
                "widget": {"kind": "string", "name": "prompt", "default": ""},
            },
        },
        "optional_inputs": {
            "model": {
                "kind": "*",
                "name": "model",
                "widget": {"kind": "string", "name": "model", "default": "qwen-3.8-27b"},
            },
        },
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": False,
    }

    def evaluate(self, node_inputs):
        self.client = None
        # load the node_inputs
        if node_inputs.get("required_inputs"):
            if "prompt" in node_inputs.get("required_inputs"):
                self.prompt = (
                    node_inputs.get("required_inputs").get("prompt").get("values")
                )

            if "model" in node_inputs.get("optional_inputs"):
                self.model = (
                    node_inputs.get("optional_inputs").get("model").get("values")
                )

        if not self.client:
            from cerebras.cloud.sdk import Cerebras

            self.client = Cerebras(
                api_key=os.environ.get("CEREBRAS_API_KEY"),
            )

        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": self.prompt,
                }
            ],
        )
        response = serialize_object(chat_completion)
        return response


class Groq_LLM:
    CATEGORY = "utilities"
    SUBCATEGORY = "ai_inference"
    DESCRIPTION = "Requests from the Groq Cloud API"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "prompt": {
                "kind": "string",
                "name": "prompt",
                "widget": {"kind": "string", "name": "prompt", "default": ""},
            },
        },
        "optional_inputs": {
            "model": {
                "kind": "*",
                "name": "model",
                "widget": {
                    "kind": "string",
                    "name": "model",
                    "default": "llama3-8b-8192",
                },
            },
        },
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": False,
    }

    def evaluate(self, node_inputs):
        self.client = None
        # load the node_inputs
        if node_inputs.get("required_inputs"):
            if "prompt" in node_inputs.get("required_inputs"):
                self.prompt = (
                    node_inputs.get("required_inputs").get("prompt").get("values")
                )

            if "model" in node_inputs.get("optional_inputs"):
                self.model = (
                    node_inputs.get("optional_inputs").get("model").get("values")
                )

        if not self.client:
            from groq import Groq

            self.client = Groq(
                # This is the default and can be omitted
                api_key=os.environ.get("GROQ_API_KEY"),
            )

        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": self.prompt,
                }
            ],
        )
        response = serialize_object(chat_completion)
        return response


EXTENSION_MAPPINGS = {
    "name": "llm",
    "version": version,
    "description": "Extension for llm inference",
    "javascript_class_name": "llm",
    "nodes": {
        "OpenAI_LLM": {
            "python_class": OpenAI_LLM,
            "javascript_class_name": "OpenAI_LLM",
            "display_name": "OpenAI_LLM",
        },
        "OpenAI_Image": {
            "python_class": OpenAI_Image,
            "javascript_class_name": "OpenAI_Image",
            "display_name": "OpenAI_Image",
        },
        "Anthropic_LLM": {
            "python_class": Anthropic_LLM,
            "javascript_class_name": "Anthropic_LLM",
            "display_name": "Anthropic_LLM",
        },
        "Perplexity_LLM": {
            "python_class": Perplexity_LLM,
            "javascript_class_name": "Perplexity_LLM",
            "display_name": "Perplexity_LLM",
        },
        "Cohere_LLM": {
            "python_class": Cohere_LLM,
            "javascript_class_name": "Cohere_LLM",
            "display_name": "Cohere_LLM",
        },
        "Cerebras_LLM": {
            "python_class": Cerebras_LLM,
            "javascript_class_name": "Cerebras_LLM",
            "display_name": "Cerebras_LLM",
        },
        "Groq_LLM": {
            "python_class": Groq_LLM,
            "javascript_class_name": "Groq_LLM",
            "display_name": "Groq_LLM",
        },
    },
    "rules": {},
}
