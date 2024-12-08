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
    DESCRIPTION = "Requests from the OpenAI API"

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
                    "default": "gpt-3.5-turbo",
                },
            },
        },
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "any",
        "name": "any",
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
                api_key=os.environ.get("OPENAI_API_KEY")
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
        "kind": "any",
        "name": "any",
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
        "kind": "any",
        "name": "any",
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
        "kind": "any",
        "name": "any",
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
                "widget": {"kind": "string", "name": "model", "default": "llama3.1-8b"},
            },
        },
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "any",
        "name": "any",
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
        "kind": "any",
        "name": "any",
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
