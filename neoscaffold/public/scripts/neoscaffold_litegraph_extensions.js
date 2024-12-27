(function (global) {
  if (global.LiteGraph === undefined) {
    console.error('LiteGraph not found');
    return;
  }
  if (global.LGraph === undefined) {
    console.error('LGraph not found');
    return;
  }
  if (global.LGraphNode === undefined) {
    console.error('LGraphNode not found');
    return;
  }
  if (global.StopWatchBookie !== undefined || !global.trackPerformance) {
    // create a stub for StopWatchBookie
    global.StopWatchBookie = {
      time: () => {},
      logTime: () => {},
      lap: () => {},
      finishLap: () => {},
      logLaps: () => {},
    };
    // TODO: add lap time logging to performance critical code
  }

  let NeoScaffoldAPI = (global.NeoScaffoldAPI = {
    baseURL: 'http://localhost:6166',
    sessionKey: 'userInfo', // default session key

    getAuthorizationHeaders() {
      if (!this.sessionKey) {
        return {};
      }
      const session = localStorage.getItem(this.sessionKey) || '{}';
      const sessionObject = JSON.parse(session);
      if (!sessionObject) {
        return {};
      }
      if (!sessionObject.token || !sessionObject.authenticator) {
        return {};
      }
      let authenticator = '';
      if (sessionObject.authenticator.includes('google')) {
        authenticator = 'google';
      }
      return {
        'Authorization': 'Bearer ' + sessionObject.token,
        'Authenticator': authenticator
      }
    },

    async queuePrompt(prompt) {
      // check if prompt is valid json
      try {
        JSON.parse(prompt);
      } catch (error) {
        console.error(error);
        return;
      }
      const authorizationHeaders = this.getAuthorizationHeaders();
      authorizationHeaders['Content-Type'] = 'application/json';

      let results;
      try {
        results = await fetch(`${this.baseURL}/prompt`, {
          method: 'POST',
          headers: authorizationHeaders,
          body: prompt,
        });
        return results.json();
      } catch (error) {
        if (
          error.message &&
          (error.message.toLowerCase().includes('401') ||
            error.message.toLowerCase().includes('token expired') ||
            error.message.toLowerCase().includes('unauthorized'))
        ) {
          global.NeoScaffold.applicationSession.invalidate();
          global.NeoScaffold.applicationRouter.transitionTo('sign-in');
        }
        throw error;
      }
    },

    async getExtensions() {
      const authorizationHeaders = this.getAuthorizationHeaders();
      authorizationHeaders['Content-Type'] = 'application/json';

      let results;
      try {
        results = await fetch(`${this.baseURL}/extensions`, {
          method: 'GET',
          headers: authorizationHeaders,
        });
        return results.json();
      } catch (error) {
        if (
          error.message &&
          (error.message.toLowerCase().includes('401') ||
            error.message.toLowerCase().includes('token expired') ||
            error.message.toLowerCase().includes('unauthorized'))
        ) {
          global.NeoScaffold.applicationSession.invalidate();
          global.NeoScaffold.applicationRouter.transitionTo('sign-in');
        }
        throw error;
      }
    },

    async postToggleBreakpoints(workflow_id, node_ids, allBreak) {
      const authorizationHeaders = this.getAuthorizationHeaders();
      authorizationHeaders['Content-Type'] = 'application/json';

      const body = JSON.stringify({
        workflow_id,
        node_ids,
        all_break: allBreak
      });

      let results;
      try {
        results = await fetch(`${this.baseURL}/interventions/breakpoints`, {
          method: 'POST',
          headers: authorizationHeaders,
          body
        });
        return results.json();
      } catch (error) {
        if (
          error.message &&
          (error.message.toLowerCase().includes('401') ||
            error.message.toLowerCase().includes('token expired') ||
            error.message.toLowerCase().includes('unauthorized'))
        ) {
          global.NeoScaffold.applicationSession.invalidate();
          global.NeoScaffold.applicationRouter.transitionTo('sign-in');
        }
        throw error;
      }
    },

    async postStepThroughBreakpoints(workflow_id, node_ids) {
      const authorizationHeaders = this.getAuthorizationHeaders();
      authorizationHeaders['Content-Type'] = 'application/json';

      const body = JSON.stringify({
        workflow_id,
        node_ids
      });

      let results;
      try {
        results = await fetch(`${this.baseURL}/interventions/breakpoints/step-through`, {
          method: 'POST',
          headers: authorizationHeaders,
          body
        });
        return results.json();
      } catch (error) {
        if (
          error.message &&
          (error.message.toLowerCase().includes('401') ||
            error.message.toLowerCase().includes('token expired') ||
            error.message.toLowerCase().includes('unauthorized'))
        ) {
          global.NeoScaffold.applicationSession.invalidate();
          global.NeoScaffold.applicationRouter.transitionTo('sign-in');
        }
        throw error;
      }
    },

    async postToggleStop(workflow_id, node_ids, allStop) {
      const authorizationHeaders = this.getAuthorizationHeaders();
      authorizationHeaders['Content-Type'] = 'application/json';

      const body = JSON.stringify({
        workflow_id,
        node_ids,
        all_stop: allStop
      });

      let results;
      try {
        results = await fetch(`${this.baseURL}/interventions/stop-points`, {
          method: 'POST',
          headers: authorizationHeaders,
          body
        });
        return results.json();
      } catch (error) {
        if (
          error.message &&
          (error.message.toLowerCase().includes('401') ||
            error.message.toLowerCase().includes('token expired') ||
            error.message.toLowerCase().includes('unauthorized'))
        ) {
          global.NeoScaffold.applicationSession.invalidate();
          global.NeoScaffold.applicationRouter.transitionTo('sign-in');
        }
        throw error;
      }
    },

    async postToggleRestart(workflow_id, node_ids, allRestart) {
      const authorizationHeaders = this.getAuthorizationHeaders();
      authorizationHeaders['Content-Type'] = 'application/json';

      const body = JSON.stringify({
        workflow_id,
        node_ids,
        all_restart: allRestart
      });

      let results;
      try {
        results = await fetch(`${this.baseURL}/interventions/restart-points`, {
          method: 'POST',
          headers: authorizationHeaders,
          body
        });
        return results.json();
      } catch (error) {
        if (
          error.message &&
          (error.message.toLowerCase().includes('401') ||
            error.message.toLowerCase().includes('token expired') ||
            error.message.toLowerCase().includes('unauthorized'))
        ) {
          global.NeoScaffold.applicationSession.invalidate();
          global.NeoScaffold.applicationRouter.transitionTo('sign-in');
        }
        throw error;
      }
    },

    initializeWebSocket() {
      const scope = this;

      let wsBaseUrl = scope.baseURL;
      if (wsBaseUrl.includes('://')) {
        wsBaseUrl = wsBaseUrl.split('://')[1];
      }

      // URL of the WebSocket server
      let wsUrl;
      if (window.location.protocol === 'https:') {
        wsUrl = `wss://${wsBaseUrl}/ws`;
      } else {
        wsUrl = `ws://${wsBaseUrl}/ws`;
      }

      // Create a new WebSocket connection
      let protocol = ['json'];
      let authenticator = '';
      let token = '';
      if (scope.sessionKey) {
        const session = localStorage.getItem(scope.sessionKey);
        const sessionObject = JSON.parse(session);
        if (!sessionObject.token || !sessionObject.authenticator) {
          return;
        }

        if (sessionObject.authenticator.includes('google')) {
          authenticator = 'google';
        }

        if (sessionObject.token) {
          token = sessionObject.token;
        }

        protocol.push(token);
        protocol.push(authenticator);
      }

      const ws = new WebSocket(wsUrl, protocol);

      scope.ws = ws;

      // Connection opened
      ws.addEventListener('open', function (event) {
          console.log('Connected to WebSocket server');
      });

      // Listen for messages
      ws.addEventListener('message', function (event) {
        // console.log('Message from server:', event.data);
        let response = JSON.parse(event.data);

        if (response && response.data) {
          let data = response.data;

          if (data.breakpoint) {
            let node = NeoScaffold.graph.getNodeById(data.breakpoint);
            if (node) {
              node.storeAndSwitchColors("#2a363b", "#2a363b");

              scope.instance.litegraphCanvas.centerOnNode(node);

              let selectedNodes = scope.instance.litegraphCanvas.selected_nodes;
              selectedNodes[node.id] = node;

              NeoScaffold['isPaused'] = true;

              NeoScaffold.graph.setDirtyCanvas(true);
              return;
            }
          }
          NeoScaffold['isPaused'] = false;

          if (data.node_errors && data.node_errors.length) {
            let node = NeoScaffold.graph.getNodeById(data.evaluation_action.node_id);
            if (node) {
              node.properties.node_errors = data.node_errors;
              node.storeAndSwitchColors("#FF0000", "#FF0000");

              scope.instance.litegraphCanvas.centerOnNode(node);

              let selectedNodes = scope.instance.litegraphCanvas.selected_nodes;
              selectedNodes[node.id] = node;

              NeoScaffold.graph.setDirtyCanvas(true);
              return;
            }
          }

          if (data.evaluation_action) {
            let node = NeoScaffold.graph.getNodeById(data.evaluation_action.node_id);
            if (node) {
              node.properties.evaluation_action = data.evaluation_action;
              if (!node.properties.result) {
                node.properties.result = {};
              }
              node.properties.result.timestamp = new Date().toLocaleString('en-US', {
                hour12: true,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                fractionalSecondDigits: 3,
                month: '2-digit',
                day: '2-digit',
                year: '2-digit',
                // timeZone: 'UTC'
              });

              node.storeAndSwitchColors(
                LiteGraph.NODE_BOX_OUTLINE_COLOR,
                LiteGraph.NODE_BOX_OUTLINE_COLOR
              );
            }
          }
          if (data.results && Object.keys(data.results).length) {
            Object.keys(data.results).forEach((resultKey) => {
              let result = data.results[resultKey];
              if (result) {
                // update the node with the data
                let node = NeoScaffold.graph.getNodeById(result.node_id);
                if (node) {
                  let resultObject = {
                    "prompt_id": data.prompt_id,
                    result
                  };

                  if (node.properties.result && node.properties.result.timestamp) {
                    resultObject.timestamp = node.properties.result.timestamp;
                  }

                  node.properties.result = resultObject;

                  // delete previous node errors
                  if (node.properties.node_errors) {
                    delete node.properties.node_errors;
                  }

                  node.restoreColors();
                }
              }
            });
          }
        }

        NeoScaffold.graph.setDirtyCanvas(true);
      });

      // Handle any errors that occur
      ws.addEventListener('error', function (error) {
          console.error('WebSocket error:', error);
      });

      // Connection closed
      ws.addEventListener('close', function (event) {
          console.log('Disconnected from WebSocket server');
      });

      return ws;
    }
  });

  // *************************************************************
  //   NeoScaffold CLASS                                   *******
  // *************************************************************

  /**
   * The Global Scope. It contains all the registered node classes.
   *
   * @class NeoScaffold
   * @constructor
   */

  let NeoScaffold = (global.NeoScaffold = {
    VERSION: 0.1,

    queueItems: [],

    processingQueue: false,

    extensions: {},
    nodes: {},
    rules: {},

    api: NeoScaffoldAPI,

    // Modeled after base64 web-safe chars, but ordered by ASCII.
    PUSH_CHARS: '-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz',

    // Timestamp of last push, used to prevent local collisions if you push twice in one ms.
    lastPushTime: 0,

    // We generate 72-bits of randomness which get turned into 12 characters and appended to the
    // timestamp to prevent collisions with other clients.  We store the last characters we
    // generated because in the event of a collision, we'll use those same characters except
    // "incremented" by one.
    lastRandChars: [],

    /**
     * Creates a unique id in the same way that firebase does it
     *
     *
     * Fancy ID generator that creates 20-character string identifiers with the following properties:
     *
     * 1. They're based on timestamp so that they sort *after* any existing ids.
     * 2. They contain 72-bits of random data after the timestamp so that IDs won't collide with other clients' IDs.
     * 3. They sort *lexicographically* (so the timestamp is converted to characters that will sort properly).
     * 4. They're monotonically increasing.  Even if you generate more than one in the same timestamp, the
     *    latter ones will sort after the former ones.  We do this by using the previous random bits
     *    but "incrementing" them by 1 (only in the case of a timestamp collision).
    */
    createPushId() {
      let now = new Date().getTime();
      let duplicateTime = (now === this.lastPushTime);
      this.lastPushTime = now;

      let timeStampChars = new Array(8);
      for (let i = 7; i >= 0; i--) {
        timeStampChars[i] = this.PUSH_CHARS.charAt(now % 64);
        // NOTE: Can't use << here because javascript will convert to int and lose the upper bits.
        now = Math.floor(now / 64);
      }
      if (now !== 0) throw new Error('We should have converted the entire timestamp.');

      let id = timeStampChars.join('');

      if (!duplicateTime) {
        for (let i = 0; i < 12; i++) {
          this.lastRandChars[i] = Math.floor(Math.random() * 64);
        }
      } else {
        // If the timestamp hasn't changed since last push, use the same random number, except incremented by 1.
        let i;
        for (i = 11; i >= 0 && this.lastRandChars[i] === 63; i--) {
          this.lastRandChars[i] = 0;
        }
        this.lastRandChars[i]++;
      }
      for (let i = 0; i < 12; i++) {
        id += this.PUSH_CHARS.charAt(this.lastRandChars[i]);
      }
      if (id.length != 20) throw new Error('Length should be 20.');

      return id;
    },

    async createGraph(canvasSelector, baseURL, sessionKey) {
      let scope = this;

      scope.api.baseURL = baseURL || scope.api.baseURL;
      scope.api.sessionKey = sessionKey;
      scope.api.instance = scope;
      let canvasIdSelector = canvasSelector || '#litegraph';

      let graph = new LGraph(); // eslint-disable-line no-undef
      let canvas = new LGraphCanvas(canvasIdSelector, graph); // eslint-disable-line no-undef

      scope.addExtraMenuOptions(canvas);
      scope.addSideMenuOptions(canvas);
      scope.addRuntimeButtons(canvas);
      scope.addKeyboardShortcuts(canvas);

      scope.litegraphCanvas = canvas;
      canvas.canvas.width = window.innerWidth;
      canvas.canvas.height = window.innerHeight - 50;

      // Bind the resize event to update the canvas width
      scope._resizeHandler = scope.updateCanvasSize.bind(scope, canvas);
      window.addEventListener('resize', scope._resizeHandler);

      scope.graph = graph;
      scope.graph.start();

      // Load extensions (pre and post hooks)
      if (global && !global['NeoScaffoldExtras']) {
        global['NeoScaffoldExtras'] = {
          ext: {},
          nodes: {}
        };
      }
      let extensionsResponse = await scope.api.getExtensions();
      // load js extensions
      let extensionsLoaded = scope.loadExtensions(extensionsResponse);
      console.log(extensionsLoaded);

      // Load previous workflow
      let restored = false;
      try {
        const workflowString = localStorage.getItem("workflow");
        if (!workflowString) {
          throw new Error("initializing workflow");
        }
        const workflow = JSON.parse(workflowString);

        scope.import(workflow);

        restored = true;
      } catch (err) {
        alert('Loading default workflow due to: ' + err.message);
        console.error("Error loading previous workflow", err);
      }

      // We failed to restore a workflow so load the default
      if (!restored) {
        scope.defaultGraph();
      }

      // Save current workflow automatically
      setInterval(async () => {
        const graph = await scope.export();
        const workflow = JSON.stringify(graph);
        localStorage.setItem("workflow", workflow);
      }, 1000);

      // Initialize WebSocket
      scope.api.initializeWebSocket();

      // periodically check if the server web socket is still open
      setInterval(() => {
        if (scope.api && scope.api.ws && scope.api.ws.readyState !== WebSocket.OPEN) {
          console.log("Server WebSocket is not open, reconnecting...");
          try {
            scope.api.initializeWebSocket();
          } catch (error) {
            console.log("Reconnecting to WebSocket");
          }
        }
      }, 1000);

    },

    loadExtensions(extensionsData) {
      let scope = this;
      Object.keys(extensionsData).forEach(function(key) {
        let extension = extensionsData[key];
        console.log(`Loading extension: ${extension['name']} version: ${extension['version']}`);

        console.log(extension);
        // try to load the javascript eval
        try {
          eval(extension['javascript']);
        } catch (error) {
          console.error(`Error loading extension: ${extension['name']} version: ${error}`, error);
        }

        let extensionInstance;
        if (scope.getIfGloballyDefined(extension['javascript_class_name'], 'ext')) {
          // extension instance constructor is passed the scope
          let classValue = scope.getIfGloballyDefined(extension['javascript_class_name'], 'ext');
          extensionInstance = new classValue(scope);
        } else {
          console.log(`No custom js extension for: ${extension['name']} version: ${extension['version']}`);
        }

        // create an extension object
        let trackedExtension = {
          name: extension['name'],
          version: extension['version'],
          description: extension['description'],
          instance: extensionInstance,

          nodes: {},
          rules: {},
        };

        // register the nodes
        if (typeof extension['nodes'] === 'object') {
          Object.keys(extension['nodes']).forEach((nodeKey) => {
            let nodeObject = extension['nodes'][nodeKey];
            nodeObject['name'] = nodeKey;

            // make sure the scope is bound
            scope.registerNodeType.bind(scope)(nodeObject, scope.nodes);

            // save the node class name
            trackedExtension['nodes'][nodeKey] = nodeObject;
          });
        }

        // register the rules
        if (typeof extension['rules'] === 'object') {
          Object.keys(extension['rules']).forEach((ruleKey) => {
            let ruleObject = extension['rules'][ruleKey];
            ruleObject['name'] = ruleKey;

            // make sure the scope is bound
            scope.registerRuleType.bind(scope)(ruleObject, scope.rules);

            // save the node class name
            trackedExtension['rules'][ruleKey] = ruleObject;
          });
        }

        scope.extensions[key] = trackedExtension;
      });
      return scope.extensions;
    },

    getIfGloballyDefined(className, type) {
      if (global && global['NeoScaffoldExtras']) {
        if (type === 'ext' && global['NeoScaffoldExtras']['ext'] && global['NeoScaffoldExtras']['ext'][className]) {
          return global['NeoScaffoldExtras']['ext'][className];
        }
        if (type === 'node' && global['NeoScaffoldExtras']['nodes'] && global['NeoScaffoldExtras']['nodes'][className]) {
          return global['NeoScaffoldExtras']['nodes'][className];
        }
        if (type === 'rule' && global['NeoScaffoldExtras']['rules'] && global['NeoScaffoldExtras']['rules'][className]) {
          return global['NeoScaffoldExtras']['rules'][className];
        }
      }
      return false;
    },

    sanitizeName(string) {
      let entityMap = {
        '&': '',
        '<': '',
        '>': '',
        '"': '',
        "'": '',
        '`': '',
        '=': '',
      };
      return String(string).replace(/[&<>"'`=]/g, function fromEntityMap(s) {
        return entityMap[s];
      });
    },

    registerNodeType(nodeObject, registeredNodes) {
      // attempt to register from global class instance
      let className = nodeObject['javascript_class_name'];
      if (this.getIfGloballyDefined(className, 'node')) {
        registeredNodes[className] = this.getIfGloballyDefined(className, 'node');
      } else {
        // otherwise register from node signature with default values
        registeredNodes[className] = this.nodeFactoryBuilder(nodeObject);
      }

      // register to litegraph
      LiteGraph.registerNodeType(className, registeredNodes[className]);
    },

    nodeFactoryBuilder(nodeObject) {
      let scope = this;
      let title = nodeObject['display_name'] || nodeObject['name'];
      let description = nodeObject['description'] || '';
      let category = nodeObject['category'] || '';
      let subcategory = nodeObject['subcategory'] || '';

      return Object.assign(
        function NeoScaffoldNode() {
          this.serialize_widgets = true; // TODO: consider why this is needed redundantly
          // inputs
          this.addInput('in_rules', 'rule_group', { pos: [10, 10] });
          this.addInput('out_rules', 'rule_group', { pos: [10, 25] });
          let inputValues = nodeObject['input'];
          if (inputValues) {
            // required inputs
            let required = inputValues['required_inputs'];
            if (required && typeof required === 'object') {
              Object.keys(required).forEach((inputKey) => {
                let input = required[inputKey];
                this.addInput(input['name'], input['kind']);
                let widget = input['widget'];
                if (widget && typeof widget === 'object') {
                  this.addWidget(
                    input['widget']['kind'],
                    input['widget']['name'],
                    input['widget']['default'],
                    input['widget']['name'], // modify the uri property
                    undefined // no special options
                  );
                }
              });
            }

            // optional inputs
            let optional = inputValues['optional_inputs'];
            if (optional && typeof optional === 'object') {
              Object.keys(optional).forEach((inputKey) => {
                let input = optional[inputKey];
                this.addInput(input['name'], input['kind']);
                let widget = input['widget'];
                if (widget && typeof widget === 'object') {
                  this.addWidget(
                    input['widget']['kind'],
                    input['widget']['name'],
                    input['widget']['default'],
                    input['widget']['name'], // modify the uri property
                    undefined // no special options
                  );
                }
              });
            }
          }

          // output
          let outputValues = nodeObject['output'];
          if (outputValues) {
            let output = outputValues;
            if (output && typeof output === 'object') {
              this.addOutput(output['name'], output['kind']);
            }
          }

          // results widget section
          scope.addNodeStatusWidget(this);
          scope.addColorMethods(this);
        },
        {
          title,
          description,
          category,
          subcategory,
          serialize_widgets: true,
        }
      );
    },

    registerRuleType(ruleObject, registeredRules) {
      // attempt to register from global class instance
      let className = ruleObject['javascript_class_name'];
      if (this.getIfGloballyDefined(className, 'rule')) {
        registeredRules[className] = this.getIfGloballyDefined(className, 'rule');
      } else {
        // otherwise register from node signature with default values
        registeredRules[className] = this.ruleFactoryBuilder(ruleObject);
      }

      // register to litegraph
      LiteGraph.registerNodeType(className, registeredRules[className]);
    },

    ruleFactoryBuilder(ruleObject) {
      let title = ruleObject['display_name'] || ruleObject['name'];
      let description = ruleObject['description'] || '';
      let category = ruleObject['category'] || '';
      let subcategory = ruleObject['subcategory'] || '';

      return Object.assign(
        function NeoScaffoldRule() {
          this.serialize_widgets = true;
          // inputs
          this.addInput('in_rules', 'rule_group', { pos: [10, 10] });
          this.addOutput('rule_group', 'rule_group');

          let parameterValues = ruleObject['parameters'];
          if (parameterValues) {
            // required parameters
            let required = parameterValues['required_parameters'];
            if (required && typeof required === 'object') {
              Object.keys(required).forEach((inputKey) => {
                let input = required[inputKey];
                this.addInput(input['name'], input['kind']);
                let widget = input['widget'];
                if (widget && typeof widget === 'object') {
                  this.addWidget(
                    input['widget']['kind'],
                    input['widget']['name'],
                    input['widget']['default'],
                    input['widget']['name'], // modify the uri property
                    undefined // no special options
                  );
                }
              });
            }

            // optional parameters
            let optional = parameterValues['optional_parameters'];
            if (optional && typeof optional === 'object') {
              Object.keys(optional).forEach((inputKey) => {
                let input = optional[inputKey];
                this.addInput(input['name'], input['kind']);
                let widget = input['widget'];
                if (widget && typeof widget === 'object') {
                  this.addWidget(
                    input['widget']['kind'],
                    input['widget']['name'],
                    input['widget']['default'],
                    input['widget']['name'], // modify the uri property
                    undefined // no special options
                  );
                }
              });
            }
          }
        },
        {
          title,
          description,
          category,
          subcategory,
          serialize_widgets: true,
        }
      );
    },

    addColorMethods(node) {
      // Add a custom method to restore the original colors
      node.restoreColors = node.restoreColors || function(resetAll) {
        if (node._originalColor) {
          node.color = node._originalColor;
          delete node._originalColor;
        }
        if (node._originalBgColor) {
          node.bgcolor = node._originalBgColor;
          delete node._originalBgColor;
        }

        // reset the error colors
        if (node.color === "#FF0000") {
          node.color = LiteGraph.NODE_DEFAULT_COLOR;
        }
        if (node.bgcolor === "#FF0000") {
          node.bgcolor = LiteGraph.NODE_DEFAULT_BGCOLOR;
        }

        // resets all the nodes to the default colors
        if (resetAll) {
          node.color = LiteGraph.NODE_DEFAULT_COLOR;
          node.bgcolor = LiteGraph.NODE_DEFAULT_BGCOLOR;
        }
      };

      // Add a custom method to store and switch the colors
      node.storeAndSwitchColors = node.storeAndSwitchColors || function(color, bgColor) {
        if (color && bgColor) {
          // Store the original colors if they are not already stored
          if (!node._originalColor) {
            node._originalColor = node.color || LiteGraph.NODE_DEFAULT_COLOR;
          }
          if (!node._originalBgColor) {
            node._originalBgColor = node.bgcolor || LiteGraph.NODE_DEFAULT_BGCOLOR;
          }

          // Switch the colors
          node.color = color;
          node.bgcolor = bgColor;
        }
      };
    },

    createDataModal(data, bgColor) {
      // Create modal container
      const modal = document.createElement('div');
      modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
      `;

      // Create modal content
      const modalContent = document.createElement('div');
      modalContent.style.cssText = `
        background: ${bgColor};
        padding: 20px;
        border-radius: 5px;
        min-width: 50%;
        max-width: 90%;
        max-height: 90vh;
        display: flex;
        flex-direction: column;
      `;

      // Create textarea
      const textarea = document.createElement('textarea');
      textarea.value = JSON.stringify(data, null, 2);
      textarea.style.cssText = `
        width: calc(100% - 20px);
        min-height: 300px;
        margin: 10px 0;
        font-family: monospace;
        padding: 10px;
      `;

      // Create close button
      const closeBtn = document.createElement('button');
      closeBtn.textContent = 'Close';
      closeBtn.style.cssText = `
        padding: 8px 16px;
        align-self: flex-end;
        border-radius: 5px;
      `;
      closeBtn.onclick = () => modal.remove();

      // Assemble and show modal
      modalContent.appendChild(textarea);
      modalContent.appendChild(closeBtn);
      modal.appendChild(modalContent);
      document.body.appendChild(modal);
    },

    addNodeStatusWidget(node) {
      // let [topLeftX, topLeftY, width, height] = node.getBounding();
      // check if the widget already exists
      if (node.widgets && node.widgets.length > 0 && node.widgets.find(w => w.type === 'status')) {
        return;
      }
      const scope = this;
      const widget = {
        type: "status",
        name: "status",
        // mouseup event
        mouse(event, pos, node) {
          if (event.type === 'mouseup') {
            const modalData = node.properties.node_errors || node.properties;
            scope.createDataModal(modalData, LiteGraph.NODE_DEFAULT_BGCOLOR);
          }
        },
        prepareStatusLines(node) {
          let statusLines = [];

          if (node.properties && node.properties.node_errors) {
            statusLines.push('NODE_ERRORS: (click to view)');
            let jsonResult = JSON.stringify(node.properties.node_errors, null, 4);
            let resultArray = jsonResult.split('\n');
            statusLines = statusLines.concat(resultArray);
            return statusLines;
          }

          if (node.properties && node.properties.result && node.properties.result.hasOwnProperty('result')) {
            statusLines.push('OUTPUT: (click to view)');
            let result = node.properties.result.result;
            let timestamp = "NOT RUN YET";
            if (node.properties.result.hasOwnProperty('timestamp')) {
              timestamp = node.properties.result.timestamp;
            }
            let jsonResult = JSON.stringify({
              timestamp,
              prompt_id: node.properties.result.prompt_id,
              values: result.values,
              input_evaluation: result.input_evaluation,
              output_evaluation: result.output_evaluation
            }, null, 4);
            let resultArray = jsonResult.split('\n');
            statusLines = statusLines.concat(resultArray);
          }


          return statusLines;
        },
        drawTextInBounding(
          ctx,
          textLineArray,
          text_color,
          secondary_text_color,
          characterSize,
          lineHeight,
          margin,
          boundingX,
          boundingY,
          boundingWidth,
          boundingHeight
        ) {

          // setup
          ctx.fillStyle = text_color;

          let currentLineHeight = 0;
          textLineArray.forEach((textLine, index) => {
            // make sure text fits vertically
            if (currentLineHeight > (boundingHeight - (margin + 5))) {
              return;
            }

            // Split text into multiple lines if it's too long
            let text = textLine;
            let lines = [];
            while (text.length * characterSize > (boundingWidth - (margin + 5))) {
              let splitPoint = Math.floor((boundingWidth - (margin + 5)) / characterSize);
              lines.push(text.substring(0, splitPoint));
              text = text.substring(splitPoint);
            }
            if (text.length > 0) {
              lines.push(text);
            }

            // Draw each line
            lines.forEach(line => {
              if (currentLineHeight > (boundingHeight - (margin + 5))) {
                return;
              }

              // draw the text
              ctx.fillText(
                line,
                margin * 2,
                currentLineHeight + boundingY + (margin + 5)
              );

              // increment the line height
              currentLineHeight = currentLineHeight + lineHeight;
            });
          });

        },
        computeSize() {
          const margin = 15;
          const MIN_SIZE = LiteGraph.NODE_WIDGET_HEIGHT + 30;
          const node = this.parent;

          let inputSectionY = LiteGraph.NODE_WIDGET_HEIGHT * Math.max(node.inputs.length, node.outputs.length) + 5;
          let displaySpaceHeight = node.size[1] - inputSectionY;

          // Compute the height of all non customtext widgets
          let cumulativeWidgetHeight = 0;
          for (let i = 0; i < node.widgets.length; i++) {
            const w = node.widgets[i];
            if (w.type !== "status") {
              if (w.computeSize) {
                cumulativeWidgetHeight += w.computeSize()[1] + 4;
              } else {
                cumulativeWidgetHeight += LiteGraph.NODE_WIDGET_HEIGHT + 5;
              }
            }
          }

          // See how large the canvas can be
          displaySpaceHeight = displaySpaceHeight - cumulativeWidgetHeight;

          // There isnt enough space for all the widgets, increase the size of the node
          if (displaySpaceHeight < MIN_SIZE) {
            displaySpaceHeight = MIN_SIZE;
            node.size[1] = inputSectionY + cumulativeWidgetHeight + displaySpaceHeight;
            node.graph.setDirtyCanvas(true);
          }

          const statusWidth = node.size[0] - (margin * 2);
          const statusHeight = displaySpaceHeight - margin;

          return [
            statusWidth,
            statusHeight
          ];
        },
        draw(
          ctx,
          node,
          widgetWidth,
          widgetY,
          widgetHeight
        ) {
          if (node.widgets[0].last_y !== null) {
            // if there are no other widgets
          }
          // let border = 2;
          let outline_color = LiteGraph.WIDGET_OUTLINE_COLOR;
          let background_color = LiteGraph.WIDGET_BGCOLOR;
          let text_color = LiteGraph.WIDGET_TEXT_COLOR;
          let secondary_text_color = LiteGraph.WIDGET_SECONDARY_TEXT_COLOR;


          // text stuff
          ctx.textAlign = 'left';
          ctx.fillStyle = background_color;

          ctx.beginPath();

          let characterSize = 6;
          let lineHeight = 16;

          let margin = 15;
          let statusX = margin;
          let statusY = widgetY + 5;

          let [statusWidth, statusHeight] = this.computeSize();

          ctx.roundRect(
            statusX,
            statusY,
            statusWidth,
            statusHeight,
            [margin * 0.7]
          );
          ctx.fill();


          // draw the text we want "at a glance"
          ctx.font = '12px "PP Mori SemiBold"';

          let statusLinesArray = this.prepareStatusLines(node);

          this.drawTextInBounding(
            ctx,
            statusLinesArray,
            text_color,
            secondary_text_color,
            characterSize,
            lineHeight,
            margin,
            statusX,
            statusY,
            statusWidth,
            statusHeight
          );
        },
      };
      widget.parent = node;

      if (!node.addCustomWidget) {
        node.addCustomWidget = function(custom_widget) {
          if (!this.widgets) {
            this.widgets = [];
          }
          this.widgets.push(custom_widget);
          return custom_widget;
        }
      }

      node.addCustomWidget(widget);
    },

    updateCanvasSize(canvas) {
      canvas.canvas.width = window.innerWidth;
      canvas.canvas.height = window.innerHeight - 50;
    },

    // TODO: make this cool again
    defaultGraph() {
      this.import({"last_node_id":23,"last_link_id":32,"nodes":[{"id":6,"type":"nsString","pos":[-359,-35],"size":{"0":210,"1":140},"flags":{},"order":0,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"text","type":"*","link":null}],"outputs":[{"name":"*","type":"*","links":[4,6,13],"slot_index":0}],"properties":{},"widgets_values":["conditionKey",null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":13,"type":"ValuePath","pos":[312,193],"size":{"0":210,"1":185},"flags":{},"order":5,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"object","type":"*","link":17},{"name":"value_path","type":"*","link":null}],"outputs":[{"name":"*","type":"*","links":[18],"slot_index":0}],"properties":{},"widgets_values":["","key",null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":1,"type":"WhileLoop","pos":[594,181],"size":{"0":260.0198974609375,"1":209.38462829589844},"flags":{},"order":6,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"condition_key","type":"string","link":18},{"name":"node_inputs","type":"*","link":null}],"outputs":[{"name":"loop","type":"control_flow","links":[2,14],"slot_index":0}],"properties":{},"widgets_values":["","",null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":4,"type":"MemoryWrite","pos":[-61,183],"size":{"0":282.33099365234375,"1":359.73834228515625},"flags":{},"order":4,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"key","type":"*","link":4},{"name":"value","type":"*","link":22}],"outputs":[{"name":"*","type":"*","links":[17],"slot_index":0}],"properties":{},"widgets_values":["","",null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":17,"type":"PassThrough","pos":[-526,369],"size":{"0":210,"1":185},"flags":{},"order":3,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"value","type":"*","link":21},{"name":"ignored_input","type":"*","link":23}],"outputs":[{"name":"*","type":"*","links":[22],"slot_index":0}],"properties":{},"widgets_values":["","",null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":5,"type":"nsInteger","pos":[-834,242],"size":{"0":210,"1":140},"flags":{},"order":1,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"value","type":"number","link":null}],"outputs":[{"name":"*","type":"*","links":[21],"slot_index":0}],"properties":{},"widgets_values":[-5,null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":21,"type":"ValuePath","pos":[1788,-406],"size":{"0":261.3745422363281,"1":326.31549072265625},"flags":{},"order":12,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"object","type":"*","link":26},{"name":"value_path","type":"*","link":null}],"outputs":[{"name":"*","type":"*","links":[28],"slot_index":0}],"properties":{},"widgets_values":["","summary",null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":18,"type":"MemoryWrite","pos":[-925,517],"size":{"0":341.07843017578125,"1":347.3846740722656},"flags":{},"order":2,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"key","type":"*","link":null},{"name":"value","type":"*","link":null}],"outputs":[{"name":"*","type":"*","links":[23],"slot_index":0}],"properties":{},"widgets_values":["thought_memory","Computers usually have a CPU.",null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":12,"type":"PassThrough","pos":[1007,219],"size":{"0":210,"1":185},"flags":{},"order":7,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"value","type":"*","link":13},{"name":"ignored_input","type":"*","link":14}],"outputs":[{"name":"*","type":"*","links":[19,31],"slot_index":0}],"properties":{},"widgets_values":["","",null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":22,"type":"MemoryRead","pos":[524,-395],"size":{"0":210,"1":140},"flags":{},"order":9,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"key","type":"*","link":32}],"outputs":[{"name":"*","type":"*","links":[30],"slot_index":0}],"properties":{},"widgets_values":["",null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":23,"type":"PassThrough","pos":[221,-313],"size":{"0":210,"1":185},"flags":{},"order":8,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"value","type":"*","link":null},{"name":"ignored_input","type":"*","link":31}],"outputs":[{"name":"*","type":"*","links":[32],"slot_index":0}],"properties":{},"widgets_values":["thought_memory","",null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":20,"type":"MemoryWrite","pos":[2184,-347],"size":{"0":402.1434326171875,"1":351.7113037109375},"flags":{},"order":13,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"key","type":"*","link":null},{"name":"value","type":"*","link":28}],"outputs":[{"name":"*","type":"*","links":[29],"slot_index":0}],"properties":{},"widgets_values":["thought_memory","",null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":19,"type":"ConcatString","pos":[862,-428],"size":{"0":334.36578369140625,"1":356.46441650390625},"flags":{},"order":10,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"a","type":"*","link":null},{"name":"b","type":"*","link":30}],"outputs":[{"name":"*","type":"*","links":[25],"slot_index":0}],"properties":{},"widgets_values":["Think about the following and describe the most impactful optimization that you can apply to computer programs: ","",null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":14,"type":"PassThrough","pos":[1405,268],"size":{"0":210,"1":185},"flags":{},"order":14,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"value","type":"*","link":19},{"name":"ignored_input","type":"*","link":29}],"outputs":[{"name":"*","type":"*","links":[20],"slot_index":0}],"properties":{},"widgets_values":["","",null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":9,"type":"MemoryRead","pos":[1723,306],"size":{"0":210,"1":140},"flags":{},"order":15,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"key","type":"*","link":20}],"outputs":[{"name":"*","type":"*","links":[9],"slot_index":0}],"properties":{},"widgets_values":["",null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":8,"type":"Add","pos":[2057,299],"size":{"0":210,"1":185},"flags":{},"order":16,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"a","type":"number","link":9},{"name":"b","type":"number","link":null}],"outputs":[{"name":"result","type":"number","links":[11],"slot_index":0}],"properties":{},"widgets_values":[0,1,null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":7,"type":"MemoryWrite","pos":[2378,211],"size":{"0":324.9847106933594,"1":346.9991455078125},"flags":{},"order":17,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"key","type":"*","link":6},{"name":"value","type":"*","link":11}],"outputs":[{"name":"*","type":"*","links":[12],"slot_index":0}],"properties":{},"widgets_values":["","",null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":11,"type":"ConsoleLog","pos":[2774,215],"size":{"0":459.69244384765625,"1":353.1351013183594},"flags":{},"order":18,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"any","type":"*","link":12}],"outputs":[{"name":"any","type":"*","links":[16],"slot_index":0}],"properties":{},"widgets_values":["",null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":3,"type":"EndWhileLoop","pos":[1336,662],"size":{"0":351.9732971191406,"1":322.6043701171875},"flags":{},"order":19,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"WhileLoop","type":"control_flow","link":2},{"name":"node_inputs","type":"*","link":16}],"outputs":[{"name":"*","type":"*","links":null}],"properties":{},"widgets_values":["",null],"color":"#B8D982","bgcolor":"#B8D982"},{"id":15,"type":"CerebrasAgent","pos":[1283,-426],"size":{"0":433.79644775390625,"1":471.2294616699219},"flags":{},"order":11,"mode":0,"inputs":[{"name":"in_rules","type":"rule_group","link":null,"pos":[10,10]},{"name":"out_rules","type":"rule_group","link":null,"pos":[10,25]},{"name":"api_key","type":"string","link":null},{"name":"prompt","type":"string","link":25}],"outputs":[{"name":"*","type":"*","links":[26],"slot_index":0}],"properties":{},"widgets_values":["demo-x8jjywxyteevcxhtrc4jm9xyt3w5ph8jpjfweyrn52kmcjce","",null],"color":"#B8D982","bgcolor":"#B8D982"}],"links":[[2,1,0,3,2,"control_flow"],[4,6,0,4,2,"*"],[6,6,0,7,2,"*"],[9,9,0,8,2,"number"],[11,8,0,7,3,"*"],[12,7,0,11,2,"*"],[13,6,0,12,2,"*"],[14,1,0,12,3,"*"],[16,11,0,3,3,"*"],[17,4,0,13,2,"*"],[18,13,0,1,2,"string"],[19,12,0,14,2,"*"],[20,14,0,9,2,"*"],[21,5,0,17,2,"*"],[22,17,0,4,3,"*"],[23,18,0,17,3,"*"],[25,19,0,15,3,"string"],[26,15,0,21,2,"*"],[28,21,0,20,3,"*"],[29,20,0,14,3,"*"],[30,22,0,19,3,"*"],[31,12,0,23,3,"*"],[32,23,0,22,2,"*"]],"groups":[],"config":{},"extra":{},"version":0.4,"NeoScaffoldVersion":0.1,"checksum":"L4y6vAh5cQxZmBgtkS445UEYWSJ5CF6yosZ/LMdwlEY="});
    },

    async graphToPrompt(graph) {
      // TODO: consider beforeQueued hook (to have frontend validation or other logic)
      const scope = this;
      const workflow = await scope.serializeGraph(graph, scope.checksumSHA256);
      const computedOrder = graph.computeExecutionOrder(false);
      const output = {};

      computedOrder.forEach((node) => {
        // Skip if mode is NEVER
        // TODO: consider node mode 4 'BYPASS'
        let skippable = node.mode === 2;
        if (skippable) {
          return;
        }
        // TODO: consider extension with getInnerNodes (convert a bunch of nodes to a single node)

        let inputs = {};

        // Store all widget values
        let widgets = node.widgets;
        if (widgets && Array.isArray(widgets)) {
          widgets.forEach((widget) => {
            if (!widget.options || widget.options.serialize !== false) {
              inputs[widget.name] = widget.value;
            }
          });
        }

        // Store all links
        let nodeInputs = node.inputs;
        if (nodeInputs && Array.isArray(nodeInputs)) {
          nodeInputs.forEach((input, slotIndex) => {
            let parentNode = node.getInputNode(slotIndex);
            if (parentNode) {
              let link = node.getInputLink(slotIndex);
              // TODO: consider node mode 4 "BYPASS"
              if (link) {
                // TODO: consider adding an "UpdateLink" Hook on Nodes

                inputs[node.inputs[slotIndex].name] = {
                  originId: String(link.origin_id),
                  // we removed originSlot because in NeoScaffold we only have one output per node
                  // originSlot: link.origin_slot,
                };
              }
            }
          });
        }

        let nodeData = {
          // input maps
          inputs,
          // functionally identify the node for backend
          type: node.type,
          // save the title for simpler debugging
          name: scope.sanitizeName(node.title),
        };

        // organize the nodes by id
        output[String(node.id)] = nodeData;
      });

      const prompt = {
        prompt: output,
        workflow,
      };

      const promptForChecksum = {
        prompt: prompt.prompt,
        workflow: prompt.workflow.checksum,
      };

      const checksum = await this.checksumSHA256(JSON.stringify(promptForChecksum));

      prompt.checksum = checksum;

      return prompt;
    },

    /**
   * Queue a prompt means to create each prompt an ID make any intermediate changes needed to the graph, send the requests to the backend concurrently, and then capture the response, and use the websocket connection to track the updates between batches and allow the user to see the progress of the prompts.
   * @param {*} missingNodeTypes
   */
    async queuePrompt(batchSize) {
      batchSize = batchSize || 1;

      let prompt = await this.graphToPrompt(this.graph);

      let queuedPrompt, promptId;
      for (let i = 0; i < batchSize; i++) {
        promptId = this.createPushId();

        // check if js environment has builtin structuredClone
        if (typeof structuredClone === 'undefined') {
          queuedPrompt = JSON.parse(JSON.stringify(prompt));
        } else {
          queuedPrompt = structuredClone(prompt);
        }
        queuedPrompt.promptId = promptId;

        this.queueItems.push({
          id: promptId,
          status: 'queued',
          queuedPrompt,
        });
      }
      if (this.processingQueue) {
        return;
      }

      this.processingQueue = true;
      let responses = {};
      try {
        let queueItem, response;
        while (this.queueItems.length) {
          queueItem = this.queueItems.pop();
          if (!queueItem) {
            break;
          }
          try {
            console.log(JSON.stringify(queueItem.queuedPrompt));
            response = await this.api.queuePrompt(JSON.stringify(queueItem.queuedPrompt));
            responses[queueItem.id] = response;
          } catch (error) {
            console.error(error);
            queueItem.status = 'error';
            break;
          }

          // TODO: consider adding afterQueued hook to widgets to update seeds for nodes that use those
        }

      } catch (error) {
        console.error(error);
      } finally {
        this.processingQueue = false;
      }
      console.log(responses);
      return responses;
    },

    clean() {
      this.graph.clear();
    },

    removeAllListeners() {
      // Remove all listeners
      window.removeEventListener('resize', this._resizeHandler);
    },

    importGraph(event) {
      const scope = this;
      const file = event.target.files[0]; // Gets the uploaded file
      if (file) {
        const reader = new FileReader();

        reader.onload = (e) => {
          const text = e.target.result;
          try {
            const obj = JSON.parse(text); // Parse the file content as JSON

            scope.import(obj);
          } catch (error) {
            console.error("Error parsing JSON:", error);
          }
        };

        reader.onerror = (e) => {
          console.error("Error reading file:", e.target.error);
        };

        reader.readAsText(file); // Read the file content as text
      }
    },

    async exportWorkflow() {
      const workflow = await this.export();
      const jsonString = JSON.stringify(workflow);

      const blob = new Blob([jsonString], { type: 'application/json' });
      const url = URL.createObjectURL(blob);

      const a = document.createElement('a');
      a.href = url;
      a.download = 'nsgraph.json'; // The filename for the download
      document.body.appendChild(a); // Append to the document
      a.click(); // Trigger the download

      document.body.removeChild(a); // Clean up
      URL.revokeObjectURL(url); // Free up memory
    },

    async export() {
      if (!this.graph) {
        return;
      }
      return await this.serializeGraph(this.graph, this.checksumSHA256);
    },

    async serializeGraph(graph, hashingFunction) {
      const serializedGraph = graph.serialize();

      serializedGraph.NeoScaffoldVersion = NeoScaffold.VERSION;

      const customSerialize = {
        last_node_id: serializedGraph.last_node_id,
        last_link_id: serializedGraph.last_link_id,
        links: serializedGraph.links,
        groups: serializedGraph.groups,
      };

      customSerialize.nodes = serializedGraph.nodes.map((node) => {
        return {
          id: node.id,
          type: node.type,
        }
      }).sort((a, b) => a.id - b.id);


      serializedGraph.checksum = await hashingFunction(JSON.stringify(customSerialize));

      return serializedGraph;
    },

    /**
     * Calculate a SHA256 checksum of a string
     * @param {string} string
     * @returns {string}
     */
    async checksumSHA256(string) {
      const utf8 = new TextEncoder().encode(string || "");
      const hashBuffer = await global.crypto.subtle.digest('SHA-256', utf8);
      // Use Uint8Array directly instead of Array.from for better performance
      const hashArray = new Uint8Array(hashBuffer);
      // Convert to base64
      return btoa(String.fromCharCode.apply(null, hashArray));
    },

    /**
     * Imports the graph
     * @param {*} graphObject
     */
    async import(graphObject) {
      this.clean();

      const scope = this;
      const missingNodeTypes = [];

      let graphClone = undefined;

      // check if js environment has builtin structuredClone
      if (typeof structuredClone === 'undefined') {
        graphClone = JSON.parse(JSON.stringify(graphObject));
      } else {
        graphClone = structuredClone(graphObject);
      }

      // TODO: extensions beforeConfigureGraph hook

      graphClone.nodes.forEach((node) => {
        // Find missing node types
        if (!(node.type in LiteGraph.registered_node_types)) {
          missingNodeTypes.push(node.type);
          node.type = scope.sanitizeName(node.type);
        }
      });

      try {
        this.graph.configure(graphClone);
      } catch (error) {
        // TODO: parse error and show error message
        return;
      }

      this.graph._nodes.forEach((node) => {
        // make nodes size accurately computed
        const size = node.computeSize();
        size[0] = Math.max(node.size[0], size[0]);
        size[1] = Math.max(node.size[1], size[1]);
        node.size = size;
        // TODO: extensions loadedGraphNode hook
      });

      if (missingNodeTypes.length) {
        this.showMissingNodesError(missingNodeTypes);
      }

      // TODO: extensions afterConfigureGraph hook (pass missingNodeTypes)

      this.graphImport = this.graph;
      return this.graphImport;
    },

    showMissingNodesError(missingNodeTypes) {
      alert('Missing node types: ' + missingNodeTypes.join(', '));
    },

    async stepThroughBreakpoints(canvas) {
      const workflowSnapshot = await NeoScaffold.export();
      if (!workflowSnapshot) {
        return;
      }
      const nodeIds = [];

      if (!canvas.selected_nodes || Object.keys(canvas.selected_nodes).length === 0) {
        alert('No nodes selected');
        return;
      }
      Object.keys(canvas.selected_nodes).forEach((nodeId) => {
        nodeIds.push(nodeId);

        if (canvas.onNodeDeselected) {
          canvas.onNodeDeselected(canvas.selected_nodes[nodeId]);
        }
      });
      canvas.selected_nodes = {};

      canvas.current_node = null;
      canvas.highlighted_links = {};
      canvas.setDirty(true);
      canvas.graph.afterChange();
      await NeoScaffold.api.postStepThroughBreakpoints(workflowSnapshot.checksum, nodeIds);
    },

    async toggleBreakpoints(canvas, allBreak) {
      const workflowSnapshot = await NeoScaffold.export();
      if (allBreak) {
        return NeoScaffold.api.postToggleBreakpoints(workflowSnapshot.checksum, [], allBreak);
      }

      if (workflowSnapshot) {
        graph = canvas.graph;
        graph.beforeChange();

        if (!canvas.hasOwnProperty("breakpoints")) {
          canvas.breakpoints = {};
        }

        if (!canvas.breakpoints.hasOwnProperty(workflowSnapshot.checksum)) {
          canvas.breakpoints[workflowSnapshot.checksum] = {};
        }

        if (!canvas.selected_nodes || Object.keys(canvas.selected_nodes).length === 0) {
          alert('No nodes selected');
          return;
        }
        Object.keys(canvas.selected_nodes).forEach((nodeId) => {
          const node = canvas.selected_nodes[nodeId];

          if (canvas.breakpoints[workflowSnapshot.checksum][nodeId]) {
            // remove the breakpoint
            delete canvas.breakpoints[workflowSnapshot.checksum][nodeId];
            node.restoreColors();

          } else {
            // adds the breakpoint
            canvas.breakpoints[workflowSnapshot.checksum][nodeId] = true;
            node.storeAndSwitchColors("#141414", "#141414");
          }

          if (canvas.onNodeDeselected) {
            canvas.onNodeDeselected(canvas.selected_nodes[nodeId]);
          }
        });
        canvas.selected_nodes = {};

        canvas.current_node = null;
        canvas.highlighted_links = {};
        canvas.setDirty(true);
        canvas.graph.afterChange();

        const nodeIds = Object.keys(canvas.breakpoints[workflowSnapshot.checksum]);
        await NeoScaffold.api.postToggleBreakpoints(workflowSnapshot.checksum, nodeIds, allBreak);
      }
    },

    async toggleStopPoints(canvas, allStop) {
      const workflowSnapshot = await NeoScaffold.export();
      if (!workflowSnapshot) {
        return;
      }
      const nodeIds = [];

      if (allStop) {
        return NeoScaffold.api.postToggleStop(workflowSnapshot.checksum, [], allStop);
      }

      if (!canvas.selected_nodes || Object.keys(canvas.selected_nodes).length === 0) {
        alert('No nodes selected');
        return;
      }
      Object.keys(canvas.selected_nodes).forEach((nodeId) => {
        nodeIds.push(nodeId);

        if (canvas.onNodeDeselected) {
          canvas.onNodeDeselected(canvas.selected_nodes[nodeId]);
        }
      });
      canvas.selected_nodes = {};

      canvas.current_node = null;
      canvas.highlighted_links = {};
      canvas.setDirty(true);
      canvas.graph.afterChange();
      await NeoScaffold.api.postToggleStop(workflowSnapshot.checksum, nodeIds, allStop);
    },

    async toggleRestartPoints(canvas, allRestart) {
      const workflowSnapshot = await NeoScaffold.export();
      if (!workflowSnapshot) {
        return;
      }
      const nodeIds = [];
      if (allRestart) {
        return NeoScaffold.api.postToggleRestart(workflowSnapshot.checksum, [], allRestart);
      }

      if (!canvas.selected_nodes || Object.keys(canvas.selected_nodes).length === 0) {
        alert('No nodes selected');
        return;
      }
      Object.keys(canvas.selected_nodes).forEach((nodeId) => {
        nodeIds.push(nodeId);

        if (canvas.onNodeDeselected) {
          canvas.onNodeDeselected(canvas.selected_nodes[nodeId]);
        }
      });
      canvas.selected_nodes = {};

      canvas.current_node = null;
      canvas.highlighted_links = {};
      canvas.setDirty(true);
      canvas.graph.afterChange();
      await NeoScaffold.api.postToggleRestart(workflowSnapshot.checksum, nodeIds, allRestart);
    },

    /**
     * Adds keyboard shortcuts to the canvas
     * @param {LiteGraphCanvas} canvas
     */
    addKeyboardShortcuts(litegraphCanvas) {
      litegraphCanvas.canvas.removeEventListener('keydown', litegraphCanvas._key_callback, true);
      document.removeEventListener('keyup', litegraphCanvas._key_callback, true);

      async function processKey(e) {
        if (!this.graph) {
          return;
        }

        var block_default = false;
        // console.log(e); //debug
        // remove the debug

        if (e.target.localName == 'input') {
          return;
        }

        if (e.type == 'keydown') {
          if (e.keyCode == 32) {
            //space
            // this.dragging_canvas = true;
            if (NeoScaffold['isPaused']) {
              await NeoScaffold.stepThroughBreakpoints(NeoScaffold.litegraphCanvas);
            } else {
              await NeoScaffold.toggleBreakpoints(NeoScaffold.litegraphCanvas, true);
            }
            block_default = true;
          }

          if (e.keyCode == 27) {
            //esc
            if (this.node_panel) this.node_panel.close();
            if (this.options_panel) this.options_panel.close();
            block_default = true;
          }

          //select all Control A
          if (e.keyCode == 65 && e.ctrlKey) {
            this.selectNodes();
            block_default = true;
          }

          if (e.keyCode === 67 && (e.metaKey || e.ctrlKey) && !e.shiftKey) {
            //copy
            if (this.selected_nodes) {
              this.copyToClipboard();
              block_default = true;
            }
          }

          if (e.keyCode === 86 && (e.metaKey || e.ctrlKey)) {
            //paste
            this.pasteFromClipboard(e.shiftKey);
          }

          //delete or backspace
          if (e.keyCode == 46 || e.keyCode == 8) {
            if (e.target.localName != 'input' && e.target.localName != 'textarea') {
              this.deleteSelectedNodes();
              block_default = true;
            }
          }

          //collapse
          //...

          //TODO
          if (this.selected_nodes) {
            for (var i in this.selected_nodes) {
              if (this.selected_nodes[i].onKeyDown) {
                this.selected_nodes[i].onKeyDown(e);
              }
            }
          }
        } else if (e.type == 'keyup') {
          // if (e.keyCode == 32) {
          //   // space
          //   this.dragging_canvas = false;
          // }

          if (this.selected_nodes) {
            for (var i in this.selected_nodes) {
              if (this.selected_nodes[i].onKeyUp) {
                this.selected_nodes[i].onKeyUp(e);
              }
            }
          }
        }

        this.graph.change();

        if (block_default) {
          e.preventDefault();
          e.stopImmediatePropagation();
          return false;
        }
      };

      litegraphCanvas.processKey = processKey.bind(litegraphCanvas);
      litegraphCanvas._key_callback = litegraphCanvas.processKey;

      litegraphCanvas.canvas.addEventListener('keydown', litegraphCanvas._key_callback, true);
      document.addEventListener('keyup', litegraphCanvas._key_callback, true); //in document, otherwise it doesn't fire keyup
      // canvas.addEventListener('keydown', async (event) => {
      //   // spacebar play
      //   switch (event.key.toLowerCase()) {
      //     case ' ':
      //       // if paused, resume
      //       if (NeoScaffold['isPaused']) {
      //         await NeoScaffold.stepThroughBreakpoints(canvas);
      //       } else {
      //         await NeoScaffold.queuePrompt(1);
      //       }
      //       break;

      //     case 'b':
      //       NeoScaffold.toggleBreakpoints(canvas, true);
      //       break;

      //     case 'r':
      //       if (event.ctrlKey) {
      //         NeoScaffold.toggleRestartPoints(canvas, true);
      //       }
      //       break;

      //     case 's':
      //       if (event.ctrlKey) {
      //         await NeoScaffold.exportWorkflow();
      //         event.preventDefault(); // Prevent browser save dialog
      //       }
      //       break;

      //     case 'i':
      //       if (event.ctrlKey) {
      //         document.getElementById('workflow-input').click();
      //         event.preventDefault();
      //       }
      //       break;
      //   }
      // });
    },

    /**
     * Creates a 4 button toolbar which is fixed 50px from the bottom of the screen which contains the following buttons:
     * - Play
     * - Pause
     * - Stop
     * - Restart
     * @param {LiteGraphCanvas} canvas
     */
    addRuntimeButtons(canvas) {
      // create a toolbar container
      const toolbar = document.createElement('div');
      toolbar.style.position = 'fixed';
      toolbar.style.bottom = '50px';
      toolbar.style.left = '50%';
      toolbar.style.transform = 'translateX(-50%)';
      toolbar.style.zIndex = '1000';
      toolbar.style.display = 'flex';
      toolbar.style.justifyContent = 'center';
      toolbar.style.alignItems = 'center';

      // add buttons to the toolbar
      const buttons = [
        {
          content: '▶️',
          async callback() {
            // if paused, resume
            if (NeoScaffold['isPaused']) {
              await NeoScaffold.stepThroughBreakpoints(canvas);
            } else {
              await NeoScaffold.queuePrompt(1);
            }
          }
        },
        {
          content: '⏸️',
          callback: () => NeoScaffold.toggleBreakpoints(canvas, true)
        },
        {
          content: '⏹️',
          callback: () => NeoScaffold.toggleStopPoints(canvas, true)
        },
        {
          content: '🔄',
          callback: () => NeoScaffold.toggleRestartPoints(canvas, true)
        },
      ];

      buttons.forEach((button) => {
        const buttonElement = document.createElement('button');
        buttonElement.innerText = button.content;
        buttonElement.style.margin = '0 5px';
        buttonElement.style.padding = '10px';
        buttonElement.style.borderRadius = '5px';
        buttonElement.style.border = 'none';
        buttonElement.style.backgroundColor = '#3c3c3c';
        buttonElement.style.color = '#fff';
        buttonElement.style.cursor = 'pointer';
        buttonElement.addEventListener('click', button.callback);
        toolbar.appendChild(buttonElement);
      });

      document.body.appendChild(toolbar);

      return toolbar;
    },

    addExtraMenuOptions(canvas) {
      // additional menu options
      canvas.getExtraMenuOptions = function(_, options) {
        options.push(
          {
            content: 'Play',
            callback: () => NeoScaffold.queuePrompt(1)
          },
          {
            content: 'Pause',
            callback: () => NeoScaffold.toggleBreakpoints(canvas, true)
          },
          {
            content: 'Stop',
            callback: () => NeoScaffold.toggleStopPoints(canvas, true)
          },
          {
            content: 'Restart',
            callback: () => NeoScaffold.toggleRestartPoints(canvas, true)
          },
        );
      };
    },

    addSideMenuOptions(canvas) {
      // Create floating side menu container
      let sideMenu = document.createElement('div');
      sideMenu.style.position = 'fixed';
      sideMenu.style.right = '20px';
      sideMenu.style.top = '50%';
      sideMenu.style.transform = 'translateY(-50%)';
      sideMenu.style.backgroundColor = '#2c2c2c';
      sideMenu.style.padding = '10px';
      sideMenu.style.borderRadius = '5px';
      sideMenu.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
      sideMenu.style.zIndex = '1000';

      // Add buttons to side menu
      const menuItems = [
        {
          label: 'Queue',
          callback: () => NeoScaffold.queuePrompt(1)
        },
        {
          label: 'Export',
          callback: () => NeoScaffold.exportWorkflow()
        },
        {
          label: 'Import',
          callback: () => document.getElementById('workflow-input').click()
        },
        {
          label: 'Toggle Breakpoints',
          callback: () => NeoScaffold.toggleBreakpoints(canvas)
        },
        {
          label: 'Step Through Breakpoints',
          callback: () => NeoScaffold.stepThroughBreakpoints(canvas)
        },
        {
          label: 'Toggle Stop Points',
          callback: () => NeoScaffold.toggleStopPoints(canvas)
        },
        {
          label: 'Toggle Restart Points',
          callback: () => NeoScaffold.toggleRestartPoints(canvas)
        },
        {
          label: 'Clear',
          callback: () => NeoScaffold.clean()
        }
      ];

      menuItems.forEach(item => {
        let button = document.createElement('button');
        button.innerText = item.label;
        button.style.display = 'block';
        button.style.width = '100%';
        button.style.padding = '8px 15px';
        button.style.marginBottom = '5px';
        button.style.border = 'none';
        button.style.borderRadius = '3px';
        button.style.backgroundColor = '#3c3c3c';
        button.style.color = '#fff';
        button.style.cursor = 'pointer';

        button.addEventListener('mouseover', () => {
          button.style.backgroundColor = '#4c4c4c';
        });

        button.addEventListener('mouseout', () => {
          button.style.backgroundColor = '#3c3c3c';
        });

        button.addEventListener('click', item.callback);
        sideMenu.appendChild(button);
      });

      document.body.appendChild(sideMenu);
    }

  });

}(this));
