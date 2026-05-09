import asyncio
import random
from time import perf_counter

version = "0.2.0"


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


def _cerebras_inputs_from(node_inputs):
    api_key = None
    prompt = None
    if node_inputs.get("required_inputs"):
        if "api_key" in node_inputs.get("required_inputs"):
            api_key = node_inputs.get("required_inputs").get("api_key").get("values")
        if "prompt" in node_inputs.get("required_inputs"):
            prompt = node_inputs.get("required_inputs").get("prompt").get("values")
    return api_key, prompt


def _run_cerebras_agent(api_key, prompt):
    import autogen

    config_list = [
        {
            "model": "zai-glm-4.7",
            "api_key": api_key,
            "api_type": "cerebras",
            "max_tokens": 8192,
            "seed": random.randint(1, 1000000),  # Random seed for reproducibility
            "stream": False,
            "temperature": 1.2,
            # "top_p": 0.2, # Note: It is recommended to set temperature or top_p but not both.
        }
    ]

    chatbot = autogen.ConversableAgent(
        name="chatbot", llm_config={"config_list": config_list}
    )

    user_proxy = autogen.UserProxyAgent(
        name="user_proxy", human_input_mode="NEVER", max_consecutive_auto_reply=0
    )

    start_time = perf_counter()
    res = user_proxy.initiate_chat(chatbot, message=prompt, silent=True)
    end_time = perf_counter()

    print(f"LLM Duration: {float(end_time - start_time)}s")

    return {
        "chat_id": res.chat_id,
        "chat_history": res.chat_history,
        "summary": res.summary,
        "cost": res.cost,
        "human_input": res.human_input,
    }


class CerebrasAgent:
    CATEGORY = "utilities"
    SUBCATEGORY = "ai_inference"
    DESCRIPTION = "Requests from the Cerebras Cloud API"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "api_key": {
                "kind": "string",
                "name": "api_key",
                "widget": {"kind": "string", "name": "api_key", "default": ""},
            },
            "prompt": {
                "kind": "string",
                "name": "prompt",
                "widget": {"kind": "string", "name": "prompt", "default": ""},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {"kind": "*", "name": "*", "cacheable": True}

    def evaluate(self, node_inputs):
        api_key, prompt = _cerebras_inputs_from(node_inputs)
        self.api_key = api_key
        self.prompt = prompt
        return _run_cerebras_agent(api_key, prompt)


class CerebrasAgentAsync:
    """Same behavior as CerebrasAgent; `evaluate` is async and runs the blocking autogen call in a thread."""

    CATEGORY = "utilities"
    SUBCATEGORY = "ai_inference"
    DESCRIPTION = "Requests from the Cerebras Cloud API (async node)"

    INPUT = CerebrasAgent.INPUT
    OUTPUT = CerebrasAgent.OUTPUT

    async def evaluate(self, node_inputs):
        api_key, prompt = _cerebras_inputs_from(node_inputs)
        self.api_key = api_key
        self.prompt = prompt
        return await asyncio.to_thread(_run_cerebras_agent, api_key, prompt)


EXTENSION_MAPPINGS = {
    "name": "agents",
    "version": version,
    "description": "Extension for agents inference",
    "javascript_class_name": "agents",
    "nodes": {
        "CerebrasAgent": {
            "python_class": CerebrasAgent,
            "javascript_class_name": "CerebrasAgent",
            "display_name": "CerebrasAgent",
        },
        "CerebrasAgentAsync": {
            "python_class": CerebrasAgentAsync,
            "javascript_class_name": "CerebrasAgentAsync",
            "display_name": "CerebrasAgentAsync",
        },
    },
    "rules": {},
}
