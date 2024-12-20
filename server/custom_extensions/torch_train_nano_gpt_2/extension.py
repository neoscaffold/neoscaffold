import os

version = "0.0.1"

# PyTorch nn.Module definitions for the GPT-2 model

class CastedLinear:
    CATEGORY = "torch"
    SUBCATEGORY = "neural_networks"
    DESCRIPTION = "CastedLinear, fully connected layer with casted weights"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "in_features": {
                "kind": "number",
                "name": "in_features",
                "widget": {"kind": "number", "name": "in_features", "default": ""},
            },
            "out_features": {
                "kind": "number",
                "name": "out_features",
                "widget": {"kind": "number", "name": "out_features", "default": ""},
            }
        },
        "optional_inputs": {
            "bias": {
                "kind": "boolean",
                "name": "bias",
                "widget": {"kind": "toggle", "name": "bias", "default": False},
            }
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "nn.Module",
        "cacheable": False,
    }

    def evaluate(self, node_inputs):
        # load the node_inputs
        if node_inputs.get("required_inputs"):
            if "in_features" in node_inputs.get("required_inputs"):
                self.in_features = (
                    node_inputs.get("required_inputs").get("in_features").get("values")
                )

            if "out_features" in node_inputs.get("required_inputs"):
                self.out_features = (
                    node_inputs.get("required_inputs").get("out_features").get("values")
                )

            if "bias" in node_inputs.get("optional_inputs"):
                self.bias = (
                    node_inputs.get("optional_inputs").get("bias").get("values")
                )

        from torch import nn
        from torch.nn.functional import linear

        class CastedLinearModule(nn.Linear):
            def __init__(self, in_features, out_features, bias=False):
                super().__init__(in_features, out_features, bias=False)

            def forward(self, x):
                return linear(x, self.weight.to(x.dtype))

        return CastedLinearModule(
            in_features=self.in_features,
            out_features=self.out_features,
            bias=self.bias
        )


class RotaryEmbedding:
    CATEGORY = "torch"
    SUBCATEGORY = "neural_networks"
    DESCRIPTION = "RotaryEmbedding"

    INPUT = {
        "required_inputs": {
            "dim": {
                "kind": "number",
                "name": "dim",
                "widget": {"kind": "number", "name": "dim", "default": ""},
            },
            "base": {
                "kind": "number",
                "name": "base",
                "widget": {"kind": "number", "name": "base", "default": 10000},
            },
        },
    }

    OUTPUT = {
        "kind": "*",
        "name": "nn.Module",
        "cacheable": False,
    }

    def evaluate(self, node_inputs):
        # load the node_inputs
        if node_inputs.get("required_inputs"):
            if "dim" in node_inputs.get("required_inputs"):
                self.input_dim = node_inputs.get("required_inputs").get("dim").get("values")

            if "base" in node_inputs.get("required_inputs"):
                self.input_base = node_inputs.get("required_inputs").get("base").get("values")

        from torch import nn, arange, outer, cat

        class RotaryEmbeddingModule(nn.Module):
            def __init__(self, dim, base=10000):
                super().__init__()
                self.register_buffer('inv_freq', (1 / base) ** (arange(0, dim, 2) / dim))
                self.seq_len_cached = None
                self.cos_cached = None
                self.sin_cached = None

            def forward(self, x):
                seq_len = x.shape[1]
                if seq_len != self.seq_len_cached:
                    t = arange(seq_len, device=x.device)
                    freqs = outer(t, self.inv_freq)
                    self.seq_len_cached = seq_len
                    self.cos_cached = freqs.cos()
                    self.sin_cached = freqs.sin()
                cos, sin = self.cos_cached[None, :, None, :], self.sin_cached[None, :, None, :]

                # apply_rotary_emb(x, cos, sin)
                x1, x2 = x.chunk(2, dim=3)
                y1 = x1 * cos + x2 * sin
                y2 = x1 * (-sin) + x2 * cos

                return cat((y1, y2), 3).type_as(x)

        return RotaryEmbeddingModule(self.input_dim, base=self.input_base)

class CausalSelfAttention:
    CATEGORY = "torch"
    SUBCATEGORY = "neural_networks"
    DESCRIPTION = "CausalSelfAttention"

    INPUT = {
        "required_inputs": {
            "dim": {
                "kind": "number",
                "name": "dim",
                "widget": {"kind": "number", "name": "dim", "default": ""},
            },
            "num_heads": {
                "kind": "number",
                "name": "num_heads",
                "widget": {"kind": "number", "name": "num_heads", "default": ""},
            },
            "query_linear": {
                "kind": "*",
                "name": "query_linear",
            },
            "keys_linear": {
                "kind": "*",
                "name": "keys_linear",
            },
            "values_linear": {
                "kind": "*",
                "name": "values_linear",
            },
            "rotary": {
                "kind": "*",
                "name": "rotary",
            },
            "context_linear": {
                "kind": "*",
                "name": "context_linear",
            },
        },
    }

    OUTPUT = {
        "kind": "*",
        "name": "nn.Module",
        "cacheable": False,
    }

    def evaluate(self, node_inputs):
        # load the node_inputs
        if node_inputs.get("required_inputs"):
            if "dim" in node_inputs.get("required_inputs"):
                self.input_dim = node_inputs.get("required_inputs").get("dim").get("values")

            if "num_heads" in node_inputs.get("required_inputs"):
                self.input_num_heads = node_inputs.get("required_inputs").get("num_heads").get("values")

            if "query_linear" in node_inputs.get("required_inputs"):
                self.input_query_linear = node_inputs.get("required_inputs").get("query_linear").get("values")

            if "keys_linear" in node_inputs.get("required_inputs"):
                self.input_keys_linear = node_inputs.get("required_inputs").get("keys_linear").get("values")

            if "values_linear" in node_inputs.get("required_inputs"):
                self.input_values_linear = node_inputs.get("required_inputs").get("values_linear").get("values")

            if "rotary" in node_inputs.get("required_inputs"):
                self.input_rotary = node_inputs.get("required_inputs").get("rotary").get("values")

            if "context_linear" in node_inputs.get("required_inputs"):
                self.input_context_linear = node_inputs.get("required_inputs").get("context_linear").get("values")

        from torch import nn, tensor
        from torch.nn.functional import rms_norm
        from torch.nn.attention.flex_attention import flex_attention

        def norm(x):
            return rms_norm(x, (x.size(-1),))

        class CausalSelfAttentionModule(nn.Module):
            def __init__(
                self,
                dim,
                num_heads,
                casted_queries,
                casted_keys,
                casted_values,
                rotary,
                casted_projection
            ):
                super().__init__()
                assert dim % num_heads == 0
                self.num_heads = num_heads
                self.casted_queries = casted_queries # CastedLinear(dim, dim)
                self.casted_keys = casted_keys # CastedLinear(dim, dim)
                self.casted_values = casted_values # CastedLinear(dim, dim)
                self.lambdas = nn.Parameter(tensor([0.5, 0.5]))
                self.rotary = rotary # RotaryEmbedding(dim // num_heads)
                self.casted_projection = casted_projection # CastedLinear(dim, dim)
                self.casted_projection.weight.data.zero_()

            def forward(self, x, vi, block_mask):
                B, T = x.size(0), x.size(1) # batch size, sequence length (Time)
                assert B == 1, "Must use batch size = 1 for FlexAttention"
                q = self.casted_queries(x).view(B, T, self.num_heads, -1)
                k = self.casted_keys(x).view(B, T, self.num_heads, -1)
                v = self.casted_values(x).view(B, T, self.num_heads, -1)
                v = self.lambdas[0] * v + self.lambdas[1] * vi.view_as(v) # @KoszarskyB & @Grad62304977

                q, k = norm(q), norm(k) # QK norm @Grad62304977
                q, k = self.rotary(q), self.rotary(k)
                y = flex_attention(
                    q.transpose(1, 2),
                    k.transpose(1, 2),
                    v.transpose(1, 2),
                    block_mask=block_mask,
                    enable_gqa=True
                )
                y = y.transpose(1, 2).contiguous().view_as(x) # re-assemble all head outputs side by side
                y = self.casted_projection(y)
                return y

        return CausalSelfAttentionModule(
            dim=self.input_dim,
            num_heads=self.input_num_heads,
            casted_queries=self.input_query_linear,
            casted_keys=self.input_keys_linear,
            casted_values=self.input_values_linear,
            rotary=self.input_rotary,
            casted_projection=self.input_context_linear
        )

class MultiLayerPerceptron:
    CATEGORY = "torch"
    SUBCATEGORY = "neural_networks"
    DESCRIPTION = "MLP, Multi Layer Perceptron"

    INPUT = {
        "required_inputs": {
            "dim": {
                "kind": "number",
                "name": "dim",
                "widget": {"kind": "number", "name": "dim", "default": ""},
            },
            "casted_fully_connected": {
                "kind": "*",
                "name": "casted_fully_connected",
            },
            "casted_up_projection": {
                "kind": "*",
                "name": "casted_up_projection",
            },
        },
    }

    OUTPUT = {
        "kind": "*",
        "name": "nn.Module",
        "cacheable": False,
    }

    def evaluate(self, node_inputs):
        if node_inputs.get("required_inputs"):
            if "dim" in node_inputs.get("required_inputs"):
                self.input_dim = node_inputs.get("required_inputs").get("dim").get("values")

            if "casted_fully_connected" in node_inputs.get("required_inputs"):
                self.input_casted_fully_connected = node_inputs.get("required_inputs").get("casted_fully_connected").get("values")

            if "casted_up_projection" in node_inputs.get("required_inputs"):
                self.input_casted_up_projection = node_inputs.get("required_inputs").get("casted_up_projection").get("values")

        from torch import nn
        from torch.nn.functional import relu

        class MLPModule(nn.Module):
            def __init__(
                self,
                casted_fully_connected,
                casted_up_projection
            ):
                super().__init__()
                self.casted_fully_connected = casted_fully_connected
                self.casted_up_projection = casted_up_projection
                self.casted_up_projection.weight.data.zero_()

            def forward(self, x):
                x = self.casted_fully_connected(x)
                x = relu(x).square() # https://arxiv.org/abs/2109.08668v2; ~1-2% better than GELU
                x = self.casted_up_projection(x)
                return x

        return MLPModule(
            casted_fully_connected=self.input_casted_fully_connected,
            casted_up_projection=self.input_casted_up_projection
        )

class TransformerBlock:
    CATEGORY = "torch"
    SUBCATEGORY = "neural_networks"
    DESCRIPTION = "Block, Transformer Block"

    INPUT = {
        "required_inputs": {
            "causal_self_attention": {
                "kind": "*",
                "name": "causal_self_attention",
            },
            "multi_layer_perceptron": {
                "kind": "*",
                "name": "multi_layer_perceptron",
            }
        },
    }

    OUTPUT = {
        "kind": "*",
        "name": "nn.Module",
        "cacheable": False,
    }

    def evaluate(self, node_inputs):
        if node_inputs.get("required_inputs"):
            if "causal_self_attention" in node_inputs.get("required_inputs"):
                self.input_causal_self_attention = node_inputs.get("required_inputs").get("causal_self_attention").get("values")

            if "multi_layer_perceptron" in node_inputs.get("required_inputs"):
                self.input_multi_layer_perceptron = node_inputs.get("required_inputs").get("multi_layer_perceptron").get("values")

        from torch import nn, tensor
        from torch.nn.functional import rms_norm

        def norm(x):
            return rms_norm(x, (x.size(-1),))

        class BlockModule(nn.Module):
            def __init__(
                self,
                causal_self_attention,
                multi_layer_perceptron
            ):
                super().__init__()
                self.causal_self_attention = causal_self_attention
                self.multi_layer_perceptron = multi_layer_perceptron
                self.lambdas = nn.Parameter(tensor([1., 0.]))

            def forward(
                self,
                x,
                vi,
                x0,
                block_mask
            ):
                x = self.lambdas[0] * x + self.lambdas[1] * x0
                x = x + self.causal_self_attention(norm(x), vi, block_mask)
                x = x + self.multi_layer_perceptron(norm(x))
                return x

        return BlockModule(
            causal_self_attention=self.input_causal_self_attention,
            multi_layer_perceptron=self.input_multi_layer_perceptron
        )


class ValueEmbedding:
    CATEGORY = "torch"
    SUBCATEGORY = "neural_networks"
    DESCRIPTION = "ValueEmbedding"

    INPUT = {
        "required_inputs": {
            "vocab_size": {
                "kind": "number",
                "name": "vocab_size",
                "widget": {"kind": "number", "name": "vocab_size", "default": ""},
            },
            "model_dim": {
                "kind": "number",
                "name": "model_dim",
                "widget": {"kind": "number", "name": "model_dim", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "*",
        "name": "nn.Module",
        "cacheable": False,
    }

    def evaluate(self, node_inputs):
        if node_inputs.get("required_inputs"):
            if "model_dim" in node_inputs.get("required_inputs"):
                self.input_model_dim = node_inputs.get("required_inputs").get("model_dim").get("values")

            if "vocab_size" in node_inputs.get("required_inputs"):
                self.input_vocab_size = node_inputs.get("required_inputs").get("vocab_size").get("values")

        import torch
        from torch import nn

        class ValueEmbeddingModule(nn.Module):
            def __init__(self, vocab_size, model_dim):
                super().__init__()
                self.embed = nn.ModuleList([nn.Embedding(vocab_size, model_dim) for _ in range(6)])

            def forward(self, inputs) -> "list[torch.Tensor]":
                ve = [emb(inputs) for emb in self.embed]
                ve += reversed(ve)
                return ve

        return ValueEmbeddingModule(
            vocab_size=self.input_vocab_size,
            model_dim=self.input_model_dim
        )

class GPT2:
    CATEGORY = "torch"
    SUBCATEGORY = "neural_networks"
    DESCRIPTION = "GPT2"

    INPUT = {
        "required_inputs": {
            "block_list": {
                "kind": "*",
                "name": "block_list",
            },
            "value_embeds": {
                "kind": "*",
                "name": "value_embeds",
            },
            "language_model_head": {
                "kind": "*",
                "name": "language_model_head",
            },
            "num_heads": {
                "kind": "number",
                "name": "num_heads",
                "widget": {"kind": "number", "name": "num_heads", "default": ""},
            },
            "model_dim": {
                "kind": "number",
                "name": "model_dim",
                "widget": {"kind": "number", "name": "model_dim", "default": ""},
            },
            "block_size": {
                "kind": "number",
                "name": "block_size",
                "widget": {"kind": "number", "name": "block_size", "default": ""},
            },
            "vocab_size": {
                "kind": "number",
                "name": "vocab_size",
                "widget": {"kind": "number", "name": "vocab_size", "default": ""},
            },
            "vocab_max_size": {
                "kind": "number",
                "name": "vocab_max_size",
                "widget": {"kind": "number", "name": "vocab_max_size", "default": ""},
            },
            "num_layers": {
                "kind": "number",
                "name": "num_layers",
                "widget": {"kind": "number", "name": "num_layers", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "*",
        "name": "nn.Module",
        "cacheable": False,
    }

    def evaluate(self, node_inputs):
        if node_inputs.get("required_inputs"):
            if "vocab_size" in node_inputs.get("required_inputs"):
                self.input_vocab_size = node_inputs.get("required_inputs").get("vocab_size").get("values")

            if "num_layers" in node_inputs.get("required_inputs"):
                self.input_num_layers = node_inputs.get("required_inputs").get("num_layers").get("values")

            if "num_heads" in node_inputs.get("required_inputs"):
                self.input_num_heads = node_inputs.get("required_inputs").get("num_heads").get("values")

            if "model_dim" in node_inputs.get("required_inputs"):
                self.input_model_dim = node_inputs.get("required_inputs").get("model_dim").get("values")

            if "block_list" in node_inputs.get("required_inputs"):
                self.input_block_list = node_inputs.get("required_inputs").get("block_list").get("values")

            if "value_embeds" in node_inputs.get("required_inputs"):
                self.input_value_embeds = node_inputs.get("required_inputs").get("value_embeds").get("values")

            if "language_model_head" in node_inputs.get("required_inputs"):
                self.input_lm_head = node_inputs.get("required_inputs").get("language_model_head").get("values")

            if "block_size" in node_inputs.get("required_inputs"):
                self.input_block_size = node_inputs.get("required_inputs").get("block_size").get("values")

            if "vocab_max_size" in node_inputs.get("required_inputs"):
                self.input_vocab_max_size = node_inputs.get("required_inputs").get("vocab_max_size").get("values")

        import torch
        from torch import nn
        from torch.nn.attention.flex_attention import BlockMask
        from torch.nn.functional import rms_norm, cross_entropy

        def norm(x):
            return rms_norm(x, (x.size(-1),))

        class GPT2Module(nn.Module):
            def __init__(
                self,
                vocab_size,
                num_layers,
                num_heads,
                model_dim,
                block_list,
                value_embeds,
                lm_head,
                block_size,
                vocab_max_size
            ):
                super().__init__()

                self.vocab_size = vocab_size
                self.num_layers = num_layers
                self.num_heads = num_heads
                self.model_dim = model_dim


                self.num_encoder_layers = num_layers // 2
                self.num_decoder_layers = num_layers - self.num_encoder_layers

                # skip connection weights for decoder layers
                self.skip_weights = nn.Parameter(torch.ones(self.num_decoder_layers))

                self.embed = nn.Embedding(vocab_size, model_dim)

                # list of blocks
                self.blocks = nn.ModuleList(block_list) # TODO: in the UI, construct the blocks into a list

                self.value_embeds = value_embeds

                self.lm_head = lm_head

                self.lm_head.weight.data.zero_()

                self.block_size = block_size
                self.vocab_max_size = vocab_max_size

            def forward(
                self,
                inputs,
                targets,
                sliding_window_num_blocks
            ):
                BLOCK_SIZE = self.block_size
                seq_len = len(inputs)
                assert seq_len % BLOCK_SIZE == 0
                total_num_blocks = seq_len // BLOCK_SIZE

                assert inputs.ndim == 1
                docs = (inputs == self.vocab_max_size).cumsum(0)
                docs_low = docs.view(-1, BLOCK_SIZE)[:, 0].contiguous()
                docs_high = docs.view(-1, BLOCK_SIZE)[:, -1].contiguous()

                def document_causal(b, h, q_idx, kv_idx):
                    causal_mask = q_idx >= kv_idx
                    document_mask = docs[q_idx] == docs[kv_idx]
                    return causal_mask & document_mask

                def dense_to_ordered(dense_mask: torch.Tensor):
                    num_blocks = dense_mask.sum(dim=-1, dtype=torch.int32)
                    indices = dense_mask.argsort(dim=-1, descending=True, stable=True).to(torch.int32)
                    return num_blocks[None, None].contiguous(), indices[None, None].contiguous()

                def create_doc_swc_block_mask(sliding_window_num_blocks: torch.Tensor):
                    kv_idx = block_idx = torch.arange(total_num_blocks, dtype=torch.int32, device="cuda")
                    q_idx = block_idx[:, None]
                    causal_bm = q_idx >= kv_idx
                    causal_full_bm = q_idx > kv_idx
                    window_bm = q_idx - kv_idx < sliding_window_num_blocks
                    window_full_bm = window_bm
                    # document_bm = (docs_low[q_idx] <= docs_high[kv_idx]) & (docs_low[kv_idx] <= docs_high[q_idx])
                    document_bm = (docs_low[:, None] <= docs_high) & (docs_low <= docs_high[:, None])
                    document_full_bm = (docs_low[:, None] == docs_high) & (docs_low == docs_high[:, None])
                    nonzero_bm = causal_bm & window_bm & document_bm
                    full_bm  = causal_full_bm & window_full_bm & document_full_bm
                    kv_num_blocks, kv_indices = dense_to_ordered(nonzero_bm ^ full_bm)
                    full_kv_num_blocks, full_kv_indices = dense_to_ordered(full_bm)

                    return BlockMask.from_kv_blocks(
                        kv_num_blocks,
                        kv_indices,
                        full_kv_num_blocks,
                        full_kv_indices,
                        BLOCK_SIZE=BLOCK_SIZE,
                        mask_mod=document_causal,
                    )

                block_mask = create_doc_swc_block_mask(sliding_window_num_blocks)

                # forward the GPT model itself
                x = self.embed(inputs[None]) # token embeddings of shape (b, t, model_dim)
                x = norm(x) # @Grad62304977
                x0 = x
                ve = self.value_embeds(inputs)
                ve_enc, ve_dec = ve[:self.num_encoder_layers], ve[self.num_encoder_layers:]

                # Store outputs for U-Net skip connections
                skip_connections = []

                # Encoder pass - process only the first half of the blocks
                for i in range(self.num_encoder_layers):
                    x = self.blocks[i](x, ve_enc[i], x0, block_mask)
                    skip_connections.append(x)

                # Decoder pass - process the remaining blocks with weighted skip connections
                for i in range(self.num_decoder_layers):
                    x = x + self.skip_weights[i] * skip_connections.pop()
                    # U-net structure on token value embeddings by @leloykun
                    x = self.blocks[self.num_encoder_layers + i](x, ve_dec[i], x0, block_mask)

                x = norm(x)
                logits = self.lm_head(x)
                logits = 30 * torch.tanh(logits / 30) # @Grad62304977
                logits = logits.float()
                loss = cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))

                return loss

        return GPT2Module(
            vocab_size=self.input_vocab_size,
            num_layers=self.input_num_layers,
            num_heads=self.input_num_heads,
            model_dim=self.input_model_dim,
            block_list=self.input_block_list,
            value_embeds=self.input_value_embeds,
            lm_head=self.input_lm_head,
            block_size=self.input_block_size,
            vocab_max_size=self.input_vocab_max_size
        )

EXTENSION_MAPPINGS = {
    "name": "torch_train_nano_gpt_2",
    "version": version,
    "description": "Extension for torch training nano gpt2",
    "javascript_class_name": "torch_train_nano_gpt_2",
    "nodes": {
        "CastedLinear": {
            "python_class": CastedLinear,
            "javascript_class_name": "CastedLinear",
            "display_name": "CastedLinear",
        },
        "RotaryEmbedding": {
            "python_class": RotaryEmbedding,
            "javascript_class_name": "RotaryEmbedding",
            "display_name": "RotaryEmbedding",
        },
        "CausalSelfAttention": {
            "python_class": CausalSelfAttention,
            "javascript_class_name": "CausalSelfAttention",
            "display_name": "CausalSelfAttention",
        },
        "MultiLayerPerceptron": {
            "python_class": MultiLayerPerceptron,
            "javascript_class_name": "MultiLayerPerceptron",
            "display_name": "MultiLayerPerceptron",
        },
        "TransformerBlock": {
            "python_class": TransformerBlock,
            "javascript_class_name": "TransformerBlock",
            "display_name": "TransformerBlock",
        },
        "ValueEmbedding": {
            "python_class": ValueEmbedding,
            "javascript_class_name": "ValueEmbedding",
            "display_name": "ValueEmbedding",
        },
        "GPT2": {
            "python_class": GPT2,
            "javascript_class_name": "GPT2",
            "display_name": "GPT2",
        },
    },
    "rules": {},
}
