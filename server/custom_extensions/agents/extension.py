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
        if node_inputs.get("required_inputs"):
            if "api_key" in node_inputs.get("required_inputs"):
                self.api_key = (
                    node_inputs.get("required_inputs").get("api_key").get("values")
                )
            if "prompt" in node_inputs.get("required_inputs"):
                self.prompt = (
                    node_inputs.get("required_inputs").get("prompt").get("values")
                )

        import autogen
        import random

        config_list = [
            {
                "model": "llama3.1-70b",
                "api_key": self.api_key,
                "api_type": "cerebras",
                "max_tokens": 8192,
                "seed": random.randint(1, 1000000),  # Random seed for reproducibility
                "stream": False,
                "temperature": 1.2,
                # "top_p": 0.2, # Note: It is recommended to set temperature or top_p but not both.
            }
        ]

        # Create the agent for tool calling
        chatbot = autogen.ConversableAgent(
            name="chatbot", llm_config={"config_list": config_list}
        )

        # Note that we have changed the termination string to be "HAVE FUN!"
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy", human_input_mode="NEVER", max_consecutive_auto_reply=0
        )

        from time import perf_counter

        start_time = perf_counter()

        # start the conversation
        res = user_proxy.initiate_chat(chatbot, message=self.prompt, silent=True)

        end_time = perf_counter()

        print(f"LLM Duration: {float(end_time - start_time)}s")
        # print(res.summary)

        res_dict = {
            "chat_id": res.chat_id,
            "chat_history": res.chat_history,
            "summary": res.summary,
            "cost": res.cost,
            "human_input": res.human_input,
        }

        return res_dict


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
    },
    "rules": {},
}
