extensions

points of intervention:
  - ui graph setup
  - ui node definitions
  - ui node status updates
  - ui node queue prompt
  - py server initialization
  - py server prompt queue validation
  - py server queue execution
  - py server queue status updates

  - EXAMINE HOW COMFYUI MANAGER DOES THIS:
    - "ComfyUI creates a local database of all the nodes and their connections using the github api then caches the data in a local database, there is no low-latency search option"
    - "Pull requests in main repo to add new nodes and it gets updated via CI/CD and approvals"
    - https://github.com/ltdrdata/ComfyUI-Manager?tab=readme-ov-file#how-to-register-your-custom-node-into-comfyui-manager
    - Comfy-Org (Not Authors of Comfy but friends) is Slowly making a "registry" https://github.com/Comfy-Org/registry-backend
    - registry insertion
    - registry removal
    - registry query
    - registry update

    - registry uses a system like npm where there is a centralized global registry of the original artifacts HOWEVER the changes are pushed to the open source search solution like elasticsearch


NOTES:

Unlike ComfyUI, every input widget has both a way to manually "insert the value" and link it in

Each input should have a small "ⓘ" in top right corner, if you click the input anywhere it opens a lightbox with a menu explaining the documentation of the input

