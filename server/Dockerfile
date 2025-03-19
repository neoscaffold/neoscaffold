FROM python:3.10-slim-bookworm

# Reference:
# https://github.com/flyteorg/flytekit/blob/master/Dockerfile

WORKDIR /root
ENV VENV /opt/venv
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONPATH /root

# Virtual environment
RUN python3 -m venv ${VENV}
ENV PATH="${VENV}/bin:$PATH"

# Run a series of commands to set up the environment:
# 1. Update and install dependencies.
# 2. Install
# 3. Clean up the apt cache to reduce image size. Reference: https://gist.github.com/marvell/7c812736565928e602c4
RUN apt-get update && apt-get install build-essential -y \
    && apt-get clean autoclean \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/

# Copy the actual code
COPY . /root

# get uv setup
RUN pip install uv

RUN uv venv .venv
RUN . .venv/bin/activate

# Install Python dependencies
RUN ls && uv sync
RUN uv pip install -r /root/custom_extensions/agents/requirements.txt
RUN uv pip install -r /root/custom_extensions/core/requirements.txt
RUN uv pip install -r /root/custom_extensions/llm/requirements.txt
RUN uv pip install -r /root/custom_extensions/network_requests/requirements.txt
RUN uv pip install -r /root/custom_extensions/torch_train_nano_gpt_2/requirements.txt

# This tag is supplied by the build script and will be used to determine the version
# when registering tasks, workflows, and launch plans
ARG tag

ARG OPENAI_API_KEY
ARG ANTHROPIC_API_KEY
ARG PPL_API_KEY
ARG CO_API_KEY
ARG CEREBRAS_API_KEY
ARG GROQ_API_KEY
ARG GOOGLE_SIGN_IN_CLIENT_ID

# GET ENV SECRETS

ENV OPENAI_API_KEY $OPENAI_API_KEY
ENV ANTHROPIC_API_KEY $ANTHROPIC_API_KEY
ENV PPL_API_KEY $PPL_API_KEY
ENV CO_API_KEY $CO_API_KEY
ENV CEREBRAS_API_KEY $CEREBRAS_API_KEY
ENV GROQ_API_KEY $GROQ_API_KEY
ENV GOOGLE_SIGN_IN_CLIENT_ID $GOOGLE_SIGN_IN_CLIENT_ID

ARG PORT=6166
EXPOSE ${PORT}

# activate the venv AND run the server
CMD . .venv/bin/activate && python /root/main.py --listen 0.0.0.0 --enable-cors-header "*"