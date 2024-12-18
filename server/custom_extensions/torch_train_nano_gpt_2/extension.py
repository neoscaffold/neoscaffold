import os

version = "0.0.1"

# import torch
# from torch import nn
# import torch.nn.functional as F
# import torch._inductor.config as config
# from torch.nn.attention.flex_attention import BlockMask, flex_attention

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
                    kv_idx = block_idx = torch.arange(512, dtype=torch.int32, device="cuda")
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

class TrainingSpeedRunGPT2:
    CATEGORY = "torch"
    SUBCATEGORY = "training"
    DESCRIPTION = "TrainingSpeedRunGPT2"

    INPUT = {
        "required_inputs": {
            "gpt2": {
                "kind": "*",
                "name": "gpt2",
                "widget": {"kind": "*", "name": "gpt2", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "*",
        "name": "summary",
        "cacheable": False,
    }

    def evaluate(self, node_inputs):
        if node_inputs.get("required_inputs"):
            if "gpt2" in node_inputs.get("required_inputs"):
                self.input_gpt2 = node_inputs.get("required_inputs").get("gpt2").get("values")


        import sys
        with open(sys.argv[0]) as f:
            code = f.read() # read the code of this file ASAP, for logging

        import uuid
        import time
        import contextlib
        from dataclasses import dataclass
        from pathlib import Path

        import torch
        import torch.distributed as dist
        import torch._inductor.config as config
        from torch.nn.parallel import DistributedDataParallel as DDP

        # -----------------------------------------------------------------------------
        # Muon optimizer

        @torch.compile
        def zeropower_via_newtonschulz5(G, steps=10, eps=1e-7):
            """
            Newton-Schulz iteration to compute the zeroth power / orthogonalization of G. We opt to use a
            quintic iteration whose coefficients are selected to maximize the slope at zero. For the purpose
            of minimizing steps, it turns out to be empirically effective to keep increasing the slope at
            zero even beyond the point where the iteration no longer converges all the way to one everywhere
            on the interval. This iteration therefore does not produce UV^T but rather something like US'V^T
            where S' is diagonal with S_{ii}' ~ Uniform(0.5, 1.5), which turns out not to hurt model
            performance at all relative to UV^T, where USV^T = G is the SVD.
            """
            assert len(G.shape) == 2
            a, b, c = (3.4445, -4.7750,  2.0315)
            X = G.bfloat16()
            X /= (X.norm() + eps) # ensure top singular value <= 1
            if G.size(0) > G.size(1):
                X = X.T
            for _ in range(steps):
                A = X @ X.T
                B = b * A + c * A @ A # adapted from suggestion by @jxbz, @leloykun, and @YouJiacheng
                X = a * X + B @ X
            if G.size(0) > G.size(1):
                X = X.T
            return X

        class Muon(torch.optim.Optimizer):
            """
            Muon - MomentUm Orthogonalized by Newton-schulz

            Muon internally runs standard SGD-momentum, and then performs an orthogonalization post-
            processing step, in which each 2D parameter's update is replaced with the nearest orthogonal
            matrix. To efficiently orthogonalize each update, we use a Newton-Schulz iteration, which has
            the advantage that it can be stably run in bfloat16 on the GPU.

            Some warnings:
            - This optimizer assumes that all parameters passed in are 2D.
            - It should not be used for the embedding layer, the final fully connected layer, or any {0,1}-D
            parameters; those should all be optimized by a standard method (e.g., AdamW).
            - To use it with 4D convolutional filters, it works well to just flatten their last 3 dimensions.
            - We believe it is unlikely to work well for training with small batch size.
            - We believe it may not work well for finetuning pretrained models, but we haven't tested this.
            - We have not yet tried this optimizer for training scenarios larger than NanoGPT (124M).

            Arguments:
                lr: The learning rate used by the internal SGD.
                momentum: The momentum used by the internal SGD.
                nesterov: Whether to use Nesterov-style momentum in the internal SGD. (recommended)
                ns_steps: The number of Newton-Schulz iteration steps to use.
            """
            def __init__(self, params, lr=0.02, momentum=0.95, nesterov=True, ns_steps=5):
                self.world_size = int(os.environ['WORLD_SIZE'])
                self.rank = int(os.environ['RANK'])
                defaults = dict(lr=lr, momentum=momentum, nesterov=nesterov, ns_steps=ns_steps)
                params = list(params)
                assert all(isinstance(p, torch.Tensor) for p in params)
                sizes = {p.numel() for p in params}
                param_groups = [
                    {
                        'params': [p for p in params if p.numel() == size],
                        'update_buffer': [
                            torch.empty(size, device='cuda', dtype=torch.bfloat16)
                            for _ in range(self.world_size)
                        ],
                    }
                    for size in sizes
                ]
                super().__init__(param_groups, defaults)

            def step(self):

                for group in self.param_groups:

                    lr = group['lr']
                    momentum = group['momentum']
                    nesterov = group['nesterov']
                    ns_steps = group['ns_steps']
                    update_buffers = group['update_buffer']
                    # generate weight updates in distributed fashion
                    params = group['params']
                    assert len(params) % self.world_size == 0
                    handle = None
                    params_world = None
                    def update_prev():
                        if params_world is None:
                            return
                        assert handle is not None
                        handle.wait()
                        for p_world, g_world in zip(params_world, update_buffers):
                            p_world.data.add_(
                                g_world.view_as(p_world),
                                alpha=-lr * max(1, p_world.size(0) / p_world.size(1)) ** 0.5,
                            )
                    for base_i in range(len(params))[::self.world_size]:
                        p = params[base_i + self.rank]
                        g = p.grad
                        assert g is not None
                        state = self.state[p]
                        if 'momentum_buffer' not in state:
                            state['momentum_buffer'] = torch.zeros_like(g)
                        buf = state['momentum_buffer']
                        buf.lerp_(g, 1 - momentum)
                        g = g.lerp_(buf, momentum) if nesterov else buf
                        g = zeropower_via_newtonschulz5(g, steps=ns_steps).flatten()
                        update_prev()
                        handle = dist.all_gather(update_buffers, g, async_op=True)
                        params_world = params[base_i : base_i + self.world_size]
                    update_prev()

        # -----------------------------------------------------------------------------
        # Our own simple Distributed Data Loader

        def _peek_data_shard(file: Path):
            # only reads the header, returns header data
            # header is 256 int32
            header = torch.from_file(f"{file}", False, 256, dtype=torch.int32)
            assert header[0] == 20240520, "magic number mismatch in the data .bin file"
            assert header[1] == 1, "unsupported version"
            return int(header[2]) # number of tokens (claimed)

        def _load_data_shard(path: Path, num_tokens):
            with path.open("rb", buffering=0) as f:
                tokens = torch.empty(num_tokens, dtype=torch.uint16, pin_memory=True)
                f.seek(256 * 4)
                nbytes = f.readinto(tokens.numpy())
                assert nbytes == 2 * num_tokens, "number of tokens read does not match header?"
            return tokens

        class DistributedDataLoader:
            def __init__(self, filename_pattern, seq_len, process_rank, num_processes):
                self.process_rank = process_rank
                self.num_processes = num_processes
                self.seq_len = seq_len

                # glob files that match the pattern
                self.files = sorted(Path.cwd().glob(filename_pattern))
                assert len(self.files) > 0, f"did not find any files that match the pattern {filename_pattern}"

                # load and validate all data shards, count number of tokens in total
                self.files_num_tokens = [_peek_data_shard(file) for file in self.files]
                assert min(self.files_num_tokens) >= num_processes * seq_len + 1
                self.total_num_tokens = sum(self.files_num_tokens)

                self.reset()

            def reset(self):
                self.current_shard = -1
                self.advance()

            def advance(self): # advance to next data shard
                self.current_shard = (self.current_shard + 1) % len(self.files)
                self.current_position = self.process_rank * self.seq_len
                self.tokens = _load_data_shard(self.files[self.current_shard], self.files_num_tokens[self.current_shard])

            def next_batch(self):
                batch_size = self.seq_len * self.num_processes
                buf = self.tokens[self.current_position:self.current_position+self.seq_len+1]
                # host side async is sufficient;
                # no performance improvement was observed when introducing a separate stream.
                inputs = buf[:-1].to(device="cuda", dtype=torch.int32, non_blocking=True) # inputs
                targets = buf[1:].to(device="cuda", dtype=torch.int64, non_blocking=True) # targets
                # advance current position and load next shard if necessary
                self.current_position += batch_size
                if self.current_position + batch_size + 1 >= len(self.tokens):
                    self.advance()
                return inputs, targets

        # -----------------------------------------------------------------------------
        # int main

        @dataclass
        class Hyperparameters:
            # data hyperparams
            input_bin : str = 'data/fineweb10B/fineweb_train_*.bin' # input .bin to train on
            input_val_bin : str = 'data/fineweb10B/fineweb_val_*.bin' # input .bin to eval validation loss on
            # optimization hyperparams
            batch_size : int = 8 # batch size, in sequences, across all devices
            sequence_length : int = 64*1024 # sequence length, in tokens
            num_iterations : int = 1480 # number of iterations to run
            warmup_iters : int = 0
            cooldown_iters : int = 600 # number of iterations of linear warmup/cooldown for triangular or trapezoidal schedule
            weight_decay : float = 0
            # evaluation and logging hyperparams
            val_loss_every : int = 125 # every how many steps to evaluate val loss? 0 for only at the end
            val_tokens : int = 10485760 # how many tokens of validation data? it's important to keep this fixed for consistent comparisons
            save_every : int = 0 # every how many steps to save the checkpoint? 0 for only at the end
        args = Hyperparameters()

        assert torch.cuda.is_available()

        # Initialize DDP settings without relying on torchrun
        def init_distributed():
            if torch.cuda.is_available():
                # Get total number of GPUs available
                num_gpus = torch.cuda.device_count()

                # Set default values for single-GPU case
                rank = 0
                local_rank = 0
                world_size = 1

                if num_gpus > 1:
                    # Multi-GPU setup
                    os.environ['MASTER_ADDR'] = 'localhost'
                    os.environ['MASTER_PORT'] = '12355'

                    # Initialize process group
                    torch.distributed.init_process_group(
                        backend='nccl',
                        init_method='env://',
                        world_size=num_gpus,
                        rank=rank
                    )
                    local_rank = rank % num_gpus
                    world_size = num_gpus

                return rank, local_rank, world_size, torch.device(f'cuda:{local_rank}')
            else:
                return 0, 0, 1, torch.device('cpu')

        # Initialize distributed setup
        ddp_rank, ddp_local_rank, ddp_world_size, device = init_distributed()

        # Set device
        torch.cuda.set_device(device)
        print(f"using device: {device}")

        # Only create barrier if using multiple GPUs
        if ddp_world_size > 1:
            dist.barrier()

        master_process = (ddp_rank == 0)

        # begin logging
        logfile = None
        if master_process:
            run_id = uuid.uuid4()
            # Create base logs directory
            logdir = Path("logs")
            logdir.mkdir(exist_ok=True)

            # Create run-specific directory and log file
            run_dir = logdir / str(run_id)
            run_dir.mkdir(exist_ok=True)

            # Create log file in the run directory
            logfile = run_dir / "training.log"
            print(f"Logging to: {logfile}")

        def print0(s, logonly=False):
            if master_process and logfile is not None:
                with logfile.open("a") as f:
                    if not logonly:
                        print(s)
                    print(s, file=f)
        # log information about the hardware/software environment this is running on
        # and print the full `nvidia-smi` to file
        print0(f"Running python {sys.version}")
        print0(f"Running pytorch {torch.version.__version__} compiled for CUDA {torch.version.cuda}\nnvidia-smi:")
        import subprocess
        result = subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print0(f'{result.stdout}', logonly=True)
        print0('='*100, logonly=True)

        # calculate the number of steps to take in the val loop.
        assert args.val_tokens % (args.sequence_length * ddp_world_size) == 0
        val_steps = args.val_tokens // (args.sequence_length * ddp_world_size)
        # calculate the steps of gradient accumulation required to attain the desired global batch size.
        assert args.batch_size % (ddp_world_size) == 0
        train_accumulation_steps = args.batch_size // ddp_world_size

        # load tokens
        train_loader = DistributedDataLoader(args.input_bin, args.sequence_length, ddp_rank, ddp_world_size)
        val_loader = DistributedDataLoader(args.input_val_bin, args.sequence_length, ddp_rank, ddp_world_size)
        print0(f"Training DataLoader: total number of tokens: {train_loader.total_num_tokens} across {len(train_loader.files)} files")
        print0(f"Validation DataLoader: total number of tokens: {val_loader.total_num_tokens} across {len(val_loader.files)} files")
        print0('='*100, logonly=True)
        inputs_train, targets_train = train_loader.next_batch()

        # there are only 50257 unique GPT-2 tokens; we extend to nearest multiple of 128 for efficiency. suggested to me by @Grad62304977.
        # this originates from Karpathy's experiments.

        # num_vocab = 50304 # (vocab_size=num_vocab, num_layers=12, num_heads=6, model_dim=768)

        model = self.input_gpt2
        model = model.cuda().bfloat16()
        for m in model.modules():
            if isinstance(m, CastedLinear):
                m.float()
        config.coordinate_descent_tuning = True # suggested by @Chillee
        model = torch.compile(model)
        # here we wrap model into DDP container
        model = DDP(model, device_ids=[ddp_local_rank], broadcast_buffers=False, gradient_as_bucket_view=True)
        raw_model = model.module # always contains the "raw" unwrapped model

        # init the optimizer(s)
        embed_params = [*raw_model.embed.parameters(), *raw_model.value_embeds.parameters()]
        optimizer1 = torch.optim.Adam(embed_params, lr=0.6, betas=(0.8, 0.95), fused=True)
        optimizer2 = torch.optim.Adam([raw_model.lm_head.weight], lr=0.008, betas=(0.8, 0.95), fused=True)
        params = list(raw_model.blocks.parameters())
        matrix_params = [p for p in params if p.ndim == 2]
        scalar_params = [p for p in params if p.ndim < 2] + [raw_model.skip_weights]
        optimizer3 = Muon(matrix_params, lr=0.05, momentum=0.95)
        optimizer4 = torch.optim.Adam(scalar_params, lr=0.04, betas=(0.8, 0.95), fused=True)
        optimizers = [optimizer1, optimizer2, optimizer3, optimizer4]
        # learning rate decay scheduler (linear warmup and cooldown)
        def get_lr(it):
            assert it <= args.num_iterations
            # 1) linear warmup for warmup_iters steps
            if it < args.warmup_iters:
                return (it+1) / args.warmup_iters
            # 2) constant lr for a while
            elif it < args.num_iterations - args.cooldown_iters:
                return 1.0
            # 3) linear cooldown
            else:
                decay_ratio = (args.num_iterations - it) / args.cooldown_iters
                return decay_ratio
        schedulers = [torch.optim.lr_scheduler.LambdaLR(opt, get_lr) for opt in optimizers]

        sliding_window_num_blocks = torch.tensor(1, dtype=torch.int32, device="cuda")
        sw_num_blocks_prev = 1
        # Start training loop
        training_time_ms = 0
        # start the clock
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        # begin training
        for step in range(args.num_iterations + 1):
            last_step = (step == args.num_iterations)
            # This effectively ignores timing first 10 steps, which are slower for weird reasons.
            # Alternately, and slightly more correctly in terms of benchmarking, we could do 10
            # steps with dummy data first, and then re-initialize the model and reset the loader.
            if step == 10:
                training_time_ms = 0
                t0 = time.perf_counter()
            timed_steps = float('nan') if step <= 11 else (step - 10) + 1 # <= 11 to avoid bug in val

            # Linearly increase the sliding window size over training in chunks of 64 from 64 -> 1792. By @fernbear.bsky.social
            frac_done = step / args.num_iterations # training progress
            sw_num_blocks = int(((1 - frac_done) * 64 + frac_done * 1792 + 64) // 128)
            if sw_num_blocks != sw_num_blocks_prev:
                sliding_window_num_blocks.copy_(sw_num_blocks, non_blocking=True)
                sw_num_blocks_prev = sw_num_blocks

            # once in a while evaluate the validation dataset
            if (last_step or (args.val_loss_every > 0 and step % args.val_loss_every == 0)):
                # stop the clock
                torch.cuda.synchronize()
                training_time_ms += 1000 * (time.perf_counter() - t0)
                # run validation batches
                model.eval()
                val_loader.reset()
                val_loss = 0.0
                for _ in range(val_steps):
                    with torch.no_grad():
                        inputs_val, targets_val = val_loader.next_batch()
                        val_loss += model(inputs_val, targets_val, sliding_window_num_blocks)
                dist.all_reduce(val_loss, op=dist.ReduceOp.AVG)
                val_loss /= val_steps
                # log val loss to console and to logfile
                print0(f'step:{step}/{args.num_iterations} val_loss:{val_loss:.4f} train_time:{training_time_ms:.0f}ms step_avg:{training_time_ms/(timed_steps-1):.2f}ms')
                # start the clock again
                torch.cuda.synchronize()
                t0 = time.perf_counter()

            if master_process and (last_step or (args.save_every > 0 and step % args.save_every == 0)):
                # stop the clock
                torch.cuda.synchronize()
                training_time_ms += 1000 * (time.perf_counter() - t0)
                # save the state of the training process
                log = dict(step=step, code=code, model=raw_model.state_dict(), optimizers=[opt.state_dict() for opt in optimizers])
                torch.save(log, 'logs/%s/state_step%06d.pt' % (run_id, step))
                # start the clock again
                torch.cuda.synchronize()
                t0 = time.perf_counter()

            # bit confusing: we want to make sure to eval on 0th iteration
            # but also after the very last iteration. so we loop for step <= num_iterations
            # instead of just < num_iterations (one extra due to <=), only to do
            # the validation/sampling one last time, and then we break right here as we're done.
            if last_step:
                break

            # --------------- TRAINING SECTION BEGIN -----------------
            model.train()
            for i in range(1, train_accumulation_steps + 1):
                with contextlib.ExitStack() as stack:
                    if i < train_accumulation_steps: # there's no need to sync gradients every accumulation step
                        stack.enter_context(model.no_sync())
                    if step >= 5:
                        stack.enter_context(torch.compiler.set_stance(skip_guard_eval_unsafe=True))
                    model(inputs_train, targets_train, sliding_window_num_blocks).backward()
                    inputs_train, targets_train = train_loader.next_batch()
            if train_accumulation_steps != 1:
                for p in model.parameters():
                    p.grad /= train_accumulation_steps
            # momentum warmup for Muon
            frac = min(step/300, 1)
            for group in optimizer3.param_groups:
                group['momentum'] = (1 - frac) * 0.85 + frac * 0.95
            # step the optimizers and schedulers
            for opt, sched in zip(optimizers, schedulers):
                opt.step()
                sched.step()
            # null the gradients
            model.zero_grad(set_to_none=True)
            # --------------- TRAINING SECTION END -------------------
            # everything that follows now is just diagnostics, prints, logging, etc.
            approx_time = training_time_ms + 1000 * (time.perf_counter() - t0)
            print0(f"step:{step+1}/{args.num_iterations} train_time:{approx_time:.0f}ms step_avg:{approx_time/timed_steps:.2f}ms")

        print0(f"peak memory consumption: {torch.cuda.max_memory_allocated() // 1024 // 1024} MiB")

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
        "TrainingSpeedRunGPT2": {
            "python_class": TrainingSpeedRunGPT2,
            "javascript_class_name": "TrainingSpeedRunGPT2",
            "display_name": "TrainingSpeedRunGPT2",
        }
    },
    "rules": {},
}
