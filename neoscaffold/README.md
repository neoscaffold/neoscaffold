# NeoScaffold

## The fastest AI GUI.

Design and execute LLM flows with NeoScaffold's nodes based interface. Check out workflow examples to explore its capabilities.

**Fast** at Swapped Inc comes in multiple flavours.

1. **Execution**: Enjoy parallelised execution. Never before seen speeds on inference. Smart Memory Caching.
2. **Development time**: The GUI interface allows users to make alterations to their flows quicker than changing the underlying code. This enables developers to make progress on their flows rapidly.
3. **Collaboration**: Flows are able to be shared as JSON files. They are extremely light by design, enabling speedy transfer of knowledge.

## Features.

- Scaffold of a scaffold:- Users will be able to extend their flows via "wrapping" or "integrating" with other flows.
- NodeBuilder Node:- Users will be able to create their own nodes via this mechanism. Users will be able to drop your python code into a tiny node and run it in between your pipeline.
- Smart Memory Caching:- Caching occurs when a flow or a part of a flow is run more than once consecutively. The system caches the results of the repeated section and
- Smart Input validations:- Inputs are validated before usage. There are 3 types of inputs, optional, required and conditionally required.
- Single Output:- Output is restricted to a single entity that may or may not be complex, i.e. composed of more than a single property.
- In-built manager:- Download custom models, community nodes, and extensions.

## Installation.

1. Clone this repository.
   `git clone https://github.com/swapnice/neoscaffold`
2. Use node version 18.
   `nvm use 18`
3. Change directories into the neoscaffold folder and install all the dependencies.
   `cd neoscaffold && npm ci`
4. Start the ember server.
   `ember s`