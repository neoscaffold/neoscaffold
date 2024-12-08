//basic nodes
(function (global) {
  var LiteGraph = global.LiteGraph;

  //Constant
  function Time() {
    this.addOutput('in ms', 'number');
    this.addOutput('in sec', 'number');
  }

  Time.title = 'Time';
  Time.desc = 'Time';

  Time.prototype.onExecute = function () {
    this.setOutputData(0, this.graph.globaltime * 1000);
    this.setOutputData(1, this.graph.globaltime);
  };

  LiteGraph.registerNodeType('basic/time', Time);

  //Subgraph: a node that contains a graph
  function Subgraph() {
    var that = this;
    this.size = [140, 80];
    this.properties = { enabled: true };
    this.enabled = true;

    //create inner graph
    this.subgraph = new LiteGraph.LGraph();
    this.subgraph._subgraph_node = this;
    this.subgraph._is_subgraph = true;

    this.subgraph.onTrigger = this.onSubgraphTrigger.bind(this);

    //nodes input node added inside
    this.subgraph.onInputAdded = this.onSubgraphNewInput.bind(this);
    this.subgraph.onInputRenamed = this.onSubgraphRenamedInput.bind(this);
    this.subgraph.onInputTypeChanged =
      this.onSubgraphTypeChangeInput.bind(this);
    this.subgraph.onInputRemoved = this.onSubgraphRemovedInput.bind(this);

    this.subgraph.onOutputAdded = this.onSubgraphNewOutput.bind(this);
    this.subgraph.onOutputRenamed = this.onSubgraphRenamedOutput.bind(this);
    this.subgraph.onOutputTypeChanged =
      this.onSubgraphTypeChangeOutput.bind(this);
    this.subgraph.onOutputRemoved = this.onSubgraphRemovedOutput.bind(this);
  }

  Subgraph.title = 'Subgraph';
  Subgraph.desc = 'Graph inside a node';
  Subgraph.title_color = '#334';

  Subgraph.prototype.onGetInputs = function () {
    return [['enabled', 'boolean']];
  };

  /*
  Subgraph.prototype.onDrawTitle = function(ctx) {
      if (this.flags.collapsed) {
          return;
      }

      ctx.fillStyle = "#555";
      var w = LiteGraph.NODE_TITLE_HEIGHT;
      var x = this.size[0] - w;
      ctx.fillRect(x, -w, w, w);
      ctx.fillStyle = "#333";
      ctx.beginPath();
      ctx.moveTo(x + w * 0.2, -w * 0.6);
      ctx.lineTo(x + w * 0.8, -w * 0.6);
      ctx.lineTo(x + w * 0.5, -w * 0.3);
      ctx.fill();
  };
*/

  Subgraph.prototype.onDblClick = function (e, pos, graphcanvas) {
    var that = this;
    setTimeout(function () {
      graphcanvas.openSubgraph(that.subgraph);
    }, 10);
  };

  /*
  Subgraph.prototype.onMouseDown = function(e, pos, graphcanvas) {
      if (
          !this.flags.collapsed &&
          pos[0] > this.size[0] - LiteGraph.NODE_TITLE_HEIGHT &&
          pos[1] < 0
      ) {
          var that = this;
          setTimeout(function() {
              graphcanvas.openSubgraph(that.subgraph);
          }, 10);
      }
  };
*/

  Subgraph.prototype.onAction = function (action, param) {
    this.subgraph.onAction(action, param);
  };

  Subgraph.prototype.onExecute = function () {
    this.enabled = this.getInputOrProperty('enabled');
    if (!this.enabled) {
      return;
    }

    //send inputs to subgraph global inputs
    if (this.inputs) {
      for (var i = 0; i < this.inputs.length; i++) {
        var input = this.inputs[i];
        var value = this.getInputData(i);
        this.subgraph.setInputData(input.name, value);
      }
    }

    //execute
    this.subgraph.runStep();

    //send subgraph global outputs to outputs
    if (this.outputs) {
      for (var i = 0; i < this.outputs.length; i++) {
        var output = this.outputs[i];
        var value = this.subgraph.getOutputData(output.name);
        this.setOutputData(i, value);
      }
    }
  };

  Subgraph.prototype.sendEventToAllNodes = function (eventname, param, mode) {
    if (this.enabled) {
      this.subgraph.sendEventToAllNodes(eventname, param, mode);
    }
  };

  Subgraph.prototype.onDrawBackground = function (
    ctx,
    graphcanvas,
    canvas,
    pos,
  ) {
    if (this.flags.collapsed) return;
    var y = this.size[1] - LiteGraph.NODE_TITLE_HEIGHT + 0.5;
    // button
    var over = LiteGraph.isInsideRectangle(
      pos[0],
      pos[1],
      this.pos[0],
      this.pos[1] + y,
      this.size[0],
      LiteGraph.NODE_TITLE_HEIGHT,
    );
    let overleft = LiteGraph.isInsideRectangle(
      pos[0],
      pos[1],
      this.pos[0],
      this.pos[1] + y,
      this.size[0] / 2,
      LiteGraph.NODE_TITLE_HEIGHT,
    );
    ctx.fillStyle = over ? '#555' : '#222';
    ctx.beginPath();
    if (this._shape == LiteGraph.BOX_SHAPE) {
      if (overleft) {
        ctx.rect(0, y, this.size[0] / 2 + 1, LiteGraph.NODE_TITLE_HEIGHT);
      } else {
        ctx.rect(
          this.size[0] / 2,
          y,
          this.size[0] / 2 + 1,
          LiteGraph.NODE_TITLE_HEIGHT,
        );
      }
    } else {
      if (overleft) {
        ctx.roundRect(
          0,
          y,
          this.size[0] / 2 + 1,
          LiteGraph.NODE_TITLE_HEIGHT,
          [0, 0, 8, 8],
        );
      } else {
        ctx.roundRect(
          this.size[0] / 2,
          y,
          this.size[0] / 2 + 1,
          LiteGraph.NODE_TITLE_HEIGHT,
          [0, 0, 8, 8],
        );
      }
    }
    if (over) {
      ctx.fill();
    } else {
      ctx.fillRect(0, y, this.size[0] + 1, LiteGraph.NODE_TITLE_HEIGHT);
    }
    // button
    ctx.textAlign = 'center';
    ctx.font = '24px Arial';
    ctx.fillStyle = over ? '#DDD' : '#999';
    ctx.fillText('+', this.size[0] * 0.25, y + 24);
    ctx.fillText('+', this.size[0] * 0.75, y + 24);
  };

  // Subgraph.prototype.onMouseDown = function(e, localpos, graphcanvas)
  // {
  // 	var y = this.size[1] - LiteGraph.NODE_TITLE_HEIGHT + 0.5;
  // 	if(localpos[1] > y)
  // 	{
  // 		graphcanvas.showSubgraphPropertiesDialog(this);
  // 	}
  // }
  Subgraph.prototype.onMouseDown = function (e, localpos, graphcanvas) {
    var y = this.size[1] - LiteGraph.NODE_TITLE_HEIGHT + 0.5;
    console.log(0);
    if (localpos[1] > y) {
      if (localpos[0] < this.size[0] / 2) {
        console.log(1);
        graphcanvas.showSubgraphPropertiesDialog(this);
      } else {
        console.log(2);
        graphcanvas.showSubgraphPropertiesDialogRight(this);
      }
    }
  };
  Subgraph.prototype.computeSize = function () {
    var num_inputs = this.inputs ? this.inputs.length : 0;
    var num_outputs = this.outputs ? this.outputs.length : 0;
    return [
      200,
      Math.max(num_inputs, num_outputs) * LiteGraph.NODE_SLOT_HEIGHT +
        LiteGraph.NODE_TITLE_HEIGHT,
    ];
  };

  //**** INPUTS ***********************************
  Subgraph.prototype.onSubgraphTrigger = function (event, param) {
    var slot = this.findOutputSlot(event);
    if (slot != -1) {
      this.triggerSlot(slot);
    }
  };

  Subgraph.prototype.onSubgraphNewInput = function (name, type) {
    var slot = this.findInputSlot(name);
    if (slot == -1) {
      //add input to the node
      this.addInput(name, type);
    }
  };

  Subgraph.prototype.onSubgraphRenamedInput = function (oldname, name) {
    var slot = this.findInputSlot(oldname);
    if (slot == -1) {
      return;
    }
    var info = this.getInputInfo(slot);
    info.name = name;
  };

  Subgraph.prototype.onSubgraphTypeChangeInput = function (name, type) {
    var slot = this.findInputSlot(name);
    if (slot == -1) {
      return;
    }
    var info = this.getInputInfo(slot);
    info.type = type;
  };

  Subgraph.prototype.onSubgraphRemovedInput = function (name) {
    var slot = this.findInputSlot(name);
    if (slot == -1) {
      return;
    }
    this.removeInput(slot);
  };

  //**** OUTPUTS ***********************************
  Subgraph.prototype.onSubgraphNewOutput = function (name, type) {
    var slot = this.findOutputSlot(name);
    if (slot == -1) {
      this.addOutput(name, type);
    }
  };

  Subgraph.prototype.onSubgraphRenamedOutput = function (oldname, name) {
    var slot = this.findOutputSlot(oldname);
    if (slot == -1) {
      return;
    }
    var info = this.getOutputInfo(slot);
    info.name = name;
  };

  Subgraph.prototype.onSubgraphTypeChangeOutput = function (name, type) {
    var slot = this.findOutputSlot(name);
    if (slot == -1) {
      return;
    }
    var info = this.getOutputInfo(slot);
    info.type = type;
  };

  Subgraph.prototype.onSubgraphRemovedOutput = function (name) {
    var slot = this.findOutputSlot(name);
    if (slot == -1) {
      return;
    }
    this.removeOutput(slot);
  };
  // *****************************************************

  Subgraph.prototype.getExtraMenuOptions = function (graphcanvas) {
    var that = this;
    return [
      {
        content: 'Open',
        callback: function () {
          graphcanvas.openSubgraph(that.subgraph);
        },
      },
    ];
  };

  Subgraph.prototype.onResize = function (size) {
    size[1] += 20;
  };

  Subgraph.prototype.serialize = function () {
    var data = LiteGraph.LGraphNode.prototype.serialize.call(this);
    data.subgraph = this.subgraph.serialize();
    return data;
  };
  //no need to define node.configure, the default method detects node.subgraph and passes the object to node.subgraph.configure()

  Subgraph.prototype.reassignSubgraphUUIDs = function (graph) {
    const idMap = { nodeIDs: {}, linkIDs: {} };

    for (const node of graph.nodes) {
      const oldID = node.id;
      const newID = LiteGraph.uuidv4();
      node.id = newID;

      if (idMap.nodeIDs[oldID] || idMap.nodeIDs[newID]) {
        throw new Error(
          `New/old node UUID wasn't unique in changed map! ${oldID} ${newID}`,
        );
      }

      idMap.nodeIDs[oldID] = newID;
      idMap.nodeIDs[newID] = oldID;
    }

    for (const link of graph.links) {
      const oldID = link[0];
      const newID = LiteGraph.uuidv4();
      link[0] = newID;

      if (idMap.linkIDs[oldID] || idMap.linkIDs[newID]) {
        throw new Error(
          `New/old link UUID wasn't unique in changed map! ${oldID} ${newID}`,
        );
      }

      idMap.linkIDs[oldID] = newID;
      idMap.linkIDs[newID] = oldID;

      const nodeFrom = link[1];
      const nodeTo = link[3];

      if (!idMap.nodeIDs[nodeFrom]) {
        throw new Error(`Old node UUID not found in mapping! ${nodeFrom}`);
      }

      link[1] = idMap.nodeIDs[nodeFrom];

      if (!idMap.nodeIDs[nodeTo]) {
        throw new Error(`Old node UUID not found in mapping! ${nodeTo}`);
      }

      link[3] = idMap.nodeIDs[nodeTo];
    }

    // Reconnect links
    for (const node of graph.nodes) {
      if (node.inputs) {
        for (const input of node.inputs) {
          if (input.link) {
            input.link = idMap.linkIDs[input.link];
          }
        }
      }
      if (node.outputs) {
        for (const output of node.outputs) {
          if (output.links) {
            output.links = output.links.map((l) => idMap.linkIDs[l]);
          }
        }
      }
    }

    // Recurse!
    for (const node of graph.nodes) {
      if (node.type === 'graph/subgraph') {
        const merge = reassignGraphUUIDs(node.subgraph);
        idMap.nodeIDs.assign(merge.nodeIDs);
        idMap.linkIDs.assign(merge.linkIDs);
      }
    }
  };

  Subgraph.prototype.clone = function () {
    var node = LiteGraph.createNode(this.type);
    var data = this.serialize();

    if (LiteGraph.use_uuids) {
      // LGraph.serialize() seems to reuse objects in the original graph. But we
      // need to change node IDs here, so clone it first.
      const subgraph = LiteGraph.cloneObject(data.subgraph);

      this.reassignSubgraphUUIDs(subgraph);

      data.subgraph = subgraph;
    }

    delete data['id'];
    delete data['inputs'];
    delete data['outputs'];
    node.configure(data);
    return node;
  };

  Subgraph.prototype.buildFromNodes = function (nodes) {
    //clear all?
    //TODO

    //nodes that connect data between parent graph and subgraph
    var subgraph_inputs = [];
    var subgraph_outputs = [];

    //mark inner nodes
    var ids = {};
    var min_x = 0;
    var max_x = 0;
    for (var i = 0; i < nodes.length; ++i) {
      var node = nodes[i];
      ids[node.id] = node;
      min_x = Math.min(node.pos[0], min_x);
      max_x = Math.max(node.pos[0], min_x);
    }

    var last_input_y = 0;
    var last_output_y = 0;

    for (var i = 0; i < nodes.length; ++i) {
      var node = nodes[i];
      //check inputs
      if (node.inputs)
        for (var j = 0; j < node.inputs.length; ++j) {
          var input = node.inputs[j];
          if (!input || !input.link) continue;
          var link = node.graph.links[input.link];
          if (!link) continue;
          if (ids[link.origin_id]) continue;
          //this.addInput(input.name,link.type);
          this.subgraph.addInput(input.name, link.type);
          /*
        var input_node = LiteGraph.createNode("graph/input");
        this.subgraph.add( input_node );
        input_node.pos = [min_x - 200, last_input_y ];
        last_input_y += 100;
        */
        }

      //check outputs
      if (node.outputs)
        for (var j = 0; j < node.outputs.length; ++j) {
          var output = node.outputs[j];
          if (!output || !output.links || !output.links.length) continue;
          var is_external = false;
          for (var k = 0; k < output.links.length; ++k) {
            var link = node.graph.links[output.links[k]];
            if (!link) continue;
            if (ids[link.target_id]) continue;
            is_external = true;
            break;
          }
          if (!is_external) continue;
          //this.addOutput(output.name,output.type);
          /*
        var output_node = LiteGraph.createNode("graph/output");
        this.subgraph.add( output_node );
        output_node.pos = [max_x + 50, last_output_y ];
        last_output_y += 100;
        */
        }
    }

    //detect inputs and outputs
    //split every connection in two data_connection nodes
    //keep track of internal connections
    //connect external connections

    //clone nodes inside subgraph and try to reconnect them

    //connect edge subgraph nodes to extarnal connections nodes
  };

  LiteGraph.Subgraph = Subgraph;
  LiteGraph.registerNodeType('graph/subgraph', Subgraph);

  //Input for a subgraph
  function GraphInput() {
    this.addOutput('', 'number');

    this.name_in_graph = '';
    this.properties = {
      name: '',
      type: 'number',
      value: 0,
    };

    var that = this;

    this.name_widget = this.addWidget(
      'text',
      'Name',
      this.properties.name,
      function (v) {
        if (!v) {
          return;
        }
        that.setProperty('name', v);
      },
    );
    this.type_widget = this.addWidget(
      'text',
      'Type',
      this.properties.type,
      function (v) {
        that.setProperty('type', v);
      },
    );

    this.value_widget = this.addWidget(
      'number',
      'Value',
      this.properties.value,
      function (v) {
        that.setProperty('value', v);
      },
    );

    this.widgets_up = true;
    this.size = [180, 90];
  }

  GraphInput.title = 'Input';
  GraphInput.desc = 'Input of the graph';

  GraphInput.prototype.onConfigure = function () {
    this.updateType();
  };

  //ensures the type in the node output and the type in the associated graph input are the same
  GraphInput.prototype.updateType = function () {
    var type = this.properties.type;
    this.type_widget.value = type;

    //update output
    if (this.outputs[0].type != type) {
      if (!LiteGraph.isValidConnection(this.outputs[0].type, type))
        this.disconnectOutput(0);
      this.outputs[0].type = type;
    }

    //update widget
    if (type == 'number') {
      this.value_widget.type = 'number';
      this.value_widget.value = 0;
    } else if (type == 'boolean') {
      this.value_widget.type = 'toggle';
      this.value_widget.value = true;
    } else if (type == 'string') {
      this.value_widget.type = 'text';
      this.value_widget.value = '';
    } else {
      this.value_widget.type = null;
      this.value_widget.value = null;
    }
    this.properties.value = this.value_widget.value;

    //update graph
    if (this.graph && this.name_in_graph) {
      this.graph.changeInputType(this.name_in_graph, type);
    }
  };

  //this is executed AFTER the property has changed
  GraphInput.prototype.onPropertyChanged = function (name, v) {
    if (name == 'name') {
      if (v == '' || v == this.name_in_graph || v == 'enabled') {
        return false;
      }
      if (this.graph) {
        if (this.name_in_graph) {
          //already added
          this.graph.renameInput(this.name_in_graph, v);
        } else {
          this.graph.addInput(v, this.properties.type);
        }
      } //what if not?!
      this.name_widget.value = v;
      this.name_in_graph = v;
    } else if (name == 'type') {
      this.updateType();
    } else if (name == 'value') {
    }
  };

  GraphInput.prototype.getTitle = function () {
    if (this.flags.collapsed) {
      return this.properties.name;
    }
    return this.title;
  };

  GraphInput.prototype.onAction = function (action, param) {
    if (this.properties.type == LiteGraph.EVENT) {
      this.triggerSlot(0, param);
    }
  };

  GraphInput.prototype.onExecute = function () {
    var name = this.properties.name;
    //read from global input
    var data = this.graph.inputs[name];
    if (!data) {
      this.setOutputData(0, this.properties.value);
      return;
    }

    this.setOutputData(
      0,
      data.value !== undefined ? data.value : this.properties.value,
    );
  };

  GraphInput.prototype.onRemoved = function () {
    if (this.name_in_graph) {
      this.graph.removeInput(this.name_in_graph);
    }
  };

  LiteGraph.GraphInput = GraphInput;
  LiteGraph.registerNodeType('graph/input', GraphInput);

  //Output for a subgraph
  function GraphOutput() {
    this.addInput('', '');

    this.name_in_graph = '';
    this.properties = { name: '', type: '' };
    var that = this;

    // Object.defineProperty(this.properties, "name", {
    //     get: function() {
    //         return that.name_in_graph;
    //     },
    //     set: function(v) {
    //         if (v == "" || v == that.name_in_graph) {
    //             return;
    //         }
    //         if (that.name_in_graph) {
    //             //already added
    //             that.graph.renameOutput(that.name_in_graph, v);
    //         } else {
    //             that.graph.addOutput(v, that.properties.type);
    //         }
    //         that.name_widget.value = v;
    //         that.name_in_graph = v;
    //     },
    //     enumerable: true
    // });

    // Object.defineProperty(this.properties, "type", {
    //     get: function() {
    //         return that.inputs[0].type;
    //     },
    //     set: function(v) {
    //         if (v == "action" || v == "event") {
    //             v = LiteGraph.ACTION;
    //         }
    //         if (!LiteGraph.isValidConnection(that.inputs[0].type,v))
    // 			that.disconnectInput(0);
    //         that.inputs[0].type = v;
    //         if (that.name_in_graph) {
    //             //already added
    //             that.graph.changeOutputType(
    //                 that.name_in_graph,
    //                 that.inputs[0].type
    //             );
    //         }
    //         that.type_widget.value = v || "";
    //     },
    //     enumerable: true
    // });

    this.name_widget = this.addWidget(
      'text',
      'Name',
      this.properties.name,
      'name',
    );
    this.type_widget = this.addWidget(
      'text',
      'Type',
      this.properties.type,
      'type',
    );
    this.widgets_up = true;
    this.size = [180, 60];
  }

  GraphOutput.title = 'Output';
  GraphOutput.desc = 'Output of the graph';

  GraphOutput.prototype.onPropertyChanged = function (name, v) {
    if (name == 'name') {
      if (v == '' || v == this.name_in_graph || v == 'enabled') {
        return false;
      }
      if (this.graph) {
        if (this.name_in_graph) {
          //already added
          this.graph.renameOutput(this.name_in_graph, v);
        } else {
          this.graph.addOutput(v, this.properties.type);
        }
      } //what if not?!
      this.name_widget.value = v;
      this.name_in_graph = v;
    } else if (name == 'type') {
      this.updateType();
    } else if (name == 'value') {
    }
  };

  GraphOutput.prototype.updateType = function () {
    var type = this.properties.type;
    if (this.type_widget) this.type_widget.value = type;

    //update output
    if (this.inputs[0].type != type) {
      if (type == 'action' || type == 'event') type = LiteGraph.EVENT;
      if (!LiteGraph.isValidConnection(this.inputs[0].type, type))
        this.disconnectInput(0);
      this.inputs[0].type = type;
    }

    //update graph
    if (this.graph && this.name_in_graph) {
      this.graph.changeOutputType(this.name_in_graph, type);
    }
  };

  GraphOutput.prototype.onExecute = function () {
    this._value = this.getInputData(0);
    this.graph.setOutputData(this.properties.name, this._value);
  };

  GraphOutput.prototype.onAction = function (action, param) {
    if (this.properties.type == LiteGraph.ACTION) {
      this.graph.trigger(this.properties.name, param);
    }
  };

  GraphOutput.prototype.onRemoved = function () {
    if (this.name_in_graph) {
      this.graph.removeOutput(this.name_in_graph);
    }
  };

  GraphOutput.prototype.getTitle = function () {
    if (this.flags.collapsed) {
      return this.properties.name;
    }
    return this.title;
  };

  LiteGraph.GraphOutput = GraphOutput;
  LiteGraph.registerNodeType('graph/output', GraphOutput);

  //Constant
  function ConstantNumber() {
    this.addOutput('value', 'number');
    this.addProperty('value', 1.0);
    this.widget = this.addWidget('number', 'value', 1, 'value');
    this.widgets_up = true;
    this.size = [180, 30];
  }

  ConstantNumber.title = 'Const Number';
  ConstantNumber.desc = 'Constant number';

  ConstantNumber.prototype.onExecute = function () {
    this.setOutputData(0, parseFloat(this.properties['value']));
  };

  ConstantNumber.prototype.getTitle = function () {
    if (this.flags.collapsed) {
      return this.properties.value;
    }
    return this.title;
  };

  ConstantNumber.prototype.setValue = function (v) {
    this.setProperty('value', v);
  };

  ConstantNumber.prototype.onDrawBackground = function (ctx) {
    //show the current value
    this.outputs[0].label = this.properties['value'].toFixed(3);
  };

  LiteGraph.registerNodeType('basic/const', ConstantNumber);

  function ConstantBoolean() {
    this.addOutput('bool', 'boolean');
    this.addProperty('value', true);
    this.widget = this.addWidget('toggle', 'value', true, 'value');
    this.serialize_widgets = true;
    this.widgets_up = true;
    this.size = [140, 30];
  }

  ConstantBoolean.title = 'Const Boolean';
  ConstantBoolean.desc = 'Constant boolean';
  ConstantBoolean.prototype.getTitle = ConstantNumber.prototype.getTitle;

  ConstantBoolean.prototype.onExecute = function () {
    this.setOutputData(0, this.properties['value']);
  };

  ConstantBoolean.prototype.setValue = ConstantNumber.prototype.setValue;

  ConstantBoolean.prototype.onGetInputs = function () {
    return [['toggle', LiteGraph.ACTION]];
  };

  ConstantBoolean.prototype.onAction = function (action) {
    this.setValue(!this.properties.value);
  };

  LiteGraph.registerNodeType('basic/boolean', ConstantBoolean);

  function ConstantString() {
    this.addOutput('string', 'string');
    this.addProperty('value', '');
    this.widget = this.addWidget('text', 'value', '', 'value'); //link to property value
    this.widgets_up = true;
    this.size = [180, 30];
  }

  ConstantString.title = 'Const String';
  ConstantString.desc = 'Constant string';

  ConstantString.prototype.getTitle = ConstantNumber.prototype.getTitle;

  ConstantString.prototype.onExecute = function () {
    this.setOutputData(0, this.properties['value']);
  };

  ConstantString.prototype.setValue = ConstantNumber.prototype.setValue;

  ConstantString.prototype.onDropFile = function (file) {
    var that = this;
    var reader = new FileReader();
    reader.onload = function (e) {
      that.setProperty('value', e.target.result);
    };
    reader.readAsText(file);
  };

  LiteGraph.registerNodeType('basic/string', ConstantString);

  function ConstantObject() {
    this.addOutput('obj', 'object');
    this.size = [120, 30];
    this._object = {};
  }

  ConstantObject.title = 'Const Object';
  ConstantObject.desc = 'Constant Object';

  ConstantObject.prototype.onExecute = function () {
    this.setOutputData(0, this._object);
  };

  LiteGraph.registerNodeType('basic/object', ConstantObject);

  function ConstantFile() {
    this.addInput('url', 'string');
    this.addOutput('file', 'string');
    this.addProperty('url', '');
    this.addProperty('type', 'text');
    this.widget = this.addWidget('text', 'url', '', 'url');
    this._data = null;
  }

  ConstantFile.title = 'Const File';
  ConstantFile.desc = 'Fetches a file from an url';
  ConstantFile['@type'] = {
    type: 'enum',
    values: ['text', 'arraybuffer', 'blob', 'json'],
  };

  ConstantFile.prototype.onPropertyChanged = function (name, value) {
    if (name == 'url') {
      if (value == null || value == '') this._data = null;
      else {
        this.fetchFile(value);
      }
    }
  };

  ConstantFile.prototype.onExecute = function () {
    var url = this.getInputData(0) || this.properties.url;
    if (url && (url != this._url || this._type != this.properties.type))
      this.fetchFile(url);
    this.setOutputData(0, this._data);
  };

  ConstantFile.prototype.setValue = ConstantNumber.prototype.setValue;

  ConstantFile.prototype.fetchFile = function (url) {
    var that = this;
    if (!url || url.constructor !== String) {
      that._data = null;
      that.boxcolor = null;
      return;
    }

    this._url = url;
    this._type = this.properties.type;
    if (url.substr(0, 4) == 'http' && LiteGraph.proxy) {
      url = LiteGraph.proxy + url.substr(url.indexOf(':') + 3);
    }
    fetch(url)
      .then(function (response) {
        if (!response.ok) throw new Error('File not found');

        if (that.properties.type == 'arraybuffer')
          return response.arrayBuffer();
        else if (that.properties.type == 'text') return response.text();
        else if (that.properties.type == 'json') return response.json();
        else if (that.properties.type == 'blob') return response.blob();
      })
      .then(function (data) {
        that._data = data;
        that.boxcolor = '#AEA';
      })
      .catch(function (error) {
        that._data = null;
        that.boxcolor = 'red';
        console.error('error fetching file:', url);
      });
  };

  ConstantFile.prototype.onDropFile = function (file) {
    var that = this;
    this._url = file.name;
    this._type = this.properties.type;
    this.properties.url = file.name;
    var reader = new FileReader();
    reader.onload = function (e) {
      that.boxcolor = '#AEA';
      var v = e.target.result;
      if (that.properties.type == 'json') v = JSON.parse(v);
      that._data = v;
    };
    if (that.properties.type == 'arraybuffer') reader.readAsArrayBuffer(file);
    else if (that.properties.type == 'text' || that.properties.type == 'json')
      reader.readAsText(file);
    else if (that.properties.type == 'blob')
      return reader.readAsBinaryString(file);
  };

  LiteGraph.registerNodeType('basic/file', ConstantFile);

  //to store json objects
  function JSONParse() {
    this.addInput('parse', LiteGraph.ACTION);
    this.addInput('json', 'string');
    this.addOutput('done', LiteGraph.EVENT);
    this.addOutput('object', 'object');
    this.widget = this.addWidget('button', 'parse', '', this.parse.bind(this));
    this._str = null;
    this._obj = null;
  }

  JSONParse.title = 'JSON Parse';
  JSONParse.desc = 'Parses JSON String into object';

  JSONParse.prototype.parse = function () {
    if (!this._str) return;

    try {
      this._str = this.getInputData(1);
      this._obj = JSON.parse(this._str);
      this.boxcolor = '#AEA';
      this.triggerSlot(0);
    } catch (err) {
      this.boxcolor = 'red';
    }
  };

  JSONParse.prototype.onExecute = function () {
    this._str = this.getInputData(1);
    this.setOutputData(1, this._obj);
  };

  JSONParse.prototype.onAction = function (name) {
    if (name == 'parse') this.parse();
  };

  LiteGraph.registerNodeType('basic/jsonparse', JSONParse);

  //to store json objects
  function ConstantData() {
    this.addOutput('data', 'object');
    this.addProperty('value', '');
    this.widget = this.addWidget('text', 'json', '', 'value');
    this.widgets_up = true;
    this.size = [140, 30];
    this._value = null;
  }

  ConstantData.title = 'Const Data';
  ConstantData.desc = 'Constant Data';

  ConstantData.prototype.onPropertyChanged = function (name, value) {
    this.widget.value = value;
    if (value == null || value == '') {
      return;
    }

    try {
      this._value = JSON.parse(value);
      this.boxcolor = '#AEA';
    } catch (err) {
      this.boxcolor = 'red';
    }
  };

  ConstantData.prototype.onExecute = function () {
    this.setOutputData(0, this._value);
  };

  ConstantData.prototype.setValue = ConstantNumber.prototype.setValue;

  LiteGraph.registerNodeType('basic/data', ConstantData);

  //to store json objects
  function ConstantArray() {
    this._value = [];
    this.addInput('json', '');
    this.addOutput('arrayOut', 'array');
    this.addOutput('length', 'number');
    this.addProperty('value', '[]');
    this.widget = this.addWidget(
      'text',
      'array',
      this.properties.value,
      'value',
    );
    this.widgets_up = true;
    this.size = [140, 50];
  }

  ConstantArray.title = 'Const Array';
  ConstantArray.desc = 'Constant Array';

  ConstantArray.prototype.onPropertyChanged = function (name, value) {
    this.widget.value = value;
    if (value == null || value == '') {
      return;
    }

    try {
      if (value[0] != '[') this._value = JSON.parse('[' + value + ']');
      else this._value = JSON.parse(value);
      this.boxcolor = '#AEA';
    } catch (err) {
      this.boxcolor = 'red';
    }
  };

  ConstantArray.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v && v.length) {
      //clone
      if (!this._value) this._value = new Array();
      this._value.length = v.length;
      for (var i = 0; i < v.length; ++i) this._value[i] = v[i];
    }
    this.setOutputData(0, this._value);
    this.setOutputData(1, this._value ? this._value.length || 0 : 0);
  };

  ConstantArray.prototype.setValue = ConstantNumber.prototype.setValue;

  LiteGraph.registerNodeType('basic/array', ConstantArray);

  function SetArray() {
    this.addInput('arr', 'array');
    this.addInput('value', '');
    this.addOutput('arr', 'array');
    this.properties = { index: 0 };
    this.widget = this.addWidget(
      'number',
      'i',
      this.properties.index,
      'index',
      { precision: 0, step: 10, min: 0 },
    );
  }

  SetArray.title = 'Set Array';
  SetArray.desc = 'Sets index of array';

  SetArray.prototype.onExecute = function () {
    var arr = this.getInputData(0);
    if (!arr) return;
    var v = this.getInputData(1);
    if (v === undefined) return;
    if (this.properties.index) arr[Math.floor(this.properties.index)] = v;
    this.setOutputData(0, arr);
  };

  LiteGraph.registerNodeType('basic/set_array', SetArray);

  function ArrayElement() {
    this.addInput('array', 'array,table,string');
    this.addInput('index', 'number');
    this.addOutput('value', '');
    this.addProperty('index', 0);
  }

  ArrayElement.title = 'Array[i]';
  ArrayElement.desc = 'Returns an element from an array';

  ArrayElement.prototype.onExecute = function () {
    var array = this.getInputData(0);
    var index = this.getInputData(1);
    if (index == null) index = this.properties.index;
    if (array == null || index == null) return;
    this.setOutputData(0, array[Math.floor(Number(index))]);
  };

  LiteGraph.registerNodeType('basic/array[]', ArrayElement);

  function TableElement() {
    this.addInput('table', 'table');
    this.addInput('row', 'number');
    this.addInput('col', 'number');
    this.addOutput('value', '');
    this.addProperty('row', 0);
    this.addProperty('column', 0);
  }

  TableElement.title = 'Table[row][col]';
  TableElement.desc = 'Returns an element from a table';

  TableElement.prototype.onExecute = function () {
    var table = this.getInputData(0);
    var row = this.getInputData(1);
    var col = this.getInputData(2);
    if (row == null) row = this.properties.row;
    if (col == null) col = this.properties.column;
    if (table == null || row == null || col == null) return;
    var row = table[Math.floor(Number(row))];
    if (row) this.setOutputData(0, row[Math.floor(Number(col))]);
    else this.setOutputData(0, null);
  };

  LiteGraph.registerNodeType('basic/table[][]', TableElement);

  function ObjectProperty() {
    this.addInput('obj', 'object');
    this.addOutput('property', 0);
    this.addProperty('value', 0);
    this.widget = this.addWidget('text', 'prop.', '', this.setValue.bind(this));
    this.widgets_up = true;
    this.size = [140, 30];
    this._value = null;
  }

  ObjectProperty.title = 'Object property';
  ObjectProperty.desc = 'Outputs the property of an object';

  ObjectProperty.prototype.setValue = function (v) {
    this.properties.value = v;
    this.widget.value = v;
  };

  ObjectProperty.prototype.getTitle = function () {
    if (this.flags.collapsed) {
      return 'in.' + this.properties.value;
    }
    return this.title;
  };

  ObjectProperty.prototype.onPropertyChanged = function (name, value) {
    this.widget.value = value;
  };

  ObjectProperty.prototype.onExecute = function () {
    var data = this.getInputData(0);
    if (data != null) {
      this.setOutputData(0, data[this.properties.value]);
    }
  };

  LiteGraph.registerNodeType('basic/object_property', ObjectProperty);

  function ObjectKeys() {
    this.addInput('obj', '');
    this.addOutput('keys', 'array');
    this.size = [140, 30];
  }

  ObjectKeys.title = 'Object keys';
  ObjectKeys.desc = 'Outputs an array with the keys of an object';

  ObjectKeys.prototype.onExecute = function () {
    var data = this.getInputData(0);
    if (data != null) {
      this.setOutputData(0, Object.keys(data));
    }
  };

  LiteGraph.registerNodeType('basic/object_keys', ObjectKeys);

  function SetObject() {
    this.addInput('obj', '');
    this.addInput('value', '');
    this.addOutput('obj', '');
    this.properties = { property: '' };
    this.name_widget = this.addWidget(
      'text',
      'prop.',
      this.properties.property,
      'property',
    );
  }

  SetObject.title = 'Set Object';
  SetObject.desc = 'Adds propertiesrty to object';

  SetObject.prototype.onExecute = function () {
    var obj = this.getInputData(0);
    if (!obj) return;
    var v = this.getInputData(1);
    if (v === undefined) return;
    if (this.properties.property) obj[this.properties.property] = v;
    this.setOutputData(0, obj);
  };

  LiteGraph.registerNodeType('basic/set_object', SetObject);

  function MergeObjects() {
    this.addInput('A', 'object');
    this.addInput('B', 'object');
    this.addOutput('out', 'object');
    this._result = {};
    var that = this;
    this.addWidget('button', 'clear', '', function () {
      that._result = {};
    });
    this.size = this.computeSize();
  }

  MergeObjects.title = 'Merge Objects';
  MergeObjects.desc = 'Creates an object copying properties from others';

  MergeObjects.prototype.onExecute = function () {
    var A = this.getInputData(0);
    var B = this.getInputData(1);
    var C = this._result;
    if (A) for (var i in A) C[i] = A[i];
    if (B) for (var i in B) C[i] = B[i];
    this.setOutputData(0, C);
  };

  LiteGraph.registerNodeType('basic/merge_objects', MergeObjects);

  //Store as variable
  function Variable() {
    this.size = [60, 30];
    this.addInput('in');
    this.addOutput('out');
    this.properties = { varname: 'myname', container: Variable.LITEGRAPH };
    this.value = null;
  }

  Variable.title = 'Variable';
  Variable.desc = 'store/read variable value';

  Variable.LITEGRAPH = 0; //between all graphs
  Variable.GRAPH = 1; //only inside this graph
  Variable.GLOBALSCOPE = 2; //attached to Window

  Variable['@container'] = {
    type: 'enum',
    values: {
      litegraph: Variable.LITEGRAPH,
      graph: Variable.GRAPH,
      global: Variable.GLOBALSCOPE,
    },
  };

  Variable.prototype.onExecute = function () {
    var container = this.getContainer();

    if (this.isInputConnected(0)) {
      this.value = this.getInputData(0);
      container[this.properties.varname] = this.value;
      this.setOutputData(0, this.value);
      return;
    }

    this.setOutputData(0, container[this.properties.varname]);
  };

  Variable.prototype.getContainer = function () {
    switch (this.properties.container) {
      case Variable.GRAPH:
        if (this.graph) return this.graph.vars;
        return {};
        break;
      case Variable.GLOBALSCOPE:
        return global;
        break;
      case Variable.LITEGRAPH:
      default:
        return LiteGraph.Globals;
        break;
    }
  };

  Variable.prototype.getTitle = function () {
    return this.properties.varname;
  };

  LiteGraph.registerNodeType('basic/variable', Variable);

  function length(v) {
    if (v && v.length != null) return Number(v.length);
    return 0;
  }

  LiteGraph.wrapFunctionAsNode('basic/length', length, [''], 'number');

  function length(v) {
    if (v && v.length != null) return Number(v.length);
    return 0;
  }

  LiteGraph.wrapFunctionAsNode(
    'basic/not',
    function (a) {
      return !a;
    },
    [''],
    'boolean',
  );

  function DownloadData() {
    this.size = [60, 30];
    this.addInput('data', 0);
    this.addInput('download', LiteGraph.ACTION);
    this.properties = { filename: 'data.json' };
    this.value = null;
    var that = this;
    this.addWidget('button', 'Download', '', function (v) {
      if (!that.value) return;
      that.downloadAsFile();
    });
  }

  DownloadData.title = 'Download';
  DownloadData.desc = 'Download some data';

  DownloadData.prototype.downloadAsFile = function () {
    if (this.value == null) return;

    var str = null;
    if (this.value.constructor === String) str = this.value;
    else str = JSON.stringify(this.value);

    var file = new Blob([str]);
    var url = URL.createObjectURL(file);
    var element = document.createElement('a');
    element.setAttribute('href', url);
    element.setAttribute('download', this.properties.filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    setTimeout(function () {
      URL.revokeObjectURL(url);
    }, 1000 * 60); //wait one minute to revoke url
  };

  DownloadData.prototype.onAction = function (action, param) {
    var that = this;
    setTimeout(function () {
      that.downloadAsFile();
    }, 100); //deferred to avoid blocking the renderer with the popup
  };

  DownloadData.prototype.onExecute = function () {
    if (this.inputs[0]) {
      this.value = this.getInputData(0);
    }
  };

  DownloadData.prototype.getTitle = function () {
    if (this.flags.collapsed) {
      return this.properties.filename;
    }
    return this.title;
  };

  LiteGraph.registerNodeType('basic/download', DownloadData);

  //Watch a value in the editor
  function Watch() {
    this.size = [60, 30];
    this.addInput('value', 0, { label: '' });
    this.value = 0;
  }

  Watch.title = 'Watch';
  Watch.desc = 'Show value of input';

  Watch.prototype.onExecute = function () {
    if (this.inputs[0]) {
      this.value = this.getInputData(0);
    }
  };

  Watch.prototype.getTitle = function () {
    if (this.flags.collapsed) {
      return this.inputs[0].label;
    }
    return this.title;
  };

  Watch.toString = function (o) {
    if (o == null) {
      return 'null';
    } else if (o.constructor === Number) {
      return o.toFixed(3);
    } else if (o.constructor === Array) {
      var str = '[';
      for (var i = 0; i < o.length; ++i) {
        str += Watch.toString(o[i]) + (i + 1 != o.length ? ',' : '');
      }
      str += ']';
      return str;
    } else {
      return String(o);
    }
  };

  Watch.prototype.onDrawBackground = function (ctx) {
    //show the current value
    this.inputs[0].label = Watch.toString(this.value);
  };

  LiteGraph.registerNodeType('basic/watch', Watch);

  //in case one type doesnt match other type but you want to connect them anyway
  function Cast() {
    this.addInput('in', 0);
    this.addOutput('out', 0);
    this.size = [40, 30];
  }

  Cast.title = 'Cast';
  Cast.desc = 'Allows to connect different types';

  Cast.prototype.onExecute = function () {
    this.setOutputData(0, this.getInputData(0));
  };

  LiteGraph.registerNodeType('basic/cast', Cast);

  //Show value inside the debug console
  function Console() {
    this.mode = LiteGraph.ON_EVENT;
    this.size = [80, 30];
    this.addProperty('msg', '');
    this.addInput('log', LiteGraph.EVENT);
    this.addInput('msg', 0);
  }

  Console.title = 'Console';
  Console.desc = 'Show value inside the console';

  Console.prototype.onAction = function (action, param) {
    // param is the action
    var msg = this.getInputData(1); //getInputDataByName("msg");
    //if (msg == null || typeof msg == "undefined") return;
    if (!msg) msg = this.properties.msg;
    if (!msg) msg = 'Event: ' + param; // msg is undefined if the slot is lost?
    if (action == 'log') {
      console.log(msg);
    } else if (action == 'warn') {
      console.warn(msg);
    } else if (action == 'error') {
      console.error(msg);
    }
  };

  Console.prototype.onExecute = function () {
    var msg = this.getInputData(1); //getInputDataByName("msg");
    if (!msg) msg = this.properties.msg;
    if (msg != null && typeof msg != 'undefined') {
      this.properties.msg = msg;
      console.log(msg);
    }
  };

  Console.prototype.onGetInputs = function () {
    return [
      ['log', LiteGraph.ACTION],
      ['warn', LiteGraph.ACTION],
      ['error', LiteGraph.ACTION],
    ];
  };

  LiteGraph.registerNodeType('basic/console', Console);

  //Show value inside the debug console
  function Alert() {
    this.mode = LiteGraph.ON_EVENT;
    this.addProperty('msg', '');
    this.addInput('', LiteGraph.EVENT);
    var that = this;
    this.widget = this.addWidget('text', 'Text', '', 'msg');
    this.widgets_up = true;
    this.size = [200, 30];
  }

  Alert.title = 'Alert';
  Alert.desc = 'Show an alert window';
  Alert.color = '#510';

  Alert.prototype.onConfigure = function (o) {
    this.widget.value = o.properties.msg;
  };

  Alert.prototype.onAction = function (action, param) {
    var msg = this.properties.msg;
    setTimeout(function () {
      alert(msg);
    }, 10);
  };

  LiteGraph.registerNodeType('basic/alert', Alert);

  //Execites simple code
  function NodeScript() {
    this.size = [60, 30];
    this.addProperty('onExecute', 'return A;');
    this.addInput('A', 0);
    this.addInput('B', 0);
    this.addOutput('out', 0);

    this._func = null;
    this.data = {};
  }

  NodeScript.prototype.onConfigure = function (o) {
    if (o.properties.onExecute && LiteGraph.allow_scripts)
      this.compileCode(o.properties.onExecute);
    else console.warn('Script not compiled, LiteGraph.allow_scripts is false');
  };

  NodeScript.title = 'Script';
  NodeScript.desc = 'executes a code (max 256 characters)';

  NodeScript.widgets_info = {
    onExecute: { type: 'code' },
  };

  NodeScript.prototype.onPropertyChanged = function (name, value) {
    if (name == 'onExecute' && LiteGraph.allow_scripts) this.compileCode(value);
    else console.warn('Script not compiled, LiteGraph.allow_scripts is false');
  };

  NodeScript.prototype.compileCode = function (code) {
    this._func = null;
    if (code.length > 256) {
      console.warn('Script too long, max 256 chars');
    } else {
      var code_low = code.toLowerCase();
      var forbidden_words = [
        'script',
        'body',
        'document',
        'eval',
        'nodescript',
        'function',
      ]; //bad security solution
      for (var i = 0; i < forbidden_words.length; ++i) {
        if (code_low.indexOf(forbidden_words[i]) != -1) {
          console.warn('invalid script');
          return;
        }
      }
      try {
        this._func = new Function('A', 'B', 'C', 'DATA', 'node', code);
      } catch (err) {
        console.error('Error parsing script');
        console.error(err);
      }
    }
  };

  NodeScript.prototype.onExecute = function () {
    if (!this._func) {
      return;
    }

    try {
      var A = this.getInputData(0);
      var B = this.getInputData(1);
      var C = this.getInputData(2);
      this.setOutputData(0, this._func(A, B, C, this.data, this));
    } catch (err) {
      console.error('Error in script');
      console.error(err);
    }
  };

  NodeScript.prototype.onGetOutputs = function () {
    return [['C', '']];
  };

  LiteGraph.registerNodeType('basic/script', NodeScript);

  function GenericCompare() {
    this.addInput('A', 0);
    this.addInput('B', 0);
    this.addOutput('true', 'boolean');
    this.addOutput('false', 'boolean');
    this.addProperty('A', 1);
    this.addProperty('B', 1);
    this.addProperty('OP', '==', 'enum', { values: GenericCompare.values });
    this.addWidget('combo', 'Op.', this.properties.OP, {
      property: 'OP',
      values: GenericCompare.values,
    });

    this.size = [80, 60];
  }

  GenericCompare.values = ['==', '!=']; //[">", "<", "==", "!=", "<=", ">=", "||", "&&" ];
  GenericCompare['@OP'] = {
    type: 'enum',
    title: 'operation',
    values: GenericCompare.values,
  };

  GenericCompare.title = 'Compare *';
  GenericCompare.desc = 'evaluates condition between A and B';

  GenericCompare.prototype.getTitle = function () {
    return '*A ' + this.properties.OP + ' *B';
  };

  GenericCompare.prototype.onExecute = function () {
    var A = this.getInputData(0);
    if (A === undefined) {
      A = this.properties.A;
    } else {
      this.properties.A = A;
    }

    var B = this.getInputData(1);
    if (B === undefined) {
      B = this.properties.B;
    } else {
      this.properties.B = B;
    }

    var result = false;
    if (typeof A == typeof B) {
      switch (this.properties.OP) {
        case '==':
        case '!=':
          // traverse both objects.. consider that this is not a true deep check! consider underscore or other library for thath :: _isEqual()
          result = true;
          switch (typeof A) {
            case 'object':
              var aProps = Object.getOwnPropertyNames(A);
              var bProps = Object.getOwnPropertyNames(B);
              if (aProps.length != bProps.length) {
                result = false;
                break;
              }
              for (var i = 0; i < aProps.length; i++) {
                var propName = aProps[i];
                if (A[propName] !== B[propName]) {
                  result = false;
                  break;
                }
              }
              break;
            default:
              result = A == B;
          }
          if (this.properties.OP == '!=') result = !result;
          break;
        /*case ">":
                  result = A > B;
                  break;
              case "<":
                  result = A < B;
                  break;
              case "<=":
                  result = A <= B;
                  break;
              case ">=":
                  result = A >= B;
                  break;
              case "||":
                  result = A || B;
                  break;
              case "&&":
                  result = A && B;
                  break;*/
      }
    }
    this.setOutputData(0, result);
    this.setOutputData(1, !result);
  };

  LiteGraph.registerNodeType('basic/CompareValues', GenericCompare);
})(this);

//event related nodes
(function (global) {
  var LiteGraph = global.LiteGraph;

  //Show value inside the debug console
  function LogEvent() {
    this.size = [60, 30];
    this.addInput('event', LiteGraph.ACTION);
  }

  LogEvent.title = 'Log Event';
  LogEvent.desc = 'Log event in console';

  LogEvent.prototype.onAction = function (action, param, options) {
    console.log(action, param);
  };

  LiteGraph.registerNodeType('events/log', LogEvent);

  //convert to Event if the value is true
  function TriggerEvent() {
    this.size = [60, 30];
    this.addInput('if', '');
    this.addOutput('true', LiteGraph.EVENT);
    this.addOutput('change', LiteGraph.EVENT);
    this.addOutput('false', LiteGraph.EVENT);
    this.properties = { only_on_change: true };
    this.prev = 0;
  }

  TriggerEvent.title = 'TriggerEvent';
  TriggerEvent.desc = 'Triggers event if input evaluates to true';

  TriggerEvent.prototype.onExecute = function (param, options) {
    var v = this.getInputData(0);
    var changed = v != this.prev;
    if (this.prev === 0) changed = false;
    var must_resend =
      (changed && this.properties.only_on_change) ||
      (!changed && !this.properties.only_on_change);
    if (v && must_resend) this.triggerSlot(0, param, null, options);
    if (!v && must_resend) this.triggerSlot(2, param, null, options);
    if (changed) this.triggerSlot(1, param, null, options);
    this.prev = v;
  };

  LiteGraph.registerNodeType('events/trigger', TriggerEvent);

  //Sequence of events
  function Sequence() {
    var that = this;
    this.addInput('', LiteGraph.ACTION);
    this.addInput('', LiteGraph.ACTION);
    this.addInput('', LiteGraph.ACTION);
    this.addOutput('', LiteGraph.EVENT);
    this.addOutput('', LiteGraph.EVENT);
    this.addOutput('', LiteGraph.EVENT);
    this.addWidget('button', '+', null, function () {
      that.addInput('', LiteGraph.ACTION);
      that.addOutput('', LiteGraph.EVENT);
    });
    this.size = [90, 70];
    this.flags = { horizontal: true, render_box: false };
  }

  Sequence.title = 'Sequence';
  Sequence.desc = 'Triggers a sequence of events when an event arrives';

  Sequence.prototype.getTitle = function () {
    return '';
  };

  Sequence.prototype.onAction = function (action, param, options) {
    if (this.outputs) {
      options = options || {};
      for (var i = 0; i < this.outputs.length; ++i) {
        var output = this.outputs[i];
        //needs more info about this...
        if (options.action_call)
          // CREATE A NEW ID FOR THE ACTION
          options.action_call = options.action_call + '_seq_' + i;
        else
          options.action_call =
            this.id +
            '_' +
            (action ? action : 'action') +
            '_seq_' +
            i +
            '_' +
            Math.floor(Math.random() * 9999);
        this.triggerSlot(i, param, null, options);
      }
    }
  };

  LiteGraph.registerNodeType('events/sequence', Sequence);

  //Sequence of events
  function WaitAll() {
    var that = this;
    this.addInput('', LiteGraph.ACTION);
    this.addInput('', LiteGraph.ACTION);
    this.addOutput('', LiteGraph.EVENT);
    this.addWidget('button', '+', null, function () {
      that.addInput('', LiteGraph.ACTION);
      that.size[0] = 90;
    });
    this.size = [90, 70];
    this.ready = [];
  }

  WaitAll.title = 'WaitAll';
  WaitAll.desc = 'Wait until all input events arrive then triggers output';

  WaitAll.prototype.getTitle = function () {
    return '';
  };

  WaitAll.prototype.onDrawBackground = function (ctx) {
    if (this.flags.collapsed) {
      return;
    }
    for (var i = 0; i < this.inputs.length; ++i) {
      var y = i * LiteGraph.NODE_SLOT_HEIGHT + 10;
      ctx.fillStyle = this.ready[i] ? '#AFB' : '#000';
      ctx.fillRect(20, y, 10, 10);
    }
  };

  WaitAll.prototype.onAction = function (action, param, options, slot_index) {
    if (slot_index == null) return;

    //check all
    this.ready.length = this.outputs.length;
    this.ready[slot_index] = true;
    for (var i = 0; i < this.ready.length; ++i) if (!this.ready[i]) return;
    //pass
    this.reset();
    this.triggerSlot(0);
  };

  WaitAll.prototype.reset = function () {
    this.ready.length = 0;
  };

  LiteGraph.registerNodeType('events/waitAll', WaitAll);

  //Sequencer for events
  function Stepper() {
    var that = this;
    this.properties = { index: 0 };
    this.addInput('index', 'number');
    this.addInput('step', LiteGraph.ACTION);
    this.addInput('reset', LiteGraph.ACTION);
    this.addOutput('index', 'number');
    this.addOutput('', LiteGraph.EVENT);
    this.addOutput('', LiteGraph.EVENT);
    this.addOutput('', LiteGraph.EVENT, { removable: true });
    this.addWidget('button', '+', null, function () {
      that.addOutput('', LiteGraph.EVENT, { removable: true });
    });
    this.size = [120, 120];
    this.flags = { render_box: false };
  }

  Stepper.title = 'Stepper';
  Stepper.desc = 'Trigger events sequentially when an tick arrives';

  Stepper.prototype.onDrawBackground = function (ctx) {
    if (this.flags.collapsed) {
      return;
    }
    var index = this.properties.index || 0;
    ctx.fillStyle = '#AFB';
    var w = this.size[0];
    var y = (index + 1) * LiteGraph.NODE_SLOT_HEIGHT + 4;
    ctx.beginPath();
    ctx.moveTo(w - 30, y);
    ctx.lineTo(w - 30, y + LiteGraph.NODE_SLOT_HEIGHT);
    ctx.lineTo(w - 15, y + LiteGraph.NODE_SLOT_HEIGHT * 0.5);
    ctx.fill();
  };

  Stepper.prototype.onExecute = function () {
    var index = this.getInputData(0);
    if (index != null) {
      index = Math.floor(index);
      index = clamp(index, 0, this.outputs ? this.outputs.length - 2 : 0);
      if (index != this.properties.index) {
        this.properties.index = index;
        this.triggerSlot(index + 1);
      }
    }

    this.setOutputData(0, this.properties.index);
  };

  Stepper.prototype.onAction = function (action, param) {
    if (action == 'reset') this.properties.index = 0;
    else if (action == 'step') {
      this.triggerSlot(this.properties.index + 1, param);
      var n = this.outputs ? this.outputs.length - 1 : 0;
      this.properties.index = (this.properties.index + 1) % n;
    }
  };

  LiteGraph.registerNodeType('events/stepper', Stepper);

  //Filter events
  function FilterEvent() {
    this.size = [60, 30];
    this.addInput('event', LiteGraph.ACTION);
    this.addOutput('event', LiteGraph.EVENT);
    this.properties = {
      equal_to: '',
      has_property: '',
      property_equal_to: '',
    };
  }

  FilterEvent.title = 'Filter Event';
  FilterEvent.desc = 'Blocks events that do not match the filter';

  FilterEvent.prototype.onAction = function (action, param, options) {
    if (param == null) {
      return;
    }

    if (this.properties.equal_to && this.properties.equal_to != param) {
      return;
    }

    if (this.properties.has_property) {
      var prop = param[this.properties.has_property];
      if (prop == null) {
        return;
      }

      if (
        this.properties.property_equal_to &&
        this.properties.property_equal_to != prop
      ) {
        return;
      }
    }

    this.triggerSlot(0, param, null, options);
  };

  LiteGraph.registerNodeType('events/filter', FilterEvent);

  function EventBranch() {
    this.addInput('in', LiteGraph.ACTION);
    this.addInput('cond', 'boolean');
    this.addOutput('true', LiteGraph.EVENT);
    this.addOutput('false', LiteGraph.EVENT);
    this.size = [120, 60];
    this._value = false;
  }

  EventBranch.title = 'Branch';
  EventBranch.desc =
    'If condition is true, outputs triggers true, otherwise false';

  EventBranch.prototype.onExecute = function () {
    this._value = this.getInputData(1);
  };

  EventBranch.prototype.onAction = function (action, param, options) {
    this._value = this.getInputData(1);
    this.triggerSlot(this._value ? 0 : 1, param, null, options);
  };

  LiteGraph.registerNodeType('events/branch', EventBranch);

  //Show value inside the debug console
  function EventCounter() {
    this.addInput('inc', LiteGraph.ACTION);
    this.addInput('dec', LiteGraph.ACTION);
    this.addInput('reset', LiteGraph.ACTION);
    this.addOutput('change', LiteGraph.EVENT);
    this.addOutput('num', 'number');
    this.addProperty('doCountExecution', false, 'boolean', {
      name: 'Count Executions',
    });
    this.addWidget(
      'toggle',
      'Count Exec.',
      this.properties.doCountExecution,
      'doCountExecution',
    );
    this.num = 0;
  }

  EventCounter.title = 'Counter';
  EventCounter.desc = 'Counts events';

  EventCounter.prototype.getTitle = function () {
    if (this.flags.collapsed) {
      return String(this.num);
    }
    return this.title;
  };

  EventCounter.prototype.onAction = function (action, param, options) {
    var v = this.num;
    if (action == 'inc') {
      this.num += 1;
    } else if (action == 'dec') {
      this.num -= 1;
    } else if (action == 'reset') {
      this.num = 0;
    }
    if (this.num != v) {
      this.trigger('change', this.num);
    }
  };

  EventCounter.prototype.onDrawBackground = function (ctx) {
    if (this.flags.collapsed) {
      return;
    }
    ctx.fillStyle = '#AAA';
    ctx.font = '20px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(this.num, this.size[0] * 0.5, this.size[1] * 0.5);
  };

  EventCounter.prototype.onExecute = function () {
    if (this.properties.doCountExecution) {
      this.num += 1;
    }
    this.setOutputData(1, this.num);
  };

  LiteGraph.registerNodeType('events/counter', EventCounter);

  //Show value inside the debug console
  function DelayEvent() {
    this.size = [60, 30];
    this.addProperty('time_in_ms', 1000);
    this.addInput('event', LiteGraph.ACTION);
    this.addOutput('on_time', LiteGraph.EVENT);

    this._pending = [];
  }

  DelayEvent.title = 'Delay';
  DelayEvent.desc = 'Delays one event';

  DelayEvent.prototype.onAction = function (action, param, options) {
    var time = this.properties.time_in_ms;
    if (time <= 0) {
      this.trigger(null, param, options);
    } else {
      this._pending.push([time, param]);
    }
  };

  DelayEvent.prototype.onExecute = function (param, options) {
    var dt = this.graph.elapsed_time * 1000; //in ms

    if (this.isInputConnected(1)) {
      this.properties.time_in_ms = this.getInputData(1);
    }

    for (var i = 0; i < this._pending.length; ++i) {
      var actionPass = this._pending[i];
      actionPass[0] -= dt;
      if (actionPass[0] > 0) {
        continue;
      }

      //remove
      this._pending.splice(i, 1);
      --i;

      //trigger
      this.trigger(null, actionPass[1], options);
    }
  };

  DelayEvent.prototype.onGetInputs = function () {
    return [
      ['event', LiteGraph.ACTION],
      ['time_in_ms', 'number'],
    ];
  };

  LiteGraph.registerNodeType('events/delay', DelayEvent);

  //Show value inside the debug console
  function TimerEvent() {
    this.addProperty('interval', 1000);
    this.addProperty('event', 'tick');
    this.addOutput('on_tick', LiteGraph.EVENT);
    this.time = 0;
    this.last_interval = 1000;
    this.triggered = false;
  }

  TimerEvent.title = 'Timer';
  TimerEvent.desc = 'Sends an event every N milliseconds';

  TimerEvent.prototype.onStart = function () {
    this.time = 0;
  };

  TimerEvent.prototype.getTitle = function () {
    return 'Timer: ' + this.last_interval.toString() + 'ms';
  };

  TimerEvent.on_color = '#AAA';
  TimerEvent.off_color = '#222';

  TimerEvent.prototype.onDrawBackground = function () {
    this.boxcolor = this.triggered ? TimerEvent.on_color : TimerEvent.off_color;
    this.triggered = false;
  };

  TimerEvent.prototype.onExecute = function () {
    var dt = this.graph.elapsed_time * 1000; //in ms

    var trigger = this.time == 0;

    this.time += dt;
    this.last_interval = Math.max(1, this.getInputOrProperty('interval') | 0);

    if (
      !trigger &&
      (this.time < this.last_interval || isNaN(this.last_interval))
    ) {
      if (this.inputs && this.inputs.length > 1 && this.inputs[1]) {
        this.setOutputData(1, false);
      }
      return;
    }

    this.triggered = true;
    this.time = this.time % this.last_interval;
    this.trigger('on_tick', this.properties.event);
    if (this.inputs && this.inputs.length > 1 && this.inputs[1]) {
      this.setOutputData(1, true);
    }
  };

  TimerEvent.prototype.onGetInputs = function () {
    return [['interval', 'number']];
  };

  TimerEvent.prototype.onGetOutputs = function () {
    return [['tick', 'boolean']];
  };

  LiteGraph.registerNodeType('events/timer', TimerEvent);

  function SemaphoreEvent() {
    this.addInput('go', LiteGraph.ACTION);
    this.addInput('green', LiteGraph.ACTION);
    this.addInput('red', LiteGraph.ACTION);
    this.addOutput('continue', LiteGraph.EVENT);
    this.addOutput('blocked', LiteGraph.EVENT);
    this.addOutput('is_green', 'boolean');
    this._ready = false;
    this.properties = {};
    var that = this;
    this.addWidget('button', 'reset', '', function () {
      that._ready = false;
    });
  }

  SemaphoreEvent.title = 'Semaphore Event';
  SemaphoreEvent.desc =
    'Until both events are not triggered, it doesnt continue.';

  SemaphoreEvent.prototype.onExecute = function () {
    this.setOutputData(1, this._ready);
    this.boxcolor = this._ready ? '#9F9' : '#FA5';
  };

  SemaphoreEvent.prototype.onAction = function (action, param) {
    if (action == 'go') this.triggerSlot(this._ready ? 0 : 1);
    else if (action == 'green') this._ready = true;
    else if (action == 'red') this._ready = false;
  };

  LiteGraph.registerNodeType('events/semaphore', SemaphoreEvent);

  function OnceEvent() {
    this.addInput('in', LiteGraph.ACTION);
    this.addInput('reset', LiteGraph.ACTION);
    this.addOutput('out', LiteGraph.EVENT);
    this._once = false;
    this.properties = {};
    var that = this;
    this.addWidget('button', 'reset', '', function () {
      that._once = false;
    });
  }

  OnceEvent.title = 'Once';
  OnceEvent.desc = 'Only passes an event once, then gets locked';

  OnceEvent.prototype.onAction = function (action, param) {
    if (action == 'in' && !this._once) {
      this._once = true;
      this.triggerSlot(0, param);
    } else if (action == 'reset') this._once = false;
  };

  LiteGraph.registerNodeType('events/once', OnceEvent);

  function DataStore() {
    this.addInput('data', 0);
    this.addInput('assign', LiteGraph.ACTION);
    this.addOutput('data', 0);
    this._last_value = null;
    this.properties = { data: null, serialize: true };
    var that = this;
    this.addWidget('button', 'store', '', function () {
      that.properties.data = that._last_value;
    });
  }

  DataStore.title = 'Data Store';
  DataStore.desc = 'Stores data and only changes when event is received';

  DataStore.prototype.onExecute = function () {
    this._last_value = this.getInputData(0);
    this.setOutputData(0, this.properties.data);
  };

  DataStore.prototype.onAction = function (action, param, options) {
    this.properties.data = this._last_value;
  };

  DataStore.prototype.onSerialize = function (o) {
    if (o.data == null) return;
    if (
      this.properties.serialize == false ||
      (o.data.constructor !== String &&
        o.data.constructor !== Number &&
        o.data.constructor !== Boolean &&
        o.data.constructor !== Array &&
        o.data.constructor !== Object)
    )
      o.data = null;
  };

  LiteGraph.registerNodeType('basic/data_store', DataStore);
})(this);

//widgets
(function (global) {
  var LiteGraph = global.LiteGraph;

  /* Button ****************/

  function WidgetButton() {
    this.addOutput('', LiteGraph.EVENT);
    this.addOutput('', 'boolean');
    this.addProperty('text', 'click me');
    this.addProperty('font_size', 30);
    this.addProperty('message', '');
    this.size = [164, 84];
    this.clicked = false;
  }

  WidgetButton.title = 'Button';
  WidgetButton.desc = 'Triggers an event';

  WidgetButton.font = 'Arial';
  WidgetButton.prototype.onDrawForeground = function (ctx) {
    if (this.flags.collapsed) {
      return;
    }
    var margin = 10;
    ctx.fillStyle = 'black';
    ctx.fillRect(
      margin + 1,
      margin + 1,
      this.size[0] - margin * 2,
      this.size[1] - margin * 2,
    );
    ctx.fillStyle = '#AAF';
    ctx.fillRect(
      margin - 1,
      margin - 1,
      this.size[0] - margin * 2,
      this.size[1] - margin * 2,
    );
    ctx.fillStyle = this.clicked ? 'white' : this.mouseOver ? '#668' : '#334';
    ctx.fillRect(
      margin,
      margin,
      this.size[0] - margin * 2,
      this.size[1] - margin * 2,
    );

    if (this.properties.text || this.properties.text === 0) {
      var font_size = this.properties.font_size || 30;
      ctx.textAlign = 'center';
      ctx.fillStyle = this.clicked ? 'black' : 'white';
      ctx.font = font_size + 'px ' + WidgetButton.font;
      ctx.fillText(
        this.properties.text,
        this.size[0] * 0.5,
        this.size[1] * 0.5 + font_size * 0.3,
      );
      ctx.textAlign = 'left';
    }
  };

  WidgetButton.prototype.onMouseDown = function (e, local_pos) {
    if (
      local_pos[0] > 1 &&
      local_pos[1] > 1 &&
      local_pos[0] < this.size[0] - 2 &&
      local_pos[1] < this.size[1] - 2
    ) {
      this.clicked = true;
      this.setOutputData(1, this.clicked);
      this.triggerSlot(0, this.properties.message);
      return true;
    }
  };

  WidgetButton.prototype.onExecute = function () {
    this.setOutputData(1, this.clicked);
  };

  WidgetButton.prototype.onMouseUp = function (e) {
    this.clicked = false;
  };

  LiteGraph.registerNodeType('widget/button', WidgetButton);

  function WidgetToggle() {
    this.addInput('', 'boolean');
    this.addInput('e', LiteGraph.ACTION);
    this.addOutput('v', 'boolean');
    this.addOutput('e', LiteGraph.EVENT);
    this.properties = { font: '', value: false };
    this.size = [160, 44];
  }

  WidgetToggle.title = 'Toggle';
  WidgetToggle.desc = 'Toggles between true or false';

  WidgetToggle.prototype.onDrawForeground = function (ctx) {
    if (this.flags.collapsed) {
      return;
    }

    var size = this.size[1] * 0.5;
    var margin = 0.25;
    var h = this.size[1] * 0.8;
    ctx.font = this.properties.font || (size * 0.8).toFixed(0) + 'px Arial';
    var w = ctx.measureText(this.title).width;
    var x = (this.size[0] - (w + size)) * 0.5;

    ctx.fillStyle = '#AAA';
    ctx.fillRect(x, h - size, size, size);

    ctx.fillStyle = this.properties.value ? '#AEF' : '#000';
    ctx.fillRect(
      x + size * margin,
      h - size + size * margin,
      size * (1 - margin * 2),
      size * (1 - margin * 2),
    );

    ctx.textAlign = 'left';
    ctx.fillStyle = '#AAA';
    ctx.fillText(this.title, size * 1.2 + x, h * 0.85);
    ctx.textAlign = 'left';
  };

  WidgetToggle.prototype.onAction = function (action) {
    this.properties.value = !this.properties.value;
    this.trigger('e', this.properties.value);
  };

  WidgetToggle.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v != null) {
      this.properties.value = v;
    }
    this.setOutputData(0, this.properties.value);
  };

  WidgetToggle.prototype.onMouseDown = function (e, local_pos) {
    if (
      local_pos[0] > 1 &&
      local_pos[1] > 1 &&
      local_pos[0] < this.size[0] - 2 &&
      local_pos[1] < this.size[1] - 2
    ) {
      this.properties.value = !this.properties.value;
      this.graph._version++;
      this.trigger('e', this.properties.value);
      return true;
    }
  };

  LiteGraph.registerNodeType('widget/toggle', WidgetToggle);

  /* Number ****************/

  function WidgetNumber() {
    this.addOutput('', 'number');
    this.size = [80, 60];
    this.properties = { min: -1000, max: 1000, value: 1, step: 1 };
    this.old_y = -1;
    this._remainder = 0;
    this._precision = 0;
    this.mouse_captured = false;
  }

  WidgetNumber.title = 'Number';
  WidgetNumber.desc = 'Widget to select number value';

  WidgetNumber.pixels_threshold = 10;
  WidgetNumber.markers_color = '#666';

  WidgetNumber.prototype.onDrawForeground = function (ctx) {
    var x = this.size[0] * 0.5;
    var h = this.size[1];
    if (h > 30) {
      ctx.fillStyle = WidgetNumber.markers_color;
      ctx.beginPath();
      ctx.moveTo(x, h * 0.1);
      ctx.lineTo(x + h * 0.1, h * 0.2);
      ctx.lineTo(x + h * -0.1, h * 0.2);
      ctx.fill();
      ctx.beginPath();
      ctx.moveTo(x, h * 0.9);
      ctx.lineTo(x + h * 0.1, h * 0.8);
      ctx.lineTo(x + h * -0.1, h * 0.8);
      ctx.fill();
      ctx.font = (h * 0.7).toFixed(1) + 'px Arial';
    } else {
      ctx.font = (h * 0.8).toFixed(1) + 'px Arial';
    }

    ctx.textAlign = 'center';
    ctx.font = (h * 0.7).toFixed(1) + 'px Arial';
    ctx.fillStyle = '#EEE';
    ctx.fillText(this.properties.value.toFixed(this._precision), x, h * 0.75);
  };

  WidgetNumber.prototype.onExecute = function () {
    this.setOutputData(0, this.properties.value);
  };

  WidgetNumber.prototype.onPropertyChanged = function (name, value) {
    var t = (this.properties.step + '').split('.');
    this._precision = t.length > 1 ? t[1].length : 0;
  };

  WidgetNumber.prototype.onMouseDown = function (e, pos) {
    if (pos[1] < 0) {
      return;
    }

    this.old_y = e.canvasY;
    this.captureInput(true);
    this.mouse_captured = true;

    return true;
  };

  WidgetNumber.prototype.onMouseMove = function (e) {
    if (!this.mouse_captured) {
      return;
    }

    var delta = this.old_y - e.canvasY;
    if (e.shiftKey) {
      delta *= 10;
    }
    if (e.metaKey || e.altKey) {
      delta *= 0.1;
    }
    this.old_y = e.canvasY;

    var steps = this._remainder + delta / WidgetNumber.pixels_threshold;
    this._remainder = steps % 1;
    steps = steps | 0;

    var v = clamp(
      this.properties.value + steps * this.properties.step,
      this.properties.min,
      this.properties.max,
    );
    this.properties.value = v;
    this.graph._version++;
    this.setDirtyCanvas(true);
  };

  WidgetNumber.prototype.onMouseUp = function (e, pos) {
    if (e.click_time < 200) {
      var steps = pos[1] > this.size[1] * 0.5 ? -1 : 1;
      this.properties.value = clamp(
        this.properties.value + steps * this.properties.step,
        this.properties.min,
        this.properties.max,
      );
      this.graph._version++;
      this.setDirtyCanvas(true);
    }

    if (this.mouse_captured) {
      this.mouse_captured = false;
      this.captureInput(false);
    }
  };

  LiteGraph.registerNodeType('widget/number', WidgetNumber);

  /* Combo ****************/

  function WidgetCombo() {
    this.addOutput('', 'string');
    this.addOutput('change', LiteGraph.EVENT);
    this.size = [80, 60];
    this.properties = { value: 'A', values: 'A;B;C' };
    this.old_y = -1;
    this.mouse_captured = false;
    this._values = this.properties.values.split(';');
    var that = this;
    this.widgets_up = true;
    this.widget = this.addWidget(
      'combo',
      '',
      this.properties.value,
      function (v) {
        that.properties.value = v;
        that.triggerSlot(1, v);
      },
      { property: 'value', values: this._values },
    );
  }

  WidgetCombo.title = 'Combo';
  WidgetCombo.desc = 'Widget to select from a list';

  WidgetCombo.prototype.onExecute = function () {
    this.setOutputData(0, this.properties.value);
  };

  WidgetCombo.prototype.onPropertyChanged = function (name, value) {
    if (name == 'values') {
      this._values = value.split(';');
      this.widget.options.values = this._values;
    } else if (name == 'value') {
      this.widget.value = value;
    }
  };

  LiteGraph.registerNodeType('widget/combo', WidgetCombo);

  /* Knob ****************/

  function WidgetKnob() {
    this.addOutput('', 'number');
    this.size = [64, 84];
    this.properties = {
      min: 0,
      max: 1,
      value: 0.5,
      color: '#7AF',
      precision: 2,
    };
    this.value = -1;
  }

  WidgetKnob.title = 'Knob';
  WidgetKnob.desc = 'Circular controller';
  WidgetKnob.size = [80, 100];

  WidgetKnob.prototype.onDrawForeground = function (ctx) {
    if (this.flags.collapsed) {
      return;
    }

    if (this.value == -1) {
      this.value =
        (this.properties.value - this.properties.min) /
        (this.properties.max - this.properties.min);
    }

    var center_x = this.size[0] * 0.5;
    var center_y = this.size[1] * 0.5;
    var radius = Math.min(this.size[0], this.size[1]) * 0.5 - 5;
    var w = Math.floor(radius * 0.05);

    ctx.globalAlpha = 1;
    ctx.save();
    ctx.translate(center_x, center_y);
    ctx.rotate(Math.PI * 0.75);

    //bg
    ctx.fillStyle = 'rgba(0,0,0,0.5)';
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, radius, 0, Math.PI * 1.5);
    ctx.fill();

    //value
    ctx.strokeStyle = 'black';
    ctx.fillStyle = this.properties.color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, radius - 4, 0, Math.PI * 1.5 * Math.max(0.01, this.value));
    ctx.closePath();
    ctx.fill();
    //ctx.stroke();
    ctx.lineWidth = 1;
    ctx.globalAlpha = 1;
    ctx.restore();

    //inner
    ctx.fillStyle = 'black';
    ctx.beginPath();
    ctx.arc(center_x, center_y, radius * 0.75, 0, Math.PI * 2, true);
    ctx.fill();

    //miniball
    ctx.fillStyle = this.mouseOver ? 'white' : this.properties.color;
    ctx.beginPath();
    var angle = this.value * Math.PI * 1.5 + Math.PI * 0.75;
    ctx.arc(
      center_x + Math.cos(angle) * radius * 0.65,
      center_y + Math.sin(angle) * radius * 0.65,
      radius * 0.05,
      0,
      Math.PI * 2,
      true,
    );
    ctx.fill();

    //text
    ctx.fillStyle = this.mouseOver ? 'white' : '#AAA';
    ctx.font = Math.floor(radius * 0.5) + 'px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(
      this.properties.value.toFixed(this.properties.precision),
      center_x,
      center_y + radius * 0.15,
    );
  };

  WidgetKnob.prototype.onExecute = function () {
    this.setOutputData(0, this.properties.value);
    this.boxcolor = LiteGraph.colorToString([
      this.value,
      this.value,
      this.value,
    ]);
  };

  WidgetKnob.prototype.onMouseDown = function (e) {
    this.center = [this.size[0] * 0.5, this.size[1] * 0.5 + 20];
    this.radius = this.size[0] * 0.5;
    if (
      e.canvasY - this.pos[1] < 20 ||
      LiteGraph.distance(
        [e.canvasX, e.canvasY],
        [this.pos[0] + this.center[0], this.pos[1] + this.center[1]],
      ) > this.radius
    ) {
      return false;
    }
    this.oldmouse = [e.canvasX - this.pos[0], e.canvasY - this.pos[1]];
    this.captureInput(true);
    return true;
  };

  WidgetKnob.prototype.onMouseMove = function (e) {
    if (!this.oldmouse) {
      return;
    }

    var m = [e.canvasX - this.pos[0], e.canvasY - this.pos[1]];

    var v = this.value;
    v -= (m[1] - this.oldmouse[1]) * 0.01;
    if (v > 1.0) {
      v = 1.0;
    } else if (v < 0.0) {
      v = 0.0;
    }
    this.value = v;
    this.properties.value =
      this.properties.min +
      (this.properties.max - this.properties.min) * this.value;
    this.oldmouse = m;
    this.setDirtyCanvas(true);
  };

  WidgetKnob.prototype.onMouseUp = function (e) {
    if (this.oldmouse) {
      this.oldmouse = null;
      this.captureInput(false);
    }
  };

  WidgetKnob.prototype.onPropertyChanged = function (name, value) {
    if (name == 'min' || name == 'max' || name == 'value') {
      this.properties[name] = parseFloat(value);
      return true; //block
    }
  };

  LiteGraph.registerNodeType('widget/knob', WidgetKnob);

  //Show value inside the debug console
  function WidgetSliderGUI() {
    this.addOutput('', 'number');
    this.properties = {
      value: 0.5,
      min: 0,
      max: 1,
      text: 'V',
    };
    var that = this;
    this.size = [140, 40];
    this.slider = this.addWidget(
      'slider',
      'V',
      this.properties.value,
      function (v) {
        that.properties.value = v;
      },
      this.properties,
    );
    this.widgets_up = true;
  }

  WidgetSliderGUI.title = 'Inner Slider';

  WidgetSliderGUI.prototype.onPropertyChanged = function (name, value) {
    if (name == 'value') {
      this.slider.value = value;
    }
  };

  WidgetSliderGUI.prototype.onExecute = function () {
    this.setOutputData(0, this.properties.value);
  };

  LiteGraph.registerNodeType('widget/internal_slider', WidgetSliderGUI);

  //Widget H SLIDER
  function WidgetHSlider() {
    this.size = [160, 26];
    this.addOutput('', 'number');
    this.properties = { color: '#7AF', min: 0, max: 1, value: 0.5 };
    this.value = -1;
  }

  WidgetHSlider.title = 'H.Slider';
  WidgetHSlider.desc = 'Linear slider controller';

  WidgetHSlider.prototype.onDrawForeground = function (ctx) {
    if (this.value == -1) {
      this.value =
        (this.properties.value - this.properties.min) /
        (this.properties.max - this.properties.min);
    }

    //border
    ctx.globalAlpha = 1;
    ctx.lineWidth = 1;
    ctx.fillStyle = '#000';
    ctx.fillRect(2, 2, this.size[0] - 4, this.size[1] - 4);

    ctx.fillStyle = this.properties.color;
    ctx.beginPath();
    ctx.rect(4, 4, (this.size[0] - 8) * this.value, this.size[1] - 8);
    ctx.fill();
  };

  WidgetHSlider.prototype.onExecute = function () {
    this.properties.value =
      this.properties.min +
      (this.properties.max - this.properties.min) * this.value;
    this.setOutputData(0, this.properties.value);
    this.boxcolor = LiteGraph.colorToString([
      this.value,
      this.value,
      this.value,
    ]);
  };

  WidgetHSlider.prototype.onMouseDown = function (e) {
    if (e.canvasY - this.pos[1] < 0) {
      return false;
    }

    this.oldmouse = [e.canvasX - this.pos[0], e.canvasY - this.pos[1]];
    this.captureInput(true);
    return true;
  };

  WidgetHSlider.prototype.onMouseMove = function (e) {
    if (!this.oldmouse) {
      return;
    }

    var m = [e.canvasX - this.pos[0], e.canvasY - this.pos[1]];

    var v = this.value;
    var delta = m[0] - this.oldmouse[0];
    v += delta / this.size[0];
    if (v > 1.0) {
      v = 1.0;
    } else if (v < 0.0) {
      v = 0.0;
    }

    this.value = v;

    this.oldmouse = m;
    this.setDirtyCanvas(true);
  };

  WidgetHSlider.prototype.onMouseUp = function (e) {
    this.oldmouse = null;
    this.captureInput(false);
  };

  WidgetHSlider.prototype.onMouseLeave = function (e) {
    //this.oldmouse = null;
  };

  LiteGraph.registerNodeType('widget/hslider', WidgetHSlider);

  function WidgetProgress() {
    this.size = [160, 26];
    this.addInput('', 'number');
    this.properties = { min: 0, max: 1, value: 0, color: '#AAF' };
  }

  WidgetProgress.title = 'Progress';
  WidgetProgress.desc = 'Shows data in linear progress';

  WidgetProgress.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v != undefined) {
      this.properties['value'] = v;
    }
  };

  WidgetProgress.prototype.onDrawForeground = function (ctx) {
    //border
    ctx.lineWidth = 1;
    ctx.fillStyle = this.properties.color;
    var v =
      (this.properties.value - this.properties.min) /
      (this.properties.max - this.properties.min);
    v = Math.min(1, v);
    v = Math.max(0, v);
    ctx.fillRect(2, 2, (this.size[0] - 4) * v, this.size[1] - 4);
  };

  LiteGraph.registerNodeType('widget/progress', WidgetProgress);

  function WidgetText() {
    this.addInputs('', 0);
    this.properties = {
      value: '...',
      font: 'Arial',
      fontsize: 18,
      color: '#AAA',
      align: 'left',
      glowSize: 0,
      decimals: 1,
    };
  }

  WidgetText.title = 'Text';
  WidgetText.desc = 'Shows the input value';
  WidgetText.widgets = [
    { name: 'resize', text: 'Resize box', type: 'button' },
    { name: 'led_text', text: 'LED', type: 'minibutton' },
    { name: 'normal_text', text: 'Normal', type: 'minibutton' },
  ];

  WidgetText.prototype.onDrawForeground = function (ctx) {
    //ctx.fillStyle="#000";
    //ctx.fillRect(0,0,100,60);
    ctx.fillStyle = this.properties['color'];
    var v = this.properties['value'];

    if (this.properties['glowSize']) {
      ctx.shadowColor = this.properties.color;
      ctx.shadowOffsetX = 0;
      ctx.shadowOffsetY = 0;
      ctx.shadowBlur = this.properties['glowSize'];
    } else {
      ctx.shadowColor = 'transparent';
    }

    var fontsize = this.properties['fontsize'];

    ctx.textAlign = this.properties['align'];
    ctx.font = fontsize.toString() + 'px ' + this.properties['font'];
    this.str =
      typeof v == 'number' ? v.toFixed(this.properties['decimals']) : v;

    if (typeof this.str == 'string') {
      var lines = this.str.replace(/[\r\n]/g, '\\n').split('\\n');
      for (var i = 0; i < lines.length; i++) {
        ctx.fillText(
          lines[i],
          this.properties['align'] == 'left' ? 15 : this.size[0] - 15,
          fontsize * -0.15 + fontsize * (parseInt(i) + 1),
        );
      }
    }

    ctx.shadowColor = 'transparent';
    this.last_ctx = ctx;
    ctx.textAlign = 'left';
  };

  WidgetText.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v != null) {
      this.properties['value'] = v;
    }
    //this.setDirtyCanvas(true);
  };

  WidgetText.prototype.resize = function () {
    if (!this.last_ctx) {
      return;
    }

    var lines = this.str.split('\\n');
    this.last_ctx.font =
      this.properties['fontsize'] + 'px ' + this.properties['font'];
    var max = 0;
    for (var i = 0; i < lines.length; i++) {
      var w = this.last_ctx.measureText(lines[i]).width;
      if (max < w) {
        max = w;
      }
    }
    this.size[0] = max + 20;
    this.size[1] = 4 + lines.length * this.properties['fontsize'];

    this.setDirtyCanvas(true);
  };

  WidgetText.prototype.onPropertyChanged = function (name, value) {
    this.properties[name] = value;
    this.str = typeof value == 'number' ? value.toFixed(3) : value;
    //this.resize();
    return true;
  };

  LiteGraph.registerNodeType('widget/text', WidgetText);

  function WidgetPanel() {
    this.size = [200, 100];
    this.properties = {
      borderColor: '#ffffff',
      bgcolorTop: '#f0f0f0',
      bgcolorBottom: '#e0e0e0',
      shadowSize: 2,
      borderRadius: 3,
    };
  }

  WidgetPanel.title = 'Panel';
  WidgetPanel.desc = 'Non interactive panel';
  WidgetPanel.widgets = [{ name: 'update', text: 'Update', type: 'button' }];

  WidgetPanel.prototype.createGradient = function (ctx) {
    if (
      this.properties['bgcolorTop'] == '' ||
      this.properties['bgcolorBottom'] == ''
    ) {
      this.lineargradient = 0;
      return;
    }

    this.lineargradient = ctx.createLinearGradient(0, 0, 0, this.size[1]);
    this.lineargradient.addColorStop(0, this.properties['bgcolorTop']);
    this.lineargradient.addColorStop(1, this.properties['bgcolorBottom']);
  };

  WidgetPanel.prototype.onDrawForeground = function (ctx) {
    if (this.flags.collapsed) {
      return;
    }

    if (this.lineargradient == null) {
      this.createGradient(ctx);
    }

    if (!this.lineargradient) {
      return;
    }

    ctx.lineWidth = 1;
    ctx.strokeStyle = this.properties['borderColor'];
    //ctx.fillStyle = "#ebebeb";
    ctx.fillStyle = this.lineargradient;

    if (this.properties['shadowSize']) {
      ctx.shadowColor = '#000';
      ctx.shadowOffsetX = 0;
      ctx.shadowOffsetY = 0;
      ctx.shadowBlur = this.properties['shadowSize'];
    } else {
      ctx.shadowColor = 'transparent';
    }

    ctx.roundRect(
      0,
      0,
      this.size[0] - 1,
      this.size[1] - 1,
      this.properties['shadowSize'],
    );
    ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.stroke();
  };

  LiteGraph.registerNodeType('widget/panel', WidgetPanel);
})(this);

(function (global) {
  var LiteGraph = global.LiteGraph;

  function GamepadInput() {
    this.addOutput('left_x_axis', 'number');
    this.addOutput('left_y_axis', 'number');
    this.addOutput('button_pressed', LiteGraph.EVENT);
    this.properties = { gamepad_index: 0, threshold: 0.1 };

    this._left_axis = new Float32Array(2);
    this._right_axis = new Float32Array(2);
    this._triggers = new Float32Array(2);
    this._previous_buttons = new Uint8Array(17);
    this._current_buttons = new Uint8Array(17);
  }

  GamepadInput.title = 'Gamepad';
  GamepadInput.desc = 'gets the input of the gamepad';

  GamepadInput.CENTER = 0;
  GamepadInput.LEFT = 1;
  GamepadInput.RIGHT = 2;
  GamepadInput.UP = 4;
  GamepadInput.DOWN = 8;

  GamepadInput.zero = new Float32Array(2);
  GamepadInput.buttons = [
    'a',
    'b',
    'x',
    'y',
    'lb',
    'rb',
    'lt',
    'rt',
    'back',
    'start',
    'ls',
    'rs',
    'home',
  ];

  GamepadInput.prototype.onExecute = function () {
    //get gamepad
    var gamepad = this.getGamepad();
    var threshold = this.properties.threshold || 0.0;

    if (gamepad) {
      this._left_axis[0] =
        Math.abs(gamepad.xbox.axes['lx']) > threshold
          ? gamepad.xbox.axes['lx']
          : 0;
      this._left_axis[1] =
        Math.abs(gamepad.xbox.axes['ly']) > threshold
          ? gamepad.xbox.axes['ly']
          : 0;
      this._right_axis[0] =
        Math.abs(gamepad.xbox.axes['rx']) > threshold
          ? gamepad.xbox.axes['rx']
          : 0;
      this._right_axis[1] =
        Math.abs(gamepad.xbox.axes['ry']) > threshold
          ? gamepad.xbox.axes['ry']
          : 0;
      this._triggers[0] =
        Math.abs(gamepad.xbox.axes['ltrigger']) > threshold
          ? gamepad.xbox.axes['ltrigger']
          : 0;
      this._triggers[1] =
        Math.abs(gamepad.xbox.axes['rtrigger']) > threshold
          ? gamepad.xbox.axes['rtrigger']
          : 0;
    }

    if (this.outputs) {
      for (var i = 0; i < this.outputs.length; i++) {
        var output = this.outputs[i];
        if (!output.links || !output.links.length) {
          continue;
        }
        var v = null;

        if (gamepad) {
          switch (output.name) {
            case 'left_axis':
              v = this._left_axis;
              break;
            case 'right_axis':
              v = this._right_axis;
              break;
            case 'left_x_axis':
              v = this._left_axis[0];
              break;
            case 'left_y_axis':
              v = this._left_axis[1];
              break;
            case 'right_x_axis':
              v = this._right_axis[0];
              break;
            case 'right_y_axis':
              v = this._right_axis[1];
              break;
            case 'trigger_left':
              v = this._triggers[0];
              break;
            case 'trigger_right':
              v = this._triggers[1];
              break;
            case 'a_button':
              v = gamepad.xbox.buttons['a'] ? 1 : 0;
              break;
            case 'b_button':
              v = gamepad.xbox.buttons['b'] ? 1 : 0;
              break;
            case 'x_button':
              v = gamepad.xbox.buttons['x'] ? 1 : 0;
              break;
            case 'y_button':
              v = gamepad.xbox.buttons['y'] ? 1 : 0;
              break;
            case 'lb_button':
              v = gamepad.xbox.buttons['lb'] ? 1 : 0;
              break;
            case 'rb_button':
              v = gamepad.xbox.buttons['rb'] ? 1 : 0;
              break;
            case 'ls_button':
              v = gamepad.xbox.buttons['ls'] ? 1 : 0;
              break;
            case 'rs_button':
              v = gamepad.xbox.buttons['rs'] ? 1 : 0;
              break;
            case 'hat_left':
              v = gamepad.xbox.hatmap & GamepadInput.LEFT;
              break;
            case 'hat_right':
              v = gamepad.xbox.hatmap & GamepadInput.RIGHT;
              break;
            case 'hat_up':
              v = gamepad.xbox.hatmap & GamepadInput.UP;
              break;
            case 'hat_down':
              v = gamepad.xbox.hatmap & GamepadInput.DOWN;
              break;
            case 'hat':
              v = gamepad.xbox.hatmap;
              break;
            case 'start_button':
              v = gamepad.xbox.buttons['start'] ? 1 : 0;
              break;
            case 'back_button':
              v = gamepad.xbox.buttons['back'] ? 1 : 0;
              break;
            case 'button_pressed':
              for (var j = 0; j < this._current_buttons.length; ++j) {
                if (this._current_buttons[j] && !this._previous_buttons[j]) {
                  this.triggerSlot(i, GamepadInput.buttons[j]);
                }
              }
              break;
            default:
              break;
          }
        } else {
          //if no gamepad is connected, output 0
          switch (output.name) {
            case 'button_pressed':
              break;
            case 'left_axis':
            case 'right_axis':
              v = GamepadInput.zero;
              break;
            default:
              v = 0;
          }
        }
        this.setOutputData(i, v);
      }
    }
  };

  GamepadInput.mapping = {
    a: 0,
    b: 1,
    x: 2,
    y: 3,
    lb: 4,
    rb: 5,
    lt: 6,
    rt: 7,
    back: 8,
    start: 9,
    ls: 10,
    rs: 11,
  };
  GamepadInput.mapping_array = [
    'a',
    'b',
    'x',
    'y',
    'lb',
    'rb',
    'lt',
    'rt',
    'back',
    'start',
    'ls',
    'rs',
  ];

  GamepadInput.prototype.getGamepad = function () {
    var getGamepads =
      navigator.getGamepads ||
      navigator.webkitGetGamepads ||
      navigator.mozGetGamepads;
    if (!getGamepads) {
      return null;
    }
    var gamepads = getGamepads.call(navigator);
    var gamepad = null;

    this._previous_buttons.set(this._current_buttons);

    //pick the first connected
    for (var i = this.properties.gamepad_index; i < 4; i++) {
      if (!gamepads[i]) {
        continue;
      }
      gamepad = gamepads[i];

      //xbox controller mapping
      var xbox = this.xbox_mapping;
      if (!xbox) {
        xbox = this.xbox_mapping = {
          axes: [],
          buttons: {},
          hat: '',
          hatmap: GamepadInput.CENTER,
        };
      }

      xbox.axes['lx'] = gamepad.axes[0];
      xbox.axes['ly'] = gamepad.axes[1];
      xbox.axes['rx'] = gamepad.axes[2];
      xbox.axes['ry'] = gamepad.axes[3];
      xbox.axes['ltrigger'] = gamepad.buttons[6].value;
      xbox.axes['rtrigger'] = gamepad.buttons[7].value;
      xbox.hat = '';
      xbox.hatmap = GamepadInput.CENTER;

      for (var j = 0; j < gamepad.buttons.length; j++) {
        this._current_buttons[j] = gamepad.buttons[j].pressed;

        if (j < 12) {
          xbox.buttons[GamepadInput.mapping_array[j]] =
            gamepad.buttons[j].pressed;
          if (gamepad.buttons[j].was_pressed)
            this.trigger(GamepadInput.mapping_array[j] + '_button_event');
        } //mapping of XBOX
        else
          switch (
            j //I use a switch to ensure that a player with another gamepad could play
          ) {
            case 12:
              if (gamepad.buttons[j].pressed) {
                xbox.hat += 'up';
                xbox.hatmap |= GamepadInput.UP;
              }
              break;
            case 13:
              if (gamepad.buttons[j].pressed) {
                xbox.hat += 'down';
                xbox.hatmap |= GamepadInput.DOWN;
              }
              break;
            case 14:
              if (gamepad.buttons[j].pressed) {
                xbox.hat += 'left';
                xbox.hatmap |= GamepadInput.LEFT;
              }
              break;
            case 15:
              if (gamepad.buttons[j].pressed) {
                xbox.hat += 'right';
                xbox.hatmap |= GamepadInput.RIGHT;
              }
              break;
            case 16:
              xbox.buttons['home'] = gamepad.buttons[j].pressed;
              break;
            default:
          }
      }
      gamepad.xbox = xbox;
      return gamepad;
    }
  };

  GamepadInput.prototype.onDrawBackground = function (ctx) {
    if (this.flags.collapsed) {
      return;
    }

    //render gamepad state?
    var la = this._left_axis;
    var ra = this._right_axis;
    ctx.strokeStyle = '#88A';
    ctx.strokeRect(
      (la[0] + 1) * 0.5 * this.size[0] - 4,
      (la[1] + 1) * 0.5 * this.size[1] - 4,
      8,
      8,
    );
    ctx.strokeStyle = '#8A8';
    ctx.strokeRect(
      (ra[0] + 1) * 0.5 * this.size[0] - 4,
      (ra[1] + 1) * 0.5 * this.size[1] - 4,
      8,
      8,
    );
    var h = this.size[1] / this._current_buttons.length;
    ctx.fillStyle = '#AEB';
    for (var i = 0; i < this._current_buttons.length; ++i) {
      if (this._current_buttons[i]) {
        ctx.fillRect(0, h * i, 6, h);
      }
    }
  };

  GamepadInput.prototype.onGetOutputs = function () {
    return [
      ['left_axis', 'vec2'],
      ['right_axis', 'vec2'],
      ['left_x_axis', 'number'],
      ['left_y_axis', 'number'],
      ['right_x_axis', 'number'],
      ['right_y_axis', 'number'],
      ['trigger_left', 'number'],
      ['trigger_right', 'number'],
      ['a_button', 'number'],
      ['b_button', 'number'],
      ['x_button', 'number'],
      ['y_button', 'number'],
      ['lb_button', 'number'],
      ['rb_button', 'number'],
      ['ls_button', 'number'],
      ['rs_button', 'number'],
      ['start_button', 'number'],
      ['back_button', 'number'],
      ['a_button_event', LiteGraph.EVENT],
      ['b_button_event', LiteGraph.EVENT],
      ['x_button_event', LiteGraph.EVENT],
      ['y_button_event', LiteGraph.EVENT],
      ['lb_button_event', LiteGraph.EVENT],
      ['rb_button_event', LiteGraph.EVENT],
      ['ls_button_event', LiteGraph.EVENT],
      ['rs_button_event', LiteGraph.EVENT],
      ['start_button_event', LiteGraph.EVENT],
      ['back_button_event', LiteGraph.EVENT],
      ['hat_left', 'number'],
      ['hat_right', 'number'],
      ['hat_up', 'number'],
      ['hat_down', 'number'],
      ['hat', 'number'],
      ['button_pressed', LiteGraph.EVENT],
    ];
  };

  LiteGraph.registerNodeType('input/gamepad', GamepadInput);
})(this);

(function (global) {
  var LiteGraph = global.LiteGraph;

  //Converter
  function Converter() {
    this.addInput('in', 0);
    this.addOutput('out', 0);
    this.size = [80, 30];
  }

  Converter.title = 'Converter';
  Converter.desc = 'type A to type B';

  Converter.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v == null) {
      return;
    }

    if (this.outputs) {
      for (var i = 0; i < this.outputs.length; i++) {
        var output = this.outputs[i];
        if (!output.links || !output.links.length) {
          continue;
        }

        var result = null;
        switch (output.name) {
          case 'number':
            result = v.length ? v[0] : parseFloat(v);
            break;
          case 'vec2':
          case 'vec3':
          case 'vec4':
            var result = null;
            var count = 1;
            switch (output.name) {
              case 'vec2':
                count = 2;
                break;
              case 'vec3':
                count = 3;
                break;
              case 'vec4':
                count = 4;
                break;
            }

            var result = new Float32Array(count);
            if (v.length) {
              for (var j = 0; j < v.length && j < result.length; j++) {
                result[j] = v[j];
              }
            } else {
              result[0] = parseFloat(v);
            }
            break;
        }
        this.setOutputData(i, result);
      }
    }
  };

  Converter.prototype.onGetOutputs = function () {
    return [
      ['number', 'number'],
      ['vec2', 'vec2'],
      ['vec3', 'vec3'],
      ['vec4', 'vec4'],
    ];
  };

  LiteGraph.registerNodeType('math/converter', Converter);

  //Bypass
  function Bypass() {
    this.addInput('in');
    this.addOutput('out');
    this.size = [80, 30];
  }

  Bypass.title = 'Bypass';
  Bypass.desc = 'removes the type';

  Bypass.prototype.onExecute = function () {
    var v = this.getInputData(0);
    this.setOutputData(0, v);
  };

  LiteGraph.registerNodeType('math/bypass', Bypass);

  function ToNumber() {
    this.addInput('in');
    this.addOutput('out');
  }

  ToNumber.title = 'to Number';
  ToNumber.desc = 'Cast to number';

  ToNumber.prototype.onExecute = function () {
    var v = this.getInputData(0);
    this.setOutputData(0, Number(v));
  };

  LiteGraph.registerNodeType('math/to_number', ToNumber);

  function MathRange() {
    this.addInput('in', 'number', { locked: true });
    this.addOutput('out', 'number', { locked: true });
    this.addOutput('clamped', 'number', { locked: true });

    this.addProperty('in', 0);
    this.addProperty('in_min', 0);
    this.addProperty('in_max', 1);
    this.addProperty('out_min', 0);
    this.addProperty('out_max', 1);

    this.size = [120, 50];
  }

  MathRange.title = 'Range';
  MathRange.desc = 'Convert a number from one range to another';

  MathRange.prototype.getTitle = function () {
    if (this.flags.collapsed) {
      return (this._last_v || 0).toFixed(2);
    }
    return this.title;
  };

  MathRange.prototype.onExecute = function () {
    if (this.inputs) {
      for (var i = 0; i < this.inputs.length; i++) {
        var input = this.inputs[i];
        var v = this.getInputData(i);
        if (v === undefined) {
          continue;
        }
        this.properties[input.name] = v;
      }
    }

    var v = this.properties['in'];
    if (v === undefined || v === null || v.constructor !== Number) {
      v = 0;
    }

    var in_min = this.properties.in_min;
    var in_max = this.properties.in_max;
    var out_min = this.properties.out_min;
    var out_max = this.properties.out_max;
    /*
  if( in_min > in_max )
  {
    in_min = in_max;
    in_max = this.properties.in_min;
  }
  if( out_min > out_max )
  {
    out_min = out_max;
    out_max = this.properties.out_min;
  }
  */

    this._last_v =
      ((v - in_min) / (in_max - in_min)) * (out_max - out_min) + out_min;
    this.setOutputData(0, this._last_v);
    this.setOutputData(1, clamp(this._last_v, out_min, out_max));
  };

  MathRange.prototype.onDrawBackground = function (ctx) {
    //show the current value
    if (this._last_v) {
      this.outputs[0].label = this._last_v.toFixed(3);
    } else {
      this.outputs[0].label = '?';
    }
  };

  MathRange.prototype.onGetInputs = function () {
    return [
      ['in_min', 'number'],
      ['in_max', 'number'],
      ['out_min', 'number'],
      ['out_max', 'number'],
    ];
  };

  LiteGraph.registerNodeType('math/range', MathRange);

  function MathRand() {
    this.addOutput('value', 'number');
    this.addProperty('min', 0);
    this.addProperty('max', 1);
    this.size = [80, 30];
  }

  MathRand.title = 'Rand';
  MathRand.desc = 'Random number';

  MathRand.prototype.onExecute = function () {
    if (this.inputs) {
      for (var i = 0; i < this.inputs.length; i++) {
        var input = this.inputs[i];
        var v = this.getInputData(i);
        if (v === undefined) {
          continue;
        }
        this.properties[input.name] = v;
      }
    }

    var min = this.properties.min;
    var max = this.properties.max;
    this._last_v = Math.random() * (max - min) + min;
    this.setOutputData(0, this._last_v);
  };

  MathRand.prototype.onDrawBackground = function (ctx) {
    //show the current value
    this.outputs[0].label = (this._last_v || 0).toFixed(3);
  };

  MathRand.prototype.onGetInputs = function () {
    return [
      ['min', 'number'],
      ['max', 'number'],
    ];
  };

  LiteGraph.registerNodeType('math/rand', MathRand);

  //basic continuous noise
  function MathNoise() {
    this.addInput('in', 'number');
    this.addOutput('out', 'number');
    this.addProperty('min', 0);
    this.addProperty('max', 1);
    this.addProperty('smooth', true);
    this.addProperty('seed', 0);
    this.addProperty('octaves', 1);
    this.addProperty('persistence', 0.8);
    this.addProperty('speed', 1);
    this.size = [90, 30];
  }

  MathNoise.title = 'Noise';
  MathNoise.desc = 'Random number with temporal continuity';
  MathNoise.data = null;

  MathNoise.getValue = function (f, smooth) {
    if (!MathNoise.data) {
      MathNoise.data = new Float32Array(1024);
      for (var i = 0; i < MathNoise.data.length; ++i) {
        MathNoise.data[i] = Math.random();
      }
    }
    f = f % 1024;
    if (f < 0) {
      f += 1024;
    }
    var f_min = Math.floor(f);
    var f = f - f_min;
    var r1 = MathNoise.data[f_min];
    var r2 = MathNoise.data[f_min == 1023 ? 0 : f_min + 1];
    if (smooth) {
      f = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
    }
    return r1 * (1 - f) + r2 * f;
  };

  MathNoise.prototype.onExecute = function () {
    var f = this.getInputData(0) || 0;
    var iterations = this.properties.octaves || 1;
    var r = 0;
    var amp = 1;
    var seed = this.properties.seed || 0;
    f += seed;
    var speed = this.properties.speed || 1;
    var total_amp = 0;
    for (var i = 0; i < iterations; ++i) {
      r +=
        MathNoise.getValue(f * (1 + i) * speed, this.properties.smooth) * amp;
      total_amp += amp;
      amp *= this.properties.persistence;
      if (amp < 0.001) break;
    }
    r /= total_amp;
    var min = this.properties.min;
    var max = this.properties.max;
    this._last_v = r * (max - min) + min;
    this.setOutputData(0, this._last_v);
  };

  MathNoise.prototype.onDrawBackground = function (ctx) {
    //show the current value
    this.outputs[0].label = (this._last_v || 0).toFixed(3);
  };

  LiteGraph.registerNodeType('math/noise', MathNoise);

  //generates spikes every random time
  function MathSpikes() {
    this.addOutput('out', 'number');
    this.addProperty('min_time', 1);
    this.addProperty('max_time', 2);
    this.addProperty('duration', 0.2);
    this.size = [90, 30];
    this._remaining_time = 0;
    this._blink_time = 0;
  }

  MathSpikes.title = 'Spikes';
  MathSpikes.desc = 'spike every random time';

  MathSpikes.prototype.onExecute = function () {
    var dt = this.graph.elapsed_time; //in secs

    this._remaining_time -= dt;
    this._blink_time -= dt;

    var v = 0;
    if (this._blink_time > 0) {
      var f = this._blink_time / this.properties.duration;
      v = 1 / (Math.pow(f * 8 - 4, 4) + 1);
    }

    if (this._remaining_time < 0) {
      this._remaining_time =
        Math.random() * (this.properties.max_time - this.properties.min_time) +
        this.properties.min_time;
      this._blink_time = this.properties.duration;
      this.boxcolor = '#FFF';
    } else {
      this.boxcolor = '#000';
    }
    this.setOutputData(0, v);
  };

  LiteGraph.registerNodeType('math/spikes', MathSpikes);

  //Math clamp
  function MathClamp() {
    this.addInput('in', 'number');
    this.addOutput('out', 'number');
    this.size = [80, 30];
    this.addProperty('min', 0);
    this.addProperty('max', 1);
  }

  MathClamp.title = 'Clamp';
  MathClamp.desc = 'Clamp number between min and max';
  //MathClamp.filter = "shader";

  MathClamp.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v == null) {
      return;
    }
    v = Math.max(this.properties.min, v);
    v = Math.min(this.properties.max, v);
    this.setOutputData(0, v);
  };

  MathClamp.prototype.getCode = function (lang) {
    var code = '';
    if (this.isInputConnected(0)) {
      code +=
        'clamp({{0}},' + this.properties.min + ',' + this.properties.max + ')';
    }
    return code;
  };

  LiteGraph.registerNodeType('math/clamp', MathClamp);

  //Math ABS
  function MathLerp() {
    this.properties = { f: 0.5 };
    this.addInput('A', 'number');
    this.addInput('B', 'number');

    this.addOutput('out', 'number');
  }

  MathLerp.title = 'Lerp';
  MathLerp.desc = 'Linear Interpolation';

  MathLerp.prototype.onExecute = function () {
    var v1 = this.getInputData(0);
    if (v1 == null) {
      v1 = 0;
    }
    var v2 = this.getInputData(1);
    if (v2 == null) {
      v2 = 0;
    }

    var f = this.properties.f;

    var _f = this.getInputData(2);
    if (_f !== undefined) {
      f = _f;
    }

    this.setOutputData(0, v1 * (1 - f) + v2 * f);
  };

  MathLerp.prototype.onGetInputs = function () {
    return [['f', 'number']];
  };

  LiteGraph.registerNodeType('math/lerp', MathLerp);

  //Math ABS
  function MathAbs() {
    this.addInput('in', 'number');
    this.addOutput('out', 'number');
    this.size = [80, 30];
  }

  MathAbs.title = 'Abs';
  MathAbs.desc = 'Absolute';

  MathAbs.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v == null) {
      return;
    }
    this.setOutputData(0, Math.abs(v));
  };

  LiteGraph.registerNodeType('math/abs', MathAbs);

  //Math Floor
  function MathFloor() {
    this.addInput('in', 'number');
    this.addOutput('out', 'number');
    this.size = [80, 30];
  }

  MathFloor.title = 'Floor';
  MathFloor.desc = 'Floor number to remove fractional part';

  MathFloor.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v == null) {
      return;
    }
    this.setOutputData(0, Math.floor(v));
  };

  LiteGraph.registerNodeType('math/floor', MathFloor);

  //Math frac
  function MathFrac() {
    this.addInput('in', 'number');
    this.addOutput('out', 'number');
    this.size = [80, 30];
  }

  MathFrac.title = 'Frac';
  MathFrac.desc = 'Returns fractional part';

  MathFrac.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v == null) {
      return;
    }
    this.setOutputData(0, v % 1);
  };

  LiteGraph.registerNodeType('math/frac', MathFrac);

  //Math Floor
  function MathSmoothStep() {
    this.addInput('in', 'number');
    this.addOutput('out', 'number');
    this.size = [80, 30];
    this.properties = { A: 0, B: 1 };
  }

  MathSmoothStep.title = 'Smoothstep';
  MathSmoothStep.desc = 'Smoothstep';

  MathSmoothStep.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v === undefined) {
      return;
    }

    var edge0 = this.properties.A;
    var edge1 = this.properties.B;

    // Scale, bias and saturate x to 0..1 range
    v = clamp((v - edge0) / (edge1 - edge0), 0.0, 1.0);
    // Evaluate polynomial
    v = v * v * (3 - 2 * v);

    this.setOutputData(0, v);
  };

  LiteGraph.registerNodeType('math/smoothstep', MathSmoothStep);

  //Math scale
  function MathScale() {
    this.addInput('in', 'number', { label: '' });
    this.addOutput('out', 'number', { label: '' });
    this.size = [80, 30];
    this.addProperty('factor', 1);
  }

  MathScale.title = 'Scale';
  MathScale.desc = 'v * factor';

  MathScale.prototype.onExecute = function () {
    var value = this.getInputData(0);
    if (value != null) {
      this.setOutputData(0, value * this.properties.factor);
    }
  };

  LiteGraph.registerNodeType('math/scale', MathScale);

  //Gate
  function Gate() {
    this.addInput('v', 'boolean');
    this.addInput('A');
    this.addInput('B');
    this.addOutput('out');
  }

  Gate.title = 'Gate';
  Gate.desc = 'if v is true, then outputs A, otherwise B';

  Gate.prototype.onExecute = function () {
    var v = this.getInputData(0);
    this.setOutputData(0, this.getInputData(v ? 1 : 2));
  };

  LiteGraph.registerNodeType('math/gate', Gate);

  //Math Average
  function MathAverageFilter() {
    this.addInput('in', 'number');
    this.addOutput('out', 'number');
    this.size = [80, 30];
    this.addProperty('samples', 10);
    this._values = new Float32Array(10);
    this._current = 0;
  }

  MathAverageFilter.title = 'Average';
  MathAverageFilter.desc = 'Average Filter';

  MathAverageFilter.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v == null) {
      v = 0;
    }

    var num_samples = this._values.length;

    this._values[this._current % num_samples] = v;
    this._current += 1;
    if (this._current > num_samples) {
      this._current = 0;
    }

    var avr = 0;
    for (var i = 0; i < num_samples; ++i) {
      avr += this._values[i];
    }

    this.setOutputData(0, avr / num_samples);
  };

  MathAverageFilter.prototype.onPropertyChanged = function (name, value) {
    if (value < 1) {
      value = 1;
    }
    this.properties.samples = Math.round(value);
    var old = this._values;

    this._values = new Float32Array(this.properties.samples);
    if (old.length <= this._values.length) {
      this._values.set(old);
    } else {
      this._values.set(old.subarray(0, this._values.length));
    }
  };

  LiteGraph.registerNodeType('math/average', MathAverageFilter);

  //Math
  function MathTendTo() {
    this.addInput('in', 'number');
    this.addOutput('out', 'number');
    this.addProperty('factor', 0.1);
    this.size = [80, 30];
    this._value = null;
  }

  MathTendTo.title = 'TendTo';
  MathTendTo.desc = 'moves the output value always closer to the input';

  MathTendTo.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v == null) {
      v = 0;
    }
    var f = this.properties.factor;
    if (this._value == null) {
      this._value = v;
    } else {
      this._value = this._value * (1 - f) + v * f;
    }
    this.setOutputData(0, this._value);
  };

  LiteGraph.registerNodeType('math/tendTo', MathTendTo);

  //Math operation
  function MathOperation() {
    this.addInput('A', 'number,array,object');
    this.addInput('B', 'number');
    this.addOutput('=', 'number');
    this.addProperty('A', 1);
    this.addProperty('B', 1);
    this.addProperty('OP', '+', 'enum', { values: MathOperation.values });
    this._func = MathOperation.funcs[this.properties.OP];
    this._result = []; //only used for arrays
  }

  MathOperation.values = ['+', '-', '*', '/', '%', '^', 'max', 'min'];
  MathOperation.funcs = {
    '+': function (A, B) {
      return A + B;
    },
    '-': function (A, B) {
      return A - B;
    },
    x: function (A, B) {
      return A * B;
    },
    X: function (A, B) {
      return A * B;
    },
    '*': function (A, B) {
      return A * B;
    },
    '/': function (A, B) {
      return A / B;
    },
    '%': function (A, B) {
      return A % B;
    },
    '^': function (A, B) {
      return Math.pow(A, B);
    },
    max: function (A, B) {
      return Math.max(A, B);
    },
    min: function (A, B) {
      return Math.min(A, B);
    },
  };

  MathOperation.title = 'Operation';
  MathOperation.desc = 'Easy math operators';
  MathOperation['@OP'] = {
    type: 'enum',
    title: 'operation',
    values: MathOperation.values,
  };
  MathOperation.size = [100, 60];

  MathOperation.prototype.getTitle = function () {
    if (this.properties.OP == 'max' || this.properties.OP == 'min')
      return this.properties.OP + '(A,B)';
    return 'A ' + this.properties.OP + ' B';
  };

  MathOperation.prototype.setValue = function (v) {
    if (typeof v == 'string') {
      v = parseFloat(v);
    }
    this.properties['value'] = v;
  };

  MathOperation.prototype.onPropertyChanged = function (name, value) {
    if (name != 'OP') return;
    this._func = MathOperation.funcs[this.properties.OP];
    if (!this._func) {
      console.warn('Unknown operation: ' + this.properties.OP);
      this._func = function (A) {
        return A;
      };
    }
  };

  MathOperation.prototype.onExecute = function () {
    var A = this.getInputData(0);
    var B = this.getInputData(1);
    if (A != null) {
      if (A.constructor === Number) this.properties['A'] = A;
    } else {
      A = this.properties['A'];
    }

    if (B != null) {
      this.properties['B'] = B;
    } else {
      B = this.properties['B'];
    }

    var func = MathOperation.funcs[this.properties.OP];

    var result;
    if (A.constructor === Number) {
      result = 0;
      result = func(A, B);
    } else if (A.constructor === Array) {
      result = this._result;
      result.length = A.length;
      for (var i = 0; i < A.length; ++i) result[i] = func(A[i], B);
    } else {
      result = {};
      for (var i in A) result[i] = func(A[i], B);
    }
    this.setOutputData(0, result);
  };

  MathOperation.prototype.onDrawBackground = function (ctx) {
    if (this.flags.collapsed) {
      return;
    }

    ctx.font = '40px Arial';
    ctx.fillStyle = '#666';
    ctx.textAlign = 'center';
    ctx.fillText(
      this.properties.OP,
      this.size[0] * 0.5,
      (this.size[1] + LiteGraph.NODE_TITLE_HEIGHT) * 0.5,
    );
    ctx.textAlign = 'left';
  };

  LiteGraph.registerNodeType('math/operation', MathOperation);

  LiteGraph.registerSearchboxExtra('math/operation', 'MAX', {
    properties: { OP: 'max' },
    title: 'MAX()',
  });

  LiteGraph.registerSearchboxExtra('math/operation', 'MIN', {
    properties: { OP: 'min' },
    title: 'MIN()',
  });

  //Math compare
  function MathCompare() {
    this.addInput('A', 'number');
    this.addInput('B', 'number');
    this.addOutput('A==B', 'boolean');
    this.addOutput('A!=B', 'boolean');
    this.addProperty('A', 0);
    this.addProperty('B', 0);
  }

  MathCompare.title = 'Compare';
  MathCompare.desc = 'compares between two values';

  MathCompare.prototype.onExecute = function () {
    var A = this.getInputData(0);
    var B = this.getInputData(1);
    if (A !== undefined) {
      this.properties['A'] = A;
    } else {
      A = this.properties['A'];
    }

    if (B !== undefined) {
      this.properties['B'] = B;
    } else {
      B = this.properties['B'];
    }

    for (var i = 0, l = this.outputs.length; i < l; ++i) {
      var output = this.outputs[i];
      if (!output.links || !output.links.length) {
        continue;
      }
      var value;
      switch (output.name) {
        case 'A==B':
          value = A == B;
          break;
        case 'A!=B':
          value = A != B;
          break;
        case 'A>B':
          value = A > B;
          break;
        case 'A<B':
          value = A < B;
          break;
        case 'A<=B':
          value = A <= B;
          break;
        case 'A>=B':
          value = A >= B;
          break;
      }
      this.setOutputData(i, value);
    }
  };

  MathCompare.prototype.onGetOutputs = function () {
    return [
      ['A==B', 'boolean'],
      ['A!=B', 'boolean'],
      ['A>B', 'boolean'],
      ['A<B', 'boolean'],
      ['A>=B', 'boolean'],
      ['A<=B', 'boolean'],
    ];
  };

  LiteGraph.registerNodeType('math/compare', MathCompare);

  LiteGraph.registerSearchboxExtra('math/compare', '==', {
    outputs: [['A==B', 'boolean']],
    title: 'A==B',
  });
  LiteGraph.registerSearchboxExtra('math/compare', '!=', {
    outputs: [['A!=B', 'boolean']],
    title: 'A!=B',
  });
  LiteGraph.registerSearchboxExtra('math/compare', '>', {
    outputs: [['A>B', 'boolean']],
    title: 'A>B',
  });
  LiteGraph.registerSearchboxExtra('math/compare', '<', {
    outputs: [['A<B', 'boolean']],
    title: 'A<B',
  });
  LiteGraph.registerSearchboxExtra('math/compare', '>=', {
    outputs: [['A>=B', 'boolean']],
    title: 'A>=B',
  });
  LiteGraph.registerSearchboxExtra('math/compare', '<=', {
    outputs: [['A<=B', 'boolean']],
    title: 'A<=B',
  });

  function MathCondition() {
    this.addInput('A', 'number');
    this.addInput('B', 'number');
    this.addOutput('true', 'boolean');
    this.addOutput('false', 'boolean');
    this.addProperty('A', 1);
    this.addProperty('B', 1);
    this.addProperty('OP', '>', 'enum', { values: MathCondition.values });
    this.addWidget('combo', 'Cond.', this.properties.OP, {
      property: 'OP',
      values: MathCondition.values,
    });

    this.size = [80, 60];
  }

  MathCondition.values = ['>', '<', '==', '!=', '<=', '>=', '||', '&&'];
  MathCondition['@OP'] = {
    type: 'enum',
    title: 'operation',
    values: MathCondition.values,
  };

  MathCondition.title = 'Condition';
  MathCondition.desc = 'evaluates condition between A and B';

  MathCondition.prototype.getTitle = function () {
    return 'A ' + this.properties.OP + ' B';
  };

  MathCondition.prototype.onExecute = function () {
    var A = this.getInputData(0);
    if (A === undefined) {
      A = this.properties.A;
    } else {
      this.properties.A = A;
    }

    var B = this.getInputData(1);
    if (B === undefined) {
      B = this.properties.B;
    } else {
      this.properties.B = B;
    }

    var result = true;
    switch (this.properties.OP) {
      case '>':
        result = A > B;
        break;
      case '<':
        result = A < B;
        break;
      case '==':
        result = A == B;
        break;
      case '!=':
        result = A != B;
        break;
      case '<=':
        result = A <= B;
        break;
      case '>=':
        result = A >= B;
        break;
      case '||':
        result = A || B;
        break;
      case '&&':
        result = A && B;
        break;
    }

    this.setOutputData(0, result);
    this.setOutputData(1, !result);
  };

  LiteGraph.registerNodeType('math/condition', MathCondition);

  function MathBranch() {
    this.addInput('in', 0);
    this.addInput('cond', 'boolean');
    this.addOutput('true', 0);
    this.addOutput('false', 0);
    this.size = [80, 60];
  }

  MathBranch.title = 'Branch';
  MathBranch.desc =
    'If condition is true, outputs IN in true, otherwise in false';

  MathBranch.prototype.onExecute = function () {
    var V = this.getInputData(0);
    var cond = this.getInputData(1);

    if (cond) {
      this.setOutputData(0, V);
      this.setOutputData(1, null);
    } else {
      this.setOutputData(0, null);
      this.setOutputData(1, V);
    }
  };

  LiteGraph.registerNodeType('math/branch', MathBranch);

  function MathAccumulate() {
    this.addInput('inc', 'number');
    this.addOutput('total', 'number');
    this.addProperty('increment', 1);
    this.addProperty('value', 0);
  }

  MathAccumulate.title = 'Accumulate';
  MathAccumulate.desc = 'Increments a value every time';

  MathAccumulate.prototype.onExecute = function () {
    if (this.properties.value === null) {
      this.properties.value = 0;
    }

    var inc = this.getInputData(0);
    if (inc !== null) {
      this.properties.value += inc;
    } else {
      this.properties.value += this.properties.increment;
    }
    this.setOutputData(0, this.properties.value);
  };

  LiteGraph.registerNodeType('math/accumulate', MathAccumulate);

  //Math Trigonometry
  function MathTrigonometry() {
    this.addInput('v', 'number');
    this.addOutput('sin', 'number');

    this.addProperty('amplitude', 1);
    this.addProperty('offset', 0);
    this.bgImageUrl = 'nodes/imgs/icon-sin.png';
  }

  MathTrigonometry.title = 'Trigonometry';
  MathTrigonometry.desc = 'Sin Cos Tan';
  //MathTrigonometry.filter = "shader";

  MathTrigonometry.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v == null) {
      v = 0;
    }
    var amplitude = this.properties['amplitude'];
    var slot = this.findInputSlot('amplitude');
    if (slot != -1) {
      amplitude = this.getInputData(slot);
    }
    var offset = this.properties['offset'];
    slot = this.findInputSlot('offset');
    if (slot != -1) {
      offset = this.getInputData(slot);
    }

    for (var i = 0, l = this.outputs.length; i < l; ++i) {
      var output = this.outputs[i];
      var value;
      switch (output.name) {
        case 'sin':
          value = Math.sin(v);
          break;
        case 'cos':
          value = Math.cos(v);
          break;
        case 'tan':
          value = Math.tan(v);
          break;
        case 'asin':
          value = Math.asin(v);
          break;
        case 'acos':
          value = Math.acos(v);
          break;
        case 'atan':
          value = Math.atan(v);
          break;
      }
      this.setOutputData(i, amplitude * value + offset);
    }
  };

  MathTrigonometry.prototype.onGetInputs = function () {
    return [
      ['v', 'number'],
      ['amplitude', 'number'],
      ['offset', 'number'],
    ];
  };

  MathTrigonometry.prototype.onGetOutputs = function () {
    return [
      ['sin', 'number'],
      ['cos', 'number'],
      ['tan', 'number'],
      ['asin', 'number'],
      ['acos', 'number'],
      ['atan', 'number'],
    ];
  };

  LiteGraph.registerNodeType('math/trigonometry', MathTrigonometry);

  LiteGraph.registerSearchboxExtra('math/trigonometry', 'SIN()', {
    outputs: [['sin', 'number']],
    title: 'SIN()',
  });
  LiteGraph.registerSearchboxExtra('math/trigonometry', 'COS()', {
    outputs: [['cos', 'number']],
    title: 'COS()',
  });
  LiteGraph.registerSearchboxExtra('math/trigonometry', 'TAN()', {
    outputs: [['tan', 'number']],
    title: 'TAN()',
  });

  //math library for safe math operations without eval
  function MathFormula() {
    this.addInput('x', 'number');
    this.addInput('y', 'number');
    this.addOutput('', 'number');
    this.properties = { x: 1.0, y: 1.0, formula: 'x+y' };
    this.code_widget = this.addWidget(
      'text',
      'F(x,y)',
      this.properties.formula,
      function (v, canvas, node) {
        node.properties.formula = v;
      },
    );
    this.addWidget('toggle', 'allow', LiteGraph.allow_scripts, function (v) {
      LiteGraph.allow_scripts = v;
    });
    this._func = null;
  }

  MathFormula.title = 'Formula';
  MathFormula.desc = 'Compute formula';
  MathFormula.size = [160, 100];

  MathAverageFilter.prototype.onPropertyChanged = function (name, value) {
    if (name == 'formula') {
      this.code_widget.value = value;
    }
  };

  MathFormula.prototype.onExecute = function () {
    if (!LiteGraph.allow_scripts) {
      return;
    }

    var x = this.getInputData(0);
    var y = this.getInputData(1);
    if (x != null) {
      this.properties['x'] = x;
    } else {
      x = this.properties['x'];
    }

    if (y != null) {
      this.properties['y'] = y;
    } else {
      y = this.properties['y'];
    }

    var f = this.properties['formula'];

    var value;
    try {
      if (!this._func || this._func_code != this.properties.formula) {
        this._func = new Function(
          'x',
          'y',
          'TIME',
          'return ' + this.properties.formula,
        );
        this._func_code = this.properties.formula;
      }
      value = this._func(x, y, this.graph.globaltime);
      this.boxcolor = null;
    } catch (err) {
      this.boxcolor = 'red';
    }
    this.setOutputData(0, value);
  };

  MathFormula.prototype.getTitle = function () {
    return this._func_code || 'Formula';
  };

  MathFormula.prototype.onDrawBackground = function () {
    var f = this.properties['formula'];
    if (this.outputs && this.outputs.length) {
      this.outputs[0].label = f;
    }
  };

  LiteGraph.registerNodeType('math/formula', MathFormula);

  function Math3DVec2ToXY() {
    this.addInput('vec2', 'vec2');
    this.addOutput('x', 'number');
    this.addOutput('y', 'number');
  }

  Math3DVec2ToXY.title = 'Vec2->XY';
  Math3DVec2ToXY.desc = 'vector 2 to components';

  Math3DVec2ToXY.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v == null) {
      return;
    }

    this.setOutputData(0, v[0]);
    this.setOutputData(1, v[1]);
  };

  LiteGraph.registerNodeType('math3d/vec2-to-xy', Math3DVec2ToXY);

  function Math3DXYToVec2() {
    this.addInputs([
      ['x', 'number'],
      ['y', 'number'],
    ]);
    this.addOutput('vec2', 'vec2');
    this.properties = { x: 0, y: 0 };
    this._data = new Float32Array(2);
  }

  Math3DXYToVec2.title = 'XY->Vec2';
  Math3DXYToVec2.desc = 'components to vector2';

  Math3DXYToVec2.prototype.onExecute = function () {
    var x = this.getInputData(0);
    if (x == null) {
      x = this.properties.x;
    }
    var y = this.getInputData(1);
    if (y == null) {
      y = this.properties.y;
    }

    var data = this._data;
    data[0] = x;
    data[1] = y;

    this.setOutputData(0, data);
  };

  LiteGraph.registerNodeType('math3d/xy-to-vec2', Math3DXYToVec2);

  function Math3DVec3ToXYZ() {
    this.addInput('vec3', 'vec3');
    this.addOutput('x', 'number');
    this.addOutput('y', 'number');
    this.addOutput('z', 'number');
  }

  Math3DVec3ToXYZ.title = 'Vec3->XYZ';
  Math3DVec3ToXYZ.desc = 'vector 3 to components';

  Math3DVec3ToXYZ.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v == null) {
      return;
    }

    this.setOutputData(0, v[0]);
    this.setOutputData(1, v[1]);
    this.setOutputData(2, v[2]);
  };

  LiteGraph.registerNodeType('math3d/vec3-to-xyz', Math3DVec3ToXYZ);

  function Math3DXYZToVec3() {
    this.addInputs([
      ['x', 'number'],
      ['y', 'number'],
      ['z', 'number'],
    ]);
    this.addOutput('vec3', 'vec3');
    this.properties = { x: 0, y: 0, z: 0 };
    this._data = new Float32Array(3);
  }

  Math3DXYZToVec3.title = 'XYZ->Vec3';
  Math3DXYZToVec3.desc = 'components to vector3';

  Math3DXYZToVec3.prototype.onExecute = function () {
    var x = this.getInputData(0);
    if (x == null) {
      x = this.properties.x;
    }
    var y = this.getInputData(1);
    if (y == null) {
      y = this.properties.y;
    }
    var z = this.getInputData(2);
    if (z == null) {
      z = this.properties.z;
    }

    var data = this._data;
    data[0] = x;
    data[1] = y;
    data[2] = z;

    this.setOutputData(0, data);
  };

  LiteGraph.registerNodeType('math3d/xyz-to-vec3', Math3DXYZToVec3);

  function Math3DVec4ToXYZW() {
    this.addInput('vec4', 'vec4');
    this.addOutput('x', 'number');
    this.addOutput('y', 'number');
    this.addOutput('z', 'number');
    this.addOutput('w', 'number');
  }

  Math3DVec4ToXYZW.title = 'Vec4->XYZW';
  Math3DVec4ToXYZW.desc = 'vector 4 to components';

  Math3DVec4ToXYZW.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v == null) {
      return;
    }

    this.setOutputData(0, v[0]);
    this.setOutputData(1, v[1]);
    this.setOutputData(2, v[2]);
    this.setOutputData(3, v[3]);
  };

  LiteGraph.registerNodeType('math3d/vec4-to-xyzw', Math3DVec4ToXYZW);

  function Math3DXYZWToVec4() {
    this.addInputs([
      ['x', 'number'],
      ['y', 'number'],
      ['z', 'number'],
      ['w', 'number'],
    ]);
    this.addOutput('vec4', 'vec4');
    this.properties = { x: 0, y: 0, z: 0, w: 0 };
    this._data = new Float32Array(4);
  }

  Math3DXYZWToVec4.title = 'XYZW->Vec4';
  Math3DXYZWToVec4.desc = 'components to vector4';

  Math3DXYZWToVec4.prototype.onExecute = function () {
    var x = this.getInputData(0);
    if (x == null) {
      x = this.properties.x;
    }
    var y = this.getInputData(1);
    if (y == null) {
      y = this.properties.y;
    }
    var z = this.getInputData(2);
    if (z == null) {
      z = this.properties.z;
    }
    var w = this.getInputData(3);
    if (w == null) {
      w = this.properties.w;
    }

    var data = this._data;
    data[0] = x;
    data[1] = y;
    data[2] = z;
    data[3] = w;

    this.setOutputData(0, data);
  };

  LiteGraph.registerNodeType('math3d/xyzw-to-vec4', Math3DXYZWToVec4);
})(this);

(function (global) {
  var LiteGraph = global.LiteGraph;

  function Math3DMat4() {
    this.addInput('T', 'vec3');
    this.addInput('R', 'vec3');
    this.addInput('S', 'vec3');
    this.addOutput('mat4', 'mat4');
    this.properties = {
      T: [0, 0, 0],
      R: [0, 0, 0],
      S: [1, 1, 1],
      R_in_degrees: true,
    };
    this._result = mat4.create();
    this._must_update = true;
  }

  Math3DMat4.title = 'mat4';
  Math3DMat4.temp_quat = new Float32Array([0, 0, 0, 1]);
  Math3DMat4.temp_mat4 = new Float32Array(16);
  Math3DMat4.temp_vec3 = new Float32Array(3);

  Math3DMat4.prototype.onPropertyChanged = function (name, value) {
    this._must_update = true;
  };

  Math3DMat4.prototype.onExecute = function () {
    var M = this._result;
    var Q = Math3DMat4.temp_quat;
    var temp_mat4 = Math3DMat4.temp_mat4;
    var temp_vec3 = Math3DMat4.temp_vec3;

    var T = this.getInputData(0);
    var R = this.getInputData(1);
    var S = this.getInputData(2);

    if (this._must_update || T || R || S) {
      T = T || this.properties.T;
      R = R || this.properties.R;
      S = S || this.properties.S;
      mat4.identity(M);
      mat4.translate(M, M, T);
      if (this.properties.R_in_degrees) {
        temp_vec3.set(R);
        vec3.scale(temp_vec3, temp_vec3, DEG2RAD);
        quat.fromEuler(Q, temp_vec3);
      } else quat.fromEuler(Q, R);
      mat4.fromQuat(temp_mat4, Q);
      mat4.multiply(M, M, temp_mat4);
      mat4.scale(M, M, S);
    }

    this.setOutputData(0, M);
  };

  LiteGraph.registerNodeType('math3d/mat4', Math3DMat4);

  //Math 3D operation
  function Math3DOperation() {
    this.addInput('A', 'number,vec3');
    this.addInput('B', 'number,vec3');
    this.addOutput('=', 'number,vec3');
    this.addProperty('OP', '+', 'enum', { values: Math3DOperation.values });
    this._result = vec3.create();
  }

  Math3DOperation.values = [
    '+',
    '-',
    '*',
    '/',
    '%',
    '^',
    'max',
    'min',
    'dot',
    'cross',
  ];

  LiteGraph.registerSearchboxExtra('math3d/operation', 'CROSS()', {
    properties: { OP: 'cross' },
    title: 'CROSS()',
  });

  LiteGraph.registerSearchboxExtra('math3d/operation', 'DOT()', {
    properties: { OP: 'dot' },
    title: 'DOT()',
  });

  Math3DOperation.title = 'Operation';
  Math3DOperation.desc = 'Easy math 3D operators';
  Math3DOperation['@OP'] = {
    type: 'enum',
    title: 'operation',
    values: Math3DOperation.values,
  };
  Math3DOperation.size = [100, 60];

  Math3DOperation.prototype.getTitle = function () {
    if (this.properties.OP == 'max' || this.properties.OP == 'min')
      return this.properties.OP + '(A,B)';
    return 'A ' + this.properties.OP + ' B';
  };

  Math3DOperation.prototype.onExecute = function () {
    var A = this.getInputData(0);
    var B = this.getInputData(1);
    if (A == null || B == null) return;
    if (A.constructor === Number) A = [A, A, A];
    if (B.constructor === Number) B = [B, B, B];

    var result = this._result;
    switch (this.properties.OP) {
      case '+':
        result = vec3.add(result, A, B);
        break;
      case '-':
        result = vec3.sub(result, A, B);
        break;
      case 'x':
      case 'X':
      case '*':
        result = vec3.mul(result, A, B);
        break;
      case '/':
        result = vec3.div(result, A, B);
        break;
      case '%':
        result[0] = A[0] % B[0];
        result[1] = A[1] % B[1];
        result[2] = A[2] % B[2];
        break;
      case '^':
        result[0] = Math.pow(A[0], B[0]);
        result[1] = Math.pow(A[1], B[1]);
        result[2] = Math.pow(A[2], B[2]);
        break;
      case 'max':
        result[0] = Math.max(A[0], B[0]);
        result[1] = Math.max(A[1], B[1]);
        result[2] = Math.max(A[2], B[2]);
        break;
      case 'min':
        result[0] = Math.min(A[0], B[0]);
        result[1] = Math.min(A[1], B[1]);
        result[2] = Math.min(A[2], B[2]);
      case 'dot':
        result = vec3.dot(A, B);
        break;
      case 'cross':
        vec3.cross(result, A, B);
        break;
      default:
        console.warn('Unknown operation: ' + this.properties.OP);
    }
    this.setOutputData(0, result);
  };

  Math3DOperation.prototype.onDrawBackground = function (ctx) {
    if (this.flags.collapsed) {
      return;
    }

    ctx.font = '40px Arial';
    ctx.fillStyle = '#666';
    ctx.textAlign = 'center';
    ctx.fillText(
      this.properties.OP,
      this.size[0] * 0.5,
      (this.size[1] + LiteGraph.NODE_TITLE_HEIGHT) * 0.5,
    );
    ctx.textAlign = 'left';
  };

  LiteGraph.registerNodeType('math3d/operation', Math3DOperation);

  function Math3DVec3Scale() {
    this.addInput('in', 'vec3');
    this.addInput('f', 'number');
    this.addOutput('out', 'vec3');
    this.properties = { f: 1 };
    this._data = new Float32Array(3);
  }

  Math3DVec3Scale.title = 'vec3_scale';
  Math3DVec3Scale.desc = 'scales the components of a vec3';

  Math3DVec3Scale.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v == null) {
      return;
    }
    var f = this.getInputData(1);
    if (f == null) {
      f = this.properties.f;
    }

    var data = this._data;
    data[0] = v[0] * f;
    data[1] = v[1] * f;
    data[2] = v[2] * f;
    this.setOutputData(0, data);
  };

  LiteGraph.registerNodeType('math3d/vec3-scale', Math3DVec3Scale);

  function Math3DVec3Length() {
    this.addInput('in', 'vec3');
    this.addOutput('out', 'number');
  }

  Math3DVec3Length.title = 'vec3_length';
  Math3DVec3Length.desc = 'returns the module of a vector';

  Math3DVec3Length.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v == null) {
      return;
    }
    var dist = Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
    this.setOutputData(0, dist);
  };

  LiteGraph.registerNodeType('math3d/vec3-length', Math3DVec3Length);

  function Math3DVec3Normalize() {
    this.addInput('in', 'vec3');
    this.addOutput('out', 'vec3');
    this._data = new Float32Array(3);
  }

  Math3DVec3Normalize.title = 'vec3_normalize';
  Math3DVec3Normalize.desc = 'returns the vector normalized';

  Math3DVec3Normalize.prototype.onExecute = function () {
    var v = this.getInputData(0);
    if (v == null) {
      return;
    }
    var dist = Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
    var data = this._data;
    data[0] = v[0] / dist;
    data[1] = v[1] / dist;
    data[2] = v[2] / dist;

    this.setOutputData(0, data);
  };

  LiteGraph.registerNodeType('math3d/vec3-normalize', Math3DVec3Normalize);

  function Math3DVec3Lerp() {
    this.addInput('A', 'vec3');
    this.addInput('B', 'vec3');
    this.addInput('f', 'vec3');
    this.addOutput('out', 'vec3');
    this.properties = { f: 0.5 };
    this._data = new Float32Array(3);
  }

  Math3DVec3Lerp.title = 'vec3_lerp';
  Math3DVec3Lerp.desc = 'returns the interpolated vector';

  Math3DVec3Lerp.prototype.onExecute = function () {
    var A = this.getInputData(0);
    if (A == null) {
      return;
    }
    var B = this.getInputData(1);
    if (B == null) {
      return;
    }
    var f = this.getInputOrProperty('f');

    var data = this._data;
    data[0] = A[0] * (1 - f) + B[0] * f;
    data[1] = A[1] * (1 - f) + B[1] * f;
    data[2] = A[2] * (1 - f) + B[2] * f;

    this.setOutputData(0, data);
  };

  LiteGraph.registerNodeType('math3d/vec3-lerp', Math3DVec3Lerp);

  function Math3DVec3Dot() {
    this.addInput('A', 'vec3');
    this.addInput('B', 'vec3');
    this.addOutput('out', 'number');
  }

  Math3DVec3Dot.title = 'vec3_dot';
  Math3DVec3Dot.desc = 'returns the dot product';

  Math3DVec3Dot.prototype.onExecute = function () {
    var A = this.getInputData(0);
    if (A == null) {
      return;
    }
    var B = this.getInputData(1);
    if (B == null) {
      return;
    }

    var dot = A[0] * B[0] + A[1] * B[1] + A[2] * B[2];
    this.setOutputData(0, dot);
  };

  LiteGraph.registerNodeType('math3d/vec3-dot', Math3DVec3Dot);

  //if glMatrix is installed...
  if (global.glMatrix) {
    function Math3DQuaternion() {
      this.addOutput('quat', 'quat');
      this.properties = { x: 0, y: 0, z: 0, w: 1, normalize: false };
      this._value = quat.create();
    }

    Math3DQuaternion.title = 'Quaternion';
    Math3DQuaternion.desc = 'quaternion';

    Math3DQuaternion.prototype.onExecute = function () {
      this._value[0] = this.getInputOrProperty('x');
      this._value[1] = this.getInputOrProperty('y');
      this._value[2] = this.getInputOrProperty('z');
      this._value[3] = this.getInputOrProperty('w');
      if (this.properties.normalize) {
        quat.normalize(this._value, this._value);
      }
      this.setOutputData(0, this._value);
    };

    Math3DQuaternion.prototype.onGetInputs = function () {
      return [
        ['x', 'number'],
        ['y', 'number'],
        ['z', 'number'],
        ['w', 'number'],
      ];
    };

    LiteGraph.registerNodeType('math3d/quaternion', Math3DQuaternion);

    function Math3DRotation() {
      this.addInputs([
        ['degrees', 'number'],
        ['axis', 'vec3'],
      ]);
      this.addOutput('quat', 'quat');
      this.properties = { angle: 90.0, axis: vec3.fromValues(0, 1, 0) };

      this._value = quat.create();
    }

    Math3DRotation.title = 'Rotation';
    Math3DRotation.desc = 'quaternion rotation';

    Math3DRotation.prototype.onExecute = function () {
      var angle = this.getInputData(0);
      if (angle == null) {
        angle = this.properties.angle;
      }
      var axis = this.getInputData(1);
      if (axis == null) {
        axis = this.properties.axis;
      }

      var R = quat.setAxisAngle(this._value, axis, angle * 0.0174532925);
      this.setOutputData(0, R);
    };

    LiteGraph.registerNodeType('math3d/rotation', Math3DRotation);

    function MathEulerToQuat() {
      this.addInput('euler', 'vec3');
      this.addOutput('quat', 'quat');
      this.properties = { euler: [0, 0, 0], use_yaw_pitch_roll: false };
      this._degs = vec3.create();
      this._value = quat.create();
    }

    MathEulerToQuat.title = 'Euler->Quat';
    MathEulerToQuat.desc = 'Converts euler angles (in degrees) to quaternion';

    MathEulerToQuat.prototype.onExecute = function () {
      var euler = this.getInputData(0);
      if (euler == null) {
        euler = this.properties.euler;
      }
      vec3.scale(this._degs, euler, DEG2RAD);
      if (this.properties.use_yaw_pitch_roll)
        this._degs = [this._degs[2], this._degs[0], this._degs[1]];
      var R = quat.fromEuler(this._value, this._degs);
      this.setOutputData(0, R);
    };

    LiteGraph.registerNodeType('math3d/euler_to_quat', MathEulerToQuat);

    function MathQuatToEuler() {
      this.addInput(['quat', 'quat']);
      this.addOutput('euler', 'vec3');
      this._value = vec3.create();
    }

    MathQuatToEuler.title = 'Euler->Quat';
    MathQuatToEuler.desc = 'Converts rotX,rotY,rotZ in degrees to quat';

    MathQuatToEuler.prototype.onExecute = function () {
      var q = this.getInputData(0);
      if (!q) return;
      var R = quat.toEuler(this._value, q);
      vec3.scale(this._value, this._value, DEG2RAD);
      this.setOutputData(0, this._value);
    };

    LiteGraph.registerNodeType('math3d/quat_to_euler', MathQuatToEuler);

    //Math3D rotate vec3
    function Math3DRotateVec3() {
      this.addInputs([
        ['vec3', 'vec3'],
        ['quat', 'quat'],
      ]);
      this.addOutput('result', 'vec3');
      this.properties = { vec: [0, 0, 1] };
    }

    Math3DRotateVec3.title = 'Rot. Vec3';
    Math3DRotateVec3.desc = 'rotate a point';

    Math3DRotateVec3.prototype.onExecute = function () {
      var vec = this.getInputData(0);
      if (vec == null) {
        vec = this.properties.vec;
      }
      var quat = this.getInputData(1);
      if (quat == null) {
        this.setOutputData(vec);
      } else {
        this.setOutputData(0, vec3.transformQuat(vec3.create(), vec, quat));
      }
    };

    LiteGraph.registerNodeType('math3d/rotate_vec3', Math3DRotateVec3);

    function Math3DMultQuat() {
      this.addInputs([
        ['A', 'quat'],
        ['B', 'quat'],
      ]);
      this.addOutput('A*B', 'quat');

      this._value = quat.create();
    }

    Math3DMultQuat.title = 'Mult. Quat';
    Math3DMultQuat.desc = 'rotate quaternion';

    Math3DMultQuat.prototype.onExecute = function () {
      var A = this.getInputData(0);
      if (A == null) {
        return;
      }
      var B = this.getInputData(1);
      if (B == null) {
        return;
      }

      var R = quat.multiply(this._value, A, B);
      this.setOutputData(0, R);
    };

    LiteGraph.registerNodeType('math3d/mult-quat', Math3DMultQuat);

    function Math3DQuatSlerp() {
      this.addInputs([
        ['A', 'quat'],
        ['B', 'quat'],
        ['factor', 'number'],
      ]);
      this.addOutput('slerp', 'quat');
      this.addProperty('factor', 0.5);

      this._value = quat.create();
    }

    Math3DQuatSlerp.title = 'Quat Slerp';
    Math3DQuatSlerp.desc = 'quaternion spherical interpolation';

    Math3DQuatSlerp.prototype.onExecute = function () {
      var A = this.getInputData(0);
      if (A == null) {
        return;
      }
      var B = this.getInputData(1);
      if (B == null) {
        return;
      }
      var factor = this.properties.factor;
      if (this.getInputData(2) != null) {
        factor = this.getInputData(2);
      }

      var R = quat.slerp(this._value, A, B, factor);
      this.setOutputData(0, R);
    };

    LiteGraph.registerNodeType('math3d/quat-slerp', Math3DQuatSlerp);

    //Math3D rotate vec3
    function Math3DRemapRange() {
      this.addInput('vec3', 'vec3');
      this.addOutput('remap', 'vec3');
      this.addOutput('clamped', 'vec3');
      this.properties = {
        clamp: true,
        range_min: [-1, -1, 0],
        range_max: [1, 1, 0],
        target_min: [-1, -1, 0],
        target_max: [1, 1, 0],
      };
      this._value = vec3.create();
      this._clamped = vec3.create();
    }

    Math3DRemapRange.title = 'Remap Range';
    Math3DRemapRange.desc = 'remap a 3D range';

    Math3DRemapRange.prototype.onExecute = function () {
      var vec = this.getInputData(0);
      if (vec) this._value.set(vec);
      var range_min = this.properties.range_min;
      var range_max = this.properties.range_max;
      var target_min = this.properties.target_min;
      var target_max = this.properties.target_max;

      //swap to avoid errors
      /*
    if(range_min > range_max)
    {
      range_min = range_max;
      range_max = this.properties.range_min;
    }

    if(target_min > target_max)
    {
      target_min = target_max;
      target_max = this.properties.target_min;
    }
    */

      for (var i = 0; i < 3; ++i) {
        var r = range_max[i] - range_min[i];
        this._clamped[i] = clamp(this._value[i], range_min[i], range_max[i]);
        if (r == 0) {
          this._value[i] = (target_min[i] + target_max[i]) * 0.5;
          continue;
        }

        var n = (this._value[i] - range_min[i]) / r;
        if (this.properties.clamp) n = clamp(n, 0, 1);
        var t = target_max[i] - target_min[i];
        this._value[i] = target_min[i] + n * t;
      }

      this.setOutputData(0, this._value);
      this.setOutputData(1, this._clamped);
    };

    LiteGraph.registerNodeType('math3d/remap_range', Math3DRemapRange);
  } //glMatrix
  else if (LiteGraph.debug)
    console.warn('No glmatrix found, some Math3D nodes may not work');
})(this);

//basic nodes
(function (global) {
  var LiteGraph = global.LiteGraph;

  function toString(a) {
    if (a && a.constructor === Object) {
      try {
        return JSON.stringify(a);
      } catch (err) {
        return String(a);
      }
    }
    return String(a);
  }

  LiteGraph.wrapFunctionAsNode('string/toString', toString, [''], 'string');

  function compare(a, b) {
    return a == b;
  }

  LiteGraph.wrapFunctionAsNode(
    'string/compare',
    compare,
    ['string', 'string'],
    'boolean',
  );

  function concatenate(a, b) {
    if (a === undefined) {
      return b;
    }
    if (b === undefined) {
      return a;
    }
    return a + b;
  }

  LiteGraph.wrapFunctionAsNode(
    'string/concatenate',
    concatenate,
    ['string', 'string'],
    'string',
  );

  function contains(a, b) {
    if (a === undefined || b === undefined) {
      return false;
    }
    return a.indexOf(b) != -1;
  }

  LiteGraph.wrapFunctionAsNode(
    'string/contains',
    contains,
    ['string', 'string'],
    'boolean',
  );

  function toUpperCase(a) {
    if (a != null && a.constructor === String) {
      return a.toUpperCase();
    }
    return a;
  }

  LiteGraph.wrapFunctionAsNode(
    'string/toUpperCase',
    toUpperCase,
    ['string'],
    'string',
  );

  function split(str, separator) {
    if (separator == null) separator = this.properties.separator;
    if (str == null) return [];
    if (str.constructor === String) return str.split(separator || ' ');
    else if (str.constructor === Array) {
      var r = [];
      for (var i = 0; i < str.length; ++i) {
        if (typeof str[i] == 'string') r[i] = str[i].split(separator || ' ');
      }
      return r;
    }
    return null;
  }

  LiteGraph.wrapFunctionAsNode(
    'string/split',
    split,
    ['string,array', 'string'],
    'array',
    { separator: ',' },
  );

  function toFixed(a) {
    if (a != null && a.constructor === Number) {
      return a.toFixed(this.properties.precision);
    }
    return a;
  }

  LiteGraph.wrapFunctionAsNode(
    'string/toFixed',
    toFixed,
    ['number'],
    'string',
    { precision: 0 },
  );

  function StringToTable() {
    this.addInput('', 'string');
    this.addOutput('table', 'table');
    this.addOutput('rows', 'number');
    this.addProperty('value', '');
    this.addProperty('separator', ',');
    this._table = null;
  }

  StringToTable.title = 'toTable';
  StringToTable.desc = 'Splits a string to table';

  StringToTable.prototype.onExecute = function () {
    var input = this.getInputData(0);
    if (!input) return;
    var separator = this.properties.separator || ',';
    if (input != this._str || separator != this._last_separator) {
      this._last_separator = separator;
      this._str = input;
      this._table = input.split('\n').map(function (a) {
        return a.trim().split(separator);
      });
    }
    this.setOutputData(0, this._table);
    this.setOutputData(1, this._table ? this._table.length : 0);
  };

  LiteGraph.registerNodeType('string/toTable', StringToTable);
})(this);

(function (global) {
  var LiteGraph = global.LiteGraph;

  function Selector() {
    this.addInput('sel', 'number');
    this.addInput('A');
    this.addInput('B');
    this.addInput('C');
    this.addInput('D');
    this.addOutput('out');

    this.selected = 0;
  }

  Selector.title = 'Selector';
  Selector.desc = 'selects an output';

  Selector.prototype.onDrawBackground = function (ctx) {
    if (this.flags.collapsed) {
      return;
    }
    ctx.fillStyle = '#AFB';
    var y = (this.selected + 1) * LiteGraph.NODE_SLOT_HEIGHT + 6;
    ctx.beginPath();
    ctx.moveTo(50, y);
    ctx.lineTo(50, y + LiteGraph.NODE_SLOT_HEIGHT);
    ctx.lineTo(34, y + LiteGraph.NODE_SLOT_HEIGHT * 0.5);
    ctx.fill();
  };

  Selector.prototype.onExecute = function () {
    var sel = this.getInputData(0);
    if (sel == null || sel.constructor !== Number) sel = 0;
    this.selected = sel = Math.round(sel) % (this.inputs.length - 1);
    var v = this.getInputData(sel + 1);
    if (v !== undefined) {
      this.setOutputData(0, v);
    }
  };

  Selector.prototype.onGetInputs = function () {
    return [
      ['E', 0],
      ['F', 0],
      ['G', 0],
      ['H', 0],
    ];
  };

  LiteGraph.registerNodeType('logic/selector', Selector);

  function Sequence() {
    this.properties = {
      sequence: 'A,B,C',
    };
    this.addInput('index', 'number');
    this.addInput('seq');
    this.addOutput('out');

    this.index = 0;
    this.values = this.properties.sequence.split(',');
  }

  Sequence.title = 'Sequence';
  Sequence.desc = 'select one element from a sequence from a string';

  Sequence.prototype.onPropertyChanged = function (name, value) {
    if (name == 'sequence') {
      this.values = value.split(',');
    }
  };

  Sequence.prototype.onExecute = function () {
    var seq = this.getInputData(1);
    if (seq && seq != this.current_sequence) {
      this.values = seq.split(',');
      this.current_sequence = seq;
    }
    var index = this.getInputData(0);
    if (index == null) {
      index = 0;
    }
    this.index = index = Math.round(index) % this.values.length;

    this.setOutputData(0, this.values[index]);
  };

  LiteGraph.registerNodeType('logic/sequence', Sequence);

  function logicAnd() {
    this.properties = {};
    this.addInput('a', 'boolean');
    this.addInput('b', 'boolean');
    this.addOutput('out', 'boolean');
  }
  logicAnd.title = 'AND';
  logicAnd.desc = 'Return true if all inputs are true';
  logicAnd.prototype.onExecute = function () {
    var ret = true;
    for (var inX in this.inputs) {
      if (!this.getInputData(inX)) {
        var ret = false;
        break;
      }
    }
    this.setOutputData(0, ret);
  };
  logicAnd.prototype.onGetInputs = function () {
    return [['and', 'boolean']];
  };
  LiteGraph.registerNodeType('logic/AND', logicAnd);

  function logicOr() {
    this.properties = {};
    this.addInput('a', 'boolean');
    this.addInput('b', 'boolean');
    this.addOutput('out', 'boolean');
  }
  logicOr.title = 'OR';
  logicOr.desc = 'Return true if at least one input is true';
  logicOr.prototype.onExecute = function () {
    var ret = false;
    for (var inX in this.inputs) {
      if (this.getInputData(inX)) {
        ret = true;
        break;
      }
    }
    this.setOutputData(0, ret);
  };
  logicOr.prototype.onGetInputs = function () {
    return [['or', 'boolean']];
  };
  LiteGraph.registerNodeType('logic/OR', logicOr);

  function logicNot() {
    this.properties = {};
    this.addInput('in', 'boolean');
    this.addOutput('out', 'boolean');
  }
  logicNot.title = 'NOT';
  logicNot.desc = 'Return the logical negation';
  logicNot.prototype.onExecute = function () {
    var ret = !this.getInputData(0);
    this.setOutputData(0, ret);
  };
  LiteGraph.registerNodeType('logic/NOT', logicNot);

  function logicCompare() {
    this.properties = {};
    this.addInput('a', 'boolean');
    this.addInput('b', 'boolean');
    this.addOutput('out', 'boolean');
  }
  logicCompare.title = 'bool == bool';
  logicCompare.desc = 'Compare for logical equality';
  logicCompare.prototype.onExecute = function () {
    var last = null;
    var ret = true;
    for (var inX in this.inputs) {
      if (last === null) last = this.getInputData(inX);
      else if (last != this.getInputData(inX)) {
        ret = false;
        break;
      }
    }
    this.setOutputData(0, ret);
  };
  logicCompare.prototype.onGetInputs = function () {
    return [['bool', 'boolean']];
  };
  LiteGraph.registerNodeType('logic/CompareBool', logicCompare);

  function logicBranch() {
    this.properties = {};
    this.addInput('onTrigger', LiteGraph.ACTION);
    this.addInput('condition', 'boolean');
    this.addOutput('true', LiteGraph.EVENT);
    this.addOutput('false', LiteGraph.EVENT);
    this.mode = LiteGraph.ON_TRIGGER;
  }
  logicBranch.title = 'Branch';
  logicBranch.desc = 'Branch execution on condition';
  logicBranch.prototype.onExecute = function (param, options) {
    var condtition = this.getInputData(1);
    if (condtition) {
      this.triggerSlot(0);
    } else {
      this.triggerSlot(1);
    }
  };
  LiteGraph.registerNodeType('logic/IF', logicBranch);
})(this);

(function (global) {
  var LiteGraph = global.LiteGraph;

  function GraphicsPlot() {
    this.addInput('A', 'Number');
    this.addInput('B', 'Number');
    this.addInput('C', 'Number');
    this.addInput('D', 'Number');

    this.values = [[], [], [], []];
    this.properties = { scale: 2 };
  }

  GraphicsPlot.title = 'Plot';
  GraphicsPlot.desc = 'Plots data over time';
  GraphicsPlot.colors = ['#FFF', '#F99', '#9F9', '#99F'];

  GraphicsPlot.prototype.onExecute = function (ctx) {
    if (this.flags.collapsed) {
      return;
    }

    var size = this.size;

    for (var i = 0; i < 4; ++i) {
      var v = this.getInputData(i);
      if (v == null) {
        continue;
      }
      var values = this.values[i];
      values.push(v);
      if (values.length > size[0]) {
        values.shift();
      }
    }
  };

  GraphicsPlot.prototype.onDrawBackground = function (ctx) {
    if (this.flags.collapsed) {
      return;
    }

    var size = this.size;

    var scale = (0.5 * size[1]) / this.properties.scale;
    var colors = GraphicsPlot.colors;
    var offset = size[1] * 0.5;

    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, size[0], size[1]);
    ctx.strokeStyle = '#555';
    ctx.beginPath();
    ctx.moveTo(0, offset);
    ctx.lineTo(size[0], offset);
    ctx.stroke();

    if (this.inputs) {
      for (var i = 0; i < 4; ++i) {
        var values = this.values[i];
        if (!this.inputs[i] || !this.inputs[i].link) {
          continue;
        }
        ctx.strokeStyle = colors[i];
        ctx.beginPath();
        var v = values[0] * scale * -1 + offset;
        ctx.moveTo(0, clamp(v, 0, size[1]));
        for (var j = 1; j < values.length && j < size[0]; ++j) {
          var v = values[j] * scale * -1 + offset;
          ctx.lineTo(j, clamp(v, 0, size[1]));
        }
        ctx.stroke();
      }
    }
  };

  LiteGraph.registerNodeType('graphics/plot', GraphicsPlot);

  function GraphicsImage() {
    this.addOutput('frame', 'image');
    this.properties = { url: '' };
  }

  GraphicsImage.title = 'Image';
  GraphicsImage.desc = 'Image loader';
  GraphicsImage.widgets = [{ name: 'load', text: 'Load', type: 'button' }];

  GraphicsImage.supported_extensions = ['jpg', 'jpeg', 'png', 'gif'];

  GraphicsImage.prototype.onAdded = function () {
    if (this.properties['url'] != '' && this.img == null) {
      this.loadImage(this.properties['url']);
    }
  };

  GraphicsImage.prototype.onDrawBackground = function (ctx) {
    if (this.flags.collapsed) {
      return;
    }
    if (this.img && this.size[0] > 5 && this.size[1] > 5 && this.img.width) {
      ctx.drawImage(this.img, 0, 0, this.size[0], this.size[1]);
    }
  };

  GraphicsImage.prototype.onExecute = function () {
    if (!this.img) {
      this.boxcolor = '#000';
    }
    if (this.img && this.img.width) {
      this.setOutputData(0, this.img);
    } else {
      this.setOutputData(0, null);
    }
    if (this.img && this.img.dirty) {
      this.img.dirty = false;
    }
  };

  GraphicsImage.prototype.onPropertyChanged = function (name, value) {
    this.properties[name] = value;
    if (name == 'url' && value != '') {
      this.loadImage(value);
    }

    return true;
  };

  GraphicsImage.prototype.loadImage = function (url, callback) {
    if (url == '') {
      this.img = null;
      return;
    }

    this.img = document.createElement('img');

    if (url.substr(0, 4) == 'http' && LiteGraph.proxy) {
      url = LiteGraph.proxy + url.substr(url.indexOf(':') + 3);
    }

    this.img.src = url;
    this.boxcolor = '#F95';
    var that = this;
    this.img.onload = function () {
      if (callback) {
        callback(this);
      }
      console.log(
        'Image loaded, size: ' + that.img.width + 'x' + that.img.height,
      );
      this.dirty = true;
      that.boxcolor = '#9F9';
      that.setDirtyCanvas(true);
    };
    this.img.onerror = function () {
      console.log('error loading the image:' + url);
    };
  };

  GraphicsImage.prototype.onWidget = function (e, widget) {
    if (widget.name == 'load') {
      this.loadImage(this.properties['url']);
    }
  };

  GraphicsImage.prototype.onDropFile = function (file) {
    var that = this;
    if (this._url) {
      URL.revokeObjectURL(this._url);
    }
    this._url = URL.createObjectURL(file);
    this.properties.url = this._url;
    this.loadImage(this._url, function (img) {
      that.size[1] = (img.height / img.width) * that.size[0];
    });
  };

  LiteGraph.registerNodeType('graphics/image', GraphicsImage);

  function ColorPalette() {
    this.addInput('f', 'number');
    this.addOutput('Color', 'color');
    this.properties = {
      colorA: '#444444',
      colorB: '#44AAFF',
      colorC: '#44FFAA',
      colorD: '#FFFFFF',
    };
  }

  ColorPalette.title = 'Palette';
  ColorPalette.desc = 'Generates a color';

  ColorPalette.prototype.onExecute = function () {
    var c = [];

    if (this.properties.colorA != null) {
      c.push(hex2num(this.properties.colorA));
    }
    if (this.properties.colorB != null) {
      c.push(hex2num(this.properties.colorB));
    }
    if (this.properties.colorC != null) {
      c.push(hex2num(this.properties.colorC));
    }
    if (this.properties.colorD != null) {
      c.push(hex2num(this.properties.colorD));
    }

    var f = this.getInputData(0);
    if (f == null) {
      f = 0.5;
    }
    if (f > 1.0) {
      f = 1.0;
    } else if (f < 0.0) {
      f = 0.0;
    }

    if (c.length == 0) {
      return;
    }

    var result = [0, 0, 0];
    if (f == 0) {
      result = c[0];
    } else if (f == 1) {
      result = c[c.length - 1];
    } else {
      var pos = (c.length - 1) * f;
      var c1 = c[Math.floor(pos)];
      var c2 = c[Math.floor(pos) + 1];
      var t = pos - Math.floor(pos);
      result[0] = c1[0] * (1 - t) + c2[0] * t;
      result[1] = c1[1] * (1 - t) + c2[1] * t;
      result[2] = c1[2] * (1 - t) + c2[2] * t;
    }

    /*
c[0] = 1.0 - Math.abs( Math.sin( 0.1 * reModular.getTime() * Math.PI) );
c[1] = Math.abs( Math.sin( 0.07 * reModular.getTime() * Math.PI) );
c[2] = Math.abs( Math.sin( 0.01 * reModular.getTime() * Math.PI) );
*/

    for (var i = 0; i < result.length; i++) {
      result[i] /= 255;
    }

    this.boxcolor = colorToString(result);
    this.setOutputData(0, result);
  };

  LiteGraph.registerNodeType('color/palette', ColorPalette);

  function ImageFrame() {
    this.addInput('', 'image,canvas');
    this.size = [200, 200];
  }

  ImageFrame.title = 'Frame';
  ImageFrame.desc = 'Frame viewerew';
  ImageFrame.widgets = [
    { name: 'resize', text: 'Resize box', type: 'button' },
    { name: 'view', text: 'View Image', type: 'button' },
  ];

  ImageFrame.prototype.onDrawBackground = function (ctx) {
    if (this.frame && !this.flags.collapsed) {
      ctx.drawImage(this.frame, 0, 0, this.size[0], this.size[1]);
    }
  };

  ImageFrame.prototype.onExecute = function () {
    this.frame = this.getInputData(0);
    this.setDirtyCanvas(true);
  };

  ImageFrame.prototype.onWidget = function (e, widget) {
    if (widget.name == 'resize' && this.frame) {
      var width = this.frame.width;
      var height = this.frame.height;

      if (!width && this.frame.videoWidth != null) {
        width = this.frame.videoWidth;
        height = this.frame.videoHeight;
      }

      if (width && height) {
        this.size = [width, height];
      }
      this.setDirtyCanvas(true, true);
    } else if (widget.name == 'view') {
      this.show();
    }
  };

  ImageFrame.prototype.show = function () {
    //var str = this.canvas.toDataURL("image/png");
    if (showElement && this.frame) {
      showElement(this.frame);
    }
  };

  LiteGraph.registerNodeType('graphics/frame', ImageFrame);

  function ImageFade() {
    this.addInputs([
      ['img1', 'image'],
      ['img2', 'image'],
      ['fade', 'number'],
    ]);
    this.addOutput('', 'image');
    this.properties = { fade: 0.5, width: 512, height: 512 };
  }

  ImageFade.title = 'Image fade';
  ImageFade.desc = 'Fades between images';
  ImageFade.widgets = [
    { name: 'resizeA', text: 'Resize to A', type: 'button' },
    { name: 'resizeB', text: 'Resize to B', type: 'button' },
  ];

  ImageFade.prototype.onAdded = function () {
    this.createCanvas();
    var ctx = this.canvas.getContext('2d');
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, this.properties['width'], this.properties['height']);
  };

  ImageFade.prototype.createCanvas = function () {
    this.canvas = document.createElement('canvas');
    this.canvas.width = this.properties['width'];
    this.canvas.height = this.properties['height'];
  };

  ImageFade.prototype.onExecute = function () {
    var ctx = this.canvas.getContext('2d');
    this.canvas.width = this.canvas.width;

    var A = this.getInputData(0);
    if (A != null) {
      ctx.drawImage(A, 0, 0, this.canvas.width, this.canvas.height);
    }

    var fade = this.getInputData(2);
    if (fade == null) {
      fade = this.properties['fade'];
    } else {
      this.properties['fade'] = fade;
    }

    ctx.globalAlpha = fade;
    var B = this.getInputData(1);
    if (B != null) {
      ctx.drawImage(B, 0, 0, this.canvas.width, this.canvas.height);
    }
    ctx.globalAlpha = 1.0;

    this.setOutputData(0, this.canvas);
    this.setDirtyCanvas(true);
  };

  LiteGraph.registerNodeType('graphics/imagefade', ImageFade);

  function ImageCrop() {
    this.addInput('', 'image');
    this.addOutput('', 'image');
    this.properties = { width: 256, height: 256, x: 0, y: 0, scale: 1.0 };
    this.size = [50, 20];
  }

  ImageCrop.title = 'Crop';
  ImageCrop.desc = 'Crop Image';

  ImageCrop.prototype.onAdded = function () {
    this.createCanvas();
  };

  ImageCrop.prototype.createCanvas = function () {
    this.canvas = document.createElement('canvas');
    this.canvas.width = this.properties['width'];
    this.canvas.height = this.properties['height'];
  };

  ImageCrop.prototype.onExecute = function () {
    var input = this.getInputData(0);
    if (!input) {
      return;
    }

    if (input.width) {
      var ctx = this.canvas.getContext('2d');

      ctx.drawImage(
        input,
        -this.properties['x'],
        -this.properties['y'],
        input.width * this.properties['scale'],
        input.height * this.properties['scale'],
      );
      this.setOutputData(0, this.canvas);
    } else {
      this.setOutputData(0, null);
    }
  };

  ImageCrop.prototype.onDrawBackground = function (ctx) {
    if (this.flags.collapsed) {
      return;
    }
    if (this.canvas) {
      ctx.drawImage(
        this.canvas,
        0,
        0,
        this.canvas.width,
        this.canvas.height,
        0,
        0,
        this.size[0],
        this.size[1],
      );
    }
  };

  ImageCrop.prototype.onPropertyChanged = function (name, value) {
    this.properties[name] = value;

    if (name == 'scale') {
      this.properties[name] = parseFloat(value);
      if (this.properties[name] == 0) {
        console.error('Error in scale');
        this.properties[name] = 1.0;
      }
    } else {
      this.properties[name] = parseInt(value);
    }

    this.createCanvas();

    return true;
  };

  LiteGraph.registerNodeType('graphics/cropImage', ImageCrop);

  //CANVAS stuff

  function CanvasNode() {
    this.addInput('clear', LiteGraph.ACTION);
    this.addOutput('', 'canvas');
    this.properties = { width: 512, height: 512, autoclear: true };

    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
  }

  CanvasNode.title = 'Canvas';
  CanvasNode.desc = 'Canvas to render stuff';

  CanvasNode.prototype.onExecute = function () {
    var canvas = this.canvas;
    var w = this.properties.width | 0;
    var h = this.properties.height | 0;
    if (canvas.width != w) {
      canvas.width = w;
    }
    if (canvas.height != h) {
      canvas.height = h;
    }

    if (this.properties.autoclear) {
      this.ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    this.setOutputData(0, canvas);
  };

  CanvasNode.prototype.onAction = function (action, param) {
    if (action == 'clear') {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
  };

  LiteGraph.registerNodeType('graphics/canvas', CanvasNode);

  function DrawImageNode() {
    this.addInput('canvas', 'canvas');
    this.addInput('img', 'image,canvas');
    this.addInput('x', 'number');
    this.addInput('y', 'number');
    this.properties = { x: 0, y: 0, opacity: 1 };
  }

  DrawImageNode.title = 'DrawImage';
  DrawImageNode.desc = 'Draws image into a canvas';

  DrawImageNode.prototype.onExecute = function () {
    var canvas = this.getInputData(0);
    if (!canvas) {
      return;
    }

    var img = this.getInputOrProperty('img');
    if (!img) {
      return;
    }

    var x = this.getInputOrProperty('x');
    var y = this.getInputOrProperty('y');
    var ctx = canvas.getContext('2d');
    ctx.drawImage(img, x, y);
  };

  LiteGraph.registerNodeType('graphics/drawImage', DrawImageNode);

  function DrawRectangleNode() {
    this.addInput('canvas', 'canvas');
    this.addInput('x', 'number');
    this.addInput('y', 'number');
    this.addInput('w', 'number');
    this.addInput('h', 'number');
    this.properties = {
      x: 0,
      y: 0,
      w: 10,
      h: 10,
      color: 'white',
      opacity: 1,
    };
  }

  DrawRectangleNode.title = 'DrawRectangle';
  DrawRectangleNode.desc = 'Draws rectangle in canvas';

  DrawRectangleNode.prototype.onExecute = function () {
    var canvas = this.getInputData(0);
    if (!canvas) {
      return;
    }

    var x = this.getInputOrProperty('x');
    var y = this.getInputOrProperty('y');
    var w = this.getInputOrProperty('w');
    var h = this.getInputOrProperty('h');
    var ctx = canvas.getContext('2d');
    ctx.fillRect(x, y, w, h);
  };

  LiteGraph.registerNodeType('graphics/drawRectangle', DrawRectangleNode);

  function ImageVideo() {
    this.addInput('t', 'number');
    this.addOutputs([
      ['frame', 'image'],
      ['t', 'number'],
      ['d', 'number'],
    ]);
    this.properties = { url: '', use_proxy: true };
  }

  ImageVideo.title = 'Video';
  ImageVideo.desc = 'Video playback';
  ImageVideo.widgets = [
    { name: 'play', text: 'PLAY', type: 'minibutton' },
    { name: 'stop', text: 'STOP', type: 'minibutton' },
    { name: 'demo', text: 'Demo video', type: 'button' },
    { name: 'mute', text: 'Mute video', type: 'button' },
  ];

  ImageVideo.prototype.onExecute = function () {
    if (!this.properties.url) {
      return;
    }

    if (this.properties.url != this._video_url) {
      this.loadVideo(this.properties.url);
    }

    if (!this._video || this._video.width == 0) {
      return;
    }

    var t = this.getInputData(0);
    if (t && t >= 0 && t <= 1.0) {
      this._video.currentTime = t * this._video.duration;
      this._video.pause();
    }

    this._video.dirty = true;
    this.setOutputData(0, this._video);
    this.setOutputData(1, this._video.currentTime);
    this.setOutputData(2, this._video.duration);
    this.setDirtyCanvas(true);
  };

  ImageVideo.prototype.onStart = function () {
    this.play();
  };

  ImageVideo.prototype.onStop = function () {
    this.stop();
  };

  ImageVideo.prototype.loadVideo = function (url) {
    this._video_url = url;

    var pos = url.substr(0, 10).indexOf(':');
    var protocol = '';
    if (pos != -1) protocol = url.substr(0, pos);

    var host = '';
    if (protocol) {
      host = url.substr(0, url.indexOf('/', protocol.length + 3));
      host = host.substr(protocol.length + 3);
    }

    if (
      this.properties.use_proxy &&
      protocol &&
      LiteGraph.proxy &&
      host != location.host
    ) {
      url = LiteGraph.proxy + url.substr(url.indexOf(':') + 3);
    }

    this._video = document.createElement('video');
    this._video.src = url;
    this._video.type = 'type=video/mp4';

    this._video.muted = true;
    this._video.autoplay = true;

    var that = this;
    this._video.addEventListener('loadedmetadata', function (e) {
      //onload
      console.log('Duration: ' + this.duration + ' seconds');
      console.log('Size: ' + this.videoWidth + ',' + this.videoHeight);
      that.setDirtyCanvas(true);
      this.width = this.videoWidth;
      this.height = this.videoHeight;
    });
    this._video.addEventListener('progress', function (e) {
      //onload
      console.log('video loading...');
    });
    this._video.addEventListener('error', function (e) {
      console.error('Error loading video: ' + this.src);
      if (this.error) {
        switch (this.error.code) {
          case this.error.MEDIA_ERR_ABORTED:
            console.error('You stopped the video.');
            break;
          case this.error.MEDIA_ERR_NETWORK:
            console.error('Network error - please try again later.');
            break;
          case this.error.MEDIA_ERR_DECODE:
            console.error('Video is broken..');
            break;
          case this.error.MEDIA_ERR_SRC_NOT_SUPPORTED:
            console.error("Sorry, your browser can't play this video.");
            break;
        }
      }
    });

    this._video.addEventListener('ended', function (e) {
      console.log('Video Ended.');
      this.play(); //loop
    });

    //document.body.appendChild(this.video);
  };

  ImageVideo.prototype.onPropertyChanged = function (name, value) {
    this.properties[name] = value;
    if (name == 'url' && value != '') {
      this.loadVideo(value);
    }

    return true;
  };

  ImageVideo.prototype.play = function () {
    if (this._video && this._video.videoWidth) {
      //is loaded
      this._video.play();
    }
  };

  ImageVideo.prototype.playPause = function () {
    if (!this._video) {
      return;
    }
    if (this._video.paused) {
      this.play();
    } else {
      this.pause();
    }
  };

  ImageVideo.prototype.stop = function () {
    if (!this._video) {
      return;
    }
    this._video.pause();
    this._video.currentTime = 0;
  };

  ImageVideo.prototype.pause = function () {
    if (!this._video) {
      return;
    }
    console.log('Video paused');
    this._video.pause();
  };

  ImageVideo.prototype.onWidget = function (e, widget) {
    /*
if(widget.name == "demo")
{
  this.loadVideo();
}
else if(widget.name == "play")
{
  if(this._video)
    this.playPause();
}
if(widget.name == "stop")
{
  this.stop();
}
else if(widget.name == "mute")
{
  if(this._video)
    this._video.muted = !this._video.muted;
}
*/
  };

  LiteGraph.registerNodeType('graphics/video', ImageVideo);

  // Texture Webcam *****************************************
  function ImageWebcam() {
    this.addOutput('Webcam', 'image');
    this.properties = { filterFacingMode: false, facingMode: 'user' };
    this.boxcolor = 'black';
    this.frame = 0;
  }

  ImageWebcam.title = 'Webcam';
  ImageWebcam.desc = 'Webcam image';
  ImageWebcam.is_webcam_open = false;

  ImageWebcam.prototype.openStream = function () {
    if (!navigator.mediaDevices.getUserMedia) {
      console.log(
        'getUserMedia() is not supported in your browser, use chrome and enable WebRTC from about://flags',
      );
      return;
    }

    this._waiting_confirmation = true;

    // Not showing vendor prefixes.
    var constraints = {
      audio: false,
      video: !this.properties.filterFacingMode
        ? true
        : { facingMode: this.properties.facingMode },
    };
    navigator.mediaDevices
      .getUserMedia(constraints)
      .then(this.streamReady.bind(this))
      .catch(onFailSoHard);

    var that = this;
    function onFailSoHard(e) {
      console.log('Webcam rejected', e);
      that._webcam_stream = false;
      ImageWebcam.is_webcam_open = false;
      that.boxcolor = 'red';
      that.trigger('stream_error');
    }
  };

  ImageWebcam.prototype.closeStream = function () {
    if (this._webcam_stream) {
      var tracks = this._webcam_stream.getTracks();
      if (tracks.length) {
        for (var i = 0; i < tracks.length; ++i) {
          tracks[i].stop();
        }
      }
      ImageWebcam.is_webcam_open = false;
      this._webcam_stream = null;
      this._video = null;
      this.boxcolor = 'black';
      this.trigger('stream_closed');
    }
  };

  ImageWebcam.prototype.onPropertyChanged = function (name, value) {
    if (name == 'facingMode') {
      this.properties.facingMode = value;
      this.closeStream();
      this.openStream();
    }
  };

  ImageWebcam.prototype.onRemoved = function () {
    this.closeStream();
  };

  ImageWebcam.prototype.streamReady = function (localMediaStream) {
    this._webcam_stream = localMediaStream;
    //this._waiting_confirmation = false;
    this.boxcolor = 'green';

    var video = this._video;
    if (!video) {
      video = document.createElement('video');
      video.autoplay = true;
      video.srcObject = localMediaStream;
      this._video = video;
      //document.body.appendChild( video ); //debug
      //when video info is loaded (size and so)
      video.onloadedmetadata = function (e) {
        // Ready to go. Do some stuff.
        console.log(e);
        ImageWebcam.is_webcam_open = true;
      };
    }

    this.trigger('stream_ready', video);
  };

  ImageWebcam.prototype.onExecute = function () {
    if (this._webcam_stream == null && !this._waiting_confirmation) {
      this.openStream();
    }

    if (!this._video || !this._video.videoWidth) {
      return;
    }

    this._video.frame = ++this.frame;
    this._video.width = this._video.videoWidth;
    this._video.height = this._video.videoHeight;
    this.setOutputData(0, this._video);
    for (var i = 1; i < this.outputs.length; ++i) {
      if (!this.outputs[i]) {
        continue;
      }
      switch (this.outputs[i].name) {
        case 'width':
          this.setOutputData(i, this._video.videoWidth);
          break;
        case 'height':
          this.setOutputData(i, this._video.videoHeight);
          break;
      }
    }
  };

  ImageWebcam.prototype.getExtraMenuOptions = function (graphcanvas) {
    var that = this;
    var txt = !that.properties.show ? 'Show Frame' : 'Hide Frame';
    return [
      {
        content: txt,
        callback: function () {
          that.properties.show = !that.properties.show;
        },
      },
    ];
  };

  ImageWebcam.prototype.onDrawBackground = function (ctx) {
    if (this.flags.collapsed || this.size[1] <= 20 || !this.properties.show) {
      return;
    }

    if (!this._video) {
      return;
    }

    //render to graph canvas
    ctx.save();
    ctx.drawImage(this._video, 0, 0, this.size[0], this.size[1]);
    ctx.restore();
  };

  ImageWebcam.prototype.onGetOutputs = function () {
    return [
      ['width', 'number'],
      ['height', 'number'],
      ['stream_ready', LiteGraph.EVENT],
      ['stream_closed', LiteGraph.EVENT],
      ['stream_error', LiteGraph.EVENT],
    ];
  };

  LiteGraph.registerNodeType('graphics/webcam', ImageWebcam);
})(this);

(function (global) {
  var LiteGraph = global.LiteGraph;
  var LGraphCanvas = global.LGraphCanvas;

  //Works with Litegl.js to create WebGL nodes
  global.LGraphTexture = null;

  if (typeof GL == 'undefined') return;

  LGraphCanvas.link_type_colors['Texture'] = '#987';

  function LGraphTexture() {
    this.addOutput('tex', 'Texture');
    this.addOutput('name', 'string');
    this.properties = { name: '', filter: true };
    this.size = [
      LGraphTexture.image_preview_size,
      LGraphTexture.image_preview_size,
    ];
  }

  global.LGraphTexture = LGraphTexture;

  LGraphTexture.title = 'Texture';
  LGraphTexture.desc = 'Texture';
  LGraphTexture.widgets_info = {
    name: { widget: 'texture' },
    filter: { widget: 'checkbox' },
  };

  //REPLACE THIS TO INTEGRATE WITH YOUR FRAMEWORK
  LGraphTexture.loadTextureCallback = null; //function in charge of loading textures when not present in the container
  LGraphTexture.image_preview_size = 256;

  //flags to choose output texture type
  LGraphTexture.UNDEFINED = 0; //not specified
  LGraphTexture.PASS_THROUGH = 1; //do not apply FX (like disable but passing the in to the out)
  LGraphTexture.COPY = 2; //create new texture with the same properties as the origin texture
  LGraphTexture.LOW = 3; //create new texture with low precision (byte)
  LGraphTexture.HIGH = 4; //create new texture with high precision (half-float)
  LGraphTexture.REUSE = 5; //reuse input texture
  LGraphTexture.DEFAULT = 2; //use the default

  LGraphTexture.MODE_VALUES = {
    undefined: LGraphTexture.UNDEFINED,
    'pass through': LGraphTexture.PASS_THROUGH,
    copy: LGraphTexture.COPY,
    low: LGraphTexture.LOW,
    high: LGraphTexture.HIGH,
    reuse: LGraphTexture.REUSE,
    default: LGraphTexture.DEFAULT,
  };

  //returns the container where all the loaded textures are stored (overwrite if you have a Resources Manager)
  LGraphTexture.getTexturesContainer = function () {
    return gl.textures;
  };

  //process the loading of a texture (overwrite it if you have a Resources Manager)
  LGraphTexture.loadTexture = function (name, options) {
    options = options || {};
    var url = name;
    if (url.substr(0, 7) == 'http://') {
      if (LiteGraph.proxy) {
        //proxy external files
        url = LiteGraph.proxy + url.substr(7);
      }
    }

    var container = LGraphTexture.getTexturesContainer();
    var tex = (container[name] = GL.Texture.fromURL(url, options));
    return tex;
  };

  LGraphTexture.getTexture = function (name) {
    var container = this.getTexturesContainer();

    if (!container) {
      throw 'Cannot load texture, container of textures not found';
    }

    var tex = container[name];
    if (!tex && name && name[0] != ':') {
      return this.loadTexture(name);
    }

    return tex;
  };

  //used to compute the appropiate output texture
  LGraphTexture.getTargetTexture = function (origin, target, mode) {
    if (!origin) {
      throw 'LGraphTexture.getTargetTexture expects a reference texture';
    }

    var tex_type = null;

    switch (mode) {
      case LGraphTexture.LOW:
        tex_type = gl.UNSIGNED_BYTE;
        break;
      case LGraphTexture.HIGH:
        tex_type = gl.HIGH_PRECISION_FORMAT;
        break;
      case LGraphTexture.REUSE:
        return origin;
        break;
      case LGraphTexture.COPY:
      default:
        tex_type = origin ? origin.type : gl.UNSIGNED_BYTE;
        break;
    }

    if (
      !target ||
      target.width != origin.width ||
      target.height != origin.height ||
      target.type != tex_type ||
      target.format != origin.format
    ) {
      target = new GL.Texture(origin.width, origin.height, {
        type: tex_type,
        format: origin.format,
        filter: gl.LINEAR,
      });
    }

    return target;
  };

  LGraphTexture.getTextureType = function (precision, ref_texture) {
    var type = ref_texture ? ref_texture.type : gl.UNSIGNED_BYTE;
    switch (precision) {
      case LGraphTexture.HIGH:
        type = gl.HIGH_PRECISION_FORMAT;
        break;
      case LGraphTexture.LOW:
        type = gl.UNSIGNED_BYTE;
        break;
      //no default
    }
    return type;
  };

  LGraphTexture.getWhiteTexture = function () {
    if (this._white_texture) {
      return this._white_texture;
    }
    var texture = (this._white_texture = GL.Texture.fromMemory(
      1,
      1,
      [255, 255, 255, 255],
      { format: gl.RGBA, wrap: gl.REPEAT, filter: gl.NEAREST },
    ));
    return texture;
  };

  LGraphTexture.getNoiseTexture = function () {
    if (this._noise_texture) {
      return this._noise_texture;
    }

    var noise = new Uint8Array(512 * 512 * 4);
    for (var i = 0; i < 512 * 512 * 4; ++i) {
      noise[i] = Math.random() * 255;
    }

    var texture = GL.Texture.fromMemory(512, 512, noise, {
      format: gl.RGBA,
      wrap: gl.REPEAT,
      filter: gl.NEAREST,
    });
    this._noise_texture = texture;
    return texture;
  };

  LGraphTexture.prototype.onDropFile = function (data, filename, file) {
    if (!data) {
      this._drop_texture = null;
      this.properties.name = '';
    } else {
      var texture = null;
      if (typeof data == 'string') {
        texture = GL.Texture.fromURL(data);
      } else if (filename.toLowerCase().indexOf('.dds') != -1) {
        texture = GL.Texture.fromDDSInMemory(data);
      } else {
        var blob = new Blob([file]);
        var url = URL.createObjectURL(blob);
        texture = GL.Texture.fromURL(url);
      }

      this._drop_texture = texture;
      this.properties.name = filename;
    }
  };

  LGraphTexture.prototype.getExtraMenuOptions = function (graphcanvas) {
    var that = this;
    if (!this._drop_texture) {
      return;
    }
    return [
      {
        content: 'Clear',
        callback: function () {
          that._drop_texture = null;
          that.properties.name = '';
        },
      },
    ];
  };

  LGraphTexture.prototype.onExecute = function () {
    var tex = null;
    if (this.isOutputConnected(1)) {
      tex = this.getInputData(0);
    }

    if (!tex && this._drop_texture) {
      tex = this._drop_texture;
    }

    if (!tex && this.properties.name) {
      tex = LGraphTexture.getTexture(this.properties.name);
    }

    if (!tex) {
      this.setOutputData(0, null);
      this.setOutputData(1, '');
      return;
    }

    this._last_tex = tex;

    if (this.properties.filter === false) {
      tex.setParameter(gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    } else {
      tex.setParameter(gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    }

    this.setOutputData(0, tex);
    this.setOutputData(1, tex.fullpath || tex.filename);

    for (var i = 2; i < this.outputs.length; i++) {
      var output = this.outputs[i];
      if (!output) {
        continue;
      }
      var v = null;
      if (output.name == 'width') {
        v = tex.width;
      } else if (output.name == 'height') {
        v = tex.height;
      } else if (output.name == 'aspect') {
        v = tex.width / tex.height;
      }
      this.setOutputData(i, v);
    }
  };

  LGraphTexture.prototype.onResourceRenamed = function (old_name, new_name) {
    if (this.properties.name == old_name) {
      this.properties.name = new_name;
    }
  };

  LGraphTexture.prototype.onDrawBackground = function (ctx) {
    if (this.flags.collapsed || this.size[1] <= 20) {
      return;
    }

    if (this._drop_texture && ctx.webgl) {
      ctx.drawImage(this._drop_texture, 0, 0, this.size[0], this.size[1]);
      //this._drop_texture.renderQuad(this.pos[0],this.pos[1],this.size[0],this.size[1]);
      return;
    }

    //Different texture? then get it from the GPU
    if (this._last_preview_tex != this._last_tex) {
      if (ctx.webgl) {
        this._canvas = this._last_tex;
      } else {
        var tex_canvas = LGraphTexture.generateLowResTexturePreview(
          this._last_tex,
        );
        if (!tex_canvas) {
          return;
        }

        this._last_preview_tex = this._last_tex;
        this._canvas = cloneCanvas(tex_canvas);
      }
    }

    if (!this._canvas) {
      return;
    }

    //render to graph canvas
    ctx.save();
    if (!ctx.webgl) {
      //reverse image
      ctx.translate(0, this.size[1]);
      ctx.scale(1, -1);
    }
    ctx.drawImage(this._canvas, 0, 0, this.size[0], this.size[1]);
    ctx.restore();
  };

  //very slow, used at your own risk
  LGraphTexture.generateLowResTexturePreview = function (tex) {
    if (!tex) {
      return null;
    }

    var size = LGraphTexture.image_preview_size;
    var temp_tex = tex;

    if (tex.format == gl.DEPTH_COMPONENT) {
      return null;
    } //cannot generate from depth

    //Generate low-level version in the GPU to speed up
    if (tex.width > size || tex.height > size) {
      temp_tex = this._preview_temp_tex;
      if (!this._preview_temp_tex) {
        temp_tex = new GL.Texture(size, size, {
          minFilter: gl.NEAREST,
        });
        this._preview_temp_tex = temp_tex;
      }

      //copy
      tex.copyTo(temp_tex);
      tex = temp_tex;
    }

    //create intermediate canvas with lowquality version
    var tex_canvas = this._preview_canvas;
    if (!tex_canvas) {
      tex_canvas = createCanvas(size, size);
      this._preview_canvas = tex_canvas;
    }

    if (temp_tex) {
      temp_tex.toCanvas(tex_canvas);
    }
    return tex_canvas;
  };

  LGraphTexture.prototype.getResources = function (res) {
    if (this.properties.name) res[this.properties.name] = GL.Texture;
    return res;
  };

  LGraphTexture.prototype.onGetInputs = function () {
    return [['in', 'Texture']];
  };

  LGraphTexture.prototype.onGetOutputs = function () {
    return [
      ['width', 'number'],
      ['height', 'number'],
      ['aspect', 'number'],
    ];
  };

  //used to replace shader code
  LGraphTexture.replaceCode = function (code, context) {
    return code.replace(/\{\{[a-zA-Z0-9_]*\}\}/g, function (v) {
      v = v.replace(/[\{\}]/g, '');
      return context[v] || '';
    });
  };

  LiteGraph.registerNodeType('texture/texture', LGraphTexture);

  //**************************
  function LGraphTexturePreview() {
    this.addInput('Texture', 'Texture');
    this.properties = { flipY: false };
    this.size = [
      LGraphTexture.image_preview_size,
      LGraphTexture.image_preview_size,
    ];
  }

  LGraphTexturePreview.title = 'Preview';
  LGraphTexturePreview.desc = 'Show a texture in the graph canvas';
  LGraphTexturePreview.allow_preview = false;

  LGraphTexturePreview.prototype.onDrawBackground = function (ctx) {
    if (this.flags.collapsed) {
      return;
    }

    if (!ctx.webgl && !LGraphTexturePreview.allow_preview) {
      return;
    } //not working well

    var tex = this.getInputData(0);
    if (!tex) {
      return;
    }

    var tex_canvas = null;

    if (!tex.handle && ctx.webgl) {
      tex_canvas = tex;
    } else {
      tex_canvas = LGraphTexture.generateLowResTexturePreview(tex);
    }

    //render to graph canvas
    ctx.save();
    if (this.properties.flipY) {
      ctx.translate(0, this.size[1]);
      ctx.scale(1, -1);
    }
    ctx.drawImage(tex_canvas, 0, 0, this.size[0], this.size[1]);
    ctx.restore();
  };

  LiteGraph.registerNodeType('texture/preview', LGraphTexturePreview);

  //**************************************

  function LGraphTextureSave() {
    this.addInput('Texture', 'Texture');
    this.addOutput('tex', 'Texture');
    this.addOutput('name', 'string');
    this.properties = { name: '', generate_mipmaps: false };
  }

  LGraphTextureSave.title = 'Save';
  LGraphTextureSave.desc = 'Save a texture in the repository';

  LGraphTextureSave.prototype.getPreviewTexture = function () {
    return this._texture;
  };

  LGraphTextureSave.prototype.onExecute = function () {
    var tex = this.getInputData(0);
    if (!tex) {
      return;
    }

    if (this.properties.generate_mipmaps) {
      tex.bind(0);
      tex.setParameter(gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
      gl.generateMipmap(tex.texture_type);
      tex.unbind(0);
    }

    if (this.properties.name) {
      //for cases where we want to perform something when storing it
      if (LGraphTexture.storeTexture) {
        LGraphTexture.storeTexture(this.properties.name, tex);
      } else {
        var container = LGraphTexture.getTexturesContainer();
        container[this.properties.name] = tex;
      }
    }

    this._texture = tex;
    this.setOutputData(0, tex);
    this.setOutputData(1, this.properties.name);
  };

  LiteGraph.registerNodeType('texture/save', LGraphTextureSave);

  //****************************************************

  function LGraphTextureOperation() {
    this.addInput('Texture', 'Texture');
    this.addInput('TextureB', 'Texture');
    this.addInput('value', 'number');
    this.addOutput('Texture', 'Texture');
    this.help =
      '<p>pixelcode must be vec3, uvcode must be vec2, is optional</p>\
  <p><strong>uv:</strong> tex. coords</p><p><strong>color:</strong> texture <strong>colorB:</strong> textureB</p><p><strong>time:</strong> scene time <strong>value:</strong> input value</p><p>For multiline you must type: result = ...</p>';

    this.properties = {
      value: 1,
      pixelcode: 'color + colorB * value',
      uvcode: '',
      precision: LGraphTexture.DEFAULT,
    };

    this.has_error = false;
  }

  LGraphTextureOperation.widgets_info = {
    uvcode: { widget: 'code' },
    pixelcode: { widget: 'code' },
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureOperation.title = 'Operation';
  LGraphTextureOperation.desc = 'Texture shader operation';

  LGraphTextureOperation.presets = {};

  LGraphTextureOperation.prototype.getExtraMenuOptions = function (
    graphcanvas,
  ) {
    var that = this;
    var txt = !that.properties.show ? 'Show Texture' : 'Hide Texture';
    return [
      {
        content: txt,
        callback: function () {
          that.properties.show = !that.properties.show;
        },
      },
    ];
  };

  LGraphTextureOperation.prototype.onPropertyChanged = function () {
    this.has_error = false;
  };

  LGraphTextureOperation.prototype.onDrawBackground = function (ctx) {
    if (this.flags.collapsed || this.size[1] <= 20 || !this.properties.show) {
      return;
    }

    if (!this._tex) {
      return;
    }

    //only works if using a webgl renderer
    if (this._tex.gl != ctx) {
      return;
    }

    //render to graph canvas
    ctx.save();
    ctx.drawImage(this._tex, 0, 0, this.size[0], this.size[1]);
    ctx.restore();
  };

  LGraphTextureOperation.prototype.onExecute = function () {
    var tex = this.getInputData(0);

    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    if (this.properties.precision === LGraphTexture.PASS_THROUGH) {
      this.setOutputData(0, tex);
      return;
    }

    var texB = this.getInputData(1);

    if (!this.properties.uvcode && !this.properties.pixelcode) {
      return;
    }

    var width = 512;
    var height = 512;
    if (tex) {
      width = tex.width;
      height = tex.height;
    } else if (texB) {
      width = texB.width;
      height = texB.height;
    }

    if (!texB) texB = GL.Texture.getWhiteTexture();

    var type = LGraphTexture.getTextureType(this.properties.precision, tex);

    if (!tex && !this._tex) {
      this._tex = new GL.Texture(width, height, {
        type: type,
        format: gl.RGBA,
        filter: gl.LINEAR,
      });
    } else {
      this._tex = LGraphTexture.getTargetTexture(
        tex || this._tex,
        this._tex,
        this.properties.precision,
      );
    }

    var uvcode = '';
    if (this.properties.uvcode) {
      uvcode = 'uv = ' + this.properties.uvcode;
      if (this.properties.uvcode.indexOf(';') != -1) {
        //there are line breaks, means multiline code
        uvcode = this.properties.uvcode;
      }
    }

    var pixelcode = '';
    if (this.properties.pixelcode) {
      pixelcode = 'result = ' + this.properties.pixelcode;
      if (this.properties.pixelcode.indexOf(';') != -1) {
        //there are line breaks, means multiline code
        pixelcode = this.properties.pixelcode;
      }
    }

    var shader = this._shader;

    if (
      !this.has_error &&
      (!shader || this._shader_code != uvcode + '|' + pixelcode)
    ) {
      var final_pixel_code = LGraphTexture.replaceCode(
        LGraphTextureOperation.pixel_shader,
        { UV_CODE: uvcode, PIXEL_CODE: pixelcode },
      );

      try {
        shader = new GL.Shader(Shader.SCREEN_VERTEX_SHADER, final_pixel_code);
        this.boxcolor = '#00FF00';
      } catch (err) {
        //console.log("Error compiling shader: ", err, final_pixel_code );
        GL.Shader.dumpErrorToConsole(
          err,
          Shader.SCREEN_VERTEX_SHADER,
          final_pixel_code,
        );
        this.boxcolor = '#FF0000';
        this.has_error = true;
        return;
      }
      this._shader = shader;
      this._shader_code = uvcode + '|' + pixelcode;
    }

    if (!this._shader) return;

    var value = this.getInputData(2);
    if (value != null) {
      this.properties.value = value;
    } else {
      value = parseFloat(this.properties.value);
    }

    var time = this.graph.getTime();

    this._tex.drawTo(function () {
      gl.disable(gl.DEPTH_TEST);
      gl.disable(gl.CULL_FACE);
      gl.disable(gl.BLEND);
      if (tex) {
        tex.bind(0);
      }
      if (texB) {
        texB.bind(1);
      }
      var mesh = Mesh.getScreenQuad();
      shader
        .uniforms({
          u_texture: 0,
          u_textureB: 1,
          value: value,
          texSize: [width, height, 1 / width, 1 / height],
          time: time,
        })
        .draw(mesh);
    });

    this.setOutputData(0, this._tex);
  };

  LGraphTextureOperation.pixel_shader =
    'precision highp float;\n\
  \n\
  uniform sampler2D u_texture;\n\
  uniform sampler2D u_textureB;\n\
  varying vec2 v_coord;\n\
  uniform vec4 texSize;\n\
  uniform float time;\n\
  uniform float value;\n\
  \n\
  void main() {\n\
    vec2 uv = v_coord;\n\
    {{UV_CODE}};\n\
    vec4 color4 = texture2D(u_texture, uv);\n\
    vec3 color = color4.rgb;\n\
    vec4 color4B = texture2D(u_textureB, uv);\n\
    vec3 colorB = color4B.rgb;\n\
    vec3 result = color;\n\
    float alpha = 1.0;\n\
    {{PIXEL_CODE}};\n\
    gl_FragColor = vec4(result, alpha);\n\
  }\n\
  ';

  LGraphTextureOperation.registerPreset = function (name, code) {
    LGraphTextureOperation.presets[name] = code;
  };

  LGraphTextureOperation.registerPreset('', '');
  LGraphTextureOperation.registerPreset('bypass', 'color');
  LGraphTextureOperation.registerPreset('add', 'color + colorB * value');
  LGraphTextureOperation.registerPreset(
    'substract',
    '(color - colorB) * value',
  );
  LGraphTextureOperation.registerPreset(
    'mate',
    'mix( color, colorB, color4B.a * value)',
  );
  LGraphTextureOperation.registerPreset('invert', 'vec3(1.0) - color');
  LGraphTextureOperation.registerPreset('multiply', 'color * colorB * value');
  LGraphTextureOperation.registerPreset('divide', '(color / colorB) / value');
  LGraphTextureOperation.registerPreset(
    'difference',
    'abs(color - colorB) * value',
  );
  LGraphTextureOperation.registerPreset('max', 'max(color, colorB) * value');
  LGraphTextureOperation.registerPreset('min', 'min(color, colorB) * value');
  LGraphTextureOperation.registerPreset(
    'displace',
    'texture2D(u_texture, uv + (colorB.xy - vec2(0.5)) * value).xyz',
  );
  LGraphTextureOperation.registerPreset(
    'grayscale',
    'vec3(color.x + color.y + color.z) * value / 3.0',
  );
  LGraphTextureOperation.registerPreset(
    'saturation',
    'mix( vec3(color.x + color.y + color.z) / 3.0, color, value )',
  );
  LGraphTextureOperation.registerPreset(
    'normalmap',
    '\n\
  float z0 = texture2D(u_texture, uv + vec2(-texSize.z, -texSize.w) ).x;\n\
  float z1 = texture2D(u_texture, uv + vec2(0.0, -texSize.w) ).x;\n\
  float z2 = texture2D(u_texture, uv + vec2(texSize.z, -texSize.w) ).x;\n\
  float z3 = texture2D(u_texture, uv + vec2(-texSize.z, 0.0) ).x;\n\
  float z4 = color.x;\n\
  float z5 = texture2D(u_texture, uv + vec2(texSize.z, 0.0) ).x;\n\
  float z6 = texture2D(u_texture, uv + vec2(-texSize.z, texSize.w) ).x;\n\
  float z7 = texture2D(u_texture, uv + vec2(0.0, texSize.w) ).x;\n\
  float z8 = texture2D(u_texture, uv + vec2(texSize.z, texSize.w) ).x;\n\
  vec3 normal = vec3( z2 + 2.0*z4 + z7 - z0 - 2.0*z3 - z5, z5 + 2.0*z6 + z7 -z0 - 2.0*z1 - z2, 1.0 );\n\
  normal.xy *= value;\n\
  result.xyz = normalize(normal) * 0.5 + vec3(0.5);\n\
',
  );
  LGraphTextureOperation.registerPreset(
    'threshold',
    'vec3(color.x > colorB.x * value ? 1.0 : 0.0,color.y > colorB.y * value ? 1.0 : 0.0,color.z > colorB.z * value ? 1.0 : 0.0)',
  );

  //webglstudio stuff...
  LGraphTextureOperation.prototype.onInspect = function (widgets) {
    var that = this;
    widgets.addCombo('Presets', '', {
      values: Object.keys(LGraphTextureOperation.presets),
      callback: function (v) {
        var code = LGraphTextureOperation.presets[v];
        if (!code) return;
        that.setProperty('pixelcode', code);
        that.title = v;
        widgets.refresh();
      },
    });
  };

  LiteGraph.registerNodeType('texture/operation', LGraphTextureOperation);

  //****************************************************

  function LGraphTextureShader() {
    this.addOutput('out', 'Texture');
    this.properties = {
      code: '',
      u_value: 1,
      u_color: [1, 1, 1, 1],
      width: 512,
      height: 512,
      precision: LGraphTexture.DEFAULT,
    };

    this.properties.code = LGraphTextureShader.pixel_shader;
    this._uniforms = {
      u_value: 1,
      u_color: vec4.create(),
      in_texture: 0,
      texSize: vec4.create(),
      time: 0,
    };
  }

  LGraphTextureShader.title = 'Shader';
  LGraphTextureShader.desc = 'Texture shader';
  LGraphTextureShader.widgets_info = {
    code: { type: 'code', lang: 'glsl' },
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureShader.prototype.onPropertyChanged = function (name, value) {
    if (name != 'code') {
      return;
    }

    var shader = this.getShader();
    if (!shader) {
      return;
    }

    //update connections
    var uniforms = shader.uniformInfo;

    //remove deprecated slots
    if (this.inputs) {
      var already = {};
      for (var i = 0; i < this.inputs.length; ++i) {
        var info = this.getInputInfo(i);
        if (!info) {
          continue;
        }

        if (uniforms[info.name] && !already[info.name]) {
          already[info.name] = true;
          continue;
        }
        this.removeInput(i);
        i--;
      }
    }

    //update existing ones
    for (var i in uniforms) {
      var info = shader.uniformInfo[i];
      if (info.loc === null) {
        continue;
      } //is an attribute, not a uniform
      if (i == 'time') {
        //default one
        continue;
      }

      var type = 'number';
      if (this._shader.samplers[i]) {
        type = 'texture';
      } else {
        switch (info.size) {
          case 1:
            type = 'number';
            break;
          case 2:
            type = 'vec2';
            break;
          case 3:
            type = 'vec3';
            break;
          case 4:
            type = 'vec4';
            break;
          case 9:
            type = 'mat3';
            break;
          case 16:
            type = 'mat4';
            break;
          default:
            continue;
        }
      }

      var slot = this.findInputSlot(i);
      if (slot == -1) {
        this.addInput(i, type);
        continue;
      }

      var input_info = this.getInputInfo(slot);
      if (!input_info) {
        this.addInput(i, type);
      } else {
        if (input_info.type == type) {
          continue;
        }
        this.removeInput(slot, type);
        this.addInput(i, type);
      }
    }
  };

  LGraphTextureShader.prototype.getShader = function () {
    //replug
    if (this._shader && this._shader_code == this.properties.code) {
      return this._shader;
    }

    this._shader_code = this.properties.code;
    this._shader = new GL.Shader(
      Shader.SCREEN_VERTEX_SHADER,
      this.properties.code,
    );
    if (!this._shader) {
      this.boxcolor = 'red';
      return null;
    } else {
      this.boxcolor = 'green';
    }
    return this._shader;
  };

  LGraphTextureShader.prototype.onExecute = function () {
    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    var shader = this.getShader();
    if (!shader) {
      return;
    }

    var tex_slot = 0;
    var in_tex = null;

    //set uniforms
    if (this.inputs)
      for (var i = 0; i < this.inputs.length; ++i) {
        var info = this.getInputInfo(i);
        var data = this.getInputData(i);
        if (data == null) {
          continue;
        }

        if (data.constructor === GL.Texture) {
          data.bind(tex_slot);
          if (!in_tex) {
            in_tex = data;
          }
          data = tex_slot;
          tex_slot++;
        }
        shader.setUniform(info.name, data); //data is tex_slot
      }

    var uniforms = this._uniforms;
    var type = LGraphTexture.getTextureType(this.properties.precision, in_tex);

    //render to texture
    var w = this.properties.width | 0;
    var h = this.properties.height | 0;
    if (w == 0) {
      w = in_tex ? in_tex.width : gl.canvas.width;
    }
    if (h == 0) {
      h = in_tex ? in_tex.height : gl.canvas.height;
    }
    uniforms.texSize[0] = w;
    uniforms.texSize[1] = h;
    uniforms.texSize[2] = 1 / w;
    uniforms.texSize[3] = 1 / h;
    uniforms.time = this.graph.getTime();
    uniforms.u_value = this.properties.u_value;
    uniforms.u_color.set(this.properties.u_color);

    if (
      !this._tex ||
      this._tex.type != type ||
      this._tex.width != w ||
      this._tex.height != h
    ) {
      this._tex = new GL.Texture(w, h, {
        type: type,
        format: gl.RGBA,
        filter: gl.LINEAR,
      });
    }
    var tex = this._tex;
    tex.drawTo(function () {
      shader.uniforms(uniforms).draw(GL.Mesh.getScreenQuad());
    });

    this.setOutputData(0, this._tex);
  };

  LGraphTextureShader.pixel_shader =
    'precision highp float;\n\
\n\
varying vec2 v_coord;\n\
uniform float time; //time in seconds\n\
uniform vec4 texSize; //tex resolution\n\
uniform float u_value;\n\
uniform vec4 u_color;\n\n\
void main() {\n\
vec2 uv = v_coord;\n\
vec3 color = vec3(0.0);\n\
//your code here\n\
color.xy=uv;\n\n\
gl_FragColor = vec4(color, 1.0);\n\
}\n\
';

  LiteGraph.registerNodeType('texture/shader', LGraphTextureShader);

  // Texture Scale Offset

  function LGraphTextureScaleOffset() {
    this.addInput('in', 'Texture');
    this.addInput('scale', 'vec2');
    this.addInput('offset', 'vec2');
    this.addOutput('out', 'Texture');
    this.properties = {
      offset: vec2.fromValues(0, 0),
      scale: vec2.fromValues(1, 1),
      precision: LGraphTexture.DEFAULT,
    };
  }

  LGraphTextureScaleOffset.widgets_info = {
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureScaleOffset.title = 'Scale/Offset';
  LGraphTextureScaleOffset.desc = 'Applies an scaling and offseting';

  LGraphTextureScaleOffset.prototype.onExecute = function () {
    var tex = this.getInputData(0);

    if (!this.isOutputConnected(0) || !tex) {
      return;
    } //saves work

    if (this.properties.precision === LGraphTexture.PASS_THROUGH) {
      this.setOutputData(0, tex);
      return;
    }

    var width = tex.width;
    var height = tex.height;
    var type =
      this.precision === LGraphTexture.LOW
        ? gl.UNSIGNED_BYTE
        : gl.HIGH_PRECISION_FORMAT;
    if (this.precision === LGraphTexture.DEFAULT) {
      type = tex.type;
    }

    if (
      !this._tex ||
      this._tex.width != width ||
      this._tex.height != height ||
      this._tex.type != type
    ) {
      this._tex = new GL.Texture(width, height, {
        type: type,
        format: gl.RGBA,
        filter: gl.LINEAR,
      });
    }

    var shader = this._shader;

    if (!shader) {
      shader = new GL.Shader(
        GL.Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureScaleOffset.pixel_shader,
      );
    }

    var scale = this.getInputData(1);
    if (scale) {
      this.properties.scale[0] = scale[0];
      this.properties.scale[1] = scale[1];
    } else {
      scale = this.properties.scale;
    }

    var offset = this.getInputData(2);
    if (offset) {
      this.properties.offset[0] = offset[0];
      this.properties.offset[1] = offset[1];
    } else {
      offset = this.properties.offset;
    }

    this._tex.drawTo(function () {
      gl.disable(gl.DEPTH_TEST);
      gl.disable(gl.CULL_FACE);
      gl.disable(gl.BLEND);
      tex.bind(0);
      var mesh = Mesh.getScreenQuad();
      shader
        .uniforms({
          u_texture: 0,
          u_scale: scale,
          u_offset: offset,
        })
        .draw(mesh);
    });

    this.setOutputData(0, this._tex);
  };

  LGraphTextureScaleOffset.pixel_shader =
    'precision highp float;\n\
  \n\
  uniform sampler2D u_texture;\n\
  uniform sampler2D u_textureB;\n\
  varying vec2 v_coord;\n\
  uniform vec2 u_scale;\n\
  uniform vec2 u_offset;\n\
  \n\
  void main() {\n\
    vec2 uv = v_coord;\n\
    uv = uv / u_scale - u_offset;\n\
    gl_FragColor = texture2D(u_texture, uv);\n\
  }\n\
  ';

  LiteGraph.registerNodeType('texture/scaleOffset', LGraphTextureScaleOffset);

  // Warp (distort a texture) *************************

  function LGraphTextureWarp() {
    this.addInput('in', 'Texture');
    this.addInput('warp', 'Texture');
    this.addInput('factor', 'number');
    this.addOutput('out', 'Texture');
    this.properties = {
      factor: 0.01,
      scale: [1, 1],
      offset: [0, 0],
      precision: LGraphTexture.DEFAULT,
    };

    this._uniforms = {
      u_texture: 0,
      u_textureB: 1,
      u_factor: 1,
      u_scale: vec2.create(),
      u_offset: vec2.create(),
    };
  }

  LGraphTextureWarp.widgets_info = {
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureWarp.title = 'Warp';
  LGraphTextureWarp.desc = 'Texture warp operation';

  LGraphTextureWarp.prototype.onExecute = function () {
    var tex = this.getInputData(0);

    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    if (this.properties.precision === LGraphTexture.PASS_THROUGH) {
      this.setOutputData(0, tex);
      return;
    }

    var texB = this.getInputData(1);

    var width = 512;
    var height = 512;
    var type = gl.UNSIGNED_BYTE;
    if (tex) {
      width = tex.width;
      height = tex.height;
      type = tex.type;
    } else if (texB) {
      width = texB.width;
      height = texB.height;
      type = texB.type;
    }

    if (!tex && !this._tex) {
      this._tex = new GL.Texture(width, height, {
        type:
          this.precision === LGraphTexture.LOW
            ? gl.UNSIGNED_BYTE
            : gl.HIGH_PRECISION_FORMAT,
        format: gl.RGBA,
        filter: gl.LINEAR,
      });
    } else {
      this._tex = LGraphTexture.getTargetTexture(
        tex || this._tex,
        this._tex,
        this.properties.precision,
      );
    }

    var shader = this._shader;

    if (!shader) {
      shader = new GL.Shader(
        GL.Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureWarp.pixel_shader,
      );
    }

    var factor = this.getInputData(2);
    if (factor != null) {
      this.properties.factor = factor;
    } else {
      factor = parseFloat(this.properties.factor);
    }
    var uniforms = this._uniforms;
    uniforms.u_factor = factor;
    uniforms.u_scale.set(this.properties.scale);
    uniforms.u_offset.set(this.properties.offset);

    this._tex.drawTo(function () {
      gl.disable(gl.DEPTH_TEST);
      gl.disable(gl.CULL_FACE);
      gl.disable(gl.BLEND);
      if (tex) {
        tex.bind(0);
      }
      if (texB) {
        texB.bind(1);
      }
      var mesh = Mesh.getScreenQuad();
      shader.uniforms(uniforms).draw(mesh);
    });

    this.setOutputData(0, this._tex);
  };

  LGraphTextureWarp.pixel_shader =
    'precision highp float;\n\
  \n\
  uniform sampler2D u_texture;\n\
  uniform sampler2D u_textureB;\n\
  varying vec2 v_coord;\n\
  uniform float u_factor;\n\
  uniform vec2 u_scale;\n\
  uniform vec2 u_offset;\n\
  \n\
  void main() {\n\
    vec2 uv = v_coord;\n\
    uv += ( texture2D(u_textureB, uv).rg - vec2(0.5)) * u_factor * u_scale + u_offset;\n\
    gl_FragColor = texture2D(u_texture, uv);\n\
  }\n\
  ';

  LiteGraph.registerNodeType('texture/warp', LGraphTextureWarp);

  //****************************************************

  // Texture to Viewport *****************************************
  function LGraphTextureToViewport() {
    this.addInput('Texture', 'Texture');
    this.properties = {
      additive: false,
      antialiasing: false,
      filter: true,
      disable_alpha: false,
      gamma: 1.0,
      viewport: [0, 0, 1, 1],
    };
    this.size[0] = 130;
  }

  LGraphTextureToViewport.title = 'to Viewport';
  LGraphTextureToViewport.desc = 'Texture to viewport';

  LGraphTextureToViewport._prev_viewport = new Float32Array(4);

  LGraphTextureToViewport.prototype.onDrawBackground = function (ctx) {
    if (this.flags.collapsed || this.size[1] <= 40) return;

    var tex = this.getInputData(0);
    if (!tex) {
      return;
    }

    ctx.drawImage(
      ctx == gl ? tex : gl.canvas,
      10,
      30,
      this.size[0] - 20,
      this.size[1] - 40,
    );
  };

  LGraphTextureToViewport.prototype.onExecute = function () {
    var tex = this.getInputData(0);
    if (!tex) {
      return;
    }

    if (this.properties.disable_alpha) {
      gl.disable(gl.BLEND);
    } else {
      gl.enable(gl.BLEND);
      if (this.properties.additive) {
        gl.blendFunc(gl.SRC_ALPHA, gl.ONE);
      } else {
        gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
      }
    }

    gl.disable(gl.DEPTH_TEST);
    var gamma = this.properties.gamma || 1.0;
    if (this.isInputConnected(1)) {
      gamma = this.getInputData(1);
    }

    tex.setParameter(
      gl.TEXTURE_MAG_FILTER,
      this.properties.filter ? gl.LINEAR : gl.NEAREST,
    );

    var old_viewport = LGraphTextureToViewport._prev_viewport;
    old_viewport.set(gl.viewport_data);
    var new_view = this.properties.viewport;
    gl.viewport(
      old_viewport[0] + old_viewport[2] * new_view[0],
      old_viewport[1] + old_viewport[3] * new_view[1],
      old_viewport[2] * new_view[2],
      old_viewport[3] * new_view[3],
    );
    var viewport = gl.getViewport(); //gl.getParameter(gl.VIEWPORT);

    if (this.properties.antialiasing) {
      if (!LGraphTextureToViewport._shader) {
        LGraphTextureToViewport._shader = new GL.Shader(
          GL.Shader.SCREEN_VERTEX_SHADER,
          LGraphTextureToViewport.aa_pixel_shader,
        );
      }

      var mesh = Mesh.getScreenQuad();
      tex.bind(0);
      LGraphTextureToViewport._shader
        .uniforms({
          u_texture: 0,
          uViewportSize: [tex.width, tex.height],
          u_igamma: 1 / gamma,
          inverseVP: [1 / tex.width, 1 / tex.height],
        })
        .draw(mesh);
    } else {
      if (gamma != 1.0) {
        if (!LGraphTextureToViewport._gamma_shader) {
          LGraphTextureToViewport._gamma_shader = new GL.Shader(
            Shader.SCREEN_VERTEX_SHADER,
            LGraphTextureToViewport.gamma_pixel_shader,
          );
        }
        tex.toViewport(LGraphTextureToViewport._gamma_shader, {
          u_texture: 0,
          u_igamma: 1 / gamma,
        });
      } else {
        tex.toViewport();
      }
    }

    gl.viewport(
      old_viewport[0],
      old_viewport[1],
      old_viewport[2],
      old_viewport[3],
    );
  };

  LGraphTextureToViewport.prototype.onGetInputs = function () {
    return [['gamma', 'number']];
  };

  LGraphTextureToViewport.aa_pixel_shader =
    'precision highp float;\n\
  precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_texture;\n\
  uniform vec2 uViewportSize;\n\
  uniform vec2 inverseVP;\n\
  uniform float u_igamma;\n\
  #define FXAA_REDUCE_MIN   (1.0/ 128.0)\n\
  #define FXAA_REDUCE_MUL   (1.0 / 8.0)\n\
  #define FXAA_SPAN_MAX     8.0\n\
  \n\
  /* from mitsuhiko/webgl-meincraft based on the code on geeks3d.com */\n\
  vec4 applyFXAA(sampler2D tex, vec2 fragCoord)\n\
  {\n\
    vec4 color = vec4(0.0);\n\
    /*vec2 inverseVP = vec2(1.0 / uViewportSize.x, 1.0 / uViewportSize.y);*/\n\
    vec3 rgbNW = texture2D(tex, (fragCoord + vec2(-1.0, -1.0)) * inverseVP).xyz;\n\
    vec3 rgbNE = texture2D(tex, (fragCoord + vec2(1.0, -1.0)) * inverseVP).xyz;\n\
    vec3 rgbSW = texture2D(tex, (fragCoord + vec2(-1.0, 1.0)) * inverseVP).xyz;\n\
    vec3 rgbSE = texture2D(tex, (fragCoord + vec2(1.0, 1.0)) * inverseVP).xyz;\n\
    vec3 rgbM  = texture2D(tex, fragCoord  * inverseVP).xyz;\n\
    vec3 luma = vec3(0.299, 0.587, 0.114);\n\
    float lumaNW = dot(rgbNW, luma);\n\
    float lumaNE = dot(rgbNE, luma);\n\
    float lumaSW = dot(rgbSW, luma);\n\
    float lumaSE = dot(rgbSE, luma);\n\
    float lumaM  = dot(rgbM,  luma);\n\
    float lumaMin = min(lumaM, min(min(lumaNW, lumaNE), min(lumaSW, lumaSE)));\n\
    float lumaMax = max(lumaM, max(max(lumaNW, lumaNE), max(lumaSW, lumaSE)));\n\
    \n\
    vec2 dir;\n\
    dir.x = -((lumaNW + lumaNE) - (lumaSW + lumaSE));\n\
    dir.y =  ((lumaNW + lumaSW) - (lumaNE + lumaSE));\n\
    \n\
    float dirReduce = max((lumaNW + lumaNE + lumaSW + lumaSE) * (0.25 * FXAA_REDUCE_MUL), FXAA_REDUCE_MIN);\n\
    \n\
    float rcpDirMin = 1.0 / (min(abs(dir.x), abs(dir.y)) + dirReduce);\n\
    dir = min(vec2(FXAA_SPAN_MAX, FXAA_SPAN_MAX), max(vec2(-FXAA_SPAN_MAX, -FXAA_SPAN_MAX), dir * rcpDirMin)) * inverseVP;\n\
    \n\
    vec3 rgbA = 0.5 * (texture2D(tex, fragCoord * inverseVP + dir * (1.0 / 3.0 - 0.5)).xyz + \n\
      texture2D(tex, fragCoord * inverseVP + dir * (2.0 / 3.0 - 0.5)).xyz);\n\
    vec3 rgbB = rgbA * 0.5 + 0.25 * (texture2D(tex, fragCoord * inverseVP + dir * -0.5).xyz + \n\
      texture2D(tex, fragCoord * inverseVP + dir * 0.5).xyz);\n\
    \n\
    //return vec4(rgbA,1.0);\n\
    float lumaB = dot(rgbB, luma);\n\
    if ((lumaB < lumaMin) || (lumaB > lumaMax))\n\
      color = vec4(rgbA, 1.0);\n\
    else\n\
      color = vec4(rgbB, 1.0);\n\
    if(u_igamma != 1.0)\n\
      color.xyz = pow( color.xyz, vec3(u_igamma) );\n\
    return color;\n\
  }\n\
  \n\
  void main() {\n\
     gl_FragColor = applyFXAA( u_texture, v_coord * uViewportSize) ;\n\
  }\n\
  ';

  LGraphTextureToViewport.gamma_pixel_shader =
    'precision highp float;\n\
  precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_texture;\n\
  uniform float u_igamma;\n\
  void main() {\n\
    vec4 color = texture2D( u_texture, v_coord);\n\
    color.xyz = pow(color.xyz, vec3(u_igamma) );\n\
     gl_FragColor = color;\n\
  }\n\
  ';

  LiteGraph.registerNodeType('texture/toviewport', LGraphTextureToViewport);

  // Texture Copy *****************************************
  function LGraphTextureCopy() {
    this.addInput('Texture', 'Texture');
    this.addOutput('', 'Texture');
    this.properties = {
      size: 0,
      generate_mipmaps: false,
      precision: LGraphTexture.DEFAULT,
    };
  }

  LGraphTextureCopy.title = 'Copy';
  LGraphTextureCopy.desc = 'Copy Texture';
  LGraphTextureCopy.widgets_info = {
    size: {
      widget: 'combo',
      values: [0, 32, 64, 128, 256, 512, 1024, 2048],
    },
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureCopy.prototype.onExecute = function () {
    var tex = this.getInputData(0);
    if (!tex && !this._temp_texture) {
      return;
    }

    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    //copy the texture
    if (tex) {
      var width = tex.width;
      var height = tex.height;

      if (this.properties.size != 0) {
        width = this.properties.size;
        height = this.properties.size;
      }

      var temp = this._temp_texture;

      var type = tex.type;
      if (this.properties.precision === LGraphTexture.LOW) {
        type = gl.UNSIGNED_BYTE;
      } else if (this.properties.precision === LGraphTexture.HIGH) {
        type = gl.HIGH_PRECISION_FORMAT;
      }

      if (
        !temp ||
        temp.width != width ||
        temp.height != height ||
        temp.type != type
      ) {
        var minFilter = gl.LINEAR;
        if (
          this.properties.generate_mipmaps &&
          isPowerOfTwo(width) &&
          isPowerOfTwo(height)
        ) {
          minFilter = gl.LINEAR_MIPMAP_LINEAR;
        }
        this._temp_texture = new GL.Texture(width, height, {
          type: type,
          format: gl.RGBA,
          minFilter: minFilter,
          magFilter: gl.LINEAR,
        });
      }
      tex.copyTo(this._temp_texture);

      if (this.properties.generate_mipmaps) {
        this._temp_texture.bind(0);
        gl.generateMipmap(this._temp_texture.texture_type);
        this._temp_texture.unbind(0);
      }
    }

    this.setOutputData(0, this._temp_texture);
  };

  LiteGraph.registerNodeType('texture/copy', LGraphTextureCopy);

  // Texture Downsample *****************************************
  function LGraphTextureDownsample() {
    this.addInput('Texture', 'Texture');
    this.addOutput('', 'Texture');
    this.properties = {
      iterations: 1,
      generate_mipmaps: false,
      precision: LGraphTexture.DEFAULT,
    };
  }

  LGraphTextureDownsample.title = 'Downsample';
  LGraphTextureDownsample.desc = 'Downsample Texture';
  LGraphTextureDownsample.widgets_info = {
    iterations: { type: 'number', step: 1, precision: 0, min: 0 },
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureDownsample.prototype.onExecute = function () {
    var tex = this.getInputData(0);
    if (!tex && !this._temp_texture) {
      return;
    }

    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    //we do not allow any texture different than texture 2D
    if (!tex || tex.texture_type !== GL.TEXTURE_2D) {
      return;
    }

    if (this.properties.iterations < 1) {
      this.setOutputData(0, tex);
      return;
    }

    var shader = LGraphTextureDownsample._shader;
    if (!shader) {
      LGraphTextureDownsample._shader = shader = new GL.Shader(
        GL.Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureDownsample.pixel_shader,
      );
    }

    var width = tex.width | 0;
    var height = tex.height | 0;
    var type = tex.type;
    if (this.properties.precision === LGraphTexture.LOW) {
      type = gl.UNSIGNED_BYTE;
    } else if (this.properties.precision === LGraphTexture.HIGH) {
      type = gl.HIGH_PRECISION_FORMAT;
    }
    var iterations = this.properties.iterations || 1;

    var origin = tex;
    var target = null;

    var temp = [];
    var options = {
      type: type,
      format: tex.format,
    };

    var offset = vec2.create();
    var uniforms = {
      u_offset: offset,
    };

    if (this._texture) {
      GL.Texture.releaseTemporary(this._texture);
    }

    for (var i = 0; i < iterations; ++i) {
      offset[0] = 1 / width;
      offset[1] = 1 / height;
      width = width >> 1 || 0;
      height = height >> 1 || 0;
      target = GL.Texture.getTemporary(width, height, options);
      temp.push(target);
      origin.setParameter(GL.TEXTURE_MAG_FILTER, GL.NEAREST);
      origin.copyTo(target, shader, uniforms);
      if (width == 1 && height == 1) {
        break;
      } //nothing else to do
      origin = target;
    }

    //keep the last texture used
    this._texture = temp.pop();

    //free the rest
    for (var i = 0; i < temp.length; ++i) {
      GL.Texture.releaseTemporary(temp[i]);
    }

    if (this.properties.generate_mipmaps) {
      this._texture.bind(0);
      gl.generateMipmap(this._texture.texture_type);
      this._texture.unbind(0);
    }

    this.setOutputData(0, this._texture);
  };

  LGraphTextureDownsample.pixel_shader =
    'precision highp float;\n\
  precision highp float;\n\
  uniform sampler2D u_texture;\n\
  uniform vec2 u_offset;\n\
  varying vec2 v_coord;\n\
  \n\
  void main() {\n\
    vec4 color = texture2D(u_texture, v_coord );\n\
    color += texture2D(u_texture, v_coord + vec2( u_offset.x, 0.0 ) );\n\
    color += texture2D(u_texture, v_coord + vec2( 0.0, u_offset.y ) );\n\
    color += texture2D(u_texture, v_coord + vec2( u_offset.x, u_offset.y ) );\n\
     gl_FragColor = color * 0.25;\n\
  }\n\
  ';

  LiteGraph.registerNodeType('texture/downsample', LGraphTextureDownsample);

  function LGraphTextureResize() {
    this.addInput('Texture', 'Texture');
    this.addOutput('', 'Texture');
    this.properties = {
      size: [512, 512],
      generate_mipmaps: false,
      precision: LGraphTexture.DEFAULT,
    };
  }

  LGraphTextureResize.title = 'Resize';
  LGraphTextureResize.desc = 'Resize Texture';
  LGraphTextureResize.widgets_info = {
    iterations: { type: 'number', step: 1, precision: 0, min: 0 },
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureResize.prototype.onExecute = function () {
    var tex = this.getInputData(0);
    if (!tex && !this._temp_texture) {
      return;
    }

    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    //we do not allow any texture different than texture 2D
    if (!tex || tex.texture_type !== GL.TEXTURE_2D) {
      return;
    }

    var width = this.properties.size[0] | 0;
    var height = this.properties.size[1] | 0;
    if (width == 0) width = tex.width;
    if (height == 0) height = tex.height;
    var type = tex.type;
    if (this.properties.precision === LGraphTexture.LOW) {
      type = gl.UNSIGNED_BYTE;
    } else if (this.properties.precision === LGraphTexture.HIGH) {
      type = gl.HIGH_PRECISION_FORMAT;
    }

    if (
      !this._texture ||
      this._texture.width != width ||
      this._texture.height != height ||
      this._texture.type != type
    )
      this._texture = new GL.Texture(width, height, { type: type });

    tex.copyTo(this._texture);

    if (this.properties.generate_mipmaps) {
      this._texture.bind(0);
      gl.generateMipmap(this._texture.texture_type);
      this._texture.unbind(0);
    }

    this.setOutputData(0, this._texture);
  };

  LiteGraph.registerNodeType('texture/resize', LGraphTextureResize);

  // Texture Average  *****************************************
  function LGraphTextureAverage() {
    this.addInput('Texture', 'Texture');
    this.addOutput('tex', 'Texture');
    this.addOutput('avg', 'vec4');
    this.addOutput('lum', 'number');
    this.properties = {
      use_previous_frame: true, //to avoid stalls
      high_quality: false, //to use as much pixels as possible
    };

    this._uniforms = {
      u_texture: 0,
      u_mipmap_offset: 0,
    };
    this._luminance = new Float32Array(4);
  }

  LGraphTextureAverage.title = 'Average';
  LGraphTextureAverage.desc =
    'Compute a partial average (32 random samples) of a texture and stores it as a 1x1 pixel texture.\n If high_quality is true, then it generates the mipmaps first and reads from the lower one.';

  LGraphTextureAverage.prototype.onExecute = function () {
    if (!this.properties.use_previous_frame) {
      this.updateAverage();
    }

    var v = this._luminance;
    this.setOutputData(0, this._temp_texture);
    this.setOutputData(1, v);
    this.setOutputData(2, (v[0] + v[1] + v[2]) / 3);
  };

  //executed before rendering the frame
  LGraphTextureAverage.prototype.onPreRenderExecute = function () {
    this.updateAverage();
  };

  LGraphTextureAverage.prototype.updateAverage = function () {
    var tex = this.getInputData(0);
    if (!tex) {
      return;
    }

    if (
      !this.isOutputConnected(0) &&
      !this.isOutputConnected(1) &&
      !this.isOutputConnected(2)
    ) {
      return;
    } //saves work

    if (!LGraphTextureAverage._shader) {
      LGraphTextureAverage._shader = new GL.Shader(
        GL.Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureAverage.pixel_shader,
      );
      //creates 256 random numbers and stores them in two mat4
      var samples = new Float32Array(16);
      for (var i = 0; i < samples.length; ++i) {
        samples[i] = Math.random(); //poorly distributed samples
      }
      //upload only once
      LGraphTextureAverage._shader.uniforms({
        u_samples_a: samples.subarray(0, 16),
        u_samples_b: samples.subarray(16, 32),
      });
    }

    var temp = this._temp_texture;
    var type = gl.UNSIGNED_BYTE;
    if (tex.type != type) {
      //force floats, half floats cannot be read with gl.readPixels
      type = gl.FLOAT;
    }

    if (!temp || temp.type != type) {
      this._temp_texture = new GL.Texture(1, 1, {
        type: type,
        format: gl.RGBA,
        filter: gl.NEAREST,
      });
    }

    this._uniforms.u_mipmap_offset = 0;

    if (this.properties.high_quality) {
      if (!this._temp_pot2_texture || this._temp_pot2_texture.type != type)
        this._temp_pot2_texture = new GL.Texture(512, 512, {
          type: type,
          format: gl.RGBA,
          minFilter: gl.LINEAR_MIPMAP_LINEAR,
          magFilter: gl.LINEAR,
        });

      tex.copyTo(this._temp_pot2_texture);
      tex = this._temp_pot2_texture;
      tex.bind(0);
      gl.generateMipmap(GL.TEXTURE_2D);
      this._uniforms.u_mipmap_offset = 9;
    }

    var shader = LGraphTextureAverage._shader;
    var uniforms = this._uniforms;
    uniforms.u_mipmap_offset = this.properties.mipmap_offset;
    gl.disable(gl.DEPTH_TEST);
    gl.disable(gl.BLEND);
    this._temp_texture.drawTo(function () {
      tex.toViewport(shader, uniforms);
    });

    if (this.isOutputConnected(1) || this.isOutputConnected(2)) {
      var pixel = this._temp_texture.getPixels();
      if (pixel) {
        var v = this._luminance;
        var type = this._temp_texture.type;
        v.set(pixel);
        if (type == gl.UNSIGNED_BYTE) {
          vec4.scale(v, v, 1 / 255);
        } else if (type == GL.HALF_FLOAT || type == GL.HALF_FLOAT_OES) {
          //no half floats possible, hard to read back unless copyed to a FLOAT texture, so temp_texture is always forced to FLOAT
        }
      }
    }
  };

  LGraphTextureAverage.pixel_shader =
    'precision highp float;\n\
  precision highp float;\n\
  uniform mat4 u_samples_a;\n\
  uniform mat4 u_samples_b;\n\
  uniform sampler2D u_texture;\n\
  uniform float u_mipmap_offset;\n\
  varying vec2 v_coord;\n\
  \n\
  void main() {\n\
    vec4 color = vec4(0.0);\n\
    //random average\n\
    for(int i = 0; i < 4; ++i)\n\
      for(int j = 0; j < 4; ++j)\n\
      {\n\
        color += texture2D(u_texture, vec2( u_samples_a[i][j], u_samples_b[i][j] ), u_mipmap_offset );\n\
        color += texture2D(u_texture, vec2( 1.0 - u_samples_a[i][j], 1.0 - u_samples_b[i][j] ), u_mipmap_offset );\n\
      }\n\
     gl_FragColor = color * 0.03125;\n\
  }\n\
  ';

  LiteGraph.registerNodeType('texture/average', LGraphTextureAverage);

  // Computes operation between pixels (max, min)  *****************************************
  function LGraphTextureMinMax() {
    this.addInput('Texture', 'Texture');
    this.addOutput('min_t', 'Texture');
    this.addOutput('max_t', 'Texture');
    this.addOutput('min', 'vec4');
    this.addOutput('max', 'vec4');
    this.properties = {
      mode: 'max',
      use_previous_frame: true, //to avoid stalls
    };

    this._uniforms = {
      u_texture: 0,
    };

    this._max = new Float32Array(4);
    this._min = new Float32Array(4);

    this._textures_chain = [];
  }

  LGraphTextureMinMax.widgets_info = {
    mode: { widget: 'combo', values: ['min', 'max', 'avg'] },
  };

  LGraphTextureMinMax.title = 'MinMax';
  LGraphTextureMinMax.desc = 'Compute the scene min max';

  LGraphTextureMinMax.prototype.onExecute = function () {
    if (!this.properties.use_previous_frame) {
      this.update();
    }

    this.setOutputData(0, this._temp_texture);
    this.setOutputData(1, this._luminance);
  };

  //executed before rendering the frame
  LGraphTextureMinMax.prototype.onPreRenderExecute = function () {
    this.update();
  };

  LGraphTextureMinMax.prototype.update = function () {
    var tex = this.getInputData(0);
    if (!tex) {
      return;
    }

    if (!this.isOutputConnected(0) && !this.isOutputConnected(1)) {
      return;
    } //saves work

    if (!LGraphTextureMinMax._shader) {
      LGraphTextureMinMax._shader = new GL.Shader(
        GL.Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureMinMax.pixel_shader,
      );
    }

    var temp = this._temp_texture;
    var type = gl.UNSIGNED_BYTE;
    if (tex.type != type) {
      //force floats, half floats cannot be read with gl.readPixels
      type = gl.FLOAT;
    }

    var size = 512;

    if (!this._textures_chain.length || this._textures_chain[0].type != type) {
      var index = 0;
      while (i) {
        this._textures_chain[i] = new GL.Texture(size, size, {
          type: type,
          format: gl.RGBA,
          filter: gl.NEAREST,
        });
        size = size >> 2;
        i++;
        if (size == 1) break;
      }
    }

    tex.copyTo(this._textures_chain[0]);
    var prev = this._textures_chain[0];
    for (var i = 1; i <= this._textures_chain.length; ++i) {
      var tex = this._textures_chain[i];

      prev = tex;
    }

    var shader = LGraphTextureMinMax._shader;
    var uniforms = this._uniforms;
    uniforms.u_mipmap_offset = this.properties.mipmap_offset;
    gl.disable(gl.DEPTH_TEST);
    gl.disable(gl.BLEND);
    this._temp_texture.drawTo(function () {
      tex.toViewport(shader, uniforms);
    });
  };

  LGraphTextureMinMax.pixel_shader =
    'precision highp float;\n\
  precision highp float;\n\
  uniform mat4 u_samples_a;\n\
  uniform mat4 u_samples_b;\n\
  uniform sampler2D u_texture;\n\
  uniform float u_mipmap_offset;\n\
  varying vec2 v_coord;\n\
  \n\
  void main() {\n\
    vec4 color = vec4(0.0);\n\
    //random average\n\
    for(int i = 0; i < 4; ++i)\n\
      for(int j = 0; j < 4; ++j)\n\
      {\n\
        color += texture2D(u_texture, vec2( u_samples_a[i][j], u_samples_b[i][j] ), u_mipmap_offset );\n\
        color += texture2D(u_texture, vec2( 1.0 - u_samples_a[i][j], 1.0 - u_samples_b[i][j] ), u_mipmap_offset );\n\
      }\n\
     gl_FragColor = color * 0.03125;\n\
  }\n\
  ';

  //LiteGraph.registerNodeType("texture/clustered_operation", LGraphTextureClusteredOperation);

  function LGraphTextureTemporalSmooth() {
    this.addInput('in', 'Texture');
    this.addInput('factor', 'Number');
    this.addOutput('out', 'Texture');
    this.properties = { factor: 0.5 };
    this._uniforms = {
      u_texture: 0,
      u_textureB: 1,
      u_factor: this.properties.factor,
    };
  }

  LGraphTextureTemporalSmooth.title = 'Smooth';
  LGraphTextureTemporalSmooth.desc = 'Smooth texture over time';

  LGraphTextureTemporalSmooth.prototype.onExecute = function () {
    var tex = this.getInputData(0);
    if (!tex || !this.isOutputConnected(0)) {
      return;
    }

    if (!LGraphTextureTemporalSmooth._shader) {
      LGraphTextureTemporalSmooth._shader = new GL.Shader(
        GL.Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureTemporalSmooth.pixel_shader,
      );
    }

    var temp = this._temp_texture;
    if (
      !temp ||
      temp.type != tex.type ||
      temp.width != tex.width ||
      temp.height != tex.height
    ) {
      var options = {
        type: tex.type,
        format: gl.RGBA,
        filter: gl.NEAREST,
      };
      this._temp_texture = new GL.Texture(tex.width, tex.height, options);
      this._temp_texture2 = new GL.Texture(tex.width, tex.height, options);
      tex.copyTo(this._temp_texture2);
    }

    var tempA = this._temp_texture;
    var tempB = this._temp_texture2;

    var shader = LGraphTextureTemporalSmooth._shader;
    var uniforms = this._uniforms;
    uniforms.u_factor = 1.0 - this.getInputOrProperty('factor');

    gl.disable(gl.BLEND);
    gl.disable(gl.DEPTH_TEST);
    tempA.drawTo(function () {
      tempB.bind(1);
      tex.toViewport(shader, uniforms);
    });

    this.setOutputData(0, tempA);

    //swap
    this._temp_texture = tempB;
    this._temp_texture2 = tempA;
  };

  LGraphTextureTemporalSmooth.pixel_shader =
    'precision highp float;\n\
  precision highp float;\n\
  uniform sampler2D u_texture;\n\
  uniform sampler2D u_textureB;\n\
  uniform float u_factor;\n\
  varying vec2 v_coord;\n\
  \n\
  void main() {\n\
    gl_FragColor = mix( texture2D( u_texture, v_coord ), texture2D( u_textureB, v_coord ), u_factor );\n\
  }\n\
  ';

  LiteGraph.registerNodeType(
    'texture/temporal_smooth',
    LGraphTextureTemporalSmooth,
  );

  function LGraphTextureLinearAvgSmooth() {
    this.addInput('in', 'Texture');
    this.addOutput('avg', 'Texture');
    this.addOutput('array', 'Texture');
    this.properties = { samples: 64, frames_interval: 1 };
    this._uniforms = {
      u_texture: 0,
      u_textureB: 1,
      u_samples: this.properties.samples,
      u_isamples: 1 / this.properties.samples,
    };
    this.frame = 0;
  }

  LGraphTextureLinearAvgSmooth.title = 'Lineal Avg Smooth';
  LGraphTextureLinearAvgSmooth.desc = 'Smooth texture linearly over time';

  LGraphTextureLinearAvgSmooth['@samples'] = {
    type: 'number',
    min: 1,
    max: 64,
    step: 1,
    precision: 1,
  };

  LGraphTextureLinearAvgSmooth.prototype.getPreviewTexture = function () {
    return this._temp_texture2;
  };

  LGraphTextureLinearAvgSmooth.prototype.onExecute = function () {
    var tex = this.getInputData(0);
    if (!tex || !this.isOutputConnected(0)) {
      return;
    }

    if (!LGraphTextureLinearAvgSmooth._shader) {
      LGraphTextureLinearAvgSmooth._shader_copy = new GL.Shader(
        GL.Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureLinearAvgSmooth.pixel_shader_copy,
      );
      LGraphTextureLinearAvgSmooth._shader_avg = new GL.Shader(
        GL.Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureLinearAvgSmooth.pixel_shader_avg,
      );
    }

    var samples = clamp(this.properties.samples, 0, 64);
    var frame = this.frame;
    var interval = this.properties.frames_interval;

    if (interval == 0 || frame % interval == 0) {
      var temp = this._temp_texture;
      if (!temp || temp.type != tex.type || temp.width != samples) {
        var options = {
          type: tex.type,
          format: gl.RGBA,
          filter: gl.NEAREST,
        };
        this._temp_texture = new GL.Texture(samples, 1, options);
        this._temp_texture2 = new GL.Texture(samples, 1, options);
        this._temp_texture_out = new GL.Texture(1, 1, options);
      }

      var tempA = this._temp_texture;
      var tempB = this._temp_texture2;

      var shader_copy = LGraphTextureLinearAvgSmooth._shader_copy;
      var shader_avg = LGraphTextureLinearAvgSmooth._shader_avg;
      var uniforms = this._uniforms;
      uniforms.u_samples = samples;
      uniforms.u_isamples = 1.0 / samples;

      gl.disable(gl.BLEND);
      gl.disable(gl.DEPTH_TEST);
      tempA.drawTo(function () {
        tempB.bind(1);
        tex.toViewport(shader_copy, uniforms);
      });

      this._temp_texture_out.drawTo(function () {
        tempA.toViewport(shader_avg, uniforms);
      });

      this.setOutputData(0, this._temp_texture_out);

      //swap
      this._temp_texture = tempB;
      this._temp_texture2 = tempA;
    } else this.setOutputData(0, this._temp_texture_out);
    this.setOutputData(1, this._temp_texture2);
    this.frame++;
  };

  LGraphTextureLinearAvgSmooth.pixel_shader_copy =
    'precision highp float;\n\
  precision highp float;\n\
  uniform sampler2D u_texture;\n\
  uniform sampler2D u_textureB;\n\
  uniform float u_isamples;\n\
  varying vec2 v_coord;\n\
  \n\
  void main() {\n\
    if( v_coord.x <= u_isamples )\n\
      gl_FragColor = texture2D( u_texture, vec2(0.5) );\n\
    else\n\
      gl_FragColor = texture2D( u_textureB, v_coord - vec2(u_isamples,0.0) );\n\
  }\n\
  ';

  LGraphTextureLinearAvgSmooth.pixel_shader_avg =
    'precision highp float;\n\
  precision highp float;\n\
  uniform sampler2D u_texture;\n\
  uniform int u_samples;\n\
  uniform float u_isamples;\n\
  varying vec2 v_coord;\n\
  \n\
  void main() {\n\
    vec4 color = vec4(0.0);\n\
    for(int i = 0; i < 64; ++i)\n\
    {\n\
      color += texture2D( u_texture, vec2( float(i)*u_isamples,0.0) );\n\
      if(i == (u_samples - 1))\n\
        break;\n\
    }\n\
    gl_FragColor = color * u_isamples;\n\
  }\n\
  ';

  LiteGraph.registerNodeType(
    'texture/linear_avg_smooth',
    LGraphTextureLinearAvgSmooth,
  );

  // Image To Texture *****************************************
  function LGraphImageToTexture() {
    this.addInput('Image', 'image');
    this.addOutput('', 'Texture');
    this.properties = {};
  }

  LGraphImageToTexture.title = 'Image to Texture';
  LGraphImageToTexture.desc = 'Uploads an image to the GPU';
  //LGraphImageToTexture.widgets_info = { size: { widget:"combo", values:[0,32,64,128,256,512,1024,2048]} };

  LGraphImageToTexture.prototype.onExecute = function () {
    var img = this.getInputData(0);
    if (!img) {
      return;
    }

    var width = img.videoWidth || img.width;
    var height = img.videoHeight || img.height;

    //this is in case we are using a webgl canvas already, no need to reupload it
    if (img.gltexture) {
      this.setOutputData(0, img.gltexture);
      return;
    }

    var temp = this._temp_texture;
    if (!temp || temp.width != width || temp.height != height) {
      this._temp_texture = new GL.Texture(width, height, {
        format: gl.RGBA,
        filter: gl.LINEAR,
      });
    }

    try {
      this._temp_texture.uploadImage(img);
    } catch (err) {
      console.error(
        'image comes from an unsafe location, cannot be uploaded to webgl: ' +
          err,
      );
      return;
    }

    this.setOutputData(0, this._temp_texture);
  };

  LiteGraph.registerNodeType('texture/imageToTexture', LGraphImageToTexture);

  // Texture LUT *****************************************
  function LGraphTextureLUT() {
    this.addInput('Texture', 'Texture');
    this.addInput('LUT', 'Texture');
    this.addInput('Intensity', 'number');
    this.addOutput('', 'Texture');
    this.properties = {
      enabled: true,
      intensity: 1,
      precision: LGraphTexture.DEFAULT,
      texture: null,
    };

    if (!LGraphTextureLUT._shader) {
      LGraphTextureLUT._shader = new GL.Shader(
        Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureLUT.pixel_shader,
      );
    }
  }

  LGraphTextureLUT.widgets_info = {
    texture: { widget: 'texture' },
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureLUT.title = 'LUT';
  LGraphTextureLUT.desc = 'Apply LUT to Texture';

  LGraphTextureLUT.prototype.onExecute = function () {
    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    var tex = this.getInputData(0);

    if (
      this.properties.precision === LGraphTexture.PASS_THROUGH ||
      this.properties.enabled === false
    ) {
      this.setOutputData(0, tex);
      return;
    }

    if (!tex) {
      return;
    }

    var lut_tex = this.getInputData(1);

    if (!lut_tex) {
      lut_tex = LGraphTexture.getTexture(this.properties.texture);
    }

    if (!lut_tex) {
      this.setOutputData(0, tex);
      return;
    }

    lut_tex.bind(0);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.bindTexture(gl.TEXTURE_2D, null);

    var intensity = this.properties.intensity;
    if (this.isInputConnected(2)) {
      this.properties.intensity = intensity = this.getInputData(2);
    }

    this._tex = LGraphTexture.getTargetTexture(
      tex,
      this._tex,
      this.properties.precision,
    );

    //var mesh = Mesh.getScreenQuad();

    this._tex.drawTo(function () {
      lut_tex.bind(1);
      tex.toViewport(LGraphTextureLUT._shader, {
        u_texture: 0,
        u_textureB: 1,
        u_amount: intensity,
      });
    });

    this.setOutputData(0, this._tex);
  };

  LGraphTextureLUT.pixel_shader =
    'precision highp float;\n\
  precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_texture;\n\
  uniform sampler2D u_textureB;\n\
  uniform float u_amount;\n\
  \n\
  void main() {\n\
     lowp vec4 textureColor = clamp( texture2D(u_texture, v_coord), vec4(0.0), vec4(1.0) );\n\
     mediump float blueColor = textureColor.b * 63.0;\n\
     mediump vec2 quad1;\n\
     quad1.y = floor(floor(blueColor) / 8.0);\n\
     quad1.x = floor(blueColor) - (quad1.y * 8.0);\n\
     mediump vec2 quad2;\n\
     quad2.y = floor(ceil(blueColor) / 8.0);\n\
     quad2.x = ceil(blueColor) - (quad2.y * 8.0);\n\
     highp vec2 texPos1;\n\
     texPos1.x = (quad1.x * 0.125) + 0.5/512.0 + ((0.125 - 1.0/512.0) * textureColor.r);\n\
     texPos1.y = 1.0 - ((quad1.y * 0.125) + 0.5/512.0 + ((0.125 - 1.0/512.0) * textureColor.g));\n\
     highp vec2 texPos2;\n\
     texPos2.x = (quad2.x * 0.125) + 0.5/512.0 + ((0.125 - 1.0/512.0) * textureColor.r);\n\
     texPos2.y = 1.0 - ((quad2.y * 0.125) + 0.5/512.0 + ((0.125 - 1.0/512.0) * textureColor.g));\n\
     lowp vec4 newColor1 = texture2D(u_textureB, texPos1);\n\
     lowp vec4 newColor2 = texture2D(u_textureB, texPos2);\n\
     lowp vec4 newColor = mix(newColor1, newColor2, fract(blueColor));\n\
     gl_FragColor = vec4( mix( textureColor.rgb, newColor.rgb, u_amount), textureColor.w);\n\
  }\n\
  ';

  LiteGraph.registerNodeType('texture/LUT', LGraphTextureLUT);

  // Texture LUT *****************************************
  function LGraphTextureEncode() {
    this.addInput('Texture', 'Texture');
    this.addInput('Atlas', 'Texture');
    this.addOutput('', 'Texture');
    this.properties = {
      enabled: true,
      num_row_symbols: 4,
      symbol_size: 16,
      brightness: 1,
      colorize: false,
      filter: false,
      invert: false,
      precision: LGraphTexture.DEFAULT,
      generate_mipmaps: false,
      texture: null,
    };

    if (!LGraphTextureEncode._shader) {
      LGraphTextureEncode._shader = new GL.Shader(
        Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureEncode.pixel_shader,
      );
    }

    this._uniforms = {
      u_texture: 0,
      u_textureB: 1,
      u_row_simbols: 4,
      u_simbol_size: 16,
      u_res: vec2.create(),
    };
  }

  LGraphTextureEncode.widgets_info = {
    texture: { widget: 'texture' },
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureEncode.title = 'Encode';
  LGraphTextureEncode.desc = 'Apply a texture atlas to encode a texture';

  LGraphTextureEncode.prototype.onExecute = function () {
    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    var tex = this.getInputData(0);

    if (
      this.properties.precision === LGraphTexture.PASS_THROUGH ||
      this.properties.enabled === false
    ) {
      this.setOutputData(0, tex);
      return;
    }

    if (!tex) {
      return;
    }

    var symbols_tex = this.getInputData(1);

    if (!symbols_tex) {
      symbols_tex = LGraphTexture.getTexture(this.properties.texture);
    }

    if (!symbols_tex) {
      this.setOutputData(0, tex);
      return;
    }

    symbols_tex.bind(0);
    gl.texParameteri(
      gl.TEXTURE_2D,
      gl.TEXTURE_MAG_FILTER,
      this.properties.filter ? gl.LINEAR : gl.NEAREST,
    );
    gl.texParameteri(
      gl.TEXTURE_2D,
      gl.TEXTURE_MIN_FILTER,
      this.properties.filter ? gl.LINEAR : gl.NEAREST,
    );
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.bindTexture(gl.TEXTURE_2D, null);

    var uniforms = this._uniforms;
    uniforms.u_row_simbols = Math.floor(this.properties.num_row_symbols);
    uniforms.u_symbol_size = this.properties.symbol_size;
    uniforms.u_brightness = this.properties.brightness;
    uniforms.u_invert = this.properties.invert ? 1 : 0;
    uniforms.u_colorize = this.properties.colorize ? 1 : 0;

    this._tex = LGraphTexture.getTargetTexture(
      tex,
      this._tex,
      this.properties.precision,
    );
    uniforms.u_res[0] = this._tex.width;
    uniforms.u_res[1] = this._tex.height;
    this._tex.bind(0);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);

    this._tex.drawTo(function () {
      symbols_tex.bind(1);
      tex.toViewport(LGraphTextureEncode._shader, uniforms);
    });

    if (this.properties.generate_mipmaps) {
      this._tex.bind(0);
      gl.generateMipmap(this._tex.texture_type);
      this._tex.unbind(0);
    }

    this.setOutputData(0, this._tex);
  };

  LGraphTextureEncode.pixel_shader =
    'precision highp float;\n\
  precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_texture;\n\
  uniform sampler2D u_textureB;\n\
  uniform float u_row_simbols;\n\
  uniform float u_symbol_size;\n\
  uniform float u_brightness;\n\
  uniform float u_invert;\n\
  uniform float u_colorize;\n\
  uniform vec2 u_res;\n\
  \n\
  void main() {\n\
    vec2 total_symbols = u_res / u_symbol_size;\n\
    vec2 uv = floor(v_coord * total_symbols) / total_symbols; //pixelate \n\
    vec2 local_uv = mod(v_coord * u_res, u_symbol_size) / u_symbol_size;\n\
    lowp vec4 textureColor = texture2D(u_texture, uv );\n\
    float lum = clamp(u_brightness * (textureColor.x + textureColor.y + textureColor.z)/3.0,0.0,1.0);\n\
    if( u_invert == 1.0 ) lum = 1.0 - lum;\n\
    float index = floor( lum * (u_row_simbols * u_row_simbols - 1.0));\n\
    float col = mod( index, u_row_simbols );\n\
    float row = u_row_simbols - floor( index / u_row_simbols ) - 1.0;\n\
    vec2 simbol_uv = ( vec2( col, row ) + local_uv ) / u_row_simbols;\n\
    vec4 color = texture2D( u_textureB, simbol_uv );\n\
    if(u_colorize == 1.0)\n\
      color *= textureColor;\n\
    gl_FragColor = color;\n\
  }\n\
  ';

  LiteGraph.registerNodeType('texture/encode', LGraphTextureEncode);

  // Texture Channels *****************************************
  function LGraphTextureChannels() {
    this.addInput('Texture', 'Texture');

    this.addOutput('R', 'Texture');
    this.addOutput('G', 'Texture');
    this.addOutput('B', 'Texture');
    this.addOutput('A', 'Texture');

    //this.properties = { use_single_channel: true };
    if (!LGraphTextureChannels._shader) {
      LGraphTextureChannels._shader = new GL.Shader(
        Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureChannels.pixel_shader,
      );
    }
  }

  LGraphTextureChannels.title = 'Texture to Channels';
  LGraphTextureChannels.desc = 'Split texture channels';

  LGraphTextureChannels.prototype.onExecute = function () {
    var texA = this.getInputData(0);
    if (!texA) {
      return;
    }

    if (!this._channels) {
      this._channels = Array(4);
    }

    //var format = this.properties.use_single_channel ? gl.LUMINANCE : gl.RGBA; //not supported by WebGL1
    var format = gl.RGB;
    var connections = 0;
    for (var i = 0; i < 4; i++) {
      if (this.isOutputConnected(i)) {
        if (
          !this._channels[i] ||
          this._channels[i].width != texA.width ||
          this._channels[i].height != texA.height ||
          this._channels[i].type != texA.type ||
          this._channels[i].format != format
        ) {
          this._channels[i] = new GL.Texture(texA.width, texA.height, {
            type: texA.type,
            format: format,
            filter: gl.LINEAR,
          });
        }
        connections++;
      } else {
        this._channels[i] = null;
      }
    }

    if (!connections) {
      return;
    }

    gl.disable(gl.BLEND);
    gl.disable(gl.DEPTH_TEST);

    var mesh = Mesh.getScreenQuad();
    var shader = LGraphTextureChannels._shader;
    var masks = [
      [1, 0, 0, 0],
      [0, 1, 0, 0],
      [0, 0, 1, 0],
      [0, 0, 0, 1],
    ];

    for (var i = 0; i < 4; i++) {
      if (!this._channels[i]) {
        continue;
      }

      this._channels[i].drawTo(function () {
        texA.bind(0);
        shader.uniforms({ u_texture: 0, u_mask: masks[i] }).draw(mesh);
      });
      this.setOutputData(i, this._channels[i]);
    }
  };

  LGraphTextureChannels.pixel_shader =
    'precision highp float;\n\
  precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_texture;\n\
  uniform vec4 u_mask;\n\
  \n\
  void main() {\n\
     gl_FragColor = vec4( vec3( length( texture2D(u_texture, v_coord) * u_mask )), 1.0 );\n\
  }\n\
  ';

  LiteGraph.registerNodeType('texture/textureChannels', LGraphTextureChannels);

  // Texture Channels to Texture *****************************************
  function LGraphChannelsTexture() {
    this.addInput('R', 'Texture');
    this.addInput('G', 'Texture');
    this.addInput('B', 'Texture');
    this.addInput('A', 'Texture');

    this.addOutput('Texture', 'Texture');

    this.properties = {
      precision: LGraphTexture.DEFAULT,
      R: 1,
      G: 1,
      B: 1,
      A: 1,
    };
    this._color = vec4.create();
    this._uniforms = {
      u_textureR: 0,
      u_textureG: 1,
      u_textureB: 2,
      u_textureA: 3,
      u_color: this._color,
    };
  }

  LGraphChannelsTexture.title = 'Channels to Texture';
  LGraphChannelsTexture.desc = 'Split texture channels';
  LGraphChannelsTexture.widgets_info = {
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphChannelsTexture.prototype.onExecute = function () {
    var white = LGraphTexture.getWhiteTexture();
    var texR = this.getInputData(0) || white;
    var texG = this.getInputData(1) || white;
    var texB = this.getInputData(2) || white;
    var texA = this.getInputData(3) || white;

    gl.disable(gl.BLEND);
    gl.disable(gl.DEPTH_TEST);

    var mesh = Mesh.getScreenQuad();
    if (!LGraphChannelsTexture._shader) {
      LGraphChannelsTexture._shader = new GL.Shader(
        Shader.SCREEN_VERTEX_SHADER,
        LGraphChannelsTexture.pixel_shader,
      );
    }
    var shader = LGraphChannelsTexture._shader;

    var w = Math.max(texR.width, texG.width, texB.width, texA.width);
    var h = Math.max(texR.height, texG.height, texB.height, texA.height);
    var type =
      this.properties.precision == LGraphTexture.HIGH
        ? LGraphTexture.HIGH_PRECISION_FORMAT
        : gl.UNSIGNED_BYTE;

    if (
      !this._texture ||
      this._texture.width != w ||
      this._texture.height != h ||
      this._texture.type != type
    ) {
      this._texture = new GL.Texture(w, h, {
        type: type,
        format: gl.RGBA,
        filter: gl.LINEAR,
      });
    }

    var color = this._color;
    color[0] = this.properties.R;
    color[1] = this.properties.G;
    color[2] = this.properties.B;
    color[3] = this.properties.A;
    var uniforms = this._uniforms;

    this._texture.drawTo(function () {
      texR.bind(0);
      texG.bind(1);
      texB.bind(2);
      texA.bind(3);
      shader.uniforms(uniforms).draw(mesh);
    });
    this.setOutputData(0, this._texture);
  };

  LGraphChannelsTexture.pixel_shader =
    'precision highp float;\n\
  precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_textureR;\n\
  uniform sampler2D u_textureG;\n\
  uniform sampler2D u_textureB;\n\
  uniform sampler2D u_textureA;\n\
  uniform vec4 u_color;\n\
  \n\
  void main() {\n\
     gl_FragColor = u_color * vec4( \
        texture2D(u_textureR, v_coord).r,\
        texture2D(u_textureG, v_coord).r,\
        texture2D(u_textureB, v_coord).r,\
        texture2D(u_textureA, v_coord).r);\n\
  }\n\
  ';

  LiteGraph.registerNodeType('texture/channelsTexture', LGraphChannelsTexture);

  // Texture Color *****************************************
  function LGraphTextureColor() {
    this.addOutput('Texture', 'Texture');

    this._tex_color = vec4.create();
    this.properties = {
      color: vec4.create(),
      precision: LGraphTexture.DEFAULT,
    };
  }

  LGraphTextureColor.title = 'Color';
  LGraphTextureColor.desc = 'Generates a 1x1 texture with a constant color';

  LGraphTextureColor.widgets_info = {
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureColor.prototype.onDrawBackground = function (ctx) {
    var c = this.properties.color;
    ctx.fillStyle =
      'rgb(' +
      Math.floor(clamp(c[0], 0, 1) * 255) +
      ',' +
      Math.floor(clamp(c[1], 0, 1) * 255) +
      ',' +
      Math.floor(clamp(c[2], 0, 1) * 255) +
      ')';
    if (this.flags.collapsed) {
      this.boxcolor = ctx.fillStyle;
    } else {
      ctx.fillRect(0, 0, this.size[0], this.size[1]);
    }
  };

  LGraphTextureColor.prototype.onExecute = function () {
    var type =
      this.properties.precision == LGraphTexture.HIGH
        ? LGraphTexture.HIGH_PRECISION_FORMAT
        : gl.UNSIGNED_BYTE;

    if (!this._tex || this._tex.type != type) {
      this._tex = new GL.Texture(1, 1, {
        format: gl.RGBA,
        type: type,
        minFilter: gl.NEAREST,
      });
    }
    var color = this.properties.color;

    if (this.inputs) {
      for (var i = 0; i < this.inputs.length; i++) {
        var input = this.inputs[i];
        var v = this.getInputData(i);
        if (v === undefined) {
          continue;
        }
        switch (input.name) {
          case 'RGB':
          case 'RGBA':
            color.set(v);
            break;
          case 'R':
            color[0] = v;
            break;
          case 'G':
            color[1] = v;
            break;
          case 'B':
            color[2] = v;
            break;
          case 'A':
            color[3] = v;
            break;
        }
      }
    }

    if (vec4.sqrDist(this._tex_color, color) > 0.001) {
      this._tex_color.set(color);
      this._tex.fill(color);
    }
    this.setOutputData(0, this._tex);
  };

  LGraphTextureColor.prototype.onGetInputs = function () {
    return [
      ['RGB', 'vec3'],
      ['RGBA', 'vec4'],
      ['R', 'number'],
      ['G', 'number'],
      ['B', 'number'],
      ['A', 'number'],
    ];
  };

  LiteGraph.registerNodeType('texture/color', LGraphTextureColor);

  // Texture Channels to Texture *****************************************
  function LGraphTextureGradient() {
    this.addInput('A', 'color');
    this.addInput('B', 'color');
    this.addOutput('Texture', 'Texture');

    this.properties = {
      angle: 0,
      scale: 1,
      A: [0, 0, 0],
      B: [1, 1, 1],
      texture_size: 32,
    };
    if (!LGraphTextureGradient._shader) {
      LGraphTextureGradient._shader = new GL.Shader(
        Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureGradient.pixel_shader,
      );
    }

    this._uniforms = {
      u_angle: 0,
      u_colorA: vec3.create(),
      u_colorB: vec3.create(),
    };
  }

  LGraphTextureGradient.title = 'Gradient';
  LGraphTextureGradient.desc = 'Generates a gradient';
  LGraphTextureGradient['@A'] = { type: 'color' };
  LGraphTextureGradient['@B'] = { type: 'color' };
  LGraphTextureGradient['@texture_size'] = {
    type: 'enum',
    values: [32, 64, 128, 256, 512],
  };

  LGraphTextureGradient.prototype.onExecute = function () {
    gl.disable(gl.BLEND);
    gl.disable(gl.DEPTH_TEST);

    var mesh = GL.Mesh.getScreenQuad();
    var shader = LGraphTextureGradient._shader;

    var A = this.getInputData(0);
    if (!A) {
      A = this.properties.A;
    }
    var B = this.getInputData(1);
    if (!B) {
      B = this.properties.B;
    }

    //angle and scale
    for (var i = 2; i < this.inputs.length; i++) {
      var input = this.inputs[i];
      var v = this.getInputData(i);
      if (v === undefined) {
        continue;
      }
      this.properties[input.name] = v;
    }

    var uniforms = this._uniforms;
    this._uniforms.u_angle = this.properties.angle * DEG2RAD;
    this._uniforms.u_scale = this.properties.scale;
    vec3.copy(uniforms.u_colorA, A);
    vec3.copy(uniforms.u_colorB, B);

    var size = parseInt(this.properties.texture_size);
    if (!this._tex || this._tex.width != size) {
      this._tex = new GL.Texture(size, size, {
        format: gl.RGB,
        filter: gl.LINEAR,
      });
    }

    this._tex.drawTo(function () {
      shader.uniforms(uniforms).draw(mesh);
    });
    this.setOutputData(0, this._tex);
  };

  LGraphTextureGradient.prototype.onGetInputs = function () {
    return [
      ['angle', 'number'],
      ['scale', 'number'],
    ];
  };

  LGraphTextureGradient.pixel_shader =
    'precision highp float;\n\
  precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform float u_angle;\n\
  uniform float u_scale;\n\
  uniform vec3 u_colorA;\n\
  uniform vec3 u_colorB;\n\
  \n\
  vec2 rotate(vec2 v, float angle)\n\
  {\n\
    vec2 result;\n\
    float _cos = cos(angle);\n\
    float _sin = sin(angle);\n\
    result.x = v.x * _cos - v.y * _sin;\n\
    result.y = v.x * _sin + v.y * _cos;\n\
    return result;\n\
  }\n\
  void main() {\n\
    float f = (rotate(u_scale * (v_coord - vec2(0.5)), u_angle) + vec2(0.5)).x;\n\
    vec3 color = mix(u_colorA,u_colorB,clamp(f,0.0,1.0));\n\
     gl_FragColor = vec4(color,1.0);\n\
  }\n\
  ';

  LiteGraph.registerNodeType('texture/gradient', LGraphTextureGradient);

  // Texture Mix *****************************************
  function LGraphTextureMix() {
    this.addInput('A', 'Texture');
    this.addInput('B', 'Texture');
    this.addInput('Mixer', 'Texture');

    this.addOutput('Texture', 'Texture');
    this.properties = {
      factor: 0.5,
      size_from_biggest: true,
      invert: false,
      precision: LGraphTexture.DEFAULT,
    };
    this._uniforms = {
      u_textureA: 0,
      u_textureB: 1,
      u_textureMix: 2,
      u_mix: vec4.create(),
    };
  }

  LGraphTextureMix.title = 'Mix';
  LGraphTextureMix.desc = 'Generates a texture mixing two textures';

  LGraphTextureMix.widgets_info = {
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureMix.prototype.onExecute = function () {
    var texA = this.getInputData(0);

    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    if (this.properties.precision === LGraphTexture.PASS_THROUGH) {
      this.setOutputData(0, texA);
      return;
    }

    var texB = this.getInputData(1);
    if (!texA || !texB) {
      return;
    }

    var texMix = this.getInputData(2);

    var factor = this.getInputData(3);

    this._tex = LGraphTexture.getTargetTexture(
      this.properties.size_from_biggest && texB.width > texA.width
        ? texB
        : texA,
      this._tex,
      this.properties.precision,
    );

    gl.disable(gl.BLEND);
    gl.disable(gl.DEPTH_TEST);

    var mesh = Mesh.getScreenQuad();
    var shader = null;
    var uniforms = this._uniforms;
    if (texMix) {
      shader = LGraphTextureMix._shader_tex;
      if (!shader) {
        shader = LGraphTextureMix._shader_tex = new GL.Shader(
          Shader.SCREEN_VERTEX_SHADER,
          LGraphTextureMix.pixel_shader,
          { MIX_TEX: '' },
        );
      }
    } else {
      shader = LGraphTextureMix._shader_factor;
      if (!shader) {
        shader = LGraphTextureMix._shader_factor = new GL.Shader(
          Shader.SCREEN_VERTEX_SHADER,
          LGraphTextureMix.pixel_shader,
        );
      }
      var f = factor == null ? this.properties.factor : factor;
      uniforms.u_mix.set([f, f, f, f]);
    }

    var invert = this.properties.invert;

    this._tex.drawTo(function () {
      texA.bind(invert ? 1 : 0);
      texB.bind(invert ? 0 : 1);
      if (texMix) {
        texMix.bind(2);
      }
      shader.uniforms(uniforms).draw(mesh);
    });

    this.setOutputData(0, this._tex);
  };

  LGraphTextureMix.prototype.onGetInputs = function () {
    return [['factor', 'number']];
  };

  LGraphTextureMix.pixel_shader =
    'precision highp float;\n\
  precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_textureA;\n\
  uniform sampler2D u_textureB;\n\
  #ifdef MIX_TEX\n\
    uniform sampler2D u_textureMix;\n\
  #else\n\
    uniform vec4 u_mix;\n\
  #endif\n\
  \n\
  void main() {\n\
    #ifdef MIX_TEX\n\
       vec4 f = texture2D(u_textureMix, v_coord);\n\
    #else\n\
       vec4 f = u_mix;\n\
    #endif\n\
     gl_FragColor = mix( texture2D(u_textureA, v_coord), texture2D(u_textureB, v_coord), f );\n\
  }\n\
  ';

  LiteGraph.registerNodeType('texture/mix', LGraphTextureMix);

  // Texture Edges detection *****************************************
  function LGraphTextureEdges() {
    this.addInput('Tex.', 'Texture');

    this.addOutput('Edges', 'Texture');
    this.properties = {
      invert: true,
      threshold: false,
      factor: 1,
      precision: LGraphTexture.DEFAULT,
    };

    if (!LGraphTextureEdges._shader) {
      LGraphTextureEdges._shader = new GL.Shader(
        Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureEdges.pixel_shader,
      );
    }
  }

  LGraphTextureEdges.title = 'Edges';
  LGraphTextureEdges.desc = 'Detects edges';

  LGraphTextureEdges.widgets_info = {
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureEdges.prototype.onExecute = function () {
    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    var tex = this.getInputData(0);

    if (this.properties.precision === LGraphTexture.PASS_THROUGH) {
      this.setOutputData(0, tex);
      return;
    }

    if (!tex) {
      return;
    }

    this._tex = LGraphTexture.getTargetTexture(
      tex,
      this._tex,
      this.properties.precision,
    );

    gl.disable(gl.BLEND);
    gl.disable(gl.DEPTH_TEST);

    var mesh = Mesh.getScreenQuad();
    var shader = LGraphTextureEdges._shader;
    var invert = this.properties.invert;
    var factor = this.properties.factor;
    var threshold = this.properties.threshold ? 1 : 0;

    this._tex.drawTo(function () {
      tex.bind(0);
      shader
        .uniforms({
          u_texture: 0,
          u_isize: [1 / tex.width, 1 / tex.height],
          u_factor: factor,
          u_threshold: threshold,
          u_invert: invert ? 1 : 0,
        })
        .draw(mesh);
    });

    this.setOutputData(0, this._tex);
  };

  LGraphTextureEdges.pixel_shader =
    'precision highp float;\n\
  precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_texture;\n\
  uniform vec2 u_isize;\n\
  uniform int u_invert;\n\
  uniform float u_factor;\n\
  uniform float u_threshold;\n\
  \n\
  void main() {\n\
    vec4 center = texture2D(u_texture, v_coord);\n\
    vec4 up = texture2D(u_texture, v_coord + u_isize * vec2(0.0,1.0) );\n\
    vec4 down = texture2D(u_texture, v_coord + u_isize * vec2(0.0,-1.0) );\n\
    vec4 left = texture2D(u_texture, v_coord + u_isize * vec2(1.0,0.0) );\n\
    vec4 right = texture2D(u_texture, v_coord + u_isize * vec2(-1.0,0.0) );\n\
    vec4 diff = abs(center - up) + abs(center - down) + abs(center - left) + abs(center - right);\n\
    diff *= u_factor;\n\
    if(u_invert == 1)\n\
      diff.xyz = vec3(1.0) - diff.xyz;\n\
    if( u_threshold == 0.0 )\n\
      gl_FragColor = vec4( diff.xyz, center.a );\n\
    else\n\
      gl_FragColor = vec4( diff.x > 0.5 ? 1.0 : 0.0, diff.y > 0.5 ? 1.0 : 0.0, diff.z > 0.5 ? 1.0 : 0.0, center.a );\n\
  }\n\
  ';

  LiteGraph.registerNodeType('texture/edges', LGraphTextureEdges);

  // Texture Depth *****************************************
  function LGraphTextureDepthRange() {
    this.addInput('Texture', 'Texture');
    this.addInput('Distance', 'number');
    this.addInput('Range', 'number');
    this.addOutput('Texture', 'Texture');
    this.properties = {
      distance: 100,
      range: 50,
      only_depth: false,
      high_precision: false,
    };
    this._uniforms = {
      u_texture: 0,
      u_distance: 100,
      u_range: 50,
      u_camera_planes: null,
    };
  }

  LGraphTextureDepthRange.title = 'Depth Range';
  LGraphTextureDepthRange.desc = 'Generates a texture with a depth range';

  LGraphTextureDepthRange.prototype.onExecute = function () {
    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    var tex = this.getInputData(0);
    if (!tex) {
      return;
    }

    var precision = gl.UNSIGNED_BYTE;
    if (this.properties.high_precision) {
      precision = gl.half_float_ext ? gl.HALF_FLOAT_OES : gl.FLOAT;
    }

    if (
      !this._temp_texture ||
      this._temp_texture.type != precision ||
      this._temp_texture.width != tex.width ||
      this._temp_texture.height != tex.height
    ) {
      this._temp_texture = new GL.Texture(tex.width, tex.height, {
        type: precision,
        format: gl.RGBA,
        filter: gl.LINEAR,
      });
    }

    var uniforms = this._uniforms;

    //iterations
    var distance = this.properties.distance;
    if (this.isInputConnected(1)) {
      distance = this.getInputData(1);
      this.properties.distance = distance;
    }

    var range = this.properties.range;
    if (this.isInputConnected(2)) {
      range = this.getInputData(2);
      this.properties.range = range;
    }

    uniforms.u_distance = distance;
    uniforms.u_range = range;

    gl.disable(gl.BLEND);
    gl.disable(gl.DEPTH_TEST);
    var mesh = Mesh.getScreenQuad();
    if (!LGraphTextureDepthRange._shader) {
      LGraphTextureDepthRange._shader = new GL.Shader(
        Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureDepthRange.pixel_shader,
      );
      LGraphTextureDepthRange._shader_onlydepth = new GL.Shader(
        Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureDepthRange.pixel_shader,
        { ONLY_DEPTH: '' },
      );
    }
    var shader = this.properties.only_depth
      ? LGraphTextureDepthRange._shader_onlydepth
      : LGraphTextureDepthRange._shader;

    //NEAR AND FAR PLANES
    var planes = null;
    if (tex.near_far_planes) {
      planes = tex.near_far_planes;
    } else if (window.LS && LS.Renderer._main_camera) {
      planes = LS.Renderer._main_camera._uniforms.u_camera_planes;
    } else {
      planes = [0.1, 1000];
    } //hardcoded
    uniforms.u_camera_planes = planes;

    this._temp_texture.drawTo(function () {
      tex.bind(0);
      shader.uniforms(uniforms).draw(mesh);
    });

    this._temp_texture.near_far_planes = planes;
    this.setOutputData(0, this._temp_texture);
  };

  LGraphTextureDepthRange.pixel_shader =
    'precision highp float;\n\
  precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_texture;\n\
  uniform vec2 u_camera_planes;\n\
  uniform float u_distance;\n\
  uniform float u_range;\n\
  \n\
  float LinearDepth()\n\
  {\n\
    float zNear = u_camera_planes.x;\n\
    float zFar = u_camera_planes.y;\n\
    float depth = texture2D(u_texture, v_coord).x;\n\
    depth = depth * 2.0 - 1.0;\n\
    return zNear * (depth + 1.0) / (zFar + zNear - depth * (zFar - zNear));\n\
  }\n\
  \n\
  void main() {\n\
    float depth = LinearDepth();\n\
    #ifdef ONLY_DEPTH\n\
       gl_FragColor = vec4(depth);\n\
    #else\n\
      float diff = abs(depth * u_camera_planes.y - u_distance);\n\
      float dof = 1.0;\n\
      if(diff <= u_range)\n\
        dof = diff / u_range;\n\
       gl_FragColor = vec4(dof);\n\
    #endif\n\
  }\n\
  ';

  LiteGraph.registerNodeType('texture/depth_range', LGraphTextureDepthRange);

  // Texture Depth *****************************************
  function LGraphTextureLinearDepth() {
    this.addInput('Texture', 'Texture');
    this.addOutput('Texture', 'Texture');
    this.properties = {
      precision: LGraphTexture.DEFAULT,
      invert: false,
    };
    this._uniforms = {
      u_texture: 0,
      u_camera_planes: null, //filled later
      u_ires: vec2.create(),
    };
  }

  LGraphTextureLinearDepth.widgets_info = {
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureLinearDepth.title = 'Linear Depth';
  LGraphTextureLinearDepth.desc = 'Creates a color texture with linear depth';

  LGraphTextureLinearDepth.prototype.onExecute = function () {
    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    var tex = this.getInputData(0);
    if (
      !tex ||
      (tex.format != gl.DEPTH_COMPONENT && tex.format != gl.DEPTH_STENCIL)
    ) {
      return;
    }

    var precision =
      this.properties.precision == LGraphTexture.HIGH
        ? gl.HIGH_PRECISION_FORMAT
        : gl.UNSIGNED_BYTE;

    if (
      !this._temp_texture ||
      this._temp_texture.type != precision ||
      this._temp_texture.width != tex.width ||
      this._temp_texture.height != tex.height
    ) {
      this._temp_texture = new GL.Texture(tex.width, tex.height, {
        type: precision,
        format: gl.RGB,
        filter: gl.LINEAR,
      });
    }

    var uniforms = this._uniforms;
    uniforms.u_invert = this.properties.invert ? 1 : 0;

    gl.disable(gl.BLEND);
    gl.disable(gl.DEPTH_TEST);
    var mesh = Mesh.getScreenQuad();
    if (!LGraphTextureLinearDepth._shader)
      LGraphTextureLinearDepth._shader = new GL.Shader(
        GL.Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureLinearDepth.pixel_shader,
      );
    var shader = LGraphTextureLinearDepth._shader;

    //NEAR AND FAR PLANES
    var planes = null;
    if (tex.near_far_planes) {
      planes = tex.near_far_planes;
    } else if (window.LS && LS.Renderer._main_camera) {
      planes = LS.Renderer._main_camera._uniforms.u_camera_planes;
    } else {
      planes = [0.1, 1000];
    } //hardcoded
    uniforms.u_camera_planes = planes;
    //uniforms.u_ires.set([1/tex.width, 1/tex.height]);
    uniforms.u_ires.set([0, 0]);

    this._temp_texture.drawTo(function () {
      tex.bind(0);
      shader.uniforms(uniforms).draw(mesh);
    });

    this._temp_texture.near_far_planes = planes;
    this.setOutputData(0, this._temp_texture);
  };

  LGraphTextureLinearDepth.pixel_shader =
    'precision highp float;\n\
  precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_texture;\n\
  uniform vec2 u_camera_planes;\n\
  uniform int u_invert;\n\
  uniform vec2 u_ires;\n\
  \n\
  void main() {\n\
    float zNear = u_camera_planes.x;\n\
    float zFar = u_camera_planes.y;\n\
    float depth = texture2D(u_texture, v_coord + u_ires*0.5).x * 2.0 - 1.0;\n\
    float f = zNear * (depth + 1.0) / (zFar + zNear - depth * (zFar - zNear));\n\
    if( u_invert == 1 )\n\
      f = 1.0 - f;\n\
    gl_FragColor = vec4(vec3(f),1.0);\n\
  }\n\
  ';

  LiteGraph.registerNodeType('texture/linear_depth', LGraphTextureLinearDepth);

  // Texture Blur *****************************************
  function LGraphTextureBlur() {
    this.addInput('Texture', 'Texture');
    this.addInput('Iterations', 'number');
    this.addInput('Intensity', 'number');
    this.addOutput('Blurred', 'Texture');
    this.properties = {
      intensity: 1,
      iterations: 1,
      preserve_aspect: false,
      scale: [1, 1],
      precision: LGraphTexture.DEFAULT,
    };
  }

  LGraphTextureBlur.title = 'Blur';
  LGraphTextureBlur.desc = 'Blur a texture';

  LGraphTextureBlur.widgets_info = {
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureBlur.max_iterations = 20;

  LGraphTextureBlur.prototype.onExecute = function () {
    var tex = this.getInputData(0);
    if (!tex) {
      return;
    }

    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    var temp = this._final_texture;

    if (
      !temp ||
      temp.width != tex.width ||
      temp.height != tex.height ||
      temp.type != tex.type
    ) {
      //we need two textures to do the blurring
      //this._temp_texture = new GL.Texture( tex.width, tex.height, { type: tex.type, format: gl.RGBA, filter: gl.LINEAR });
      temp = this._final_texture = new GL.Texture(tex.width, tex.height, {
        type: tex.type,
        format: gl.RGBA,
        filter: gl.LINEAR,
      });
    }

    //iterations
    var iterations = this.properties.iterations;
    if (this.isInputConnected(1)) {
      iterations = this.getInputData(1);
      this.properties.iterations = iterations;
    }
    iterations = Math.min(
      Math.floor(iterations),
      LGraphTextureBlur.max_iterations,
    );
    if (iterations == 0) {
      //skip blurring
      this.setOutputData(0, tex);
      return;
    }

    var intensity = this.properties.intensity;
    if (this.isInputConnected(2)) {
      intensity = this.getInputData(2);
      this.properties.intensity = intensity;
    }

    //blur sometimes needs an aspect correction
    var aspect = LiteGraph.camera_aspect;
    if (!aspect && window.gl !== undefined) {
      aspect = gl.canvas.height / gl.canvas.width;
    }
    if (!aspect) {
      aspect = 1;
    }
    aspect = this.properties.preserve_aspect ? aspect : 1;

    var scale = this.properties.scale || [1, 1];
    tex.applyBlur(aspect * scale[0], scale[1], intensity, temp);
    for (var i = 1; i < iterations; ++i) {
      temp.applyBlur(
        aspect * scale[0] * (i + 1),
        scale[1] * (i + 1),
        intensity,
      );
    }

    this.setOutputData(0, temp);
  };

  /*
LGraphTextureBlur.pixel_shader = "precision highp float;\n\
  precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_texture;\n\
  uniform vec2 u_offset;\n\
  uniform float u_intensity;\n\
  void main() {\n\
     vec4 sum = vec4(0.0);\n\
     vec4 center = texture2D(u_texture, v_coord);\n\
     sum += texture2D(u_texture, v_coord + u_offset * -4.0) * 0.05/0.98;\n\
     sum += texture2D(u_texture, v_coord + u_offset * -3.0) * 0.09/0.98;\n\
     sum += texture2D(u_texture, v_coord + u_offset * -2.0) * 0.12/0.98;\n\
     sum += texture2D(u_texture, v_coord + u_offset * -1.0) * 0.15/0.98;\n\
     sum += center * 0.16/0.98;\n\
     sum += texture2D(u_texture, v_coord + u_offset * 4.0) * 0.05/0.98;\n\
     sum += texture2D(u_texture, v_coord + u_offset * 3.0) * 0.09/0.98;\n\
     sum += texture2D(u_texture, v_coord + u_offset * 2.0) * 0.12/0.98;\n\
     sum += texture2D(u_texture, v_coord + u_offset * 1.0) * 0.15/0.98;\n\
     gl_FragColor = u_intensity * sum;\n\
  }\n\
  ";
*/

  LiteGraph.registerNodeType('texture/blur', LGraphTextureBlur);

  //Independent glow FX
  //based on https://catlikecoding.com/unity/tutorials/advanced-rendering/bloom/
  function FXGlow() {
    this.intensity = 0.5;
    this.persistence = 0.6;
    this.iterations = 8;
    this.threshold = 0.8;
    this.scale = 1;

    this.dirt_texture = null;
    this.dirt_factor = 0.5;

    this._textures = [];
    this._uniforms = {
      u_intensity: 1,
      u_texture: 0,
      u_glow_texture: 1,
      u_threshold: 0,
      u_texel_size: vec2.create(),
    };
  }

  FXGlow.prototype.applyFX = function (
    tex,
    output_texture,
    glow_texture,
    average_texture,
  ) {
    var width = tex.width;
    var height = tex.height;

    var texture_info = {
      format: tex.format,
      type: tex.type,
      minFilter: GL.LINEAR,
      magFilter: GL.LINEAR,
      wrap: gl.CLAMP_TO_EDGE,
    };

    var uniforms = this._uniforms;
    var textures = this._textures;

    //cut
    var shader = FXGlow._cut_shader;
    if (!shader) {
      shader = FXGlow._cut_shader = new GL.Shader(
        GL.Shader.SCREEN_VERTEX_SHADER,
        FXGlow.cut_pixel_shader,
      );
    }

    gl.disable(gl.DEPTH_TEST);
    gl.disable(gl.BLEND);

    uniforms.u_threshold = this.threshold;
    var currentDestination = (textures[0] = GL.Texture.getTemporary(
      width,
      height,
      texture_info,
    ));
    tex.blit(currentDestination, shader.uniforms(uniforms));
    var currentSource = currentDestination;

    var iterations = this.iterations;
    iterations = clamp(iterations, 1, 16) | 0;
    var texel_size = uniforms.u_texel_size;
    var intensity = this.intensity;

    uniforms.u_intensity = 1;
    uniforms.u_delta = this.scale; //1

    //downscale/upscale shader
    var shader = FXGlow._shader;
    if (!shader) {
      shader = FXGlow._shader = new GL.Shader(
        GL.Shader.SCREEN_VERTEX_SHADER,
        FXGlow.scale_pixel_shader,
      );
    }

    var i = 1;
    //downscale
    for (; i < iterations; i++) {
      width = width >> 1;
      if ((height | 0) > 1) {
        height = height >> 1;
      }
      if (width < 2) {
        break;
      }
      currentDestination = textures[i] = GL.Texture.getTemporary(
        width,
        height,
        texture_info,
      );
      texel_size[0] = 1 / currentSource.width;
      texel_size[1] = 1 / currentSource.height;
      currentSource.blit(currentDestination, shader.uniforms(uniforms));
      currentSource = currentDestination;
    }

    //average
    if (average_texture) {
      texel_size[0] = 1 / currentSource.width;
      texel_size[1] = 1 / currentSource.height;
      uniforms.u_intensity = intensity;
      uniforms.u_delta = 1;
      currentSource.blit(average_texture, shader.uniforms(uniforms));
    }

    //upscale and blend
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE);
    uniforms.u_intensity = this.persistence;
    uniforms.u_delta = 0.5;

    // i-=2 => -1 to point to last element in array, -1 to go to texture above
    for (i -= 2; i >= 0; i--) {
      currentDestination = textures[i];
      textures[i] = null;
      texel_size[0] = 1 / currentSource.width;
      texel_size[1] = 1 / currentSource.height;
      currentSource.blit(currentDestination, shader.uniforms(uniforms));
      GL.Texture.releaseTemporary(currentSource);
      currentSource = currentDestination;
    }
    gl.disable(gl.BLEND);

    //glow
    if (glow_texture) {
      currentSource.blit(glow_texture);
    }

    //final composition
    if (output_texture) {
      var final_texture = output_texture;
      var dirt_texture = this.dirt_texture;
      var dirt_factor = this.dirt_factor;
      uniforms.u_intensity = intensity;

      shader = dirt_texture ? FXGlow._dirt_final_shader : FXGlow._final_shader;
      if (!shader) {
        if (dirt_texture) {
          shader = FXGlow._dirt_final_shader = new GL.Shader(
            GL.Shader.SCREEN_VERTEX_SHADER,
            FXGlow.final_pixel_shader,
            { USE_DIRT: '' },
          );
        } else {
          shader = FXGlow._final_shader = new GL.Shader(
            GL.Shader.SCREEN_VERTEX_SHADER,
            FXGlow.final_pixel_shader,
          );
        }
      }

      final_texture.drawTo(function () {
        tex.bind(0);
        currentSource.bind(1);
        if (dirt_texture) {
          shader.setUniform('u_dirt_factor', dirt_factor);
          shader.setUniform('u_dirt_texture', dirt_texture.bind(2));
        }
        shader.toViewport(uniforms);
      });
    }

    GL.Texture.releaseTemporary(currentSource);
  };

  FXGlow.cut_pixel_shader =
    'precision highp float;\n\
varying vec2 v_coord;\n\
uniform sampler2D u_texture;\n\
uniform float u_threshold;\n\
void main() {\n\
  gl_FragColor = max( texture2D( u_texture, v_coord ) - vec4( u_threshold ), vec4(0.0) );\n\
}';

  FXGlow.scale_pixel_shader =
    'precision highp float;\n\
varying vec2 v_coord;\n\
uniform sampler2D u_texture;\n\
uniform vec2 u_texel_size;\n\
uniform float u_delta;\n\
uniform float u_intensity;\n\
\n\
vec4 sampleBox(vec2 uv) {\n\
  vec4 o = u_texel_size.xyxy * vec2(-u_delta, u_delta).xxyy;\n\
  vec4 s = texture2D( u_texture, uv + o.xy ) + texture2D( u_texture, uv + o.zy) + texture2D( u_texture, uv + o.xw) + texture2D( u_texture, uv + o.zw);\n\
  return s * 0.25;\n\
}\n\
void main() {\n\
  gl_FragColor = u_intensity * sampleBox( v_coord );\n\
}';

  FXGlow.final_pixel_shader =
    'precision highp float;\n\
varying vec2 v_coord;\n\
uniform sampler2D u_texture;\n\
uniform sampler2D u_glow_texture;\n\
#ifdef USE_DIRT\n\
  uniform sampler2D u_dirt_texture;\n\
#endif\n\
uniform vec2 u_texel_size;\n\
uniform float u_delta;\n\
uniform float u_intensity;\n\
uniform float u_dirt_factor;\n\
\n\
vec4 sampleBox(vec2 uv) {\n\
  vec4 o = u_texel_size.xyxy * vec2(-u_delta, u_delta).xxyy;\n\
  vec4 s = texture2D( u_glow_texture, uv + o.xy ) + texture2D( u_glow_texture, uv + o.zy) + texture2D( u_glow_texture, uv + o.xw) + texture2D( u_glow_texture, uv + o.zw);\n\
  return s * 0.25;\n\
}\n\
void main() {\n\
  vec4 glow = sampleBox( v_coord );\n\
  #ifdef USE_DIRT\n\
    glow = mix( glow, glow * texture2D( u_dirt_texture, v_coord ), u_dirt_factor );\n\
  #endif\n\
  gl_FragColor = texture2D( u_texture, v_coord ) + u_intensity * glow;\n\
}';

  // Texture Glow *****************************************
  function LGraphTextureGlow() {
    this.addInput('in', 'Texture');
    this.addInput('dirt', 'Texture');
    this.addOutput('out', 'Texture');
    this.addOutput('glow', 'Texture');
    this.properties = {
      enabled: true,
      intensity: 1,
      persistence: 0.99,
      iterations: 16,
      threshold: 0,
      scale: 1,
      dirt_factor: 0.5,
      precision: LGraphTexture.DEFAULT,
    };

    this.fx = new FXGlow();
  }

  LGraphTextureGlow.title = 'Glow';
  LGraphTextureGlow.desc = 'Filters a texture giving it a glow effect';

  LGraphTextureGlow.widgets_info = {
    iterations: {
      type: 'number',
      min: 0,
      max: 16,
      step: 1,
      precision: 0,
    },
    threshold: {
      type: 'number',
      min: 0,
      max: 10,
      step: 0.01,
      precision: 2,
    },
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureGlow.prototype.onGetInputs = function () {
    return [
      ['enabled', 'boolean'],
      ['threshold', 'number'],
      ['intensity', 'number'],
      ['persistence', 'number'],
      ['iterations', 'number'],
      ['dirt_factor', 'number'],
    ];
  };

  LGraphTextureGlow.prototype.onGetOutputs = function () {
    return [['average', 'Texture']];
  };

  LGraphTextureGlow.prototype.onExecute = function () {
    var tex = this.getInputData(0);
    if (!tex) {
      return;
    }

    if (!this.isAnyOutputConnected()) {
      return;
    } //saves work

    if (
      this.properties.precision === LGraphTexture.PASS_THROUGH ||
      this.getInputOrProperty('enabled') === false
    ) {
      this.setOutputData(0, tex);
      return;
    }

    var width = tex.width;
    var height = tex.height;

    var fx = this.fx;
    fx.threshold = this.getInputOrProperty('threshold');
    fx.iterations = this.getInputOrProperty('iterations');
    fx.intensity = this.getInputOrProperty('intensity');
    fx.persistence = this.getInputOrProperty('persistence');
    fx.dirt_texture = this.getInputData(1);
    fx.dirt_factor = this.getInputOrProperty('dirt_factor');
    fx.scale = this.properties.scale;

    var type = LGraphTexture.getTextureType(this.properties.precision, tex);

    var average_texture = null;
    if (this.isOutputConnected(2)) {
      average_texture = this._average_texture;
      if (
        !average_texture ||
        average_texture.type != tex.type ||
        average_texture.format != tex.format
      ) {
        average_texture = this._average_texture = new GL.Texture(1, 1, {
          type: tex.type,
          format: tex.format,
          filter: gl.LINEAR,
        });
      }
    }

    var glow_texture = null;
    if (this.isOutputConnected(1)) {
      glow_texture = this._glow_texture;
      if (
        !glow_texture ||
        glow_texture.width != tex.width ||
        glow_texture.height != tex.height ||
        glow_texture.type != type ||
        glow_texture.format != tex.format
      ) {
        glow_texture = this._glow_texture = new GL.Texture(
          tex.width,
          tex.height,
          { type: type, format: tex.format, filter: gl.LINEAR },
        );
      }
    }

    var final_texture = null;
    if (this.isOutputConnected(0)) {
      final_texture = this._final_texture;
      if (
        !final_texture ||
        final_texture.width != tex.width ||
        final_texture.height != tex.height ||
        final_texture.type != type ||
        final_texture.format != tex.format
      ) {
        final_texture = this._final_texture = new GL.Texture(
          tex.width,
          tex.height,
          { type: type, format: tex.format, filter: gl.LINEAR },
        );
      }
    }

    //apply FX
    fx.applyFX(tex, final_texture, glow_texture, average_texture);

    if (this.isOutputConnected(0)) this.setOutputData(0, final_texture);

    if (this.isOutputConnected(1)) this.setOutputData(1, average_texture);

    if (this.isOutputConnected(2)) this.setOutputData(2, glow_texture);
  };

  LiteGraph.registerNodeType('texture/glow', LGraphTextureGlow);

  // Texture Filter *****************************************
  function LGraphTextureKuwaharaFilter() {
    this.addInput('Texture', 'Texture');
    this.addOutput('Filtered', 'Texture');
    this.properties = { intensity: 1, radius: 5 };
  }

  LGraphTextureKuwaharaFilter.title = 'Kuwahara Filter';
  LGraphTextureKuwaharaFilter.desc =
    'Filters a texture giving an artistic oil canvas painting';

  LGraphTextureKuwaharaFilter.max_radius = 10;
  LGraphTextureKuwaharaFilter._shaders = [];

  LGraphTextureKuwaharaFilter.prototype.onExecute = function () {
    var tex = this.getInputData(0);
    if (!tex) {
      return;
    }

    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    var temp = this._temp_texture;

    if (
      !temp ||
      temp.width != tex.width ||
      temp.height != tex.height ||
      temp.type != tex.type
    ) {
      this._temp_texture = new GL.Texture(tex.width, tex.height, {
        type: tex.type,
        format: gl.RGBA,
        filter: gl.LINEAR,
      });
    }

    //iterations
    var radius = this.properties.radius;
    radius = Math.min(
      Math.floor(radius),
      LGraphTextureKuwaharaFilter.max_radius,
    );
    if (radius == 0) {
      //skip blurring
      this.setOutputData(0, tex);
      return;
    }

    var intensity = this.properties.intensity;

    //blur sometimes needs an aspect correction
    var aspect = LiteGraph.camera_aspect;
    if (!aspect && window.gl !== undefined) {
      aspect = gl.canvas.height / gl.canvas.width;
    }
    if (!aspect) {
      aspect = 1;
    }
    aspect = this.properties.preserve_aspect ? aspect : 1;

    if (!LGraphTextureKuwaharaFilter._shaders[radius]) {
      LGraphTextureKuwaharaFilter._shaders[radius] = new GL.Shader(
        Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureKuwaharaFilter.pixel_shader,
        { RADIUS: radius.toFixed(0) },
      );
    }

    var shader = LGraphTextureKuwaharaFilter._shaders[radius];
    var mesh = GL.Mesh.getScreenQuad();
    tex.bind(0);

    this._temp_texture.drawTo(function () {
      shader
        .uniforms({
          u_texture: 0,
          u_intensity: intensity,
          u_resolution: [tex.width, tex.height],
          u_iResolution: [1 / tex.width, 1 / tex.height],
        })
        .draw(mesh);
    });

    this.setOutputData(0, this._temp_texture);
  };

  //from https://www.shadertoy.com/view/MsXSz4
  LGraphTextureKuwaharaFilter.pixel_shader =
    '\n\
precision highp float;\n\
varying vec2 v_coord;\n\
uniform sampler2D u_texture;\n\
uniform float u_intensity;\n\
uniform vec2 u_resolution;\n\
uniform vec2 u_iResolution;\n\
#ifndef RADIUS\n\
#define RADIUS 7\n\
#endif\n\
void main() {\n\
\n\
const int radius = RADIUS;\n\
vec2 fragCoord = v_coord;\n\
vec2 src_size = u_iResolution;\n\
vec2 uv = v_coord;\n\
float n = float((radius + 1) * (radius + 1));\n\
int i;\n\
int j;\n\
vec3 m0 = vec3(0.0); vec3 m1 = vec3(0.0); vec3 m2 = vec3(0.0); vec3 m3 = vec3(0.0);\n\
vec3 s0 = vec3(0.0); vec3 s1 = vec3(0.0); vec3 s2 = vec3(0.0); vec3 s3 = vec3(0.0);\n\
vec3 c;\n\
\n\
for (int j = -radius; j <= 0; ++j)  {\n\
  for (int i = -radius; i <= 0; ++i)  {\n\
    c = texture2D(u_texture, uv + vec2(i,j) * src_size).rgb;\n\
    m0 += c;\n\
    s0 += c * c;\n\
  }\n\
}\n\
\n\
for (int j = -radius; j <= 0; ++j)  {\n\
  for (int i = 0; i <= radius; ++i)  {\n\
    c = texture2D(u_texture, uv + vec2(i,j) * src_size).rgb;\n\
    m1 += c;\n\
    s1 += c * c;\n\
  }\n\
}\n\
\n\
for (int j = 0; j <= radius; ++j)  {\n\
  for (int i = 0; i <= radius; ++i)  {\n\
    c = texture2D(u_texture, uv + vec2(i,j) * src_size).rgb;\n\
    m2 += c;\n\
    s2 += c * c;\n\
  }\n\
}\n\
\n\
for (int j = 0; j <= radius; ++j)  {\n\
  for (int i = -radius; i <= 0; ++i)  {\n\
    c = texture2D(u_texture, uv + vec2(i,j) * src_size).rgb;\n\
    m3 += c;\n\
    s3 += c * c;\n\
  }\n\
}\n\
\n\
float min_sigma2 = 1e+2;\n\
m0 /= n;\n\
s0 = abs(s0 / n - m0 * m0);\n\
\n\
float sigma2 = s0.r + s0.g + s0.b;\n\
if (sigma2 < min_sigma2) {\n\
  min_sigma2 = sigma2;\n\
  gl_FragColor = vec4(m0, 1.0);\n\
}\n\
\n\
m1 /= n;\n\
s1 = abs(s1 / n - m1 * m1);\n\
\n\
sigma2 = s1.r + s1.g + s1.b;\n\
if (sigma2 < min_sigma2) {\n\
  min_sigma2 = sigma2;\n\
  gl_FragColor = vec4(m1, 1.0);\n\
}\n\
\n\
m2 /= n;\n\
s2 = abs(s2 / n - m2 * m2);\n\
\n\
sigma2 = s2.r + s2.g + s2.b;\n\
if (sigma2 < min_sigma2) {\n\
  min_sigma2 = sigma2;\n\
  gl_FragColor = vec4(m2, 1.0);\n\
}\n\
\n\
m3 /= n;\n\
s3 = abs(s3 / n - m3 * m3);\n\
\n\
sigma2 = s3.r + s3.g + s3.b;\n\
if (sigma2 < min_sigma2) {\n\
  min_sigma2 = sigma2;\n\
  gl_FragColor = vec4(m3, 1.0);\n\
}\n\
}\n\
';

  LiteGraph.registerNodeType('texture/kuwahara', LGraphTextureKuwaharaFilter);

  // Texture  *****************************************
  function LGraphTextureXDoGFilter() {
    this.addInput('Texture', 'Texture');
    this.addOutput('Filtered', 'Texture');
    this.properties = {
      sigma: 1.4,
      k: 1.6,
      p: 21.7,
      epsilon: 79,
      phi: 0.017,
    };
  }

  LGraphTextureXDoGFilter.title = 'XDoG Filter';
  LGraphTextureXDoGFilter.desc =
    'Filters a texture giving an artistic ink style';

  LGraphTextureXDoGFilter.max_radius = 10;
  LGraphTextureXDoGFilter._shaders = [];

  LGraphTextureXDoGFilter.prototype.onExecute = function () {
    var tex = this.getInputData(0);
    if (!tex) {
      return;
    }

    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    var temp = this._temp_texture;
    if (
      !temp ||
      temp.width != tex.width ||
      temp.height != tex.height ||
      temp.type != tex.type
    ) {
      this._temp_texture = new GL.Texture(tex.width, tex.height, {
        type: tex.type,
        format: gl.RGBA,
        filter: gl.LINEAR,
      });
    }

    if (!LGraphTextureXDoGFilter._xdog_shader) {
      LGraphTextureXDoGFilter._xdog_shader = new GL.Shader(
        Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureXDoGFilter.xdog_pixel_shader,
      );
    }
    var shader = LGraphTextureXDoGFilter._xdog_shader;
    var mesh = GL.Mesh.getScreenQuad();

    var sigma = this.properties.sigma;
    var k = this.properties.k;
    var p = this.properties.p;
    var epsilon = this.properties.epsilon;
    var phi = this.properties.phi;
    tex.bind(0);
    this._temp_texture.drawTo(function () {
      shader
        .uniforms({
          src: 0,
          sigma: sigma,
          k: k,
          p: p,
          epsilon: epsilon,
          phi: phi,
          cvsWidth: tex.width,
          cvsHeight: tex.height,
        })
        .draw(mesh);
    });

    this.setOutputData(0, this._temp_texture);
  };

  //from https://github.com/RaymondMcGuire/GPU-Based-Image-Processing-Tools/blob/master/lib_webgl/scripts/main.js
  LGraphTextureXDoGFilter.xdog_pixel_shader =
    '\n\
precision highp float;\n\
uniform sampler2D src;\n\n\
uniform float cvsHeight;\n\
uniform float cvsWidth;\n\n\
uniform float sigma;\n\
uniform float k;\n\
uniform float p;\n\
uniform float epsilon;\n\
uniform float phi;\n\
varying vec2 v_coord;\n\n\
float cosh(float val)\n\
{\n\
float tmp = exp(val);\n\
float cosH = (tmp + 1.0 / tmp) / 2.0;\n\
return cosH;\n\
}\n\n\
float tanh(float val)\n\
{\n\
float tmp = exp(val);\n\
float tanH = (tmp - 1.0 / tmp) / (tmp + 1.0 / tmp);\n\
return tanH;\n\
}\n\n\
float sinh(float val)\n\
{\n\
float tmp = exp(val);\n\
float sinH = (tmp - 1.0 / tmp) / 2.0;\n\
return sinH;\n\
}\n\n\
void main(void){\n\
vec3 destColor = vec3(0.0);\n\
float tFrag = 1.0 / cvsHeight;\n\
float sFrag = 1.0 / cvsWidth;\n\
vec2 Frag = vec2(sFrag,tFrag);\n\
vec2 uv = gl_FragCoord.st;\n\
float twoSigmaESquared = 2.0 * sigma * sigma;\n\
float twoSigmaRSquared = twoSigmaESquared * k * k;\n\
int halfWidth = int(ceil( 1.0 * sigma * k ));\n\n\
const int MAX_NUM_ITERATION = 99999;\n\
vec2 sum = vec2(0.0);\n\
vec2 norm = vec2(0.0);\n\n\
for(int cnt=0;cnt<MAX_NUM_ITERATION;cnt++){\n\
  if(cnt > (2*halfWidth+1)*(2*halfWidth+1)){break;}\n\
  int i = int(cnt / (2*halfWidth+1)) - halfWidth;\n\
  int j = cnt - halfWidth - int(cnt / (2*halfWidth+1)) * (2*halfWidth+1);\n\n\
  float d = length(vec2(i,j));\n\
  vec2 kernel = vec2( exp( -d * d / twoSigmaESquared ), \n\
            exp( -d * d / twoSigmaRSquared ));\n\n\
  vec2 L = texture2D(src, (uv + vec2(i,j)) * Frag).xx;\n\n\
  norm += kernel;\n\
  sum += kernel * L;\n\
}\n\n\
sum /= norm;\n\n\
float H = 100.0 * ((1.0 + p) * sum.x - p * sum.y);\n\
float edge = ( H > epsilon )? 1.0 : 1.0 + tanh( phi * (H - epsilon));\n\
destColor = vec3(edge);\n\
gl_FragColor = vec4(destColor, 1.0);\n\
}';

  LiteGraph.registerNodeType('texture/xDoG', LGraphTextureXDoGFilter);

  // Texture Webcam *****************************************
  function LGraphTextureWebcam() {
    this.addOutput('Webcam', 'Texture');
    this.properties = { texture_name: '', facingMode: 'user' };
    this.boxcolor = 'black';
    this.version = 0;
  }

  LGraphTextureWebcam.title = 'Webcam';
  LGraphTextureWebcam.desc = 'Webcam texture';

  LGraphTextureWebcam.is_webcam_open = false;

  LGraphTextureWebcam.prototype.openStream = function () {
    if (!navigator.getUserMedia) {
      //console.log('getUserMedia() is not supported in your browser, use chrome and enable WebRTC from about://flags');
      return;
    }

    this._waiting_confirmation = true;

    // Not showing vendor prefixes.
    var constraints = {
      audio: false,
      video: { facingMode: this.properties.facingMode },
    };
    navigator.mediaDevices
      .getUserMedia(constraints)
      .then(this.streamReady.bind(this))
      .catch(onFailSoHard);

    var that = this;
    function onFailSoHard(e) {
      LGraphTextureWebcam.is_webcam_open = false;
      console.log('Webcam rejected', e);
      that._webcam_stream = false;
      that.boxcolor = 'red';
      that.trigger('stream_error');
    }
  };

  LGraphTextureWebcam.prototype.closeStream = function () {
    if (this._webcam_stream) {
      var tracks = this._webcam_stream.getTracks();
      if (tracks.length) {
        for (var i = 0; i < tracks.length; ++i) {
          tracks[i].stop();
        }
      }
      LGraphTextureWebcam.is_webcam_open = false;
      this._webcam_stream = null;
      this._video = null;
      this.boxcolor = 'black';
      this.trigger('stream_closed');
    }
  };

  LGraphTextureWebcam.prototype.streamReady = function (localMediaStream) {
    this._webcam_stream = localMediaStream;
    //this._waiting_confirmation = false;
    this.boxcolor = 'green';
    var video = this._video;
    if (!video) {
      video = document.createElement('video');
      video.autoplay = true;
      video.srcObject = localMediaStream;
      this._video = video;
      //document.body.appendChild( video ); //debug
      //when video info is loaded (size and so)
      video.onloadedmetadata = function (e) {
        // Ready to go. Do some stuff.
        LGraphTextureWebcam.is_webcam_open = true;
        console.log(e);
      };
    }
    this.trigger('stream_ready', video);
  };

  LGraphTextureWebcam.prototype.onPropertyChanged = function (name, value) {
    if (name == 'facingMode') {
      this.properties.facingMode = value;
      this.closeStream();
      this.openStream();
    }
  };

  LGraphTextureWebcam.prototype.onRemoved = function () {
    if (!this._webcam_stream) {
      return;
    }

    var tracks = this._webcam_stream.getTracks();
    if (tracks.length) {
      for (var i = 0; i < tracks.length; ++i) {
        tracks[i].stop();
      }
    }

    this._webcam_stream = null;
    this._video = null;
  };

  LGraphTextureWebcam.prototype.onDrawBackground = function (ctx) {
    if (this.flags.collapsed || this.size[1] <= 20) {
      return;
    }

    if (!this._video) {
      return;
    }

    //render to graph canvas
    ctx.save();
    if (!ctx.webgl) {
      //reverse image
      ctx.drawImage(this._video, 0, 0, this.size[0], this.size[1]);
    } else {
      if (this._video_texture) {
        ctx.drawImage(this._video_texture, 0, 0, this.size[0], this.size[1]);
      }
    }
    ctx.restore();
  };

  LGraphTextureWebcam.prototype.onExecute = function () {
    if (this._webcam_stream == null && !this._waiting_confirmation) {
      this.openStream();
    }

    if (!this._video || !this._video.videoWidth) {
      return;
    }

    var width = this._video.videoWidth;
    var height = this._video.videoHeight;

    var temp = this._video_texture;
    if (!temp || temp.width != width || temp.height != height) {
      this._video_texture = new GL.Texture(width, height, {
        format: gl.RGB,
        filter: gl.LINEAR,
      });
    }

    this._video_texture.uploadImage(this._video);
    this._video_texture.version = ++this.version;

    if (this.properties.texture_name) {
      var container = LGraphTexture.getTexturesContainer();
      container[this.properties.texture_name] = this._video_texture;
    }

    this.setOutputData(0, this._video_texture);
    for (var i = 1; i < this.outputs.length; ++i) {
      if (!this.outputs[i]) {
        continue;
      }
      switch (this.outputs[i].name) {
        case 'width':
          this.setOutputData(i, this._video.videoWidth);
          break;
        case 'height':
          this.setOutputData(i, this._video.videoHeight);
          break;
      }
    }
  };

  LGraphTextureWebcam.prototype.onGetOutputs = function () {
    return [
      ['width', 'number'],
      ['height', 'number'],
      ['stream_ready', LiteGraph.EVENT],
      ['stream_closed', LiteGraph.EVENT],
      ['stream_error', LiteGraph.EVENT],
    ];
  };

  LiteGraph.registerNodeType('texture/webcam', LGraphTextureWebcam);

  //from https://github.com/spite/Wagner
  function LGraphLensFX() {
    this.addInput('in', 'Texture');
    this.addInput('f', 'number');
    this.addOutput('out', 'Texture');
    this.properties = {
      enabled: true,
      factor: 1,
      precision: LGraphTexture.LOW,
    };

    this._uniforms = { u_texture: 0, u_factor: 1 };
  }

  LGraphLensFX.title = 'Lens FX';
  LGraphLensFX.desc = 'distortion and chromatic aberration';

  LGraphLensFX.widgets_info = {
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphLensFX.prototype.onGetInputs = function () {
    return [['enabled', 'boolean']];
  };

  LGraphLensFX.prototype.onExecute = function () {
    var tex = this.getInputData(0);
    if (!tex) {
      return;
    }

    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    if (
      this.properties.precision === LGraphTexture.PASS_THROUGH ||
      this.getInputOrProperty('enabled') === false
    ) {
      this.setOutputData(0, tex);
      return;
    }

    var temp = this._temp_texture;
    if (
      !temp ||
      temp.width != tex.width ||
      temp.height != tex.height ||
      temp.type != tex.type
    ) {
      temp = this._temp_texture = new GL.Texture(tex.width, tex.height, {
        type: tex.type,
        format: gl.RGBA,
        filter: gl.LINEAR,
      });
    }

    var shader = LGraphLensFX._shader;
    if (!shader) {
      shader = LGraphLensFX._shader = new GL.Shader(
        GL.Shader.SCREEN_VERTEX_SHADER,
        LGraphLensFX.pixel_shader,
      );
    }

    var factor = this.getInputData(1);
    if (factor == null) {
      factor = this.properties.factor;
    }

    var uniforms = this._uniforms;
    uniforms.u_factor = factor;

    //apply shader
    gl.disable(gl.DEPTH_TEST);
    temp.drawTo(function () {
      tex.bind(0);
      shader.uniforms(uniforms).draw(GL.Mesh.getScreenQuad());
    });

    this.setOutputData(0, temp);
  };

  LGraphLensFX.pixel_shader =
    'precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_texture;\n\
  uniform float u_factor;\n\
  vec2 barrelDistortion(vec2 coord, float amt) {\n\
    vec2 cc = coord - 0.5;\n\
    float dist = dot(cc, cc);\n\
    return coord + cc * dist * amt;\n\
  }\n\
  \n\
  float sat( float t )\n\
  {\n\
    return clamp( t, 0.0, 1.0 );\n\
  }\n\
  \n\
  float linterp( float t ) {\n\
    return sat( 1.0 - abs( 2.0*t - 1.0 ) );\n\
  }\n\
  \n\
  float remap( float t, float a, float b ) {\n\
    return sat( (t - a) / (b - a) );\n\
  }\n\
  \n\
  vec4 spectrum_offset( float t ) {\n\
    vec4 ret;\n\
    float lo = step(t,0.5);\n\
    float hi = 1.0-lo;\n\
    float w = linterp( remap( t, 1.0/6.0, 5.0/6.0 ) );\n\
    ret = vec4(lo,1.0,hi, 1.) * vec4(1.0-w, w, 1.0-w, 1.);\n\
  \n\
    return pow( ret, vec4(1.0/2.2) );\n\
  }\n\
  \n\
  const float max_distort = 2.2;\n\
  const int num_iter = 12;\n\
  const float reci_num_iter_f = 1.0 / float(num_iter);\n\
  \n\
  void main()\n\
  {	\n\
    vec2 uv=v_coord;\n\
    vec4 sumcol = vec4(0.0);\n\
    vec4 sumw = vec4(0.0);	\n\
    for ( int i=0; i<num_iter;++i )\n\
    {\n\
      float t = float(i) * reci_num_iter_f;\n\
      vec4 w = spectrum_offset( t );\n\
      sumw += w;\n\
      sumcol += w * texture2D( u_texture, barrelDistortion(uv, .6 * max_distort*t * u_factor ) );\n\
    }\n\
    gl_FragColor = sumcol / sumw;\n\
  }';

  LiteGraph.registerNodeType('texture/lensfx', LGraphLensFX);

  function LGraphTextureFromData() {
    this.addInput('in', '');
    this.properties = {
      precision: LGraphTexture.LOW,
      width: 0,
      height: 0,
      channels: 1,
    };
    this.addOutput('out', 'Texture');
  }

  LGraphTextureFromData.title = 'Data->Tex';
  LGraphTextureFromData.desc = 'Generates or applies a curve to a texture';
  LGraphTextureFromData.widgets_info = {
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureFromData.prototype.onExecute = function () {
    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    var data = this.getInputData(0);
    if (!data) return;

    var channels = this.properties.channels;
    var w = this.properties.width;
    var h = this.properties.height;
    if (!w || !h) {
      w = Math.floor(data.length / channels);
      h = 1;
    }
    var format = gl.RGBA;
    if (channels == 3) format = gl.RGB;
    else if (channels == 1) format = gl.LUMINANCE;

    var temp = this._temp_texture;
    var type = LGraphTexture.getTextureType(this.properties.precision);
    if (!temp || temp.width != w || temp.height != h || temp.type != type) {
      temp = this._temp_texture = new GL.Texture(w, h, {
        type: type,
        format: format,
        filter: gl.LINEAR,
      });
    }

    temp.uploadData(data);
    this.setOutputData(0, temp);
  };

  LiteGraph.registerNodeType('texture/fromdata', LGraphTextureFromData);

  //applies a curve (or generates one)
  function LGraphTextureCurve() {
    this.addInput('in', 'Texture');
    this.addOutput('out', 'Texture');
    this.properties = { precision: LGraphTexture.LOW, split_channels: false };
    this._values = new Uint8Array(256 * 4);
    this._values.fill(255);
    this._curve_texture = null;
    this._uniforms = { u_texture: 0, u_curve: 1, u_range: 1.0 };
    this._must_update = true;
    this._points = {
      RGB: [
        [0, 0],
        [1, 1],
      ],
      R: [
        [0, 0],
        [1, 1],
      ],
      G: [
        [0, 0],
        [1, 1],
      ],
      B: [
        [0, 0],
        [1, 1],
      ],
    };
    this.curve_editor = null;
    this.addWidget('toggle', 'Split Channels', false, 'split_channels');
    this.addWidget('combo', 'Channel', 'RGB', {
      values: ['RGB', 'R', 'G', 'B'],
    });
    this.curve_offset = 68;
    this.size = [240, 160];
  }

  LGraphTextureCurve.title = 'Curve';
  LGraphTextureCurve.desc = 'Generates or applies a curve to a texture';
  LGraphTextureCurve.widgets_info = {
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureCurve.prototype.onExecute = function () {
    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    var tex = this.getInputData(0);

    var temp = this._temp_texture;
    if (!tex) {
      //generate one texture, nothing else
      if (this._must_update || !this._curve_texture) this.updateCurve();
      this.setOutputData(0, this._curve_texture);
      return;
    }

    var type = LGraphTexture.getTextureType(this.properties.precision, tex);

    //apply curve to input texture
    if (
      !temp ||
      temp.type != type ||
      temp.width != tex.width ||
      temp.height != tex.height ||
      temp.format != tex.format
    )
      temp = this._temp_texture = new GL.Texture(tex.width, tex.height, {
        type: type,
        format: tex.format,
        filter: gl.LINEAR,
      });

    var shader = LGraphTextureCurve._shader;
    if (!shader) {
      shader = LGraphTextureCurve._shader = new GL.Shader(
        GL.Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureCurve.pixel_shader,
      );
    }

    if (this._must_update || !this._curve_texture) this.updateCurve();

    var uniforms = this._uniforms;
    var curve_texture = this._curve_texture;

    //apply shader
    temp.drawTo(function () {
      gl.disable(gl.DEPTH_TEST);
      tex.bind(0);
      curve_texture.bind(1);
      shader.uniforms(uniforms).draw(GL.Mesh.getScreenQuad());
    });

    this.setOutputData(0, temp);
  };

  LGraphTextureCurve.prototype.sampleCurve = function (f, points) {
    var points = points || this._points.RGB;
    if (!points) return;
    for (var i = 0; i < points.length - 1; ++i) {
      var p = points[i];
      var pn = points[i + 1];
      if (pn[0] < f) continue;
      var r = pn[0] - p[0];
      if (Math.abs(r) < 0.00001) return p[1];
      var local_f = (f - p[0]) / r;
      return p[1] * (1.0 - local_f) + pn[1] * local_f;
    }
    return 0;
  };

  LGraphTextureCurve.prototype.updateCurve = function () {
    var values = this._values;
    var num = values.length / 4;
    var split = this.properties.split_channels;
    for (var i = 0; i < num; ++i) {
      if (split) {
        values[i * 4] = clamp(
          this.sampleCurve(i / num, this._points.R) * 255,
          0,
          255,
        );
        values[i * 4 + 1] = clamp(
          this.sampleCurve(i / num, this._points.G) * 255,
          0,
          255,
        );
        values[i * 4 + 2] = clamp(
          this.sampleCurve(i / num, this._points.B) * 255,
          0,
          255,
        );
      } else {
        var v = this.sampleCurve(i / num); //sample curve
        values[i * 4] =
          values[i * 4 + 1] =
          values[i * 4 + 2] =
            clamp(v * 255, 0, 255);
      }
      values[i * 4 + 3] = 255; //alpha fixed
    }
    if (!this._curve_texture)
      this._curve_texture = new GL.Texture(256, 1, {
        format: gl.RGBA,
        magFilter: gl.LINEAR,
        wrap: gl.CLAMP_TO_EDGE,
      });
    this._curve_texture.uploadData(values, null, true);
  };

  LGraphTextureCurve.prototype.onSerialize = function (o) {
    var curves = {};
    for (var i in this._points) curves[i] = this._points[i].concat();
    o.curves = curves;
  };

  LGraphTextureCurve.prototype.onConfigure = function (o) {
    this._points = o.curves;
    if (this.curve_editor) curve_editor.points = this._points;
    this._must_update = true;
  };

  LGraphTextureCurve.prototype.onMouseDown = function (
    e,
    localpos,
    graphcanvas,
  ) {
    if (this.curve_editor) {
      var r = this.curve_editor.onMouseDown(
        [localpos[0], localpos[1] - this.curve_offset],
        graphcanvas,
      );
      if (r) this.captureInput(true);
      return r;
    }
  };

  LGraphTextureCurve.prototype.onMouseMove = function (
    e,
    localpos,
    graphcanvas,
  ) {
    if (this.curve_editor)
      return this.curve_editor.onMouseMove(
        [localpos[0], localpos[1] - this.curve_offset],
        graphcanvas,
      );
  };

  LGraphTextureCurve.prototype.onMouseUp = function (e, localpos, graphcanvas) {
    if (this.curve_editor)
      return this.curve_editor.onMouseUp(
        [localpos[0], localpos[1] - this.curve_offset],
        graphcanvas,
      );
    this.captureInput(false);
  };

  LGraphTextureCurve.channel_line_colors = {
    RGB: '#666',
    R: '#F33',
    G: '#3F3',
    B: '#33F',
  };

  LGraphTextureCurve.prototype.onDrawBackground = function (ctx, graphcanvas) {
    if (this.flags.collapsed) return;

    if (!this.curve_editor)
      this.curve_editor = new LiteGraph.CurveEditor(this._points.R);
    ctx.save();
    ctx.translate(0, this.curve_offset);
    var channel = this.widgets[1].value;

    if (this.properties.split_channels) {
      if (channel == 'RGB') {
        this.widgets[1].value = channel = 'R';
        this.widgets[1].disabled = false;
      }
      this.curve_editor.points = this._points.R;
      this.curve_editor.draw(
        ctx,
        [this.size[0], this.size[1] - this.curve_offset],
        graphcanvas,
        '#111',
        LGraphTextureCurve.channel_line_colors.R,
        true,
      );
      ctx.globalCompositeOperation = 'lighten';
      this.curve_editor.points = this._points.G;
      this.curve_editor.draw(
        ctx,
        [this.size[0], this.size[1] - this.curve_offset],
        graphcanvas,
        null,
        LGraphTextureCurve.channel_line_colors.G,
        true,
      );
      this.curve_editor.points = this._points.B;
      this.curve_editor.draw(
        ctx,
        [this.size[0], this.size[1] - this.curve_offset],
        graphcanvas,
        null,
        LGraphTextureCurve.channel_line_colors.B,
        true,
      );
      ctx.globalCompositeOperation = 'source-over';
    } else {
      this.widgets[1].value = channel = 'RGB';
      this.widgets[1].disabled = true;
    }

    this.curve_editor.points = this._points[channel];
    this.curve_editor.draw(
      ctx,
      [this.size[0], this.size[1] - this.curve_offset],
      graphcanvas,
      this.properties.split_channels ? null : '#111',
      LGraphTextureCurve.channel_line_colors[channel],
    );
    ctx.restore();
  };

  LGraphTextureCurve.pixel_shader =
    'precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_texture;\n\
  uniform sampler2D u_curve;\n\
  uniform float u_range;\n\
  \n\
  void main() {\n\
    vec4 color = texture2D( u_texture, v_coord ) * u_range;\n\
    color.x = texture2D( u_curve, vec2( color.x, 0.5 ) ).x;\n\
    color.y = texture2D( u_curve, vec2( color.y, 0.5 ) ).y;\n\
    color.z = texture2D( u_curve, vec2( color.z, 0.5 ) ).z;\n\
    //color.w = texture2D( u_curve, vec2( color.w, 0.5 ) ).w;\n\
    gl_FragColor = color;\n\
  }';

  LiteGraph.registerNodeType('texture/curve', LGraphTextureCurve);

  //simple exposition, but plan to expand it to support different gamma curves
  function LGraphExposition() {
    this.addInput('in', 'Texture');
    this.addInput('exp', 'number');
    this.addOutput('out', 'Texture');
    this.properties = { exposition: 1, precision: LGraphTexture.LOW };
    this._uniforms = { u_texture: 0, u_exposition: 1 };
  }

  LGraphExposition.title = 'Exposition';
  LGraphExposition.desc = 'Controls texture exposition';

  LGraphExposition.widgets_info = {
    exposition: { widget: 'slider', min: 0, max: 3 },
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphExposition.prototype.onExecute = function () {
    var tex = this.getInputData(0);
    if (!tex) {
      return;
    }

    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    var temp = this._temp_texture;
    if (
      !temp ||
      temp.width != tex.width ||
      temp.height != tex.height ||
      temp.type != tex.type
    ) {
      temp = this._temp_texture = new GL.Texture(tex.width, tex.height, {
        type: tex.type,
        format: gl.RGBA,
        filter: gl.LINEAR,
      });
    }

    var shader = LGraphExposition._shader;
    if (!shader) {
      shader = LGraphExposition._shader = new GL.Shader(
        GL.Shader.SCREEN_VERTEX_SHADER,
        LGraphExposition.pixel_shader,
      );
    }

    var exp = this.properties.exposition;
    var exp_input = this.getInputData(1);
    if (exp_input != null) {
      exp = this.properties.exposition = exp_input;
    }
    var uniforms = this._uniforms;

    //apply shader
    temp.drawTo(function () {
      gl.disable(gl.DEPTH_TEST);
      tex.bind(0);
      shader.uniforms(uniforms).draw(GL.Mesh.getScreenQuad());
    });

    this.setOutputData(0, temp);
  };

  LGraphExposition.pixel_shader =
    'precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_texture;\n\
  uniform float u_exposition;\n\
  \n\
  void main() {\n\
    vec4 color = texture2D( u_texture, v_coord );\n\
    gl_FragColor = vec4( color.xyz * u_exposition, color.a );\n\
  }';

  LiteGraph.registerNodeType('texture/exposition', LGraphExposition);

  function LGraphToneMapping() {
    this.addInput('in', 'Texture');
    this.addInput('avg', 'number,Texture');
    this.addOutput('out', 'Texture');
    this.properties = {
      enabled: true,
      scale: 1,
      gamma: 1,
      average_lum: 1,
      lum_white: 1,
      precision: LGraphTexture.LOW,
    };

    this._uniforms = {
      u_texture: 0,
      u_lumwhite2: 1,
      u_igamma: 1,
      u_scale: 1,
      u_average_lum: 1,
    };
  }

  LGraphToneMapping.title = 'Tone Mapping';
  LGraphToneMapping.desc = 'Applies Tone Mapping to convert from high to low';

  LGraphToneMapping.widgets_info = {
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphToneMapping.prototype.onGetInputs = function () {
    return [['enabled', 'boolean']];
  };

  LGraphToneMapping.prototype.onExecute = function () {
    var tex = this.getInputData(0);
    if (!tex) {
      return;
    }

    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    if (
      this.properties.precision === LGraphTexture.PASS_THROUGH ||
      this.getInputOrProperty('enabled') === false
    ) {
      this.setOutputData(0, tex);
      return;
    }

    var temp = this._temp_texture;

    if (
      !temp ||
      temp.width != tex.width ||
      temp.height != tex.height ||
      temp.type != tex.type
    ) {
      temp = this._temp_texture = new GL.Texture(tex.width, tex.height, {
        type: tex.type,
        format: gl.RGBA,
        filter: gl.LINEAR,
      });
    }

    var avg = this.getInputData(1);
    if (avg == null) {
      avg = this.properties.average_lum;
    }

    var uniforms = this._uniforms;
    var shader = null;

    if (avg.constructor === Number) {
      this.properties.average_lum = avg;
      uniforms.u_average_lum = this.properties.average_lum;
      shader = LGraphToneMapping._shader;
      if (!shader) {
        shader = LGraphToneMapping._shader = new GL.Shader(
          GL.Shader.SCREEN_VERTEX_SHADER,
          LGraphToneMapping.pixel_shader,
        );
      }
    } else if (avg.constructor === GL.Texture) {
      uniforms.u_average_texture = avg.bind(1);
      shader = LGraphToneMapping._shader_texture;
      if (!shader) {
        shader = LGraphToneMapping._shader_texture = new GL.Shader(
          GL.Shader.SCREEN_VERTEX_SHADER,
          LGraphToneMapping.pixel_shader,
          { AVG_TEXTURE: '' },
        );
      }
    }

    uniforms.u_lumwhite2 =
      this.properties.lum_white * this.properties.lum_white;
    uniforms.u_scale = this.properties.scale;
    uniforms.u_igamma = 1 / this.properties.gamma;

    //apply shader
    gl.disable(gl.DEPTH_TEST);
    temp.drawTo(function () {
      tex.bind(0);
      shader.uniforms(uniforms).draw(GL.Mesh.getScreenQuad());
    });

    this.setOutputData(0, this._temp_texture);
  };

  LGraphToneMapping.pixel_shader =
    'precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_texture;\n\
  uniform float u_scale;\n\
  #ifdef AVG_TEXTURE\n\
    uniform sampler2D u_average_texture;\n\
  #else\n\
    uniform float u_average_lum;\n\
  #endif\n\
  uniform float u_lumwhite2;\n\
  uniform float u_igamma;\n\
  vec3 RGB2xyY (vec3 rgb)\n\
  {\n\
     const mat3 RGB2XYZ = mat3(0.4124, 0.3576, 0.1805,\n\
                   0.2126, 0.7152, 0.0722,\n\
                   0.0193, 0.1192, 0.9505);\n\
    vec3 XYZ = RGB2XYZ * rgb;\n\
    \n\
    float f = (XYZ.x + XYZ.y + XYZ.z);\n\
    return vec3(XYZ.x / f,\n\
          XYZ.y / f,\n\
          XYZ.y);\n\
  }\n\
  \n\
  void main() {\n\
    vec4 color = texture2D( u_texture, v_coord );\n\
    vec3 rgb = color.xyz;\n\
    float average_lum = 0.0;\n\
    #ifdef AVG_TEXTURE\n\
      vec3 pixel = texture2D(u_average_texture,vec2(0.5)).xyz;\n\
      average_lum = (pixel.x + pixel.y + pixel.z) / 3.0;\n\
    #else\n\
      average_lum = u_average_lum;\n\
    #endif\n\
    //Ld - this part of the code is the same for both versions\n\
    float lum = dot(rgb, vec3(0.2126, 0.7152, 0.0722));\n\
    float L = (u_scale / average_lum) * lum;\n\
    float Ld = (L * (1.0 + L / u_lumwhite2)) / (1.0 + L);\n\
    //first\n\
    //vec3 xyY = RGB2xyY(rgb);\n\
    //xyY.z *= Ld;\n\
    //rgb = xyYtoRGB(xyY);\n\
    //second\n\
    rgb = (rgb / lum) * Ld;\n\
    rgb = max(rgb,vec3(0.001));\n\
    rgb = pow( rgb, vec3( u_igamma ) );\n\
    gl_FragColor = vec4( rgb, color.a );\n\
  }';

  LiteGraph.registerNodeType('texture/tonemapping', LGraphToneMapping);

  function LGraphTexturePerlin() {
    this.addOutput('out', 'Texture');
    this.properties = {
      width: 512,
      height: 512,
      seed: 0,
      persistence: 0.1,
      octaves: 8,
      scale: 1,
      offset: [0, 0],
      amplitude: 1,
      precision: LGraphTexture.DEFAULT,
    };
    this._key = 0;
    this._texture = null;
    this._uniforms = {
      u_persistence: 0.1,
      u_seed: 0,
      u_offset: vec2.create(),
      u_scale: 1,
      u_viewport: vec2.create(),
    };
  }

  LGraphTexturePerlin.title = 'Perlin';
  LGraphTexturePerlin.desc = 'Generates a perlin noise texture';

  LGraphTexturePerlin.widgets_info = {
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
    width: { type: 'number', precision: 0, step: 1 },
    height: { type: 'number', precision: 0, step: 1 },
    octaves: { type: 'number', precision: 0, step: 1, min: 1, max: 50 },
  };

  LGraphTexturePerlin.prototype.onGetInputs = function () {
    return [
      ['seed', 'number'],
      ['persistence', 'number'],
      ['octaves', 'number'],
      ['scale', 'number'],
      ['amplitude', 'number'],
      ['offset', 'vec2'],
    ];
  };

  LGraphTexturePerlin.prototype.onExecute = function () {
    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    var w = this.properties.width | 0;
    var h = this.properties.height | 0;
    if (w == 0) {
      w = gl.viewport_data[2];
    } //0 means default
    if (h == 0) {
      h = gl.viewport_data[3];
    } //0 means default
    var type = LGraphTexture.getTextureType(this.properties.precision);

    var temp = this._texture;
    if (!temp || temp.width != w || temp.height != h || temp.type != type) {
      temp = this._texture = new GL.Texture(w, h, {
        type: type,
        format: gl.RGB,
        filter: gl.LINEAR,
      });
    }

    var persistence = this.getInputOrProperty('persistence');
    var octaves = this.getInputOrProperty('octaves');
    var offset = this.getInputOrProperty('offset');
    var scale = this.getInputOrProperty('scale');
    var amplitude = this.getInputOrProperty('amplitude');
    var seed = this.getInputOrProperty('seed');

    //reusing old texture
    var key =
      '' +
      w +
      h +
      type +
      persistence +
      octaves +
      scale +
      seed +
      offset[0] +
      offset[1] +
      amplitude;
    if (key == this._key) {
      this.setOutputData(0, temp);
      return;
    }
    this._key = key;

    //gather uniforms
    var uniforms = this._uniforms;
    uniforms.u_persistence = persistence;
    uniforms.u_octaves = octaves;
    uniforms.u_offset.set(offset);
    uniforms.u_scale = scale;
    uniforms.u_amplitude = amplitude;
    uniforms.u_seed = seed * 128;
    uniforms.u_viewport[0] = w;
    uniforms.u_viewport[1] = h;

    //render
    var shader = LGraphTexturePerlin._shader;
    if (!shader) {
      shader = LGraphTexturePerlin._shader = new GL.Shader(
        GL.Shader.SCREEN_VERTEX_SHADER,
        LGraphTexturePerlin.pixel_shader,
      );
    }

    gl.disable(gl.BLEND);
    gl.disable(gl.DEPTH_TEST);

    temp.drawTo(function () {
      shader.uniforms(uniforms).draw(GL.Mesh.getScreenQuad());
    });

    this.setOutputData(0, temp);
  };

  LGraphTexturePerlin.pixel_shader =
    'precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform vec2 u_offset;\n\
  uniform float u_scale;\n\
  uniform float u_persistence;\n\
  uniform int u_octaves;\n\
  uniform float u_amplitude;\n\
  uniform vec2 u_viewport;\n\
  uniform float u_seed;\n\
  #define M_PI 3.14159265358979323846\n\
  \n\
  float rand(vec2 c){	return fract(sin(dot(c.xy ,vec2( 12.9898 + u_seed,78.233 + u_seed))) * 43758.5453); }\n\
  \n\
  float noise(vec2 p, float freq ){\n\
    float unit = u_viewport.x/freq;\n\
    vec2 ij = floor(p/unit);\n\
    vec2 xy = mod(p,unit)/unit;\n\
    //xy = 3.*xy*xy-2.*xy*xy*xy;\n\
    xy = .5*(1.-cos(M_PI*xy));\n\
    float a = rand((ij+vec2(0.,0.)));\n\
    float b = rand((ij+vec2(1.,0.)));\n\
    float c = rand((ij+vec2(0.,1.)));\n\
    float d = rand((ij+vec2(1.,1.)));\n\
    float x1 = mix(a, b, xy.x);\n\
    float x2 = mix(c, d, xy.x);\n\
    return mix(x1, x2, xy.y);\n\
  }\n\
  \n\
  float pNoise(vec2 p, int res){\n\
    float persistance = u_persistence;\n\
    float n = 0.;\n\
    float normK = 0.;\n\
    float f = 4.;\n\
    float amp = 1.0;\n\
    int iCount = 0;\n\
    for (int i = 0; i<50; i++){\n\
      n+=amp*noise(p, f);\n\
      f*=2.;\n\
      normK+=amp;\n\
      amp*=persistance;\n\
      if (iCount >= res)\n\
        break;\n\
      iCount++;\n\
    }\n\
    float nf = n/normK;\n\
    return nf*nf*nf*nf;\n\
  }\n\
  void main() {\n\
    vec2 uv = v_coord * u_scale * u_viewport + u_offset * u_scale;\n\
    vec4 color = vec4( pNoise( uv, u_octaves ) * u_amplitude );\n\
    gl_FragColor = color;\n\
  }';

  LiteGraph.registerNodeType('texture/perlin', LGraphTexturePerlin);

  function LGraphTextureCanvas2D() {
    this.addInput('v');
    this.addOutput('out', 'Texture');
    this.properties = {
      code: LGraphTextureCanvas2D.default_code,
      width: 512,
      height: 512,
      clear: true,
      precision: LGraphTexture.DEFAULT,
      use_html_canvas: false,
    };
    this._func = null;
    this._temp_texture = null;
    this.compileCode();
  }

  LGraphTextureCanvas2D.title = 'Canvas2D';
  LGraphTextureCanvas2D.desc =
    'Executes Canvas2D code inside a texture or the viewport.';
  LGraphTextureCanvas2D.help =
    'Set width and height to 0 to match viewport size.';

  LGraphTextureCanvas2D.default_code =
    "//vars: canvas,ctx,time\nctx.fillStyle='red';\nctx.fillRect(0,0,50,50);\n";

  LGraphTextureCanvas2D.widgets_info = {
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
    code: { type: 'code' },
    width: { type: 'number', precision: 0, step: 1 },
    height: { type: 'number', precision: 0, step: 1 },
  };

  LGraphTextureCanvas2D.prototype.onPropertyChanged = function (name, value) {
    if (name == 'code') this.compileCode(value);
  };

  LGraphTextureCanvas2D.prototype.compileCode = function (code) {
    this._func = null;
    if (!LiteGraph.allow_scripts) return;

    try {
      this._func = new Function('canvas', 'ctx', 'time', 'script', 'v', code);
      this.boxcolor = '#00FF00';
    } catch (err) {
      this.boxcolor = '#FF0000';
      console.error('Error parsing script');
      console.error(err);
    }
  };

  LGraphTextureCanvas2D.prototype.onExecute = function () {
    var func = this._func;
    if (!func || !this.isOutputConnected(0)) {
      return;
    }
    this.executeDraw(func);
  };

  LGraphTextureCanvas2D.prototype.executeDraw = function (func_context) {
    var width = this.properties.width || gl.canvas.width;
    var height = this.properties.height || gl.canvas.height;
    var temp = this._temp_texture;
    var type = LGraphTexture.getTextureType(this.properties.precision);
    if (
      !temp ||
      temp.width != width ||
      temp.height != height ||
      temp.type != type
    ) {
      temp = this._temp_texture = new GL.Texture(width, height, {
        format: gl.RGBA,
        filter: gl.LINEAR,
        type: type,
      });
    }

    var v = this.getInputData(0);

    var properties = this.properties;
    var that = this;
    var time = this.graph.getTime();
    var ctx = gl;
    var canvas = gl.canvas;
    if (this.properties.use_html_canvas || !global.enableWebGLCanvas) {
      if (!this._canvas) {
        canvas = this._canvas = createCanvas(width.height);
        ctx = this._ctx = canvas.getContext('2d');
      } else {
        canvas = this._canvas;
        ctx = this._ctx;
      }
      canvas.width = width;
      canvas.height = height;
    }

    if (ctx == gl)
      //using Canvas2DtoWebGL
      temp.drawTo(function () {
        gl.start2D();
        if (properties.clear) {
          gl.clearColor(0, 0, 0, 0);
          gl.clear(gl.COLOR_BUFFER_BIT);
        }

        try {
          if (func_context.draw) {
            func_context.draw.call(that, canvas, ctx, time, func_context, v);
          } else {
            func_context.call(that, canvas, ctx, time, func_context, v);
          }
          that.boxcolor = '#00FF00';
        } catch (err) {
          that.boxcolor = '#FF0000';
          console.error('Error executing script');
          console.error(err);
        }
        gl.finish2D();
      });
    //rendering to offscreen canvas and uploading to texture
    else {
      if (properties.clear) ctx.clearRect(0, 0, canvas.width, canvas.height);

      try {
        if (func_context.draw) {
          func_context.draw.call(this, canvas, ctx, time, func_context, v);
        } else {
          func_context.call(this, canvas, ctx, time, func_context, v);
        }
        this.boxcolor = '#00FF00';
      } catch (err) {
        this.boxcolor = '#FF0000';
        console.error('Error executing script');
        console.error(err);
      }
      temp.uploadImage(canvas);
    }

    this.setOutputData(0, temp);
  };

  LiteGraph.registerNodeType('texture/canvas2D', LGraphTextureCanvas2D);

  // To do chroma keying *****************

  function LGraphTextureMatte() {
    this.addInput('in', 'Texture');

    this.addOutput('out', 'Texture');
    this.properties = {
      key_color: vec3.fromValues(0, 1, 0),
      threshold: 0.8,
      slope: 0.2,
      precision: LGraphTexture.DEFAULT,
    };
  }

  LGraphTextureMatte.title = 'Matte';
  LGraphTextureMatte.desc = 'Extracts background';

  LGraphTextureMatte.widgets_info = {
    key_color: { widget: 'color' },
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphTextureMatte.prototype.onExecute = function () {
    if (!this.isOutputConnected(0)) {
      return;
    } //saves work

    var tex = this.getInputData(0);

    if (this.properties.precision === LGraphTexture.PASS_THROUGH) {
      this.setOutputData(0, tex);
      return;
    }

    if (!tex) {
      return;
    }

    this._tex = LGraphTexture.getTargetTexture(
      tex,
      this._tex,
      this.properties.precision,
    );

    gl.disable(gl.BLEND);
    gl.disable(gl.DEPTH_TEST);

    if (!this._uniforms) {
      this._uniforms = {
        u_texture: 0,
        u_key_color: this.properties.key_color,
        u_threshold: 1,
        u_slope: 1,
      };
    }
    var uniforms = this._uniforms;

    var mesh = Mesh.getScreenQuad();
    var shader = LGraphTextureMatte._shader;
    if (!shader) {
      shader = LGraphTextureMatte._shader = new GL.Shader(
        GL.Shader.SCREEN_VERTEX_SHADER,
        LGraphTextureMatte.pixel_shader,
      );
    }

    uniforms.u_key_color = this.properties.key_color;
    uniforms.u_threshold = this.properties.threshold;
    uniforms.u_slope = this.properties.slope;

    this._tex.drawTo(function () {
      tex.bind(0);
      shader.uniforms(uniforms).draw(mesh);
    });

    this.setOutputData(0, this._tex);
  };

  LGraphTextureMatte.pixel_shader =
    'precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_texture;\n\
  uniform vec3 u_key_color;\n\
  uniform float u_threshold;\n\
  uniform float u_slope;\n\
  \n\
  void main() {\n\
    vec3 color = texture2D( u_texture, v_coord ).xyz;\n\
    float diff = length( normalize(color) - normalize(u_key_color) );\n\
    float edge = u_threshold * (1.0 - u_slope);\n\
    float alpha = smoothstep( edge, u_threshold, diff);\n\
    gl_FragColor = vec4( color, alpha );\n\
  }';

  LiteGraph.registerNodeType('texture/matte', LGraphTextureMatte);

  //***********************************
  function LGraphCubemapToTexture2D() {
    this.addInput('in', 'texture');
    this.addInput('yaw', 'number');
    this.addOutput('out', 'texture');
    this.properties = { yaw: 0 };
  }

  LGraphCubemapToTexture2D.title = 'CubemapToTexture2D';
  LGraphCubemapToTexture2D.desc =
    'Transforms a CUBEMAP texture into a TEXTURE2D in Polar Representation';

  LGraphCubemapToTexture2D.prototype.onExecute = function () {
    if (!this.isOutputConnected(0)) return;

    var tex = this.getInputData(0);
    if (!tex || tex.texture_type != GL.TEXTURE_CUBE_MAP) return;
    if (
      this._last_tex &&
      (this._last_tex.height != tex.height || this._last_tex.type != tex.type)
    )
      this._last_tex = null;
    var yaw = this.getInputOrProperty('yaw');
    this._last_tex = GL.Texture.cubemapToTexture2D(
      tex,
      tex.height,
      this._last_tex,
      true,
      yaw,
    );
    this.setOutputData(0, this._last_tex);
  };

  LiteGraph.registerNodeType(
    'texture/cubemapToTexture2D',
    LGraphCubemapToTexture2D,
  );
})(this);

(function (global) {
  if (typeof GL == 'undefined') return;

  var LiteGraph = global.LiteGraph;
  var LGraphCanvas = global.LGraphCanvas;

  var SHADERNODES_COLOR = '#345';

  var LGShaders = (LiteGraph.Shaders = {});

  var GLSL_types = (LGShaders.GLSL_types = [
    'float',
    'vec2',
    'vec3',
    'vec4',
    'mat3',
    'mat4',
    'sampler2D',
    'samplerCube',
  ]);
  var GLSL_types_const = (LGShaders.GLSL_types_const = [
    'float',
    'vec2',
    'vec3',
    'vec4',
  ]);

  var GLSL_functions_desc = {
    radians: 'T radians(T degrees)',
    degrees: 'T degrees(T radians)',
    sin: 'T sin(T angle)',
    cos: 'T cos(T angle)',
    tan: 'T tan(T angle)',
    asin: 'T asin(T x)',
    acos: 'T acos(T x)',
    atan: 'T atan(T x)',
    atan2: 'T atan(T x,T y)',
    pow: 'T pow(T x,T y)',
    exp: 'T exp(T x)',
    log: 'T log(T x)',
    exp2: 'T exp2(T x)',
    log2: 'T log2(T x)',
    sqrt: 'T sqrt(T x)',
    inversesqrt: 'T inversesqrt(T x)',
    abs: 'T abs(T x)',
    sign: 'T sign(T x)',
    floor: 'T floor(T x)',
    round: 'T round(T x)',
    ceil: 'T ceil(T x)',
    fract: 'T fract(T x)',
    mod: 'T mod(T x,T y)', //"T mod(T x,float y)"
    min: 'T min(T x,T y)',
    max: 'T max(T x,T y)',
    clamp: 'T clamp(T x,T minVal = 0.0,T maxVal = 1.0)',
    mix: 'T mix(T x,T y,T a)', //"T mix(T x,T y,float a)"
    step: 'T step(T edge, T edge2, T x)', //"T step(float edge, T x)"
    smoothstep: 'T smoothstep(T edge, T edge2, T x)', //"T smoothstep(float edge, T x)"
    length: 'float length(T x)',
    distance: 'float distance(T p0, T p1)',
    normalize: 'T normalize(T x)',
    dot: 'float dot(T x,T y)',
    cross: 'vec3 cross(vec3 x,vec3 y)',
    reflect: 'vec3 reflect(vec3 V,vec3 N)',
    refract: 'vec3 refract(vec3 V,vec3 N, float IOR)',
  };

  //parse them
  var GLSL_functions = {};
  var GLSL_functions_name = [];
  parseGLSLDescriptions();

  LGShaders.ALL_TYPES = 'float,vec2,vec3,vec4';

  function parseGLSLDescriptions() {
    GLSL_functions_name.length = 0;

    for (var i in GLSL_functions_desc) {
      var op = GLSL_functions_desc[i];
      var index = op.indexOf(' ');
      var return_type = op.substr(0, index);
      var index2 = op.indexOf('(', index);
      var func_name = op.substr(index, index2 - index).trim();
      var params = op.substr(index2 + 1, op.length - index2 - 2).split(',');
      for (var j in params) {
        var p = params[j].split(' ').filter(function (a) {
          return a;
        });
        params[j] = { type: p[0].trim(), name: p[1].trim() };
        if (p[2] == '=') params[j].value = p[3].trim();
      }
      GLSL_functions[i] = {
        return_type: return_type,
        func: func_name,
        params: params,
      };
      GLSL_functions_name.push(func_name);
      //console.log( GLSL_functions[i] );
    }
  }

  //common actions to all shader node classes
  function registerShaderNode(type, node_ctor) {
    //static attributes
    node_ctor.color = SHADERNODES_COLOR;
    node_ctor.filter = 'shader';

    //common methods
    node_ctor.prototype.clearDestination = function () {
      this.shader_destination = {};
    };
    node_ctor.prototype.propagateDestination = function propagateDestination(
      dest_name,
    ) {
      this.shader_destination[dest_name] = true;
      if (this.inputs)
        for (var i = 0; i < this.inputs.length; ++i) {
          var origin_node = this.getInputNode(i);
          if (origin_node) origin_node.propagateDestination(dest_name);
        }
    };
    if (!node_ctor.prototype.onPropertyChanged)
      node_ctor.prototype.onPropertyChanged = function () {
        if (this.graph) this.graph._version++;
      };

    /*
  if(!node_ctor.prototype.onGetCode)
    node_ctor.prototype.onGetCode = function()
    {
      //check destination to avoid lonely nodes
      if(!this.shader_destination)
        return;
      //grab inputs with types
      var inputs = [];
      if(this.inputs)
      for(var i = 0; i < this.inputs.length; ++i)
        inputs.push({ type: this.getInputData(i), name: getInputLinkID(this,i) });
      var outputs = [];
      if(this.outputs)
      for(var i = 0; i < this.outputs.length; ++i)
        outputs.push({ name: getOutputLinkID(this,i) });
      //pass to code func
      var results = this.extractCode(inputs);
      //grab output, pass to next
      if(results)
      for(var i = 0; i < results.length; ++i)
      {
        var r = results[i];
        if(!r)
          continue;
        this.setOutputData(i,r.value);
      }
    }
  */

    LiteGraph.registerNodeType('shader::' + type, node_ctor);
  }

  function getShaderNodeVarName(node, name) {
    return 'VAR_' + (name || 'TEMP') + '_' + node.id;
  }

  function getInputLinkID(node, slot) {
    if (!node.inputs) return null;
    var link = node.getInputLink(slot);
    if (!link) return null;
    var origin_node = node.graph.getNodeById(link.origin_id);
    if (!origin_node) return null;
    if (origin_node.getOutputVarName)
      return origin_node.getOutputVarName(link.origin_slot);
    //generate
    return 'link_' + origin_node.id + '_' + link.origin_slot;
  }

  function getOutputLinkID(node, slot) {
    if (!node.isOutputConnected(slot)) return null;
    return 'link_' + node.id + '_' + slot;
  }

  LGShaders.registerShaderNode = registerShaderNode;
  LGShaders.getInputLinkID = getInputLinkID;
  LGShaders.getOutputLinkID = getOutputLinkID;
  LGShaders.getShaderNodeVarName = getShaderNodeVarName;
  LGShaders.parseGLSLDescriptions = parseGLSLDescriptions;

  //given a const number, it transform it to a string that matches a type
  var valueToGLSL = (LiteGraph.valueToGLSL = function valueToGLSL(
    v,
    type,
    precision,
  ) {
    var n = 5; //num decimals
    if (precision != null) n = precision;
    if (!type) {
      if (v.constructor === Number) type = 'float';
      else if (v.length) {
        switch (v.length) {
          case 2:
            type = 'vec2';
            break;
          case 3:
            type = 'vec3';
            break;
          case 4:
            type = 'vec4';
            break;
          case 9:
            type = 'mat3';
            break;
          case 16:
            type = 'mat4';
            break;
          default:
            throw 'unknown type for glsl value size';
        }
      } else throw 'unknown type for glsl value: ' + v.constructor;
    }
    switch (type) {
      case 'float':
        return v.toFixed(n);
        break;
      case 'vec2':
        return 'vec2(' + v[0].toFixed(n) + ',' + v[1].toFixed(n) + ')';
        break;
      case 'color3':
      case 'vec3':
        return (
          'vec3(' +
          v[0].toFixed(n) +
          ',' +
          v[1].toFixed(n) +
          ',' +
          v[2].toFixed(n) +
          ')'
        );
        break;
      case 'color4':
      case 'vec4':
        return (
          'vec4(' +
          v[0].toFixed(n) +
          ',' +
          v[1].toFixed(n) +
          ',' +
          v[2].toFixed(n) +
          ',' +
          v[3].toFixed(n) +
          ')'
        );
        break;
      case 'mat3':
        return 'mat3(1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0)';
        break; //not fully supported yet
      case 'mat4':
        return 'mat4(1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0)';
        break; //not fully supported yet
      default:
        throw ('unknown glsl type in valueToGLSL:', type);
    }

    return '';
  });

  //makes sure that a var is of a type, and if not, it converts it
  var varToTypeGLSL = (LiteGraph.varToTypeGLSL = function varToTypeGLSL(
    v,
    input_type,
    output_type,
  ) {
    if (input_type == output_type) return v;
    if (v == null)
      switch (output_type) {
        case 'float':
          return '0.0';
        case 'vec2':
          return 'vec2(0.0)';
        case 'vec3':
          return 'vec3(0.0)';
        case 'vec4':
          return 'vec4(0.0,0.0,0.0,1.0)';
        default: //null
          return null;
      }

    if (!output_type) throw 'error: no output type specified';
    if (output_type == 'float') {
      switch (input_type) {
        //case "float":
        case 'vec2':
        case 'vec3':
        case 'vec4':
          return v + '.x';
          break;
        default: //null
          return '0.0';
          break;
      }
    } else if (output_type == 'vec2') {
      switch (input_type) {
        case 'float':
          return 'vec2(' + v + ')';
        //case "vec2":
        case 'vec3':
        case 'vec4':
          return v + '.xy';
        default: //null
          return 'vec2(0.0)';
      }
    } else if (output_type == 'vec3') {
      switch (input_type) {
        case 'float':
          return 'vec3(' + v + ')';
        case 'vec2':
          return 'vec3(' + v + ',0.0)';
        //case "vec3":
        case 'vec4':
          return v + '.xyz';
        default: //null
          return 'vec3(0.0)';
      }
    } else if (output_type == 'vec4') {
      switch (input_type) {
        case 'float':
          return 'vec4(' + v + ')';
        case 'vec2':
          return 'vec4(' + v + ',0.0,1.0)';
        case 'vec3':
          return 'vec4(' + v + ',1.0)';
        default: //null
          return 'vec4(0.0,0.0,0.0,1.0)';
      }
    }
    throw 'type cannot be converted';
  });

  //used to plug incompatible stuff
  var convertVarToGLSLType = (LiteGraph.convertVarToGLSLType =
    function convertVarToGLSLType(varname, type, target_type) {
      if (type == target_type) return varname;
      if (type == 'float') return target_type + '(' + varname + ')';
      if (target_type == 'vec2')
        //works for vec2,vec3 and vec4
        return 'vec2(' + varname + '.xy)';
      if (target_type == 'vec3') {
        //works for vec2,vec3 and vec4
        if (type == 'vec2') return 'vec3(' + varname + ',0.0)';
        if (type == 'vec4') return 'vec4(' + varname + '.xyz)';
      }
      if (target_type == 'vec4') {
        if (type == 'vec2') return 'vec4(' + varname + ',0.0,0.0)';
        if (target_type == 'vec3') return 'vec4(' + varname + ',1.0)';
      }
      return null;
    });

  //used to host a shader body **************************************
  function LGShaderContext() {
    //to store the code template
    this.vs_template = '';
    this.fs_template = '';

    //required so nodes now where to fetch the input data
    this.buffer_names = {
      uvs: 'v_coord',
    };

    this.extra = {}; //to store custom info from the nodes (like if this shader supports a feature, etc)

    this._functions = {};
    this._uniforms = {};
    this._codeparts = {};
    this._uniform_value = null;
  }

  LGShaderContext.prototype.clear = function () {
    this._uniforms = {};
    this._functions = {};
    this._codeparts = {};
    this._uniform_value = null;

    this.extra = {};
  };

  LGShaderContext.prototype.addUniform = function (name, type, value) {
    this._uniforms[name] = type;
    if (value != null) {
      if (!this._uniform_value) this._uniform_value = {};
      this._uniform_value[name] = value;
    }
  };

  LGShaderContext.prototype.addFunction = function (name, code) {
    this._functions[name] = code;
  };

  LGShaderContext.prototype.addCode = function (hook, code, destinations) {
    destinations = destinations || { '': '' };
    for (var i in destinations) {
      var h = i ? i + '_' + hook : hook;
      if (!this._codeparts[h]) this._codeparts[h] = code + '\n';
      else this._codeparts[h] += code + '\n';
    }
  };

  //the system works by grabbing code fragments from every node and concatenating them in blocks depending on where must they be attached
  LGShaderContext.prototype.computeCodeBlocks = function (
    graph,
    extra_uniforms,
  ) {
    //prepare context
    this.clear();

    //grab output nodes
    var vertexout = graph.findNodesByType('shader::output/vertex');
    vertexout = vertexout && vertexout.length ? vertexout[0] : null;
    var fragmentout = graph.findNodesByType('shader::output/fragcolor');
    fragmentout = fragmentout && fragmentout.length ? fragmentout[0] : null;
    if (!fragmentout)
      //??
      return null;

    //propagate back destinations
    graph.sendEventToAllNodes('clearDestination');
    if (vertexout) vertexout.propagateDestination('vs');
    if (fragmentout) fragmentout.propagateDestination('fs');

    //gets code from graph
    graph.sendEventToAllNodes('onGetCode', this);

    var uniforms = '';
    for (var i in this._uniforms)
      uniforms += 'uniform ' + this._uniforms[i] + ' ' + i + ';\n';
    if (extra_uniforms)
      for (var i in extra_uniforms)
        uniforms += 'uniform ' + extra_uniforms[i] + ' ' + i + ';\n';

    var functions = '';
    for (var i in this._functions)
      functions += '//' + i + '\n' + this._functions[i] + '\n';

    var blocks = this._codeparts;
    blocks.uniforms = uniforms;
    blocks.functions = functions;
    return blocks;
  };

  //replaces blocks using the vs and fs template and returns the final codes
  LGShaderContext.prototype.computeShaderCode = function (graph) {
    var blocks = this.computeCodeBlocks(graph);
    var vs_code = GL.Shader.replaceCodeUsingContext(this.vs_template, blocks);
    var fs_code = GL.Shader.replaceCodeUsingContext(this.fs_template, blocks);
    return {
      vs_code: vs_code,
      fs_code: fs_code,
    };
  };

  //generates the shader code from the template and the
  LGShaderContext.prototype.computeShader = function (graph, shader) {
    var finalcode = this.computeShaderCode(graph);
    console.log(finalcode.vs_code, finalcode.fs_code);

    if (!LiteGraph.catch_exceptions) {
      this._shader_error = true;
      if (shader) shader.updateShader(finalcode.vs_code, finalcode.fs_code);
      else shader = new GL.Shader(finalcode.vs_code, finalcode.fs_code);
      this._shader_error = false;
      return shader;
    }

    try {
      if (shader) shader.updateShader(finalcode.vs_code, finalcode.fs_code);
      else shader = new GL.Shader(finalcode.vs_code, finalcode.fs_code);
      this._shader_error = false;
      return shader;
    } catch (err) {
      if (!this._shader_error) {
        console.error(err);
        if (err.indexOf('Fragment shader') != -1)
          console.log(
            finalcode.fs_code
              .split('\n')
              .map(function (v, i) {
                return i + '.- ' + v;
              })
              .join('\n'),
          );
        else console.log(finalcode.vs_code);
      }
      this._shader_error = true;
      return null;
    }

    return null; //never here
  };

  LGShaderContext.prototype.getShader = function (graph) {
    //if graph not changed?
    if (this._shader && this._shader._version == graph._version)
      return this._shader;

    //compile shader
    var shader = this.computeShader(graph, this._shader);
    if (!shader) return null;

    this._shader = shader;
    shader._version = graph._version;
    return shader;
  };

  //some shader nodes could require to fill the box with some uniforms
  LGShaderContext.prototype.fillUniforms = function (uniforms, param) {
    if (!this._uniform_value) return;

    for (var i in this._uniform_value) {
      var v = this._uniform_value[i];
      if (v == null) continue;
      if (v.constructor === Function) uniforms[i] = v.call(this, param);
      else if (v.constructor === GL.Texture) {
        //todo...
      } else uniforms[i] = v;
    }
  };

  LiteGraph.ShaderContext = LiteGraph.Shaders.Context = LGShaderContext;

  // LGraphShaderGraph *****************************
  // applies a shader graph to texture, it can be uses as an example

  function LGraphShaderGraph() {
    //before inputs
    this.subgraph = new LiteGraph.LGraph();
    this.subgraph._subgraph_node = this;
    this.subgraph._is_subgraph = true;
    this.subgraph.filter = 'shader';

    this.addInput('in', 'texture');
    this.addOutput('out', 'texture');
    this.properties = {
      width: 0,
      height: 0,
      alpha: false,
      precision:
        typeof LGraphTexture != 'undefined' ? LGraphTexture.DEFAULT : 2,
    };

    var inputNode = this.subgraph.findNodesByType('shader::input/uniform')[0];
    inputNode.pos = [200, 300];

    var sampler = LiteGraph.createNode('shader::texture/sampler2D');
    sampler.pos = [400, 300];
    this.subgraph.add(sampler);

    var outnode = LiteGraph.createNode('shader::output/fragcolor');
    outnode.pos = [600, 300];
    this.subgraph.add(outnode);

    inputNode.connect(0, sampler);
    sampler.connect(0, outnode);

    this.size = [180, 60];
    this.redraw_on_mouse = true; //force redraw

    this._uniforms = {};
    this._shader = null;
    this._context = new LGShaderContext();
    this._context.vs_template =
      '#define VERTEX\n' + GL.Shader.SCREEN_VERTEX_SHADER;
    this._context.fs_template = LGraphShaderGraph.template;
  }

  LGraphShaderGraph.template =
    '\n\
#define FRAGMENT\n\
precision highp float;\n\
varying vec2 v_coord;\n\
{{varying}}\n\
{{uniforms}}\n\
{{functions}}\n\
{{fs_functions}}\n\
void main() {\n\n\
vec2 uv = v_coord;\n\
vec4 fragcolor = vec4(0.0);\n\
vec4 fragcolor1 = vec4(0.0);\n\
{{fs_code}}\n\
gl_FragColor = fragcolor;\n\
}\n\
';

  LGraphShaderGraph.widgets_info = {
    precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
  };

  LGraphShaderGraph.title = 'ShaderGraph';
  LGraphShaderGraph.desc = 'Builds a shader using a graph';
  LGraphShaderGraph.input_node_type = 'input/uniform';
  LGraphShaderGraph.output_node_type = 'output/fragcolor';
  LGraphShaderGraph.title_color = SHADERNODES_COLOR;

  LGraphShaderGraph.prototype.onSerialize = function (o) {
    o.subgraph = this.subgraph.serialize();
  };

  LGraphShaderGraph.prototype.onConfigure = function (o) {
    this.subgraph.configure(o.subgraph);
  };

  LGraphShaderGraph.prototype.onExecute = function () {
    if (!this.isOutputConnected(0)) return;

    //read input texture
    var intex = this.getInputData(0);
    if (intex && intex.constructor != GL.Texture) intex = null;

    var w = this.properties.width | 0;
    var h = this.properties.height | 0;
    if (w == 0) {
      w = intex ? intex.width : gl.viewport_data[2];
    } //0 means default
    if (h == 0) {
      h = intex ? intex.height : gl.viewport_data[3];
    } //0 means default

    var type = LGraphTexture.getTextureType(this.properties.precision, intex);

    var texture = this._texture;
    if (
      !texture ||
      texture.width != w ||
      texture.height != h ||
      texture.type != type
    ) {
      texture = this._texture = new GL.Texture(w, h, {
        type: type,
        format: this.alpha ? gl.RGBA : gl.RGB,
        filter: gl.LINEAR,
      });
    }

    var shader = this.getShader(this.subgraph);
    if (!shader) return;

    var uniforms = this._uniforms;
    this._context.fillUniforms(uniforms);

    var tex_slot = 0;
    if (this.inputs)
      for (var i = 0; i < this.inputs.length; ++i) {
        var input = this.inputs[i];
        var data = this.getInputData(i);
        if (input.type == 'texture') {
          if (!data) data = GL.Texture.getWhiteTexture();
          data = data.bind(tex_slot++);
        }

        if (data != null) uniforms['u_' + input.name] = data;
      }

    var mesh = GL.Mesh.getScreenQuad();

    gl.disable(gl.DEPTH_TEST);
    gl.disable(gl.BLEND);

    texture.drawTo(function () {
      shader.uniforms(uniforms);
      shader.draw(mesh);
    });

    //use subgraph output
    this.setOutputData(0, texture);
  };

  //add input node inside subgraph
  LGraphShaderGraph.prototype.onInputAdded = function (slot_info) {
    var subnode = LiteGraph.createNode('shader::input/uniform');
    subnode.setProperty('name', slot_info.name);
    subnode.setProperty('type', slot_info.type);
    this.subgraph.add(subnode);
  };

  //remove all
  LGraphShaderGraph.prototype.onInputRemoved = function (slot, slot_info) {
    var nodes = this.subgraph.findNodesByType('shader::input/uniform');
    for (var i = 0; i < nodes.length; ++i) {
      var node = nodes[i];
      if (node.properties.name == slot_info.name) this.subgraph.remove(node);
    }
  };

  LGraphShaderGraph.prototype.computeSize = function () {
    var num_inputs = this.inputs ? this.inputs.length : 0;
    var num_outputs = this.outputs ? this.outputs.length : 0;
    return [
      200,
      Math.max(num_inputs, num_outputs) * LiteGraph.NODE_SLOT_HEIGHT +
        LiteGraph.NODE_TITLE_HEIGHT +
        10,
    ];
  };

  LGraphShaderGraph.prototype.getShader = function () {
    var shader = this._context.getShader(this.subgraph);
    if (!shader) this.boxcolor = 'red';
    else this.boxcolor = null;
    return shader;
  };

  LGraphShaderGraph.prototype.onDrawBackground = function (
    ctx,
    graphcanvas,
    canvas,
    pos,
  ) {
    if (this.flags.collapsed) return;

    //allows to preview the node if the canvas is a webgl canvas
    var tex = this.getOutputData(0);
    var inputs_y = this.inputs
      ? this.inputs.length * LiteGraph.NODE_SLOT_HEIGHT
      : 0;
    if (
      tex &&
      ctx == tex.gl &&
      this.size[1] > inputs_y + LiteGraph.NODE_TITLE_HEIGHT
    ) {
      ctx.drawImage(
        tex,
        10,
        y,
        this.size[0] - 20,
        this.size[1] - inputs_y - LiteGraph.NODE_TITLE_HEIGHT,
      );
    }

    var y = this.size[1] - LiteGraph.NODE_TITLE_HEIGHT + 0.5;

    //button
    var over = LiteGraph.isInsideRectangle(
      pos[0],
      pos[1],
      this.pos[0],
      this.pos[1] + y,
      this.size[0],
      LiteGraph.NODE_TITLE_HEIGHT,
    );
    ctx.fillStyle = over ? '#555' : '#222';
    ctx.beginPath();
    if (this._shape == LiteGraph.BOX_SHAPE)
      ctx.rect(0, y, this.size[0] + 1, LiteGraph.NODE_TITLE_HEIGHT);
    else
      ctx.roundRect(0, y, this.size[0] + 1, LiteGraph.NODE_TITLE_HEIGHT, 0, 8);
    ctx.fill();

    //button
    ctx.textAlign = 'center';
    ctx.font = '24px Arial';
    ctx.fillStyle = over ? '#DDD' : '#999';
    ctx.fillText('+', this.size[0] * 0.5, y + 24);
  };

  LGraphShaderGraph.prototype.onMouseDown = function (
    e,
    localpos,
    graphcanvas,
  ) {
    var y = this.size[1] - LiteGraph.NODE_TITLE_HEIGHT + 0.5;
    if (localpos[1] > y) {
      graphcanvas.showSubgraphPropertiesDialog(this);
    }
  };

  LGraphShaderGraph.prototype.onDrawSubgraphBackground = function (
    graphcanvas,
  ) {
    //TODO
  };

  LGraphShaderGraph.prototype.getExtraMenuOptions = function (graphcanvas) {
    var that = this;
    var options = [
      {
        content: 'Print Code',
        callback: function () {
          var code = that._context.computeShaderCode();
          console.log(code.vs_code, code.fs_code);
        },
      },
    ];

    return options;
  };

  LiteGraph.registerNodeType('texture/shaderGraph', LGraphShaderGraph);

  function shaderNodeFromFunction(classname, params, return_type, code) {
    //TODO
  }

  //Shader Nodes ***********************************************************

  //applies a shader graph to a code
  function LGraphShaderUniform() {
    this.addOutput('out', '');
    this.properties = { name: '', type: '' };
  }

  LGraphShaderUniform.title = 'Uniform';
  LGraphShaderUniform.desc = 'Input data for the shader';

  LGraphShaderUniform.prototype.getTitle = function () {
    if (this.properties.name && this.flags.collapsed)
      return this.properties.type + ' ' + this.properties.name;
    return 'Uniform';
  };

  LGraphShaderUniform.prototype.onPropertyChanged = function (name, value) {
    this.outputs[0].name = this.properties.type + ' ' + this.properties.name;
  };

  LGraphShaderUniform.prototype.onGetCode = function (context) {
    if (!this.shader_destination) return;

    var type = this.properties.type;
    if (!type) {
      if (!context.onGetPropertyInfo) return;
      var info = context.onGetPropertyInfo(this.property.name);
      if (!info) return;
      type = info.type;
    }
    if (type == 'number') type = 'float';
    else if (type == 'texture') type = 'sampler2D';
    if (LGShaders.GLSL_types.indexOf(type) == -1) return;

    context.addUniform('u_' + this.properties.name, type);
    this.setOutputData(0, type);
  };

  LGraphShaderUniform.prototype.getOutputVarName = function (slot) {
    return 'u_' + this.properties.name;
  };

  registerShaderNode('input/uniform', LGraphShaderUniform);

  function LGraphShaderAttribute() {
    this.addOutput('out', 'vec2');
    this.properties = { name: 'coord', type: 'vec2' };
  }

  LGraphShaderAttribute.title = 'Attribute';
  LGraphShaderAttribute.desc = 'Input data from mesh attribute';

  LGraphShaderAttribute.prototype.getTitle = function () {
    return 'att. ' + this.properties.name;
  };

  LGraphShaderAttribute.prototype.onGetCode = function (context) {
    if (!this.shader_destination) return;

    var type = this.properties.type;
    if (!type || LGShaders.GLSL_types.indexOf(type) == -1) return;
    if (type == 'number') type = 'float';
    if (this.properties.name != 'coord') {
      context.addCode(
        'varying',
        ' varying ' + type + ' v_' + this.properties.name + ';',
      );
      //if( !context.varyings[ this.properties.name ] )
      //context.addCode( "vs_code", "v_" + this.properties.name + " = " + input_name + ";" );
    }
    this.setOutputData(0, type);
  };

  LGraphShaderAttribute.prototype.getOutputVarName = function (slot) {
    return 'v_' + this.properties.name;
  };

  registerShaderNode('input/attribute', LGraphShaderAttribute);

  function LGraphShaderSampler2D() {
    this.addInput('tex', 'sampler2D');
    this.addInput('uv', 'vec2');
    this.addOutput('rgba', 'vec4');
    this.addOutput('rgb', 'vec3');
  }

  LGraphShaderSampler2D.title = 'Sampler2D';
  LGraphShaderSampler2D.desc = 'Reads a pixel from a texture';

  LGraphShaderSampler2D.prototype.onGetCode = function (context) {
    if (!this.shader_destination) return;

    var texname = getInputLinkID(this, 0);
    var varname = getShaderNodeVarName(this);
    var code = 'vec4 ' + varname + ' = vec4(0.0);\n';
    if (texname) {
      var uvname = getInputLinkID(this, 1) || context.buffer_names.uvs;
      code += varname + ' = texture2D(' + texname + ',' + uvname + ');\n';
    }

    var link0 = getOutputLinkID(this, 0);
    if (link0)
      code += 'vec4 ' + getOutputLinkID(this, 0) + ' = ' + varname + ';\n';

    var link1 = getOutputLinkID(this, 1);
    if (link1)
      code += 'vec3 ' + getOutputLinkID(this, 1) + ' = ' + varname + '.xyz;\n';

    context.addCode('code', code, this.shader_destination);
    this.setOutputData(0, 'vec4');
    this.setOutputData(1, 'vec3');
  };

  registerShaderNode('texture/sampler2D', LGraphShaderSampler2D);

  //*********************************

  function LGraphShaderConstant() {
    this.addOutput('', 'float');

    this.properties = {
      type: 'float',
      value: 0,
    };

    this.addWidget('combo', 'type', 'float', null, {
      values: GLSL_types_const,
      property: 'type',
    });
    this.updateWidgets();
  }

  LGraphShaderConstant.title = 'const';

  LGraphShaderConstant.prototype.getTitle = function () {
    if (this.flags.collapsed)
      return valueToGLSL(this.properties.value, this.properties.type, 2);
    return 'Const';
  };

  LGraphShaderConstant.prototype.onPropertyChanged = function (name, value) {
    var that = this;
    if (name == 'type') {
      if (this.outputs[0].type != value) {
        this.disconnectOutput(0);
        this.outputs[0].type = value;
      }
      this.widgets.length = 1; //remove extra widgets
      this.updateWidgets();
    }
    if (name == 'value') {
      if (!value.length) this.widgets[1].value = value;
      else {
        this.widgets[1].value = value[1];
        if (value.length > 2) this.widgets[2].value = value[2];
        if (value.length > 3) this.widgets[3].value = value[3];
      }
    }
  };

  LGraphShaderConstant.prototype.updateWidgets = function (old_value) {
    var that = this;
    var old_value = this.properties.value;
    var options = { step: 0.01 };
    switch (this.properties.type) {
      case 'float':
        this.properties.value = 0;
        this.addWidget('number', 'v', 0, { step: 0.01, property: 'value' });
        break;
      case 'vec2':
        this.properties.value =
          old_value && old_value.length == 2
            ? [old_value[0], old_value[1]]
            : [0, 0, 0];
        this.addWidget(
          'number',
          'x',
          this.properties.value[0],
          function (v) {
            that.properties.value[0] = v;
          },
          options,
        );
        this.addWidget(
          'number',
          'y',
          this.properties.value[1],
          function (v) {
            that.properties.value[1] = v;
          },
          options,
        );
        break;
      case 'vec3':
        this.properties.value =
          old_value && old_value.length == 3
            ? [old_value[0], old_value[1], old_value[2]]
            : [0, 0, 0];
        this.addWidget(
          'number',
          'x',
          this.properties.value[0],
          function (v) {
            that.properties.value[0] = v;
          },
          options,
        );
        this.addWidget(
          'number',
          'y',
          this.properties.value[1],
          function (v) {
            that.properties.value[1] = v;
          },
          options,
        );
        this.addWidget(
          'number',
          'z',
          this.properties.value[2],
          function (v) {
            that.properties.value[2] = v;
          },
          options,
        );
        break;
      case 'vec4':
        this.properties.value =
          old_value && old_value.length == 4
            ? [old_value[0], old_value[1], old_value[2], old_value[3]]
            : [0, 0, 0, 0];
        this.addWidget(
          'number',
          'x',
          this.properties.value[0],
          function (v) {
            that.properties.value[0] = v;
          },
          options,
        );
        this.addWidget(
          'number',
          'y',
          this.properties.value[1],
          function (v) {
            that.properties.value[1] = v;
          },
          options,
        );
        this.addWidget(
          'number',
          'z',
          this.properties.value[2],
          function (v) {
            that.properties.value[2] = v;
          },
          options,
        );
        this.addWidget(
          'number',
          'w',
          this.properties.value[3],
          function (v) {
            that.properties.value[3] = v;
          },
          options,
        );
        break;
      default:
        console.error('unknown type for constant');
    }
  };

  LGraphShaderConstant.prototype.onGetCode = function (context) {
    if (!this.shader_destination) return;

    var value = valueToGLSL(this.properties.value, this.properties.type);
    var link_name = getOutputLinkID(this, 0);
    if (!link_name)
      //not connected
      return;

    var code =
      '	' + this.properties.type + ' ' + link_name + ' = ' + value + ';';
    context.addCode('code', code, this.shader_destination);

    this.setOutputData(0, this.properties.type);
  };

  registerShaderNode('const/const', LGraphShaderConstant);

  function LGraphShaderVec2() {
    this.addInput('xy', 'vec2');
    this.addInput('x', 'float');
    this.addInput('y', 'float');
    this.addOutput('xy', 'vec2');
    this.addOutput('x', 'float');
    this.addOutput('y', 'float');

    this.properties = { x: 0, y: 0 };
  }

  LGraphShaderVec2.title = 'vec2';
  LGraphShaderVec2.varmodes = ['xy', 'x', 'y'];

  LGraphShaderVec2.prototype.onPropertyChanged = function () {
    if (this.graph) this.graph._version++;
  };

  LGraphShaderVec2.prototype.onGetCode = function (context) {
    if (!this.shader_destination) return;

    var props = this.properties;

    var varname = getShaderNodeVarName(this);
    var code =
      '	vec2 ' + varname + ' = ' + valueToGLSL([props.x, props.y]) + ';\n';

    for (var i = 0; i < LGraphShaderVec2.varmodes.length; ++i) {
      var varmode = LGraphShaderVec2.varmodes[i];
      var inlink = getInputLinkID(this, i);
      if (!inlink) continue;
      code += '	' + varname + '.' + varmode + ' = ' + inlink + ';\n';
    }

    for (var i = 0; i < LGraphShaderVec2.varmodes.length; ++i) {
      var varmode = LGraphShaderVec2.varmodes[i];
      var outlink = getOutputLinkID(this, i);
      if (!outlink) continue;
      var type = GLSL_types_const[varmode.length - 1];
      code +=
        '	' + type + ' ' + outlink + ' = ' + varname + '.' + varmode + ';\n';
      this.setOutputData(i, type);
    }

    context.addCode('code', code, this.shader_destination);
  };

  registerShaderNode('const/vec2', LGraphShaderVec2);

  function LGraphShaderVec3() {
    this.addInput('xyz', 'vec3');
    this.addInput('x', 'float');
    this.addInput('y', 'float');
    this.addInput('z', 'float');
    this.addInput('xy', 'vec2');
    this.addInput('xz', 'vec2');
    this.addInput('yz', 'vec2');
    this.addOutput('xyz', 'vec3');
    this.addOutput('x', 'float');
    this.addOutput('y', 'float');
    this.addOutput('z', 'float');
    this.addOutput('xy', 'vec2');
    this.addOutput('xz', 'vec2');
    this.addOutput('yz', 'vec2');

    this.properties = { x: 0, y: 0, z: 0 };
  }

  LGraphShaderVec3.title = 'vec3';
  LGraphShaderVec3.varmodes = ['xyz', 'x', 'y', 'z', 'xy', 'xz', 'yz'];

  LGraphShaderVec3.prototype.onPropertyChanged = function () {
    if (this.graph) this.graph._version++;
  };

  LGraphShaderVec3.prototype.onGetCode = function (context) {
    if (!this.shader_destination) return;

    var props = this.properties;

    var varname = getShaderNodeVarName(this);
    var code =
      'vec3 ' +
      varname +
      ' = ' +
      valueToGLSL([props.x, props.y, props.z]) +
      ';\n';

    for (var i = 0; i < LGraphShaderVec3.varmodes.length; ++i) {
      var varmode = LGraphShaderVec3.varmodes[i];
      var inlink = getInputLinkID(this, i);
      if (!inlink) continue;
      code += '	' + varname + '.' + varmode + ' = ' + inlink + ';\n';
    }

    for (var i = 0; i < LGraphShaderVec3.varmodes.length; ++i) {
      var varmode = LGraphShaderVec3.varmodes[i];
      var outlink = getOutputLinkID(this, i);
      if (!outlink) continue;
      var type = GLSL_types_const[varmode.length - 1];
      code +=
        '	' + type + ' ' + outlink + ' = ' + varname + '.' + varmode + ';\n';
      this.setOutputData(i, type);
    }

    context.addCode('code', code, this.shader_destination);
  };

  registerShaderNode('const/vec3', LGraphShaderVec3);

  function LGraphShaderVec4() {
    this.addInput('xyzw', 'vec4');
    this.addInput('xyz', 'vec3');
    this.addInput('x', 'float');
    this.addInput('y', 'float');
    this.addInput('z', 'float');
    this.addInput('w', 'float');
    this.addInput('xy', 'vec2');
    this.addInput('yz', 'vec2');
    this.addInput('zw', 'vec2');
    this.addOutput('xyzw', 'vec4');
    this.addOutput('xyz', 'vec3');
    this.addOutput('x', 'float');
    this.addOutput('y', 'float');
    this.addOutput('z', 'float');
    this.addOutput('xy', 'vec2');
    this.addOutput('yz', 'vec2');
    this.addOutput('zw', 'vec2');

    this.properties = { x: 0, y: 0, z: 0, w: 0 };
  }

  LGraphShaderVec4.title = 'vec4';
  LGraphShaderVec4.varmodes = [
    'xyzw',
    'xyz',
    'x',
    'y',
    'z',
    'w',
    'xy',
    'yz',
    'zw',
  ];

  LGraphShaderVec4.prototype.onPropertyChanged = function () {
    if (this.graph) this.graph._version++;
  };

  LGraphShaderVec4.prototype.onGetCode = function (context) {
    if (!this.shader_destination) return;

    var props = this.properties;

    var varname = getShaderNodeVarName(this);
    var code =
      'vec4 ' +
      varname +
      ' = ' +
      valueToGLSL([props.x, props.y, props.z, props.w]) +
      ';\n';

    for (var i = 0; i < LGraphShaderVec4.varmodes.length; ++i) {
      var varmode = LGraphShaderVec4.varmodes[i];
      var inlink = getInputLinkID(this, i);
      if (!inlink) continue;
      code += '	' + varname + '.' + varmode + ' = ' + inlink + ';\n';
    }

    for (var i = 0; i < LGraphShaderVec4.varmodes.length; ++i) {
      var varmode = LGraphShaderVec4.varmodes[i];
      var outlink = getOutputLinkID(this, i);
      if (!outlink) continue;
      var type = GLSL_types_const[varmode.length - 1];
      code +=
        '	' + type + ' ' + outlink + ' = ' + varname + '.' + varmode + ';\n';
      this.setOutputData(i, type);
    }

    context.addCode('code', code, this.shader_destination);
  };

  registerShaderNode('const/vec4', LGraphShaderVec4);

  //*********************************

  function LGraphShaderFragColor() {
    this.addInput('color', LGShaders.ALL_TYPES);
    this.block_delete = true;
  }

  LGraphShaderFragColor.title = 'FragColor';
  LGraphShaderFragColor.desc = 'Pixel final color';

  LGraphShaderFragColor.prototype.onGetCode = function (context) {
    var link_name = getInputLinkID(this, 0);
    if (!link_name) return;
    var type = this.getInputData(0);
    var code = varToTypeGLSL(link_name, type, 'vec4');
    context.addCode('fs_code', 'fragcolor = ' + code + ';');
  };

  registerShaderNode('output/fragcolor', LGraphShaderFragColor);

  /*
function LGraphShaderDiscard()
{
  this.addInput("v","T");
  this.addInput("min","T");
  this.properties = { min_value: 0.0 };
  this.addWidget("number","min",0,{ step: 0.01, property: "min_value" });
}

LGraphShaderDiscard.title = "Discard";

LGraphShaderDiscard.prototype.onGetCode = function( context )
{
  if(!this.isOutputConnected(0))
    return;

  var inlink = getInputLinkID(this,0);
  var inlink1 = getInputLinkID(this,1);

  if(!inlink && !inlink1) //not connected
    return;
  context.addCode("code", return_type + " " + outlink + " = ( (" + inlink + " - "+minv+") / ("+ maxv+" - "+minv+") ) * ("+ maxv2+" - "+minv2+") + " + minv2 + ";", this.shader_destination );
  this.setOutputData( 0, return_type );
}

registerShaderNode( "output/discard", LGraphShaderDiscard );
*/

  // *************************************************

  function LGraphShaderOperation() {
    this.addInput('A', LGShaders.ALL_TYPES);
    this.addInput('B', LGShaders.ALL_TYPES);
    this.addOutput('out', '');
    this.properties = {
      operation: '*',
    };
    this.addWidget('combo', 'op.', this.properties.operation, {
      property: 'operation',
      values: LGraphShaderOperation.operations,
    });
  }

  LGraphShaderOperation.title = 'Operation';
  LGraphShaderOperation.operations = ['+', '-', '*', '/'];

  LGraphShaderOperation.prototype.getTitle = function () {
    if (this.flags.collapsed) return 'A' + this.properties.operation + 'B';
    else return 'Operation';
  };

  LGraphShaderOperation.prototype.onGetCode = function (context) {
    if (!this.shader_destination) return;

    if (!this.isOutputConnected(0)) return;

    var inlinks = [];
    for (var i = 0; i < 3; ++i)
      inlinks.push({
        name: getInputLinkID(this, i),
        type: this.getInputData(i) || 'float',
      });

    var outlink = getOutputLinkID(this, 0);
    if (!outlink)
      //not connected
      return;

    //func_desc
    var base_type = inlinks[0].type;
    var return_type = base_type;
    var op = this.properties.operation;

    var params = [];
    for (var i = 0; i < 2; ++i) {
      var param_code = inlinks[i].name;
      if (param_code == null) {
        //not plugged
        param_code = p.value != null ? p.value : '(1.0)';
        inlinks[i].type = 'float';
      }

      //convert
      if (inlinks[i].type != base_type) {
        if (inlinks[i].type == 'float' && (op == '*' || op == '/')) {
          //I find hard to create the opposite condition now, so I prefeer an else
        } else
          param_code = convertVarToGLSLType(
            param_code,
            inlinks[i].type,
            base_type,
          );
      }
      params.push(param_code);
    }

    context.addCode(
      'code',
      return_type + ' ' + outlink + ' = ' + params[0] + op + params[1] + ';',
      this.shader_destination,
    );
    this.setOutputData(0, return_type);
  };

  registerShaderNode('math/operation', LGraphShaderOperation);

  function LGraphShaderFunc() {
    this.addInput('A', LGShaders.ALL_TYPES);
    this.addInput('B', LGShaders.ALL_TYPES);
    this.addOutput('out', '');
    this.properties = {
      func: 'floor',
    };
    this._current = 'floor';
    this.addWidget('combo', 'func', this.properties.func, {
      property: 'func',
      values: GLSL_functions_name,
    });
  }

  LGraphShaderFunc.title = 'Func';

  LGraphShaderFunc.prototype.onPropertyChanged = function (name, value) {
    if (this.graph) this.graph._version++;

    if (name == 'func') {
      var func_desc = GLSL_functions[value];
      if (!func_desc) return;

      //remove extra inputs
      for (var i = func_desc.params.length; i < this.inputs.length; ++i)
        this.removeInput(i);

      //add and update inputs
      for (var i = 0; i < func_desc.params.length; ++i) {
        var p = func_desc.params[i];
        if (this.inputs[i])
          this.inputs[i].name = p.name + (p.value ? ' (' + p.value + ')' : '');
        else this.addInput(p.name, LGShaders.ALL_TYPES);
      }
    }
  };

  LGraphShaderFunc.prototype.getTitle = function () {
    if (this.flags.collapsed) return this.properties.func;
    else return 'Func';
  };

  LGraphShaderFunc.prototype.onGetCode = function (context) {
    if (!this.shader_destination) return;

    if (!this.isOutputConnected(0)) return;

    var inlinks = [];
    for (var i = 0; i < 3; ++i)
      inlinks.push({
        name: getInputLinkID(this, i),
        type: this.getInputData(i) || 'float',
      });

    var outlink = getOutputLinkID(this, 0);
    if (!outlink)
      //not connected
      return;

    var func_desc = GLSL_functions[this.properties.func];
    if (!func_desc) return;

    //func_desc
    var base_type = inlinks[0].type;
    var return_type = func_desc.return_type;
    if (return_type == 'T') return_type = base_type;

    var params = [];
    for (var i = 0; i < func_desc.params.length; ++i) {
      var p = func_desc.params[i];
      var param_code = inlinks[i].name;
      if (param_code == null) {
        //not plugged
        param_code = p.value != null ? p.value : '(1.0)';
        inlinks[i].type = 'float';
      }
      if (
        (p.type == 'T' && inlinks[i].type != base_type) ||
        (p.type != 'T' && inlinks[i].type != base_type)
      )
        param_code = convertVarToGLSLType(
          param_code,
          inlinks[i].type,
          base_type,
        );
      params.push(param_code);
    }

    context.addFunction(
      'round',
      'float round(float v){ return floor(v+0.5); }\nvec2 round(vec2 v){ return floor(v+vec2(0.5));}\nvec3 round(vec3 v){ return floor(v+vec3(0.5));}\nvec4 round(vec4 v){ return floor(v+vec4(0.5)); }\n',
    );
    context.addCode(
      'code',
      return_type +
        ' ' +
        outlink +
        ' = ' +
        func_desc.func +
        '(' +
        params.join(',') +
        ');',
      this.shader_destination,
    );

    this.setOutputData(0, return_type);
  };

  registerShaderNode('math/func', LGraphShaderFunc);

  function LGraphShaderSnippet() {
    this.addInput('A', LGShaders.ALL_TYPES);
    this.addInput('B', LGShaders.ALL_TYPES);
    this.addOutput('C', 'vec4');
    this.properties = {
      code: 'C = A+B',
      type: 'vec4',
    };
    this.addWidget('text', 'code', this.properties.code, { property: 'code' });
    this.addWidget('combo', 'type', this.properties.type, {
      values: ['float', 'vec2', 'vec3', 'vec4'],
      property: 'type',
    });
  }

  LGraphShaderSnippet.title = 'Snippet';

  LGraphShaderSnippet.prototype.onPropertyChanged = function (name, value) {
    if (this.graph) this.graph._version++;

    if (name == 'type' && this.outputs[0].type != value) {
      this.disconnectOutput(0);
      this.outputs[0].type = value;
    }
  };

  LGraphShaderSnippet.prototype.getTitle = function () {
    if (this.flags.collapsed) return this.properties.code;
    else return 'Snippet';
  };

  LGraphShaderSnippet.prototype.onGetCode = function (context) {
    if (!this.shader_destination || !this.isOutputConnected(0)) return;

    var inlinkA = getInputLinkID(this, 0);
    if (!inlinkA) inlinkA = '1.0';
    var inlinkB = getInputLinkID(this, 1);
    if (!inlinkB) inlinkB = '1.0';
    var outlink = getOutputLinkID(this, 0);
    if (!outlink)
      //not connected
      return;

    var inA_type = this.getInputData(0) || 'float';
    var inB_type = this.getInputData(1) || 'float';
    var return_type = this.properties.type;

    //cannot resolve input
    if (inA_type == 'T' || inB_type == 'T') {
      return null;
    }

    var funcname = 'funcSnippet' + this.id;

    var func_code =
      '\n' +
      return_type +
      ' ' +
      funcname +
      '( ' +
      inA_type +
      ' A, ' +
      inB_type +
      ' B) {\n';
    func_code += '	' + return_type + ' C = ' + return_type + '(0.0);\n';
    func_code += '	' + this.properties.code + ';\n';
    func_code += '	return C;\n}\n';

    context.addCode('functions', func_code, this.shader_destination);
    context.addCode(
      'code',
      return_type +
        ' ' +
        outlink +
        ' = ' +
        funcname +
        '(' +
        inlinkA +
        ',' +
        inlinkB +
        ');',
      this.shader_destination,
    );

    this.setOutputData(0, return_type);
  };

  registerShaderNode('utils/snippet', LGraphShaderSnippet);

  //************************************

  function LGraphShaderRand() {
    this.addOutput('out', 'float');
  }

  LGraphShaderRand.title = 'Rand';

  LGraphShaderRand.prototype.onGetCode = function (context) {
    if (!this.shader_destination || !this.isOutputConnected(0)) return;

    var outlink = getOutputLinkID(this, 0);

    context.addUniform('u_rand' + this.id, 'float', function () {
      return Math.random();
    });
    context.addCode(
      'code',
      'float ' + outlink + ' = u_rand' + this.id + ';',
      this.shader_destination,
    );
    this.setOutputData(0, 'float');
  };

  registerShaderNode('input/rand', LGraphShaderRand);

  //noise
  //https://gist.github.com/patriciogonzalezvivo/670c22f3966e662d2f83
  function LGraphShaderNoise() {
    this.addInput('out', LGShaders.ALL_TYPES);
    this.addInput('scale', 'float');
    this.addOutput('out', 'float');
    this.properties = {
      type: 'noise',
      scale: 1,
    };
    this.addWidget('combo', 'type', this.properties.type, {
      property: 'type',
      values: LGraphShaderNoise.NOISE_TYPES,
    });
    this.addWidget('number', 'scale', this.properties.scale, {
      property: 'scale',
    });
  }

  LGraphShaderNoise.NOISE_TYPES = ['noise', 'rand'];

  LGraphShaderNoise.title = 'noise';

  LGraphShaderNoise.prototype.onGetCode = function (context) {
    if (!this.shader_destination || !this.isOutputConnected(0)) return;

    var inlink = getInputLinkID(this, 0);
    var outlink = getOutputLinkID(this, 0);

    var intype = this.getInputData(0);
    if (!inlink) {
      intype = 'vec2';
      inlink = context.buffer_names.uvs;
    }

    context.addFunction('noise', LGraphShaderNoise.shader_functions);
    context.addUniform(
      'u_noise_scale' + this.id,
      'float',
      this.properties.scale,
    );
    if (intype == 'float')
      context.addCode(
        'code',
        'float ' +
          outlink +
          ' = snoise( vec2(' +
          inlink +
          ') * u_noise_scale' +
          this.id +
          ');',
        this.shader_destination,
      );
    else if (intype == 'vec2' || intype == 'vec3')
      context.addCode(
        'code',
        'float ' +
          outlink +
          ' = snoise(' +
          inlink +
          ' * u_noise_scale' +
          this.id +
          ');',
        this.shader_destination,
      );
    else if (intype == 'vec4')
      context.addCode(
        'code',
        'float ' +
          outlink +
          ' = snoise(' +
          inlink +
          '.xyz * u_noise_scale' +
          this.id +
          ');',
        this.shader_destination,
      );
    this.setOutputData(0, 'float');
  };

  registerShaderNode('math/noise', LGraphShaderNoise);

  LGraphShaderNoise.shader_functions =
    '\n\
vec3 permute(vec3 x) { return mod(((x*34.0)+1.0)*x, 289.0); }\n\
\n\
float snoise(vec2 v){\n\
const vec4 C = vec4(0.211324865405187, 0.366025403784439,-0.577350269189626, 0.024390243902439);\n\
vec2 i  = floor(v + dot(v, C.yy) );\n\
vec2 x0 = v -   i + dot(i, C.xx);\n\
vec2 i1;\n\
i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);\n\
vec4 x12 = x0.xyxy + C.xxzz;\n\
x12.xy -= i1;\n\
i = mod(i, 289.0);\n\
vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0 ))\n\
+ i.x + vec3(0.0, i1.x, 1.0 ));\n\
vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy),dot(x12.zw,x12.zw)), 0.0);\n\
m = m*m ;\n\
m = m*m ;\n\
vec3 x = 2.0 * fract(p * C.www) - 1.0;\n\
vec3 h = abs(x) - 0.5;\n\
vec3 ox = floor(x + 0.5);\n\
vec3 a0 = x - ox;\n\
m *= 1.79284291400159 - 0.85373472095314 * ( a0*a0 + h*h );\n\
vec3 g;\n\
g.x  = a0.x  * x0.x  + h.x  * x0.y;\n\
g.yz = a0.yz * x12.xz + h.yz * x12.yw;\n\
return 130.0 * dot(m, g);\n\
}\n\
vec4 permute(vec4 x){return mod(((x*34.0)+1.0)*x, 289.0);}\n\
vec4 taylorInvSqrt(vec4 r){return 1.79284291400159 - 0.85373472095314 * r;}\n\
\n\
float snoise(vec3 v){ \n\
const vec2  C = vec2(1.0/6.0, 1.0/3.0) ;\n\
const vec4  D = vec4(0.0, 0.5, 1.0, 2.0);\n\
\n\
// First corner\n\
vec3 i  = floor(v + dot(v, C.yyy) );\n\
vec3 x0 =   v - i + dot(i, C.xxx) ;\n\
\n\
// Other corners\n\
vec3 g = step(x0.yzx, x0.xyz);\n\
vec3 l = 1.0 - g;\n\
vec3 i1 = min( g.xyz, l.zxy );\n\
vec3 i2 = max( g.xyz, l.zxy );\n\
\n\
//  x0 = x0 - 0. + 0.0 * C \n\
vec3 x1 = x0 - i1 + 1.0 * C.xxx;\n\
vec3 x2 = x0 - i2 + 2.0 * C.xxx;\n\
vec3 x3 = x0 - 1. + 3.0 * C.xxx;\n\
\n\
// Permutations\n\
i = mod(i, 289.0 ); \n\
vec4 p = permute( permute( permute( \n\
           i.z + vec4(0.0, i1.z, i2.z, 1.0 ))\n\
         + i.y + vec4(0.0, i1.y, i2.y, 1.0 )) \n\
         + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));\n\
\n\
// Gradients\n\
// ( N*N points uniformly over a square, mapped onto an octahedron.)\n\
float n_ = 1.0/7.0; // N=7\n\
vec3  ns = n_ * D.wyz - D.xzx;\n\
\n\
vec4 j = p - 49.0 * floor(p * ns.z *ns.z);  //  mod(p,N*N)\n\
\n\
vec4 x_ = floor(j * ns.z);\n\
vec4 y_ = floor(j - 7.0 * x_ );    // mod(j,N)\n\
\n\
vec4 x = x_ *ns.x + ns.yyyy;\n\
vec4 y = y_ *ns.x + ns.yyyy;\n\
vec4 h = 1.0 - abs(x) - abs(y);\n\
\n\
vec4 b0 = vec4( x.xy, y.xy );\n\
vec4 b1 = vec4( x.zw, y.zw );\n\
\n\
vec4 s0 = floor(b0)*2.0 + 1.0;\n\
vec4 s1 = floor(b1)*2.0 + 1.0;\n\
vec4 sh = -step(h, vec4(0.0));\n\
\n\
vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy ;\n\
vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww ;\n\
\n\
vec3 p0 = vec3(a0.xy,h.x);\n\
vec3 p1 = vec3(a0.zw,h.y);\n\
vec3 p2 = vec3(a1.xy,h.z);\n\
vec3 p3 = vec3(a1.zw,h.w);\n\
\n\
//Normalise gradients\n\
vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));\n\
p0 *= norm.x;\n\
p1 *= norm.y;\n\
p2 *= norm.z;\n\
p3 *= norm.w;\n\
\n\
// Mix final noise value\n\
vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);\n\
m = m * m;\n\
return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1),dot(p2,x2), dot(p3,x3) ) );\n\
}\n\
\n\
vec3 hash3( vec2 p ){\n\
  vec3 q = vec3( dot(p,vec2(127.1,311.7)), \n\
         dot(p,vec2(269.5,183.3)), \n\
         dot(p,vec2(419.2,371.9)) );\n\
return fract(sin(q)*43758.5453);\n\
}\n\
vec4 hash4( vec3 p ){\n\
  vec4 q = vec4( dot(p,vec3(127.1,311.7,257.3)), \n\
         dot(p,vec3(269.5,183.3,335.1)), \n\
         dot(p,vec3(314.5,235.1,467.3)), \n\
         dot(p,vec3(419.2,371.9,114.9)) );\n\
return fract(sin(q)*43758.5453);\n\
}\n\
\n\
float iqnoise( in vec2 x, float u, float v ){\n\
  vec2 p = floor(x);\n\
  vec2 f = fract(x);\n\
\n\
float k = 1.0+63.0*pow(1.0-v,4.0);\n\
\n\
float va = 0.0;\n\
float wt = 0.0;\n\
  for( int j=-2; j<=2; j++ )\n\
  for( int i=-2; i<=2; i++ )\n\
  {\n\
      vec2 g = vec2( float(i),float(j) );\n\
  vec3 o = hash3( p + g )*vec3(u,u,1.0);\n\
  vec2 r = g - f + o.xy;\n\
  float d = dot(r,r);\n\
  float ww = pow( 1.0-smoothstep(0.0,1.414,sqrt(d)), k );\n\
  va += o.z*ww;\n\
  wt += ww;\n\
  }\n\
\n\
  return va/wt;\n\
}\n\
';

  function LGraphShaderTime() {
    this.addOutput('out', 'float');
  }

  LGraphShaderTime.title = 'Time';

  LGraphShaderTime.prototype.onGetCode = function (context) {
    if (!this.shader_destination || !this.isOutputConnected(0)) return;

    var outlink = getOutputLinkID(this, 0);

    context.addUniform('u_time' + this.id, 'float', function () {
      return getTime() * 0.001;
    });
    context.addCode(
      'code',
      'float ' + outlink + ' = u_time' + this.id + ';',
      this.shader_destination,
    );
    this.setOutputData(0, 'float');
  };

  registerShaderNode('input/time', LGraphShaderTime);

  function LGraphShaderDither() {
    this.addInput('in', 'T');
    this.addOutput('out', 'float');
  }

  LGraphShaderDither.title = 'Dither';

  LGraphShaderDither.prototype.onGetCode = function (context) {
    if (!this.shader_destination || !this.isOutputConnected(0)) return;

    var inlink = getInputLinkID(this, 0);
    var return_type = 'float';
    var outlink = getOutputLinkID(this, 0);
    var intype = this.getInputData(0);
    inlink = varToTypeGLSL(inlink, intype, 'float');
    context.addFunction('dither8x8', LGraphShaderDither.dither_func);
    context.addCode(
      'code',
      return_type + ' ' + outlink + ' = dither8x8(' + inlink + ');',
      this.shader_destination,
    );
    this.setOutputData(0, return_type);
  };

  LGraphShaderDither.dither_values = [
    0.515625, 0.140625, 0.640625, 0.046875, 0.546875, 0.171875, 0.671875,
    0.765625, 0.265625, 0.890625, 0.390625, 0.796875, 0.296875, 0.921875,
    0.421875, 0.203125, 0.703125, 0.078125, 0.578125, 0.234375, 0.734375,
    0.109375, 0.609375, 0.953125, 0.453125, 0.828125, 0.328125, 0.984375,
    0.484375, 0.859375, 0.359375, 0.0625, 0.5625, 0.1875, 0.6875, 0.03125,
    0.53125, 0.15625, 0.65625, 0.8125, 0.3125, 0.9375, 0.4375, 0.78125, 0.28125,
    0.90625, 0.40625, 0.25, 0.75, 0.125, 0.625, 0.21875, 0.71875, 0.09375,
    0.59375, 1.0001, 0.5, 0.875, 0.375, 0.96875, 0.46875, 0.84375, 0.34375,
  ];

  (LGraphShaderDither.dither_func =
    '\n\
  float dither8x8(float brightness) {\n\
    vec2 position = vec2(0.0);\n\
    #ifdef FRAGMENT\n\
    position = gl_FragCoord.xy;\n\
    #endif\n\
    int x = int(mod(position.x, 8.0));\n\
    int y = int(mod(position.y, 8.0));\n\
    int index = x + y * 8;\n\
    float limit = 0.0;\n\
    if (x < 8) {\n\
    if(index==0) limit = 0.015625;\n\
    ' +
    LGraphShaderDither.dither_values
      .map(function (v, i) {
        return 'else if(index== ' + (i + 1) + ') limit = ' + v + ';';
      })
      .join('\n') +
    '\n\
    }\n\
    return brightness < limit ? 0.0 : 1.0;\n\
  }\n'),
    registerShaderNode('math/dither', LGraphShaderDither);

  function LGraphShaderRemap() {
    this.addInput('', LGShaders.ALL_TYPES);
    this.addOutput('', '');
    this.properties = {
      min_value: 0,
      max_value: 1,
      min_value2: 0,
      max_value2: 1,
    };
    this.addWidget('number', 'min', 0, { step: 0.1, property: 'min_value' });
    this.addWidget('number', 'max', 1, { step: 0.1, property: 'max_value' });
    this.addWidget('number', 'min2', 0, { step: 0.1, property: 'min_value2' });
    this.addWidget('number', 'max2', 1, { step: 0.1, property: 'max_value2' });
  }

  LGraphShaderRemap.title = 'Remap';

  LGraphShaderRemap.prototype.onPropertyChanged = function () {
    if (this.graph) this.graph._version++;
  };

  LGraphShaderRemap.prototype.onConnectionsChange = function () {
    var return_type = this.getInputDataType(0);
    this.outputs[0].type = return_type || 'T';
  };

  LGraphShaderRemap.prototype.onGetCode = function (context) {
    if (!this.shader_destination || !this.isOutputConnected(0)) return;

    var inlink = getInputLinkID(this, 0);
    var outlink = getOutputLinkID(this, 0);
    if (!inlink && !outlink)
      //not connected
      return;

    var return_type = this.getInputDataType(0);
    this.outputs[0].type = return_type;
    if (return_type == 'T') {
      console.warn('node type is T and cannot be resolved');
      return;
    }

    if (!inlink) {
      context.addCode(
        'code',
        '	' + return_type + ' ' + outlink + ' = ' + return_type + '(0.0);\n',
      );
      return;
    }

    var minv = valueToGLSL(this.properties.min_value);
    var maxv = valueToGLSL(this.properties.max_value);
    var minv2 = valueToGLSL(this.properties.min_value2);
    var maxv2 = valueToGLSL(this.properties.max_value2);

    context.addCode(
      'code',
      return_type +
        ' ' +
        outlink +
        ' = ( (' +
        inlink +
        ' - ' +
        minv +
        ') / (' +
        maxv +
        ' - ' +
        minv +
        ') ) * (' +
        maxv2 +
        ' - ' +
        minv2 +
        ') + ' +
        minv2 +
        ';',
      this.shader_destination,
    );
    this.setOutputData(0, return_type);
  };

  registerShaderNode('math/remap', LGraphShaderRemap);
})(this);

(function (global) {
  var LiteGraph = global.LiteGraph;

  var view_matrix = new Float32Array(16);
  var projection_matrix = new Float32Array(16);
  var viewprojection_matrix = new Float32Array(16);
  var model_matrix = new Float32Array(16);
  var global_uniforms = {
    u_view: view_matrix,
    u_projection: projection_matrix,
    u_viewprojection: viewprojection_matrix,
    u_model: model_matrix,
  };

  LiteGraph.LGraphRender = {
    onRequestCameraMatrices: null, //overwrite with your 3D engine specifics, it will receive (view_matrix, projection_matrix,viewprojection_matrix) and must be filled
  };

  function generateGeometryId() {
    return (Math.random() * 100000) | 0;
  }

  function LGraphPoints3D() {
    this.addInput('obj', '');
    this.addInput('radius', 'number');

    this.addOutput('out', 'geometry');
    this.addOutput('points', '[vec3]');
    this.properties = {
      radius: 1,
      num_points: 4096,
      generate_normals: true,
      regular: false,
      mode: LGraphPoints3D.SPHERE,
      force_update: false,
    };

    this.points = new Float32Array(this.properties.num_points * 3);
    this.normals = new Float32Array(this.properties.num_points * 3);
    this.must_update = true;
    this.version = 0;

    var that = this;
    this.addWidget('button', 'update', null, function () {
      that.must_update = true;
    });

    this.geometry = {
      vertices: null,
      _id: generateGeometryId(),
    };

    this._old_obj = null;
    this._last_radius = null;
  }

  global.LGraphPoints3D = LGraphPoints3D;

  LGraphPoints3D.RECTANGLE = 1;
  LGraphPoints3D.CIRCLE = 2;

  LGraphPoints3D.CUBE = 10;
  LGraphPoints3D.SPHERE = 11;
  LGraphPoints3D.HEMISPHERE = 12;
  LGraphPoints3D.INSIDE_SPHERE = 13;

  LGraphPoints3D.OBJECT = 20;
  LGraphPoints3D.OBJECT_UNIFORMLY = 21;
  LGraphPoints3D.OBJECT_INSIDE = 22;

  LGraphPoints3D.MODE_VALUES = {
    rectangle: LGraphPoints3D.RECTANGLE,
    circle: LGraphPoints3D.CIRCLE,
    cube: LGraphPoints3D.CUBE,
    sphere: LGraphPoints3D.SPHERE,
    hemisphere: LGraphPoints3D.HEMISPHERE,
    inside_sphere: LGraphPoints3D.INSIDE_SPHERE,
    object: LGraphPoints3D.OBJECT,
    object_uniformly: LGraphPoints3D.OBJECT_UNIFORMLY,
    object_inside: LGraphPoints3D.OBJECT_INSIDE,
  };

  LGraphPoints3D.widgets_info = {
    mode: { widget: 'combo', values: LGraphPoints3D.MODE_VALUES },
  };

  LGraphPoints3D.title = 'list of points';
  LGraphPoints3D.desc = 'returns an array of points';

  LGraphPoints3D.prototype.onPropertyChanged = function (name, value) {
    this.must_update = true;
  };

  LGraphPoints3D.prototype.onExecute = function () {
    var obj = this.getInputData(0);
    if (
      obj != this._old_obj ||
      (obj && obj._version != this._old_obj_version)
    ) {
      this._old_obj = obj;
      this.must_update = true;
    }

    var radius = this.getInputData(1);
    if (radius == null) radius = this.properties.radius;
    if (this._last_radius != radius) {
      this._last_radius = radius;
      this.must_update = true;
    }

    if (this.must_update || this.properties.force_update) {
      this.must_update = false;
      this.updatePoints();
    }

    this.geometry.vertices = this.points;
    this.geometry.normals = this.normals;
    this.geometry._version = this.version;

    this.setOutputData(0, this.geometry);
  };

  LGraphPoints3D.prototype.updatePoints = function () {
    var num_points = this.properties.num_points | 0;
    if (num_points < 1) num_points = 1;

    if (!this.points || this.points.length != num_points * 3)
      this.points = new Float32Array(num_points * 3);

    if (this.properties.generate_normals) {
      if (!this.normals || this.normals.length != this.points.length)
        this.normals = new Float32Array(this.points.length);
    } else this.normals = null;

    var radius = this._last_radius || this.properties.radius;
    var mode = this.properties.mode;

    var obj = this.getInputData(0);
    this._old_obj_version = obj ? obj._version : null;

    this.points = LGraphPoints3D.generatePoints(
      radius,
      num_points,
      mode,
      this.points,
      this.normals,
      this.properties.regular,
      obj,
    );

    this.version++;
  };

  //global
  LGraphPoints3D.generatePoints = function (
    radius,
    num_points,
    mode,
    points,
    normals,
    regular,
    obj,
  ) {
    var size = num_points * 3;
    if (!points || points.length != size) points = new Float32Array(size);
    var temp = new Float32Array(3);
    var UP = new Float32Array([0, 1, 0]);

    if (regular) {
      if (mode == LGraphPoints3D.RECTANGLE) {
        var side = Math.floor(Math.sqrt(num_points));
        for (var i = 0; i < side; ++i)
          for (var j = 0; j < side; ++j) {
            var pos = i * 3 + j * 3 * side;
            points[pos] = (i / side - 0.5) * radius * 2;
            points[pos + 1] = 0;
            points[pos + 2] = (j / side - 0.5) * radius * 2;
          }
        points = new Float32Array(points.subarray(0, side * side * 3));
        if (normals) {
          for (var i = 0; i < normals.length; i += 3) normals.set(UP, i);
        }
      } else if (mode == LGraphPoints3D.SPHERE) {
        var side = Math.floor(Math.sqrt(num_points));
        for (var i = 0; i < side; ++i)
          for (var j = 0; j < side; ++j) {
            var pos = i * 3 + j * 3 * side;
            polarToCartesian(
              temp,
              (i / side) * 2 * Math.PI,
              (j / side - 0.5) * 2 * Math.PI,
              radius,
            );
            points[pos] = temp[0];
            points[pos + 1] = temp[1];
            points[pos + 2] = temp[2];
          }
        points = new Float32Array(points.subarray(0, side * side * 3));
        if (normals) LGraphPoints3D.generateSphericalNormals(points, normals);
      } else if (mode == LGraphPoints3D.CIRCLE) {
        for (var i = 0; i < size; i += 3) {
          var angle = 2 * Math.PI * (i / size);
          points[i] = Math.cos(angle) * radius;
          points[i + 1] = 0;
          points[i + 2] = Math.sin(angle) * radius;
        }
        if (normals) {
          for (var i = 0; i < normals.length; i += 3) normals.set(UP, i);
        }
      }
    } //non regular
    else {
      if (mode == LGraphPoints3D.RECTANGLE) {
        for (var i = 0; i < size; i += 3) {
          points[i] = (Math.random() - 0.5) * radius * 2;
          points[i + 1] = 0;
          points[i + 2] = (Math.random() - 0.5) * radius * 2;
        }
        if (normals) {
          for (var i = 0; i < normals.length; i += 3) normals.set(UP, i);
        }
      } else if (mode == LGraphPoints3D.CUBE) {
        for (var i = 0; i < size; i += 3) {
          points[i] = (Math.random() - 0.5) * radius * 2;
          points[i + 1] = (Math.random() - 0.5) * radius * 2;
          points[i + 2] = (Math.random() - 0.5) * radius * 2;
        }
        if (normals) {
          for (var i = 0; i < normals.length; i += 3) normals.set(UP, i);
        }
      } else if (mode == LGraphPoints3D.SPHERE) {
        LGraphPoints3D.generateSphere(points, size, radius);
        if (normals) LGraphPoints3D.generateSphericalNormals(points, normals);
      } else if (mode == LGraphPoints3D.HEMISPHERE) {
        LGraphPoints3D.generateHemisphere(points, size, radius);
        if (normals) LGraphPoints3D.generateSphericalNormals(points, normals);
      } else if (mode == LGraphPoints3D.CIRCLE) {
        LGraphPoints3D.generateInsideCircle(points, size, radius);
        if (normals) LGraphPoints3D.generateSphericalNormals(points, normals);
      } else if (mode == LGraphPoints3D.INSIDE_SPHERE) {
        LGraphPoints3D.generateInsideSphere(points, size, radius);
        if (normals) LGraphPoints3D.generateSphericalNormals(points, normals);
      } else if (mode == LGraphPoints3D.OBJECT) {
        LGraphPoints3D.generateFromObject(points, normals, size, obj, false);
      } else if (mode == LGraphPoints3D.OBJECT_UNIFORMLY) {
        LGraphPoints3D.generateFromObject(points, normals, size, obj, true);
      } else if (mode == LGraphPoints3D.OBJECT_INSIDE) {
        LGraphPoints3D.generateFromInsideObject(points, size, obj);
        //if(normals)
        //	LGraphPoints3D.generateSphericalNormals( points, normals );
      } else console.warn('wrong mode in LGraphPoints3D');
    }

    return points;
  };

  LGraphPoints3D.generateSphericalNormals = function (points, normals) {
    var temp = new Float32Array(3);
    for (var i = 0; i < normals.length; i += 3) {
      temp[0] = points[i];
      temp[1] = points[i + 1];
      temp[2] = points[i + 2];
      vec3.normalize(temp, temp);
      normals.set(temp, i);
    }
  };

  LGraphPoints3D.generateSphere = function (points, size, radius) {
    for (var i = 0; i < size; i += 3) {
      var r1 = Math.random();
      var r2 = Math.random();
      var x = 2 * Math.cos(2 * Math.PI * r1) * Math.sqrt(r2 * (1 - r2));
      var y = 1 - 2 * r2;
      var z = 2 * Math.sin(2 * Math.PI * r1) * Math.sqrt(r2 * (1 - r2));
      points[i] = x * radius;
      points[i + 1] = y * radius;
      points[i + 2] = z * radius;
    }
  };

  LGraphPoints3D.generateHemisphere = function (points, size, radius) {
    for (var i = 0; i < size; i += 3) {
      var r1 = Math.random();
      var r2 = Math.random();
      var x = Math.cos(2 * Math.PI * r1) * Math.sqrt(1 - r2 * r2);
      var y = r2;
      var z = Math.sin(2 * Math.PI * r1) * Math.sqrt(1 - r2 * r2);
      points[i] = x * radius;
      points[i + 1] = y * radius;
      points[i + 2] = z * radius;
    }
  };

  LGraphPoints3D.generateInsideCircle = function (points, size, radius) {
    for (var i = 0; i < size; i += 3) {
      var r1 = Math.random();
      var r2 = Math.random();
      var x = Math.cos(2 * Math.PI * r1) * Math.sqrt(1 - r2 * r2);
      var y = r2;
      var z = Math.sin(2 * Math.PI * r1) * Math.sqrt(1 - r2 * r2);
      points[i] = x * radius;
      points[i + 1] = 0;
      points[i + 2] = z * radius;
    }
  };

  LGraphPoints3D.generateInsideSphere = function (points, size, radius) {
    for (var i = 0; i < size; i += 3) {
      var u = Math.random();
      var v = Math.random();
      var theta = u * 2.0 * Math.PI;
      var phi = Math.acos(2.0 * v - 1.0);
      var r = Math.cbrt(Math.random()) * radius;
      var sinTheta = Math.sin(theta);
      var cosTheta = Math.cos(theta);
      var sinPhi = Math.sin(phi);
      var cosPhi = Math.cos(phi);
      points[i] = r * sinPhi * cosTheta;
      points[i + 1] = r * sinPhi * sinTheta;
      points[i + 2] = r * cosPhi;
    }
  };

  function findRandomTriangle(areas, f) {
    var l = areas.length;
    var imin = 0;
    var imid = 0;
    var imax = l;

    if (l == 0) return -1;
    if (l == 1) return 0;
    //dichotomic search
    while (imax >= imin) {
      imid = ((imax + imin) * 0.5) | 0;
      var t = areas[imid];
      if (t == f) return imid;
      if (imin == imax - 1) return imin;
      if (t < f) imin = imid;
      else imax = imid;
    }
    return imid;
  }

  LGraphPoints3D.generateFromObject = function (
    points,
    normals,
    size,
    obj,
    evenly,
  ) {
    if (!obj) return;

    var vertices = null;
    var mesh_normals = null;
    var indices = null;
    var areas = null;
    if (obj.constructor === GL.Mesh) {
      vertices = obj.vertexBuffers.vertices.data;
      mesh_normals = obj.vertexBuffers.normals
        ? obj.vertexBuffers.normals.data
        : null;
      indices = obj.indexBuffers.indices ? obj.indexBuffers.indices.data : null;
      if (!indices)
        indices = obj.indexBuffers.triangles
          ? obj.indexBuffers.triangles.data
          : null;
    }
    if (!vertices) return null;
    var num_triangles = indices
      ? indices.length / 3
      : vertices.length / (3 * 3);
    var total_area = 0; //sum of areas of all triangles

    if (evenly) {
      areas = new Float32Array(num_triangles); //accum
      for (var i = 0; i < num_triangles; ++i) {
        if (indices) {
          a = indices[i * 3] * 3;
          b = indices[i * 3 + 1] * 3;
          c = indices[i * 3 + 2] * 3;
        } else {
          a = i * 9;
          b = i * 9 + 3;
          c = i * 9 + 6;
        }
        var P1 = vertices.subarray(a, a + 3);
        var P2 = vertices.subarray(b, b + 3);
        var P3 = vertices.subarray(c, c + 3);
        var aL = vec3.distance(P1, P2);
        var bL = vec3.distance(P2, P3);
        var cL = vec3.distance(P3, P1);
        var s = (aL + bL + cL) / 2;
        total_area += Math.sqrt(s * (s - aL) * (s - bL) * (s - cL));
        areas[i] = total_area;
      }
      for (
        var i = 0;
        i < num_triangles;
        ++i //normalize
      )
        areas[i] /= total_area;
    }

    for (var i = 0; i < size; i += 3) {
      var r = Math.random();
      var index = evenly
        ? findRandomTriangle(areas, r)
        : Math.floor(r * num_triangles);
      //get random triangle
      var a = 0;
      var b = 0;
      var c = 0;
      if (indices) {
        a = indices[index * 3] * 3;
        b = indices[index * 3 + 1] * 3;
        c = indices[index * 3 + 2] * 3;
      } else {
        a = index * 9;
        b = index * 9 + 3;
        c = index * 9 + 6;
      }
      var s = Math.random();
      var t = Math.random();
      var sqrt_s = Math.sqrt(s);
      var af = 1 - sqrt_s;
      var bf = sqrt_s * (1 - t);
      var cf = t * sqrt_s;
      points[i] = af * vertices[a] + bf * vertices[b] + cf * vertices[c];
      points[i + 1] =
        af * vertices[a + 1] + bf * vertices[b + 1] + cf * vertices[c + 1];
      points[i + 2] =
        af * vertices[a + 2] + bf * vertices[b + 2] + cf * vertices[c + 2];
      if (normals && mesh_normals) {
        normals[i] =
          af * mesh_normals[a] + bf * mesh_normals[b] + cf * mesh_normals[c];
        normals[i + 1] =
          af * mesh_normals[a + 1] +
          bf * mesh_normals[b + 1] +
          cf * mesh_normals[c + 1];
        normals[i + 2] =
          af * mesh_normals[a + 2] +
          bf * mesh_normals[b + 2] +
          cf * mesh_normals[c + 2];
        var N = normals.subarray(i, i + 3);
        vec3.normalize(N, N);
      }
    }
  };

  LGraphPoints3D.generateFromInsideObject = function (points, size, mesh) {
    if (!mesh || mesh.constructor !== GL.Mesh) return;

    var aabb = mesh.getBoundingBox();
    if (!mesh.octree) mesh.octree = new GL.Octree(mesh);
    var octree = mesh.octree;
    var origin = vec3.create();
    var direction = vec3.fromValues(1, 0, 0);
    var temp = vec3.create();
    var i = 0;
    var tries = 0;
    while (i < size && tries < points.length * 10) {
      //limit to avoid problems
      tries += 1;
      var r = vec3.random(temp); //random point inside the aabb
      r[0] = (r[0] * 2 - 1) * aabb[3] + aabb[0];
      r[1] = (r[1] * 2 - 1) * aabb[4] + aabb[1];
      r[2] = (r[2] * 2 - 1) * aabb[5] + aabb[2];
      origin.set(r);
      var hit = octree.testRay(
        origin,
        direction,
        0,
        10000,
        true,
        GL.Octree.ALL,
      );
      if (!hit || hit.length % 2 == 0)
        //not inside
        continue;
      points.set(r, i);
      i += 3;
    }
  };

  LiteGraph.registerNodeType('geometry/points3D', LGraphPoints3D);

  function LGraphPointsToInstances() {
    this.addInput('points', 'geometry');
    this.addOutput('instances', '[mat4]');
    this.properties = {
      mode: 1,
      autoupdate: true,
    };

    this.must_update = true;
    this.matrices = [];
    this.first_time = true;
  }

  LGraphPointsToInstances.NORMAL = 0;
  LGraphPointsToInstances.VERTICAL = 1;
  LGraphPointsToInstances.SPHERICAL = 2;
  LGraphPointsToInstances.RANDOM = 3;
  LGraphPointsToInstances.RANDOM_VERTICAL = 4;

  LGraphPointsToInstances.modes = {
    normal: 0,
    vertical: 1,
    spherical: 2,
    random: 3,
    random_vertical: 4,
  };
  LGraphPointsToInstances.widgets_info = {
    mode: { widget: 'combo', values: LGraphPointsToInstances.modes },
  };

  LGraphPointsToInstances.title = 'points to inst';

  LGraphPointsToInstances.prototype.onExecute = function () {
    var geo = this.getInputData(0);
    if (!geo) {
      this.setOutputData(0, null);
      return;
    }

    if (!this.isOutputConnected(0)) return;

    var has_changed =
      geo._version != this._version || geo._id != this._geometry_id;

    if ((has_changed && this.properties.autoupdate) || this.first_time) {
      this.first_time = false;
      this.updateInstances(geo);
    }

    this.setOutputData(0, this.matrices);
  };

  LGraphPointsToInstances.prototype.updateInstances = function (geometry) {
    var vertices = geometry.vertices;
    if (!vertices) return null;
    var normals = geometry.normals;

    var matrices = this.matrices;
    var num_points = vertices.length / 3;
    if (matrices.length != num_points) matrices.length = num_points;
    var identity = mat4.create();
    var temp = vec3.create();
    var zero = vec3.create();
    var UP = vec3.fromValues(0, 1, 0);
    var FRONT = vec3.fromValues(0, 0, -1);
    var RIGHT = vec3.fromValues(1, 0, 0);
    var R = quat.create();

    var front = vec3.create();
    var right = vec3.create();
    var top = vec3.create();

    for (var i = 0; i < vertices.length; i += 3) {
      var index = i / 3;
      var m = matrices[index];
      if (!m) m = matrices[index] = mat4.create();
      m.set(identity);
      var point = vertices.subarray(i, i + 3);

      switch (this.properties.mode) {
        case LGraphPointsToInstances.NORMAL:
          mat4.setTranslation(m, point);
          if (normals) {
            var normal = normals.subarray(i, i + 3);
            top.set(normal);
            vec3.normalize(top, top);
            vec3.cross(right, FRONT, top);
            vec3.normalize(right, right);
            vec3.cross(front, right, top);
            vec3.normalize(front, front);
            m.set(right, 0);
            m.set(top, 4);
            m.set(front, 8);
            mat4.setTranslation(m, point);
          }
          break;
        case LGraphPointsToInstances.VERTICAL:
          mat4.setTranslation(m, point);
          break;
        case LGraphPointsToInstances.SPHERICAL:
          front.set(point);
          vec3.normalize(front, front);
          vec3.cross(right, UP, front);
          vec3.normalize(right, right);
          vec3.cross(top, front, right);
          vec3.normalize(top, top);
          m.set(right, 0);
          m.set(top, 4);
          m.set(front, 8);
          mat4.setTranslation(m, point);
          break;
        case LGraphPointsToInstances.RANDOM:
          temp[0] = Math.random() * 2 - 1;
          temp[1] = Math.random() * 2 - 1;
          temp[2] = Math.random() * 2 - 1;
          vec3.normalize(temp, temp);
          quat.setAxisAngle(R, temp, Math.random() * 2 * Math.PI);
          mat4.fromQuat(m, R);
          mat4.setTranslation(m, point);
          break;
        case LGraphPointsToInstances.RANDOM_VERTICAL:
          quat.setAxisAngle(R, UP, Math.random() * 2 * Math.PI);
          mat4.fromQuat(m, R);
          mat4.setTranslation(m, point);
          break;
      }
    }

    this._version = geometry._version;
    this._geometry_id = geometry._id;
  };

  LiteGraph.registerNodeType(
    'geometry/points_to_instances',
    LGraphPointsToInstances,
  );

  function LGraphGeometryTransform() {
    this.addInput('in', 'geometry,[mat4]');
    this.addInput('mat4', 'mat4');
    this.addOutput('out', 'geometry');
    this.properties = {};

    this.geometry = {
      type: 'triangles',
      vertices: null,
      _id: generateGeometryId(),
      _version: 0,
    };

    this._last_geometry_id = -1;
    this._last_version = -1;
    this._last_key = '';

    this.must_update = true;
  }

  LGraphGeometryTransform.title = 'Transform';

  LGraphGeometryTransform.prototype.onExecute = function () {
    var input = this.getInputData(0);
    var model = this.getInputData(1);

    if (!input) return;

    //array of matrices
    if (input.constructor === Array) {
      if (input.length == 0) return;
      this.outputs[0].type = '[mat4]';
      if (!this.isOutputConnected(0)) return;

      if (!model) {
        this.setOutputData(0, input);
        return;
      }

      if (!this._output) this._output = new Array();
      if (this._output.length != input.length)
        this._output.length = input.length;
      for (var i = 0; i < input.length; ++i) {
        var m = this._output[i];
        if (!m) m = this._output[i] = mat4.create();
        mat4.multiply(m, input[i], model);
      }
      this.setOutputData(0, this._output);
      return;
    }

    //geometry
    if (!input.vertices || !input.vertices.length) return;
    var geo = input;
    this.outputs[0].type = 'geometry';
    if (!this.isOutputConnected(0)) return;
    if (!model) {
      this.setOutputData(0, geo);
      return;
    }

    var key = typedArrayToArray(model).join(',');

    if (
      this.must_update ||
      geo._id != this._last_geometry_id ||
      geo._version != this._last_version ||
      key != this._last_key
    ) {
      this.updateGeometry(geo, model);
      this._last_key = key;
      this._last_version = geo._version;
      this._last_geometry_id = geo._id;
      this.must_update = false;
    }

    this.setOutputData(0, this.geometry);
  };

  LGraphGeometryTransform.prototype.updateGeometry = function (
    geometry,
    model,
  ) {
    var old_vertices = geometry.vertices;
    var vertices = this.geometry.vertices;
    if (!vertices || vertices.length != old_vertices.length)
      vertices = this.geometry.vertices = new Float32Array(old_vertices.length);
    var temp = vec3.create();

    for (var i = 0, l = vertices.length; i < l; i += 3) {
      temp[0] = old_vertices[i];
      temp[1] = old_vertices[i + 1];
      temp[2] = old_vertices[i + 2];
      mat4.multiplyVec3(temp, model, temp);
      vertices[i] = temp[0];
      vertices[i + 1] = temp[1];
      vertices[i + 2] = temp[2];
    }

    if (geometry.normals) {
      if (
        !this.geometry.normals ||
        this.geometry.normals.length != geometry.normals.length
      )
        this.geometry.normals = new Float32Array(geometry.normals.length);
      var normals = this.geometry.normals;
      var normal_model = mat4.invert(mat4.create(), model);
      if (normal_model) mat4.transpose(normal_model, normal_model);
      var old_normals = geometry.normals;
      for (var i = 0, l = normals.length; i < l; i += 3) {
        temp[0] = old_normals[i];
        temp[1] = old_normals[i + 1];
        temp[2] = old_normals[i + 2];
        mat4.multiplyVec3(temp, normal_model, temp);
        normals[i] = temp[0];
        normals[i + 1] = temp[1];
        normals[i + 2] = temp[2];
      }
    }

    this.geometry.type = geometry.type;
    this.geometry._version++;
  };

  LiteGraph.registerNodeType('geometry/transform', LGraphGeometryTransform);

  function LGraphGeometryPolygon() {
    this.addInput('sides', 'number');
    this.addInput('radius', 'number');
    this.addOutput('out', 'geometry');
    this.properties = { sides: 6, radius: 1, uvs: false };

    this.geometry = {
      type: 'line_loop',
      vertices: null,
      _id: generateGeometryId(),
    };
    this.geometry_id = -1;
    this.version = -1;
    this.must_update = true;

    this.last_info = { sides: -1, radius: -1 };
  }

  LGraphGeometryPolygon.title = 'Polygon';

  LGraphGeometryPolygon.prototype.onExecute = function () {
    if (!this.isOutputConnected(0)) return;

    var sides = this.getInputOrProperty('sides');
    var radius = this.getInputOrProperty('radius');
    sides = Math.max(3, sides) | 0;

    //update
    if (this.last_info.sides != sides || this.last_info.radius != radius)
      this.updateGeometry(sides, radius);

    this.setOutputData(0, this.geometry);
  };

  LGraphGeometryPolygon.prototype.updateGeometry = function (sides, radius) {
    var num = 3 * sides;
    var vertices = this.geometry.vertices;
    if (!vertices || vertices.length != num)
      vertices = this.geometry.vertices = new Float32Array(3 * sides);
    var delta = (Math.PI * 2) / sides;
    var gen_uvs = this.properties.uvs;
    if (gen_uvs) {
      uvs = this.geometry.coords = new Float32Array(3 * sides);
    }

    for (var i = 0; i < sides; ++i) {
      var angle = delta * -i;
      var x = Math.cos(angle) * radius;
      var y = 0;
      var z = Math.sin(angle) * radius;
      vertices[i * 3] = x;
      vertices[i * 3 + 1] = y;
      vertices[i * 3 + 2] = z;

      if (gen_uvs) {
      }
    }
    this.geometry._id = ++this.geometry_id;
    this.geometry._version = ++this.version;
    this.last_info.sides = sides;
    this.last_info.radius = radius;
  };

  LiteGraph.registerNodeType('geometry/polygon', LGraphGeometryPolygon);

  function LGraphGeometryExtrude() {
    this.addInput('', 'geometry');
    this.addOutput('', 'geometry');
    this.properties = { top_cap: true, bottom_cap: true, offset: [0, 100, 0] };
    this.version = -1;

    this._last_geo_version = -1;
    this._must_update = true;
  }

  LGraphGeometryExtrude.title = 'extrude';

  LGraphGeometryExtrude.prototype.onPropertyChanged = function (name, value) {
    this._must_update = true;
  };

  LGraphGeometryExtrude.prototype.onExecute = function () {
    var geo = this.getInputData(0);
    if (!geo || !this.isOutputConnected(0)) return;

    if (geo.version != this._last_geo_version || this._must_update) {
      this._geo = this.extrudeGeometry(geo, this._geo);
      if (this._geo) this._geo.version = this.version++;
      this._must_update = false;
    }

    this.setOutputData(0, this._geo);
  };

  LGraphGeometryExtrude.prototype.extrudeGeometry = function (geo) {
    //for every pair of vertices
    var vertices = geo.vertices;
    var num_points = vertices.length / 3;

    var tempA = vec3.create();
    var tempB = vec3.create();
    var tempC = vec3.create();
    var tempD = vec3.create();
    var offset = new Float32Array(this.properties.offset);

    if (geo.type == 'line_loop') {
      var new_vertices = new Float32Array(num_points * 6 * 3); //every points become 6 ( caps not included )
      var npos = 0;
      for (var i = 0, l = vertices.length; i < l; i += 3) {
        tempA[0] = vertices[i];
        tempA[1] = vertices[i + 1];
        tempA[2] = vertices[i + 2];

        if (i + 3 < l) {
          //loop
          tempB[0] = vertices[i + 3];
          tempB[1] = vertices[i + 4];
          tempB[2] = vertices[i + 5];
        } else {
          tempB[0] = vertices[0];
          tempB[1] = vertices[1];
          tempB[2] = vertices[2];
        }

        vec3.add(tempC, tempA, offset);
        vec3.add(tempD, tempB, offset);

        new_vertices.set(tempA, npos);
        npos += 3;
        new_vertices.set(tempB, npos);
        npos += 3;
        new_vertices.set(tempC, npos);
        npos += 3;

        new_vertices.set(tempB, npos);
        npos += 3;
        new_vertices.set(tempD, npos);
        npos += 3;
        new_vertices.set(tempC, npos);
        npos += 3;
      }
    }

    var out_geo = {
      _id: generateGeometryId(),
      type: 'triangles',
      vertices: new_vertices,
    };

    return out_geo;
  };

  LiteGraph.registerNodeType('geometry/extrude', LGraphGeometryExtrude);

  function LGraphGeometryEval() {
    this.addInput('in', 'geometry');
    this.addOutput('out', 'geometry');

    this.properties = {
      code: 'V[1] += 0.01 * Math.sin(I + T*0.001);',
      execute_every_frame: false,
    };

    this.geometry = null;
    this.geometry_id = -1;
    this.version = -1;
    this.must_update = true;

    this.vertices = null;
    this.func = null;
  }

  LGraphGeometryEval.title = 'geoeval';
  LGraphGeometryEval.desc = 'eval code';

  LGraphGeometryEval.widgets_info = {
    code: { widget: 'code' },
  };

  LGraphGeometryEval.prototype.onConfigure = function (o) {
    this.compileCode();
  };

  LGraphGeometryEval.prototype.compileCode = function () {
    if (!this.properties.code) return;

    try {
      this.func = new Function('V', 'I', 'T', this.properties.code);
      this.boxcolor = '#AFA';
      this.must_update = true;
    } catch (err) {
      this.boxcolor = 'red';
    }
  };

  LGraphGeometryEval.prototype.onPropertyChanged = function (name, value) {
    if (name == 'code') {
      this.properties.code = value;
      this.compileCode();
    }
  };

  LGraphGeometryEval.prototype.onExecute = function () {
    var geometry = this.getInputData(0);
    if (!geometry) return;

    if (!this.func) {
      this.setOutputData(0, geometry);
      return;
    }

    if (
      this.geometry_id != geometry._id ||
      this.version != geometry._version ||
      this.must_update ||
      this.properties.execute_every_frame
    ) {
      this.must_update = false;
      this.geometry_id = geometry._id;
      if (this.properties.execute_every_frame) this.version++;
      else this.version = geometry._version;
      var func = this.func;
      var T = getTime();

      //clone
      if (!this.geometry) this.geometry = {};
      for (var i in geometry) {
        if (geometry[i] == null) continue;
        if (geometry[i].constructor == Float32Array)
          this.geometry[i] = new Float32Array(geometry[i]);
        else this.geometry[i] = geometry[i];
      }
      this.geometry._id = geometry._id;
      if (this.properties.execute_every_frame)
        this.geometry._version = this.version;
      else this.geometry._version = geometry._version + 1;

      var V = vec3.create();
      var vertices = this.vertices;
      if (!vertices || this.vertices.length != geometry.vertices.length)
        vertices = this.vertices = new Float32Array(geometry.vertices);
      else vertices.set(geometry.vertices);
      for (var i = 0; i < vertices.length; i += 3) {
        V[0] = vertices[i];
        V[1] = vertices[i + 1];
        V[2] = vertices[i + 2];
        func(V, i / 3, T);
        vertices[i] = V[0];
        vertices[i + 1] = V[1];
        vertices[i + 2] = V[2];
      }
      this.geometry.vertices = vertices;
    }

    this.setOutputData(0, this.geometry);
  };

  LiteGraph.registerNodeType('geometry/eval', LGraphGeometryEval);

  /*
function LGraphGeometryDisplace() {
  this.addInput("in", "geometry");
  this.addInput("img", "image");
  this.addOutput("out", "geometry");

  this.properties = {
    grid_size: 1
  };

  this.geometry = null;
  this.geometry_id = -1;
  this.version = -1;
  this.must_update = true;

  this.vertices = null;
}

LGraphGeometryDisplace.title = "displace";
LGraphGeometryDisplace.desc = "displace points";

LGraphGeometryDisplace.prototype.onExecute = function() {
  var geometry = this.getInputData(0);
  var image = this.getInputData(1);
  if(!geometry)
    return;

  if(!image)
  {
    this.setOutputData(0,geometry);
    return;
  }

  if( this.geometry_id != geometry._id || this.version != geometry._version || this.must_update )
  {
    this.must_update = false;
    this.geometry_id = geometry._id;
    this.version = geometry._version;

    //copy
    this.geometry = {};
    for(var i in geometry)
      this.geometry[i] = geometry[i];
    this.geometry._id = geometry._id;
    this.geometry._version = geometry._version + 1;

    var grid_size = this.properties.grid_size;
    if(grid_size != 0)
    {
      var vertices = this.vertices;
      if(!vertices || this.vertices.length != this.geometry.vertices.length)
        vertices = this.vertices = new Float32Array( this.geometry.vertices );
      for(var i = 0; i < vertices.length; i+=3)
      {
        vertices[i] = Math.round(vertices[i]/grid_size) * grid_size;
        vertices[i+1] = Math.round(vertices[i+1]/grid_size) * grid_size;
        vertices[i+2] = Math.round(vertices[i+2]/grid_size) * grid_size;
      }
      this.geometry.vertices = vertices;
    }
  }

  this.setOutputData(0,this.geometry);
}

LiteGraph.registerNodeType( "geometry/displace", LGraphGeometryDisplace );
*/

  function LGraphConnectPoints() {
    this.addInput('in', 'geometry');
    this.addOutput('out', 'geometry');

    this.properties = {
      min_dist: 0.4,
      max_dist: 0.5,
      max_connections: 0,
      probability: 1,
    };

    this.geometry_id = -1;
    this.version = -1;
    this.my_version = 1;
    this.must_update = true;
  }

  LGraphConnectPoints.title = 'connect points';
  LGraphConnectPoints.desc = 'adds indices between near points';

  LGraphConnectPoints.prototype.onPropertyChanged = function (name, value) {
    this.must_update = true;
  };

  LGraphConnectPoints.prototype.onExecute = function () {
    var geometry = this.getInputData(0);
    if (!geometry) return;

    if (
      this.geometry_id != geometry._id ||
      this.version != geometry._version ||
      this.must_update
    ) {
      this.must_update = false;
      this.geometry_id = geometry._id;
      this.version = geometry._version;

      //copy
      this.geometry = {};
      for (var i in geometry) this.geometry[i] = geometry[i];
      this.geometry._id = generateGeometryId();
      this.geometry._version = this.my_version++;

      var vertices = geometry.vertices;
      var l = vertices.length;
      var min_dist = this.properties.min_dist;
      var max_dist = this.properties.max_dist;
      var probability = this.properties.probability;
      var max_connections = this.properties.max_connections;
      var indices = [];

      for (var i = 0; i < l; i += 3) {
        var x = vertices[i];
        var y = vertices[i + 1];
        var z = vertices[i + 2];
        var connections = 0;
        for (var j = i + 3; j < l; j += 3) {
          var x2 = vertices[j];
          var y2 = vertices[j + 1];
          var z2 = vertices[j + 2];
          var dist = Math.sqrt(
            (x - x2) * (x - x2) + (y - y2) * (y - y2) + (z - z2) * (z - z2),
          );
          if (
            dist > max_dist ||
            dist < min_dist ||
            (probability < 1 && probability < Math.random())
          )
            continue;
          indices.push(i / 3, j / 3);
          connections += 1;
          if (max_connections && connections > max_connections) break;
        }
      }
      this.geometry.indices = this.indices = new Uint32Array(indices);
    }

    if (this.indices && this.indices.length) {
      this.geometry.indices = this.indices;
      this.setOutputData(0, this.geometry);
    } else this.setOutputData(0, null);
  };

  LiteGraph.registerNodeType('geometry/connectPoints', LGraphConnectPoints);

  //Works with Litegl.js to create WebGL nodes
  if (typeof GL == 'undefined')
    //LiteGL RELATED **********************************************
    return;

  function LGraphToGeometry() {
    this.addInput('mesh', 'mesh');
    this.addOutput('out', 'geometry');

    this.geometry = {};
    this.last_mesh = null;
  }

  LGraphToGeometry.title = 'to geometry';
  LGraphToGeometry.desc = 'converts a mesh to geometry';

  LGraphToGeometry.prototype.onExecute = function () {
    var mesh = this.getInputData(0);
    if (!mesh) return;

    if (mesh != this.last_mesh) {
      this.last_mesh = mesh;
      for (i in mesh.vertexBuffers) {
        var buffer = mesh.vertexBuffers[i];
        this.geometry[i] = buffer.data;
      }
      if (mesh.indexBuffers['triangles'])
        this.geometry.indices = mesh.indexBuffers['triangles'].data;

      this.geometry._id = generateGeometryId();
      this.geometry._version = 0;
    }

    this.setOutputData(0, this.geometry);
    if (this.geometry) this.setOutputData(1, this.geometry.vertices);
  };

  LiteGraph.registerNodeType('geometry/toGeometry', LGraphToGeometry);

  function LGraphGeometryToMesh() {
    this.addInput('in', 'geometry');
    this.addOutput('mesh', 'mesh');
    this.properties = {};
    this.version = -1;
    this.mesh = null;
  }

  LGraphGeometryToMesh.title = 'Geo to Mesh';

  LGraphGeometryToMesh.prototype.updateMesh = function (geometry) {
    if (!this.mesh) this.mesh = new GL.Mesh();

    for (var i in geometry) {
      if (i[0] == '_') continue;

      var buffer_data = geometry[i];

      var info = GL.Mesh.common_buffers[i];
      if (!info && i != 'indices')
        //unknown buffer
        continue;
      var spacing = info ? info.spacing : 3;
      var mesh_buffer = this.mesh.vertexBuffers[i];

      if (!mesh_buffer || mesh_buffer.data.length != buffer_data.length) {
        mesh_buffer = new GL.Buffer(
          i == 'indices' ? GL.ELEMENT_ARRAY_BUFFER : GL.ARRAY_BUFFER,
          buffer_data,
          spacing,
          GL.DYNAMIC_DRAW,
        );
      } else {
        mesh_buffer.data.set(buffer_data);
        mesh_buffer.upload(GL.DYNAMIC_DRAW);
      }

      this.mesh.addBuffer(i, mesh_buffer);
    }

    if (
      this.mesh.vertexBuffers.normals &&
      this.mesh.vertexBuffers.normals.data.length !=
        this.mesh.vertexBuffers.vertices.data.length
    ) {
      var n = new Float32Array([0, 1, 0]);
      var normals = new Float32Array(
        this.mesh.vertexBuffers.vertices.data.length,
      );
      for (var i = 0; i < normals.length; i += 3) normals.set(n, i);
      mesh_buffer = new GL.Buffer(GL.ARRAY_BUFFER, normals, 3);
      this.mesh.addBuffer('normals', mesh_buffer);
    }

    this.mesh.updateBoundingBox();
    this.geometry_id = this.mesh.id = geometry._id;
    this.version = this.mesh.version = geometry._version;
    return this.mesh;
  };

  LGraphGeometryToMesh.prototype.onExecute = function () {
    var geometry = this.getInputData(0);
    if (!geometry) return;
    if (this.version != geometry._version || this.geometry_id != geometry._id)
      this.updateMesh(geometry);
    this.setOutputData(0, this.mesh);
  };

  LiteGraph.registerNodeType('geometry/toMesh', LGraphGeometryToMesh);

  function LGraphRenderMesh() {
    this.addInput('mesh', 'mesh');
    this.addInput('mat4', 'mat4');
    this.addInput('tex', 'texture');

    this.properties = {
      enabled: true,
      primitive: GL.TRIANGLES,
      additive: false,
      color: [1, 1, 1],
      opacity: 1,
    };

    this.color = vec4.create([1, 1, 1, 1]);
    this.model_matrix = mat4.create();
    this.uniforms = {
      u_color: this.color,
      u_model: this.model_matrix,
    };
  }

  LGraphRenderMesh.title = 'Render Mesh';
  LGraphRenderMesh.desc = 'renders a mesh flat';

  LGraphRenderMesh.PRIMITIVE_VALUES = {
    points: GL.POINTS,
    lines: GL.LINES,
    line_loop: GL.LINE_LOOP,
    line_strip: GL.LINE_STRIP,
    triangles: GL.TRIANGLES,
    triangle_fan: GL.TRIANGLE_FAN,
    triangle_strip: GL.TRIANGLE_STRIP,
  };

  LGraphRenderMesh.widgets_info = {
    primitive: { widget: 'combo', values: LGraphRenderMesh.PRIMITIVE_VALUES },
    color: { widget: 'color' },
  };

  LGraphRenderMesh.prototype.onExecute = function () {
    if (!this.properties.enabled) return;

    var mesh = this.getInputData(0);
    if (!mesh) return;

    if (!LiteGraph.LGraphRender.onRequestCameraMatrices) {
      console.warn(
        'cannot render geometry, LiteGraph.onRequestCameraMatrices is null, remember to fill this with a callback(view_matrix, projection_matrix,viewprojection_matrix) to use 3D rendering from the graph',
      );
      return;
    }

    LiteGraph.LGraphRender.onRequestCameraMatrices(
      view_matrix,
      projection_matrix,
      viewprojection_matrix,
    );
    var shader = null;
    var texture = this.getInputData(2);
    if (texture) {
      shader = gl.shaders['textured'];
      if (!shader)
        shader = gl.shaders['textured'] = new GL.Shader(
          LGraphRenderPoints.vertex_shader_code,
          LGraphRenderPoints.fragment_shader_code,
          { USE_TEXTURE: '' },
        );
    } else {
      shader = gl.shaders['flat'];
      if (!shader)
        shader = gl.shaders['flat'] = new GL.Shader(
          LGraphRenderPoints.vertex_shader_code,
          LGraphRenderPoints.fragment_shader_code,
        );
    }

    this.color.set(this.properties.color);
    this.color[3] = this.properties.opacity;

    var model_matrix = this.model_matrix;
    var m = this.getInputData(1);
    if (m) model_matrix.set(m);
    else mat4.identity(model_matrix);

    this.uniforms.u_point_size = 1;
    var primitive = this.properties.primitive;

    shader.uniforms(global_uniforms);
    shader.uniforms(this.uniforms);

    if (this.properties.opacity >= 1) gl.disable(gl.BLEND);
    else gl.enable(gl.BLEND);
    gl.enable(gl.DEPTH_TEST);
    if (this.properties.additive) {
      gl.blendFunc(gl.SRC_ALPHA, gl.ONE);
      gl.depthMask(false);
    } else gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    var indices = 'indices';
    if (mesh.indexBuffers.triangles) indices = 'triangles';
    shader.draw(mesh, primitive, indices);
    gl.disable(gl.BLEND);
    gl.depthMask(true);
  };

  LiteGraph.registerNodeType('geometry/render_mesh', LGraphRenderMesh);

  //**************************

  function LGraphGeometryPrimitive() {
    this.addInput('size', 'number');
    this.addOutput('out', 'mesh');
    this.properties = { type: 1, size: 1, subdivisions: 32 };

    this.version = (Math.random() * 100000) | 0;
    this.last_info = { type: -1, size: -1, subdivisions: -1 };
  }

  LGraphGeometryPrimitive.title = 'Primitive';

  LGraphGeometryPrimitive.VALID = {
    CUBE: 1,
    PLANE: 2,
    CYLINDER: 3,
    SPHERE: 4,
    CIRCLE: 5,
    HEMISPHERE: 6,
    ICOSAHEDRON: 7,
    CONE: 8,
    QUAD: 9,
  };
  LGraphGeometryPrimitive.widgets_info = {
    type: { widget: 'combo', values: LGraphGeometryPrimitive.VALID },
  };

  LGraphGeometryPrimitive.prototype.onExecute = function () {
    if (!this.isOutputConnected(0)) return;

    var size = this.getInputOrProperty('size');

    //update
    if (
      this.last_info.type != this.properties.type ||
      this.last_info.size != size ||
      this.last_info.subdivisions != this.properties.subdivisions
    )
      this.updateMesh(this.properties.type, size, this.properties.subdivisions);

    this.setOutputData(0, this._mesh);
  };

  LGraphGeometryPrimitive.prototype.updateMesh = function (
    type,
    size,
    subdivisions,
  ) {
    subdivisions = Math.max(0, subdivisions) | 0;

    switch (type) {
      case 1: //CUBE:
        this._mesh = GL.Mesh.cube({ size: size, normals: true, coords: true });
        break;
      case 2: //PLANE:
        this._mesh = GL.Mesh.plane({
          size: size,
          xz: true,
          detail: subdivisions,
          normals: true,
          coords: true,
        });
        break;
      case 3: //CYLINDER:
        this._mesh = GL.Mesh.cylinder({
          size: size,
          subdivisions: subdivisions,
          normals: true,
          coords: true,
        });
        break;
      case 4: //SPHERE:
        this._mesh = GL.Mesh.sphere({
          size: size,
          long: subdivisions,
          lat: subdivisions,
          normals: true,
          coords: true,
        });
        break;
      case 5: //CIRCLE:
        this._mesh = GL.Mesh.circle({
          size: size,
          slices: subdivisions,
          normals: true,
          coords: true,
        });
        break;
      case 6: //HEMISPHERE:
        this._mesh = GL.Mesh.sphere({
          size: size,
          long: subdivisions,
          lat: subdivisions,
          normals: true,
          coords: true,
          hemi: true,
        });
        break;
      case 7: //ICOSAHEDRON:
        this._mesh = GL.Mesh.icosahedron({
          size: size,
          subdivisions: subdivisions,
        });
        break;
      case 8: //CONE:
        this._mesh = GL.Mesh.cone({
          radius: size,
          height: size,
          subdivisions: subdivisions,
        });
        break;
      case 9: //QUAD:
        this._mesh = GL.Mesh.plane({
          size: size,
          xz: false,
          detail: subdivisions,
          normals: true,
          coords: true,
        });
        break;
    }

    this.last_info.type = type;
    this.last_info.size = size;
    this.last_info.subdivisions = subdivisions;
    this._mesh.version = this.version++;
  };

  LiteGraph.registerNodeType(
    'geometry/mesh_primitive',
    LGraphGeometryPrimitive,
  );

  function LGraphRenderPoints() {
    this.addInput('in', 'geometry');
    this.addInput('mat4', 'mat4');
    this.addInput('tex', 'texture');
    this.properties = {
      enabled: true,
      point_size: 0.1,
      fixed_size: false,
      additive: true,
      color: [1, 1, 1],
      opacity: 1,
    };

    this.color = vec4.create([1, 1, 1, 1]);

    this.uniforms = {
      u_point_size: 1,
      u_perspective: 1,
      u_point_perspective: 1,
      u_color: this.color,
    };

    this.geometry_id = -1;
    this.version = -1;
    this.mesh = null;
  }

  LGraphRenderPoints.title = 'renderPoints';
  LGraphRenderPoints.desc = 'render points with a texture';

  LGraphRenderPoints.widgets_info = {
    color: { widget: 'color' },
  };

  LGraphRenderPoints.prototype.updateMesh = function (geometry) {
    var buffer = this.buffer;
    if (
      !this.buffer ||
      !this.buffer.data ||
      this.buffer.data.length != geometry.vertices.length
    )
      this.buffer = new GL.Buffer(
        GL.ARRAY_BUFFER,
        geometry.vertices,
        3,
        GL.DYNAMIC_DRAW,
      );
    else {
      this.buffer.data.set(geometry.vertices);
      this.buffer.upload(GL.DYNAMIC_DRAW);
    }

    if (!this.mesh) this.mesh = new GL.Mesh();

    this.mesh.addBuffer('vertices', this.buffer);
    this.geometry_id = this.mesh.id = geometry._id;
    this.version = this.mesh.version = geometry._version;
  };

  LGraphRenderPoints.prototype.onExecute = function () {
    if (!this.properties.enabled) return;

    var geometry = this.getInputData(0);
    if (!geometry) return;
    if (this.version != geometry._version || this.geometry_id != geometry._id)
      this.updateMesh(geometry);

    if (!LiteGraph.LGraphRender.onRequestCameraMatrices) {
      console.warn(
        'cannot render geometry, LiteGraph.onRequestCameraMatrices is null, remember to fill this with a callback(view_matrix, projection_matrix,viewprojection_matrix) to use 3D rendering from the graph',
      );
      return;
    }

    LiteGraph.LGraphRender.onRequestCameraMatrices(
      view_matrix,
      projection_matrix,
      viewprojection_matrix,
    );
    var shader = null;

    var texture = this.getInputData(2);

    if (texture) {
      shader = gl.shaders['textured_points'];
      if (!shader)
        shader = gl.shaders['textured_points'] = new GL.Shader(
          LGraphRenderPoints.vertex_shader_code,
          LGraphRenderPoints.fragment_shader_code,
          { USE_TEXTURED_POINTS: '' },
        );
    } else {
      shader = gl.shaders['points'];
      if (!shader)
        shader = gl.shaders['points'] = new GL.Shader(
          LGraphRenderPoints.vertex_shader_code,
          LGraphRenderPoints.fragment_shader_code,
          { USE_POINTS: '' },
        );
    }

    this.color.set(this.properties.color);
    this.color[3] = this.properties.opacity;

    var m = this.getInputData(1);
    if (m) model_matrix.set(m);
    else mat4.identity(model_matrix);

    this.uniforms.u_point_size = this.properties.point_size;
    this.uniforms.u_point_perspective = this.properties.fixed_size ? 0 : 1;
    this.uniforms.u_perspective = gl.viewport_data[3] * projection_matrix[5];

    shader.uniforms(global_uniforms);
    shader.uniforms(this.uniforms);

    if (this.properties.opacity >= 1) gl.disable(gl.BLEND);
    else gl.enable(gl.BLEND);

    gl.enable(gl.DEPTH_TEST);
    if (this.properties.additive) {
      gl.blendFunc(gl.SRC_ALPHA, gl.ONE);
      gl.depthMask(false);
    } else gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    shader.draw(this.mesh, GL.POINTS);

    gl.disable(gl.BLEND);
    gl.depthMask(true);
  };

  LiteGraph.registerNodeType('geometry/render_points', LGraphRenderPoints);

  LGraphRenderPoints.vertex_shader_code =
    '\
  precision mediump float;\n\
  attribute vec3 a_vertex;\n\
  varying vec3 v_vertex;\n\
  attribute vec3 a_normal;\n\
  varying vec3 v_normal;\n\
  #ifdef USE_COLOR\n\
    attribute vec4 a_color;\n\
    varying vec4 v_color;\n\
  #endif\n\
  attribute vec2 a_coord;\n\
  varying vec2 v_coord;\n\
  #ifdef USE_SIZE\n\
    attribute float a_extra;\n\
  #endif\n\
  #ifdef USE_INSTANCING\n\
    attribute mat4 u_model;\n\
  #else\n\
    uniform mat4 u_model;\n\
  #endif\n\
  uniform mat4 u_viewprojection;\n\
  uniform float u_point_size;\n\
  uniform float u_perspective;\n\
  uniform float u_point_perspective;\n\
  float computePointSize(float radius, float w)\n\
  {\n\
    if(radius < 0.0)\n\
      return -radius;\n\
    return u_perspective * radius / w;\n\
  }\n\
  void main() {\n\
    v_coord = a_coord;\n\
    #ifdef USE_COLOR\n\
      v_color = a_color;\n\
    #endif\n\
    v_vertex = ( u_model * vec4( a_vertex, 1.0 )).xyz;\n\
    v_normal = ( u_model * vec4( a_normal, 0.0 )).xyz;\n\
    gl_Position = u_viewprojection * vec4(v_vertex,1.0);\n\
    gl_PointSize = u_point_size;\n\
    #ifdef USE_SIZE\n\
      gl_PointSize = a_extra;\n\
    #endif\n\
    if(u_point_perspective != 0.0)\n\
      gl_PointSize = computePointSize( gl_PointSize, gl_Position.w );\n\
  }\
';

  LGraphRenderPoints.fragment_shader_code =
    '\
  precision mediump float;\n\
  uniform vec4 u_color;\n\
  #ifdef USE_COLOR\n\
    varying vec4 v_color;\n\
  #endif\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_texture;\n\
  void main() {\n\
    vec4 color = u_color;\n\
    #ifdef USE_TEXTURED_POINTS\n\
      color *= texture2D(u_texture, gl_PointCoord.xy);\n\
    #else\n\
      #ifdef USE_TEXTURE\n\
        color *= texture2D(u_texture, v_coord);\n\
        if(color.a < 0.1)\n\
        discard;\n\
      #endif\n\
      #ifdef USE_POINTS\n\
        float dist = length( gl_PointCoord.xy - vec2(0.5) );\n\
        if( dist > 0.45 )\n\
          discard;\n\
      #endif\n\
    #endif\n\
    #ifdef USE_COLOR\n\
      color *= v_color;\n\
    #endif\n\
    gl_FragColor = color;\n\
  }\
';

  //based on https://inconvergent.net/2019/depth-of-field/
  /*
function LGraphRenderGeometryDOF() {
  this.addInput("in", "geometry");
  this.addInput("mat4", "mat4");
  this.addInput("tex", "texture");
  this.properties = {
    enabled: true,
    lines: true,
    point_size: 0.1,
    fixed_size: false,
    additive: true,
    color: [1,1,1],
    opacity: 1
  };

  this.color = vec4.create([1,1,1,1]);

  this.uniforms = {
    u_point_size: 1,
    u_perspective: 1,
    u_point_perspective: 1,
    u_color: this.color
  };

  this.geometry_id = -1;
  this.version = -1;
  this.mesh = null;
}

LGraphRenderGeometryDOF.widgets_info = {
  color: { widget: "color" }
};

LGraphRenderGeometryDOF.prototype.updateMesh = function(geometry)
{
  var buffer = this.buffer;
  if(!this.buffer || this.buffer.data.length != geometry.vertices.length)
    this.buffer = new GL.Buffer( GL.ARRAY_BUFFER, geometry.vertices,3,GL.DYNAMIC_DRAW);
  else
  {
    this.buffer.data.set( geometry.vertices );
    this.buffer.upload(GL.DYNAMIC_DRAW);
  }

  if(!this.mesh)
    this.mesh = new GL.Mesh();

  this.mesh.addBuffer("vertices",this.buffer);
  this.geometry_id = this.mesh.id = geometry._id;
  this.version = this.mesh.version = geometry._version;
}

LGraphRenderGeometryDOF.prototype.onExecute = function() {

  if(!this.properties.enabled)
    return;

  var geometry = this.getInputData(0);
  if(!geometry)
    return;
  if(this.version != geometry._version || this.geometry_id != geometry._id )
    this.updateMesh( geometry );

  if(!LiteGraph.LGraphRender.onRequestCameraMatrices)
  {
    console.warn("cannot render geometry, LiteGraph.onRequestCameraMatrices is null, remember to fill this with a callback(view_matrix, projection_matrix,viewprojection_matrix) to use 3D rendering from the graph");
    return;
  }

  LiteGraph.LGraphRender.onRequestCameraMatrices( view_matrix, projection_matrix,viewprojection_matrix );
  var shader = null;

  var texture = this.getInputData(2);

  if(texture)
  {
    shader = gl.shaders["textured_points"];
    if(!shader)
      shader = gl.shaders["textured_points"] = new GL.Shader( LGraphRenderGeometryDOF.vertex_shader_code, LGraphRenderGeometryDOF.fragment_shader_code, { USE_TEXTURED_POINTS:"" });
  }
  else
  {
    shader = gl.shaders["points"];
    if(!shader)
      shader = gl.shaders["points"] = new GL.Shader( LGraphRenderGeometryDOF.vertex_shader_code, LGraphRenderGeometryDOF.fragment_shader_code, { USE_POINTS: "" });
  }

  this.color.set( this.properties.color );
  this.color[3] = this.properties.opacity;

  var m = this.getInputData(1);
  if(m)
    model_matrix.set(m);
  else
    mat4.identity( model_matrix );

  this.uniforms.u_point_size = this.properties.point_size;
  this.uniforms.u_point_perspective = this.properties.fixed_size ? 0 : 1;
  this.uniforms.u_perspective = gl.viewport_data[3] * projection_matrix[5];

  shader.uniforms( global_uniforms );
  shader.uniforms( this.uniforms );

  if(this.properties.opacity >= 1)
    gl.disable( gl.BLEND );
  else
    gl.enable( gl.BLEND );

  gl.enable( gl.DEPTH_TEST );
  if( this.properties.additive )
  {
    gl.blendFunc( gl.SRC_ALPHA, gl.ONE );
    gl.depthMask( false );
  }
  else
    gl.blendFunc( gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA );

  shader.draw( this.mesh, GL.POINTS );

  gl.disable( gl.BLEND );
  gl.depthMask( true );
}

LiteGraph.registerNodeType( "geometry/render_dof", LGraphRenderGeometryDOF );

LGraphRenderGeometryDOF.vertex_shader_code = '\
  precision mediump float;\n\
  attribute vec3 a_vertex;\n\
  varying vec3 v_vertex;\n\
  attribute vec3 a_normal;\n\
  varying vec3 v_normal;\n\
  #ifdef USE_COLOR\n\
    attribute vec4 a_color;\n\
    varying vec4 v_color;\n\
  #endif\n\
  attribute vec2 a_coord;\n\
  varying vec2 v_coord;\n\
  #ifdef USE_SIZE\n\
    attribute float a_extra;\n\
  #endif\n\
  #ifdef USE_INSTANCING\n\
    attribute mat4 u_model;\n\
  #else\n\
    uniform mat4 u_model;\n\
  #endif\n\
  uniform mat4 u_viewprojection;\n\
  uniform float u_point_size;\n\
  uniform float u_perspective;\n\
  uniform float u_point_perspective;\n\
  float computePointSize(float radius, float w)\n\
  {\n\
    if(radius < 0.0)\n\
      return -radius;\n\
    return u_perspective * radius / w;\n\
  }\n\
  void main() {\n\
    v_coord = a_coord;\n\
    #ifdef USE_COLOR\n\
      v_color = a_color;\n\
    #endif\n\
    v_vertex = ( u_model * vec4( a_vertex, 1.0 )).xyz;\n\
    v_normal = ( u_model * vec4( a_normal, 0.0 )).xyz;\n\
    gl_Position = u_viewprojection * vec4(v_vertex,1.0);\n\
    gl_PointSize = u_point_size;\n\
    #ifdef USE_SIZE\n\
      gl_PointSize = a_extra;\n\
    #endif\n\
    if(u_point_perspective != 0.0)\n\
      gl_PointSize = computePointSize( gl_PointSize, gl_Position.w );\n\
  }\
';

LGraphRenderGeometryDOF.fragment_shader_code = '\
  precision mediump float;\n\
  uniform vec4 u_color;\n\
  #ifdef USE_COLOR\n\
    varying vec4 v_color;\n\
  #endif\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_texture;\n\
  void main() {\n\
    vec4 color = u_color;\n\
    #ifdef USE_TEXTURED_POINTS\n\
      color *= texture2D(u_texture, gl_PointCoord.xy);\n\
    #else\n\
      #ifdef USE_TEXTURE\n\
        color *= texture2D(u_texture, v_coord);\n\
        if(color.a < 0.1)\n\
        discard;\n\
      #endif\n\
      #ifdef USE_POINTS\n\
        float dist = length( gl_PointCoord.xy - vec2(0.5) );\n\
        if( dist > 0.45 )\n\
          discard;\n\
      #endif\n\
    #endif\n\
    #ifdef USE_COLOR\n\
      color *= v_color;\n\
    #endif\n\
    gl_FragColor = color;\n\
  }\
';
*/
})(this);
(function (global) {
  var LiteGraph = global.LiteGraph;
  var LGraphTexture = global.LGraphTexture;

  //Works with Litegl.js to create WebGL nodes
  if (typeof GL != 'undefined') {
    // Texture Lens *****************************************
    function LGraphFXLens() {
      this.addInput('Texture', 'Texture');
      this.addInput('Aberration', 'number');
      this.addInput('Distortion', 'number');
      this.addInput('Blur', 'number');
      this.addOutput('Texture', 'Texture');
      this.properties = {
        aberration: 1.0,
        distortion: 1.0,
        blur: 1.0,
        precision: LGraphTexture.DEFAULT,
      };

      if (!LGraphFXLens._shader) {
        LGraphFXLens._shader = new GL.Shader(
          GL.Shader.SCREEN_VERTEX_SHADER,
          LGraphFXLens.pixel_shader,
        );
        LGraphFXLens._texture = new GL.Texture(3, 1, {
          format: gl.RGB,
          wrap: gl.CLAMP_TO_EDGE,
          magFilter: gl.LINEAR,
          minFilter: gl.LINEAR,
          pixel_data: [255, 0, 0, 0, 255, 0, 0, 0, 255],
        });
      }
    }

    LGraphFXLens.title = 'Lens';
    LGraphFXLens.desc = 'Camera Lens distortion';
    LGraphFXLens.widgets_info = {
      precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
    };

    LGraphFXLens.prototype.onExecute = function () {
      var tex = this.getInputData(0);
      if (this.properties.precision === LGraphTexture.PASS_THROUGH) {
        this.setOutputData(0, tex);
        return;
      }

      if (!tex) {
        return;
      }

      this._tex = LGraphTexture.getTargetTexture(
        tex,
        this._tex,
        this.properties.precision,
      );

      var aberration = this.properties.aberration;
      if (this.isInputConnected(1)) {
        aberration = this.getInputData(1);
        this.properties.aberration = aberration;
      }

      var distortion = this.properties.distortion;
      if (this.isInputConnected(2)) {
        distortion = this.getInputData(2);
        this.properties.distortion = distortion;
      }

      var blur = this.properties.blur;
      if (this.isInputConnected(3)) {
        blur = this.getInputData(3);
        this.properties.blur = blur;
      }

      gl.disable(gl.BLEND);
      gl.disable(gl.DEPTH_TEST);
      var mesh = Mesh.getScreenQuad();
      var shader = LGraphFXLens._shader;
      //var camera = LS.Renderer._current_camera;

      this._tex.drawTo(function () {
        tex.bind(0);
        shader
          .uniforms({
            u_texture: 0,
            u_aberration: aberration,
            u_distortion: distortion,
            u_blur: blur,
          })
          .draw(mesh);
      });

      this.setOutputData(0, this._tex);
    };

    LGraphFXLens.pixel_shader =
      'precision highp float;\n\
    precision highp float;\n\
    varying vec2 v_coord;\n\
    uniform sampler2D u_texture;\n\
    uniform vec2 u_camera_planes;\n\
    uniform float u_aberration;\n\
    uniform float u_distortion;\n\
    uniform float u_blur;\n\
    \n\
    void main() {\n\
      vec2 coord = v_coord;\n\
      float dist = distance(vec2(0.5), coord);\n\
      vec2 dist_coord = coord - vec2(0.5);\n\
      float percent = 1.0 + ((0.5 - dist) / 0.5) * u_distortion;\n\
      dist_coord *= percent;\n\
      coord = dist_coord + vec2(0.5);\n\
      vec4 color = texture2D(u_texture,coord, u_blur * dist);\n\
      color.r = texture2D(u_texture,vec2(0.5) + dist_coord * (1.0+0.01*u_aberration), u_blur * dist ).r;\n\
      color.b = texture2D(u_texture,vec2(0.5) + dist_coord * (1.0-0.01*u_aberration), u_blur * dist ).b;\n\
      gl_FragColor = color;\n\
    }\n\
    ';
    /*
    float normalized_tunable_sigmoid(float xs, float k)\n\
    {\n\
      xs = xs * 2.0 - 1.0;\n\
      float signx = sign(xs);\n\
      float absx = abs(xs);\n\
      return signx * ((-k - 1.0)*absx)/(2.0*(-2.0*k*absx+k-1.0)) + 0.5;\n\
    }\n\
  */

    LiteGraph.registerNodeType('fx/lens', LGraphFXLens);
    global.LGraphFXLens = LGraphFXLens;

    /* not working yet
function LGraphDepthOfField()
{
  this.addInput("Color","Texture");
  this.addInput("Linear Depth","Texture");
  this.addInput("Camera","camera");
  this.addOutput("Texture","Texture");
  this.properties = { high_precision: false };
}

LGraphDepthOfField.title = "Depth Of Field";
LGraphDepthOfField.desc = "Applies a depth of field effect";

LGraphDepthOfField.prototype.onExecute = function()
{
  var tex = this.getInputData(0);
  var depth = this.getInputData(1);
  var camera = this.getInputData(2);

  if(!tex || !depth || !camera)
  {
    this.setOutputData(0, tex);
    return;
  }

  var precision = gl.UNSIGNED_BYTE;
  if(this.properties.high_precision)
    precision = gl.half_float_ext ? gl.HALF_FLOAT_OES : gl.FLOAT;
  if(!this._temp_texture || this._temp_texture.type != precision ||
    this._temp_texture.width != tex.width || this._temp_texture.height != tex.height)
    this._temp_texture = new GL.Texture( tex.width, tex.height, { type: precision, format: gl.RGBA, filter: gl.LINEAR });

  var shader = LGraphDepthOfField._shader = new GL.Shader( GL.Shader.SCREEN_VERTEX_SHADER, LGraphDepthOfField._pixel_shader );

  var screen_mesh = Mesh.getScreenQuad();

  gl.disable( gl.DEPTH_TEST );
  gl.disable( gl.BLEND );

  var camera_position = camera.getEye();
  var focus_point = camera.getCenter();
  var distance = vec3.distance( camera_position, focus_point );
  var far = camera.far;
  var focus_range = distance * 0.5;

  this._temp_texture.drawTo( function() {
    tex.bind(0);
    depth.bind(1);
    shader.uniforms({u_texture:0, u_depth_texture:1, u_resolution: [1/tex.width, 1/tex.height], u_far: far, u_focus_point: distance, u_focus_scale: focus_range }).draw(screen_mesh);
  });

  this.setOutputData(0, this._temp_texture);
}

//from http://tuxedolabs.blogspot.com.es/2018/05/bokeh-depth-of-field-in-single-pass.html
LGraphDepthOfField._pixel_shader = "\n\
  precision highp float;\n\
  varying vec2 v_coord;\n\
  uniform sampler2D u_texture; //Image to be processed\n\
  uniform sampler2D u_depth_texture; //Linear depth, where 1.0 == far plane\n\
  uniform vec2 u_iresolution; //The size of a pixel: vec2(1.0/width, 1.0/height)\n\
  uniform float u_far; // Far plane\n\
  uniform float u_focus_point;\n\
  uniform float u_focus_scale;\n\
  \n\
  const float GOLDEN_ANGLE = 2.39996323;\n\
  const float MAX_BLUR_SIZE = 20.0;\n\
  const float RAD_SCALE = 0.5; // Smaller = nicer blur, larger = faster\n\
  \n\
  float getBlurSize(float depth, float focusPoint, float focusScale)\n\
  {\n\
   float coc = clamp((1.0 / focusPoint - 1.0 / depth)*focusScale, -1.0, 1.0);\n\
   return abs(coc) * MAX_BLUR_SIZE;\n\
  }\n\
  \n\
  vec3 depthOfField(vec2 texCoord, float focusPoint, float focusScale)\n\
  {\n\
   float centerDepth = texture2D(u_depth_texture, texCoord).r * u_far;\n\
   float centerSize = getBlurSize(centerDepth, focusPoint, focusScale);\n\
   vec3 color = texture2D(u_texture, v_coord).rgb;\n\
   float tot = 1.0;\n\
  \n\
   float radius = RAD_SCALE;\n\
   for (float ang = 0.0; ang < 100.0; ang += GOLDEN_ANGLE)\n\
   {\n\
    vec2 tc = texCoord + vec2(cos(ang), sin(ang)) * u_iresolution * radius;\n\
    \n\
    vec3 sampleColor = texture2D(u_texture, tc).rgb;\n\
    float sampleDepth = texture2D(u_depth_texture, tc).r * u_far;\n\
    float sampleSize = getBlurSize( sampleDepth, focusPoint, focusScale );\n\
    if (sampleDepth > centerDepth)\n\
     sampleSize = clamp(sampleSize, 0.0, centerSize*2.0);\n\
    \n\
    float m = smoothstep(radius-0.5, radius+0.5, sampleSize);\n\
    color += mix(color/tot, sampleColor, m);\n\
    tot += 1.0;\n\
    radius += RAD_SCALE/radius;\n\
    if(radius>=MAX_BLUR_SIZE)\n\
     return color / tot;\n\
   }\n\
   return color / tot;\n\
  }\n\
  void main()\n\
  {\n\
    gl_FragColor = vec4( depthOfField( v_coord, u_focus_point, u_focus_scale ), 1.0 );\n\
    //gl_FragColor = vec4( texture2D(u_depth_texture, v_coord).r );\n\
  }\n\
  ";

LiteGraph.registerNodeType("fx/DOF", LGraphDepthOfField );
global.LGraphDepthOfField = LGraphDepthOfField;
*/

    //*******************************************************

    function LGraphFXBokeh() {
      this.addInput('Texture', 'Texture');
      this.addInput('Blurred', 'Texture');
      this.addInput('Mask', 'Texture');
      this.addInput('Threshold', 'number');
      this.addOutput('Texture', 'Texture');
      this.properties = {
        shape: '',
        size: 10,
        alpha: 1.0,
        threshold: 1.0,
        high_precision: false,
      };
    }

    LGraphFXBokeh.title = 'Bokeh';
    LGraphFXBokeh.desc = 'applies an Bokeh effect';

    LGraphFXBokeh.widgets_info = { shape: { widget: 'texture' } };

    LGraphFXBokeh.prototype.onExecute = function () {
      var tex = this.getInputData(0);
      var blurred_tex = this.getInputData(1);
      var mask_tex = this.getInputData(2);
      if (!tex || !mask_tex || !this.properties.shape) {
        this.setOutputData(0, tex);
        return;
      }

      if (!blurred_tex) {
        blurred_tex = tex;
      }

      var shape_tex = LGraphTexture.getTexture(this.properties.shape);
      if (!shape_tex) {
        return;
      }

      var threshold = this.properties.threshold;
      if (this.isInputConnected(3)) {
        threshold = this.getInputData(3);
        this.properties.threshold = threshold;
      }

      var precision = gl.UNSIGNED_BYTE;
      if (this.properties.high_precision) {
        precision = gl.half_float_ext ? gl.HALF_FLOAT_OES : gl.FLOAT;
      }
      if (
        !this._temp_texture ||
        this._temp_texture.type != precision ||
        this._temp_texture.width != tex.width ||
        this._temp_texture.height != tex.height
      ) {
        this._temp_texture = new GL.Texture(tex.width, tex.height, {
          type: precision,
          format: gl.RGBA,
          filter: gl.LINEAR,
        });
      }

      //iterations
      var size = this.properties.size;

      var first_shader = LGraphFXBokeh._first_shader;
      if (!first_shader) {
        first_shader = LGraphFXBokeh._first_shader = new GL.Shader(
          Shader.SCREEN_VERTEX_SHADER,
          LGraphFXBokeh._first_pixel_shader,
        );
      }

      var second_shader = LGraphFXBokeh._second_shader;
      if (!second_shader) {
        second_shader = LGraphFXBokeh._second_shader = new GL.Shader(
          LGraphFXBokeh._second_vertex_shader,
          LGraphFXBokeh._second_pixel_shader,
        );
      }

      var points_mesh = this._points_mesh;
      if (
        !points_mesh ||
        points_mesh._width != tex.width ||
        points_mesh._height != tex.height ||
        points_mesh._spacing != 2
      ) {
        points_mesh = this.createPointsMesh(tex.width, tex.height, 2);
      }

      var screen_mesh = Mesh.getScreenQuad();

      var point_size = this.properties.size;
      var min_light = this.properties.min_light;
      var alpha = this.properties.alpha;

      gl.disable(gl.DEPTH_TEST);
      gl.disable(gl.BLEND);

      this._temp_texture.drawTo(function () {
        tex.bind(0);
        blurred_tex.bind(1);
        mask_tex.bind(2);
        first_shader
          .uniforms({
            u_texture: 0,
            u_texture_blur: 1,
            u_mask: 2,
            u_texsize: [tex.width, tex.height],
          })
          .draw(screen_mesh);
      });

      this._temp_texture.drawTo(function () {
        //clear because we use blending
        //gl.clearColor(0.0,0.0,0.0,1.0);
        //gl.clear( gl.COLOR_BUFFER_BIT );
        gl.enable(gl.BLEND);
        gl.blendFunc(gl.ONE, gl.ONE);

        tex.bind(0);
        shape_tex.bind(3);
        second_shader
          .uniforms({
            u_texture: 0,
            u_mask: 2,
            u_shape: 3,
            u_alpha: alpha,
            u_threshold: threshold,
            u_pointSize: point_size,
            u_itexsize: [1.0 / tex.width, 1.0 / tex.height],
          })
          .draw(points_mesh, gl.POINTS);
      });

      this.setOutputData(0, this._temp_texture);
    };

    LGraphFXBokeh.prototype.createPointsMesh = function (
      width,
      height,
      spacing,
    ) {
      var nwidth = Math.round(width / spacing);
      var nheight = Math.round(height / spacing);

      var vertices = new Float32Array(nwidth * nheight * 2);

      var ny = -1;
      var dx = (2 / width) * spacing;
      var dy = (2 / height) * spacing;
      for (var y = 0; y < nheight; ++y) {
        var nx = -1;
        for (var x = 0; x < nwidth; ++x) {
          var pos = y * nwidth * 2 + x * 2;
          vertices[pos] = nx;
          vertices[pos + 1] = ny;
          nx += dx;
        }
        ny += dy;
      }

      this._points_mesh = GL.Mesh.load({ vertices2D: vertices });
      this._points_mesh._width = width;
      this._points_mesh._height = height;
      this._points_mesh._spacing = spacing;

      return this._points_mesh;
    };

    /*
LGraphTextureBokeh._pixel_shader = "precision highp float;\n\
    varying vec2 a_coord;\n\
    uniform sampler2D u_texture;\n\
    uniform sampler2D u_shape;\n\
    \n\
    void main() {\n\
      vec4 color = texture2D( u_texture, gl_PointCoord );\n\
      color *= v_color * u_alpha;\n\
      gl_FragColor = color;\n\
    }\n";
*/

    LGraphFXBokeh._first_pixel_shader =
      'precision highp float;\n\
    precision highp float;\n\
    varying vec2 v_coord;\n\
    uniform sampler2D u_texture;\n\
    uniform sampler2D u_texture_blur;\n\
    uniform sampler2D u_mask;\n\
    \n\
    void main() {\n\
      vec4 color = texture2D(u_texture, v_coord);\n\
      vec4 blurred_color = texture2D(u_texture_blur, v_coord);\n\
      float mask = texture2D(u_mask, v_coord).x;\n\
       gl_FragColor = mix(color, blurred_color, mask);\n\
    }\n\
    ';

    LGraphFXBokeh._second_vertex_shader =
      'precision highp float;\n\
    attribute vec2 a_vertex2D;\n\
    varying vec4 v_color;\n\
    uniform sampler2D u_texture;\n\
    uniform sampler2D u_mask;\n\
    uniform vec2 u_itexsize;\n\
    uniform float u_pointSize;\n\
    uniform float u_threshold;\n\
    void main() {\n\
      vec2 coord = a_vertex2D * 0.5 + 0.5;\n\
      v_color = texture2D( u_texture, coord );\n\
      v_color += texture2D( u_texture, coord + vec2(u_itexsize.x, 0.0) );\n\
      v_color += texture2D( u_texture, coord + vec2(0.0, u_itexsize.y));\n\
      v_color += texture2D( u_texture, coord + u_itexsize);\n\
      v_color *= 0.25;\n\
      float mask = texture2D(u_mask, coord).x;\n\
      float luminance = length(v_color) * mask;\n\
      /*luminance /= (u_pointSize*u_pointSize)*0.01 */;\n\
      luminance -= u_threshold;\n\
      if(luminance < 0.0)\n\
      {\n\
        gl_Position.x = -100.0;\n\
        return;\n\
      }\n\
      gl_PointSize = u_pointSize;\n\
      gl_Position = vec4(a_vertex2D,0.0,1.0);\n\
    }\n\
    ';

    LGraphFXBokeh._second_pixel_shader =
      'precision highp float;\n\
    varying vec4 v_color;\n\
    uniform sampler2D u_shape;\n\
    uniform float u_alpha;\n\
    \n\
    void main() {\n\
      vec4 color = texture2D( u_shape, gl_PointCoord );\n\
      color *= v_color * u_alpha;\n\
      gl_FragColor = color;\n\
    }\n';

    LiteGraph.registerNodeType('fx/bokeh', LGraphFXBokeh);
    global.LGraphFXBokeh = LGraphFXBokeh;

    //************************************************

    function LGraphFXGeneric() {
      this.addInput('Texture', 'Texture');
      this.addInput('value1', 'number');
      this.addInput('value2', 'number');
      this.addOutput('Texture', 'Texture');
      this.properties = {
        fx: 'halftone',
        value1: 1,
        value2: 1,
        precision: LGraphTexture.DEFAULT,
      };
    }

    LGraphFXGeneric.title = 'FX';
    LGraphFXGeneric.desc = 'applies an FX from a list';

    LGraphFXGeneric.widgets_info = {
      fx: {
        widget: 'combo',
        values: ['halftone', 'pixelate', 'lowpalette', 'noise', 'gamma'],
      },
      precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
    };
    LGraphFXGeneric.shaders = {};

    LGraphFXGeneric.prototype.onExecute = function () {
      if (!this.isOutputConnected(0)) {
        return;
      } //saves work

      var tex = this.getInputData(0);
      if (this.properties.precision === LGraphTexture.PASS_THROUGH) {
        this.setOutputData(0, tex);
        return;
      }

      if (!tex) {
        return;
      }

      this._tex = LGraphTexture.getTargetTexture(
        tex,
        this._tex,
        this.properties.precision,
      );

      //iterations
      var value1 = this.properties.value1;
      if (this.isInputConnected(1)) {
        value1 = this.getInputData(1);
        this.properties.value1 = value1;
      }

      var value2 = this.properties.value2;
      if (this.isInputConnected(2)) {
        value2 = this.getInputData(2);
        this.properties.value2 = value2;
      }

      var fx = this.properties.fx;
      var shader = LGraphFXGeneric.shaders[fx];
      if (!shader) {
        var pixel_shader_code = LGraphFXGeneric['pixel_shader_' + fx];
        if (!pixel_shader_code) {
          return;
        }

        shader = LGraphFXGeneric.shaders[fx] = new GL.Shader(
          Shader.SCREEN_VERTEX_SHADER,
          pixel_shader_code,
        );
      }

      gl.disable(gl.BLEND);
      gl.disable(gl.DEPTH_TEST);
      var mesh = Mesh.getScreenQuad();
      var camera = global.LS ? LS.Renderer._current_camera : null;
      var camera_planes;
      if (camera) {
        camera_planes = [
          LS.Renderer._current_camera.near,
          LS.Renderer._current_camera.far,
        ];
      } else {
        camera_planes = [1, 100];
      }

      var noise = null;
      if (fx == 'noise') {
        noise = LGraphTexture.getNoiseTexture();
      }

      this._tex.drawTo(function () {
        tex.bind(0);
        if (fx == 'noise') {
          noise.bind(1);
        }

        shader
          .uniforms({
            u_texture: 0,
            u_noise: 1,
            u_size: [tex.width, tex.height],
            u_rand: [Math.random(), Math.random()],
            u_value1: value1,
            u_value2: value2,
            u_camera_planes: camera_planes,
          })
          .draw(mesh);
      });

      this.setOutputData(0, this._tex);
    };

    LGraphFXGeneric.pixel_shader_halftone =
      'precision highp float;\n\
    varying vec2 v_coord;\n\
    uniform sampler2D u_texture;\n\
    uniform vec2 u_camera_planes;\n\
    uniform vec2 u_size;\n\
    uniform float u_value1;\n\
    uniform float u_value2;\n\
    \n\
    float pattern() {\n\
      float s = sin(u_value1 * 3.1415), c = cos(u_value1 * 3.1415);\n\
      vec2 tex = v_coord * u_size.xy;\n\
      vec2 point = vec2(\n\
         c * tex.x - s * tex.y ,\n\
         s * tex.x + c * tex.y \n\
      ) * u_value2;\n\
      return (sin(point.x) * sin(point.y)) * 4.0;\n\
    }\n\
    void main() {\n\
      vec4 color = texture2D(u_texture, v_coord);\n\
      float average = (color.r + color.g + color.b) / 3.0;\n\
      gl_FragColor = vec4(vec3(average * 10.0 - 5.0 + pattern()), color.a);\n\
    }\n';

    LGraphFXGeneric.pixel_shader_pixelate =
      'precision highp float;\n\
    varying vec2 v_coord;\n\
    uniform sampler2D u_texture;\n\
    uniform vec2 u_camera_planes;\n\
    uniform vec2 u_size;\n\
    uniform float u_value1;\n\
    uniform float u_value2;\n\
    \n\
    void main() {\n\
      vec2 coord = vec2( floor(v_coord.x * u_value1) / u_value1, floor(v_coord.y * u_value2) / u_value2 );\n\
      vec4 color = texture2D(u_texture, coord);\n\
      gl_FragColor = color;\n\
    }\n';

    LGraphFXGeneric.pixel_shader_lowpalette =
      'precision highp float;\n\
    varying vec2 v_coord;\n\
    uniform sampler2D u_texture;\n\
    uniform vec2 u_camera_planes;\n\
    uniform vec2 u_size;\n\
    uniform float u_value1;\n\
    uniform float u_value2;\n\
    \n\
    void main() {\n\
      vec4 color = texture2D(u_texture, v_coord);\n\
      gl_FragColor = floor(color * u_value1) / u_value1;\n\
    }\n';

    LGraphFXGeneric.pixel_shader_noise =
      'precision highp float;\n\
    varying vec2 v_coord;\n\
    uniform sampler2D u_texture;\n\
    uniform sampler2D u_noise;\n\
    uniform vec2 u_size;\n\
    uniform float u_value1;\n\
    uniform float u_value2;\n\
    uniform vec2 u_rand;\n\
    \n\
    void main() {\n\
      vec4 color = texture2D(u_texture, v_coord);\n\
      vec3 noise = texture2D(u_noise, v_coord * vec2(u_size.x / 512.0, u_size.y / 512.0) + u_rand).xyz - vec3(0.5);\n\
      gl_FragColor = vec4( color.xyz + noise * u_value1, color.a );\n\
    }\n';

    LGraphFXGeneric.pixel_shader_gamma =
      'precision highp float;\n\
    varying vec2 v_coord;\n\
    uniform sampler2D u_texture;\n\
    uniform float u_value1;\n\
    \n\
    void main() {\n\
      vec4 color = texture2D(u_texture, v_coord);\n\
      float gamma = 1.0 / u_value1;\n\
      gl_FragColor = vec4( pow( color.xyz, vec3(gamma) ), color.a );\n\
    }\n';

    LiteGraph.registerNodeType('fx/generic', LGraphFXGeneric);
    global.LGraphFXGeneric = LGraphFXGeneric;

    // Vigneting ************************************

    function LGraphFXVigneting() {
      this.addInput('Tex.', 'Texture');
      this.addInput('intensity', 'number');

      this.addOutput('Texture', 'Texture');
      this.properties = {
        intensity: 1,
        invert: false,
        precision: LGraphTexture.DEFAULT,
      };

      if (!LGraphFXVigneting._shader) {
        LGraphFXVigneting._shader = new GL.Shader(
          Shader.SCREEN_VERTEX_SHADER,
          LGraphFXVigneting.pixel_shader,
        );
      }
    }

    LGraphFXVigneting.title = 'Vigneting';
    LGraphFXVigneting.desc = 'Vigneting';

    LGraphFXVigneting.widgets_info = {
      precision: { widget: 'combo', values: LGraphTexture.MODE_VALUES },
    };

    LGraphFXVigneting.prototype.onExecute = function () {
      var tex = this.getInputData(0);

      if (this.properties.precision === LGraphTexture.PASS_THROUGH) {
        this.setOutputData(0, tex);
        return;
      }

      if (!tex) {
        return;
      }

      this._tex = LGraphTexture.getTargetTexture(
        tex,
        this._tex,
        this.properties.precision,
      );

      var intensity = this.properties.intensity;
      if (this.isInputConnected(1)) {
        intensity = this.getInputData(1);
        this.properties.intensity = intensity;
      }

      gl.disable(gl.BLEND);
      gl.disable(gl.DEPTH_TEST);

      var mesh = Mesh.getScreenQuad();
      var shader = LGraphFXVigneting._shader;
      var invert = this.properties.invert;

      this._tex.drawTo(function () {
        tex.bind(0);
        shader
          .uniforms({
            u_texture: 0,
            u_intensity: intensity,
            u_isize: [1 / tex.width, 1 / tex.height],
            u_invert: invert ? 1 : 0,
          })
          .draw(mesh);
      });

      this.setOutputData(0, this._tex);
    };

    LGraphFXVigneting.pixel_shader =
      'precision highp float;\n\
    precision highp float;\n\
    varying vec2 v_coord;\n\
    uniform sampler2D u_texture;\n\
    uniform float u_intensity;\n\
    uniform int u_invert;\n\
    \n\
    void main() {\n\
      float luminance = 1.0 - length( v_coord - vec2(0.5) ) * 1.414;\n\
      vec4 color = texture2D(u_texture, v_coord);\n\
      if(u_invert == 1)\n\
        luminance = 1.0 - luminance;\n\
      luminance = mix(1.0, luminance, u_intensity);\n\
       gl_FragColor = vec4( luminance * color.xyz, color.a);\n\
    }\n\
    ';

    LiteGraph.registerNodeType('fx/vigneting', LGraphFXVigneting);
    global.LGraphFXVigneting = LGraphFXVigneting;
  }
})(this);

(function (global) {
  var LiteGraph = global.LiteGraph;
  var MIDI_COLOR = '#243';

  function MIDIEvent(data) {
    this.channel = 0;
    this.cmd = 0;
    this.data = new Uint32Array(3);

    if (data) {
      this.setup(data);
    }
  }

  LiteGraph.MIDIEvent = MIDIEvent;

  MIDIEvent.prototype.fromJSON = function (o) {
    this.setup(o.data);
  };

  MIDIEvent.prototype.setup = function (data) {
    var raw_data = data;
    if (data.constructor === Object) {
      raw_data = data.data;
    }

    this.data.set(raw_data);

    var midiStatus = raw_data[0];
    this.status = midiStatus;

    var midiCommand = midiStatus & 0xf0;

    if (midiStatus >= 0xf0) {
      this.cmd = midiStatus;
    } else {
      this.cmd = midiCommand;
    }

    if (this.cmd == MIDIEvent.NOTEON && this.velocity == 0) {
      this.cmd = MIDIEvent.NOTEOFF;
    }

    this.cmd_str = MIDIEvent.commands[this.cmd] || '';

    if (midiCommand >= MIDIEvent.NOTEON || midiCommand <= MIDIEvent.NOTEOFF) {
      this.channel = midiStatus & 0x0f;
    }
  };

  Object.defineProperty(MIDIEvent.prototype, 'velocity', {
    get: function () {
      if (this.cmd == MIDIEvent.NOTEON) {
        return this.data[2];
      }
      return -1;
    },
    set: function (v) {
      this.data[2] = v; //  v / 127;
    },
    enumerable: true,
  });

  MIDIEvent.notes = [
    'A',
    'A#',
    'B',
    'C',
    'C#',
    'D',
    'D#',
    'E',
    'F',
    'F#',
    'G',
    'G#',
  ];
  MIDIEvent.note_to_index = {
    A: 0,
    'A#': 1,
    B: 2,
    C: 3,
    'C#': 4,
    D: 5,
    'D#': 6,
    E: 7,
    F: 8,
    'F#': 9,
    G: 10,
    'G#': 11,
  };

  Object.defineProperty(MIDIEvent.prototype, 'note', {
    get: function () {
      if (this.cmd != MIDIEvent.NOTEON) {
        return -1;
      }
      return MIDIEvent.toNoteString(this.data[1], true);
    },
    set: function (v) {
      throw 'notes cannot be assigned this way, must modify the data[1]';
    },
    enumerable: true,
  });

  Object.defineProperty(MIDIEvent.prototype, 'octave', {
    get: function () {
      if (this.cmd != MIDIEvent.NOTEON) {
        return -1;
      }
      var octave = this.data[1] - 24;
      return Math.floor(octave / 12 + 1);
    },
    set: function (v) {
      throw 'octave cannot be assigned this way, must modify the data[1]';
    },
    enumerable: true,
  });

  //returns HZs
  MIDIEvent.prototype.getPitch = function () {
    return Math.pow(2, (this.data[1] - 69) / 12) * 440;
  };

  MIDIEvent.computePitch = function (note) {
    return Math.pow(2, (note - 69) / 12) * 440;
  };

  MIDIEvent.prototype.getCC = function () {
    return this.data[1];
  };

  MIDIEvent.prototype.getCCValue = function () {
    return this.data[2];
  };

  //not tested, there is a formula missing here
  MIDIEvent.prototype.getPitchBend = function () {
    return this.data[1] + (this.data[2] << 7) - 8192;
  };

  MIDIEvent.computePitchBend = function (v1, v2) {
    return v1 + (v2 << 7) - 8192;
  };

  MIDIEvent.prototype.setCommandFromString = function (str) {
    this.cmd = MIDIEvent.computeCommandFromString(str);
  };

  MIDIEvent.computeCommandFromString = function (str) {
    if (!str) {
      return 0;
    }

    if (str && str.constructor === Number) {
      return str;
    }

    str = str.toUpperCase();
    switch (str) {
      case 'NOTE ON':
      case 'NOTEON':
        return MIDIEvent.NOTEON;
        break;
      case 'NOTE OFF':
      case 'NOTEOFF':
        return MIDIEvent.NOTEON;
        break;
      case 'KEY PRESSURE':
      case 'KEYPRESSURE':
        return MIDIEvent.KEYPRESSURE;
        break;
      case 'CONTROLLER CHANGE':
      case 'CONTROLLERCHANGE':
      case 'CC':
        return MIDIEvent.CONTROLLERCHANGE;
        break;
      case 'PROGRAM CHANGE':
      case 'PROGRAMCHANGE':
      case 'PC':
        return MIDIEvent.PROGRAMCHANGE;
        break;
      case 'CHANNEL PRESSURE':
      case 'CHANNELPRESSURE':
        return MIDIEvent.CHANNELPRESSURE;
        break;
      case 'PITCH BEND':
      case 'PITCHBEND':
        return MIDIEvent.PITCHBEND;
        break;
      case 'TIME TICK':
      case 'TIMETICK':
        return MIDIEvent.TIMETICK;
        break;
      default:
        return Number(str); //assume its a hex code
    }
  };

  //transform from a pitch number to string like "C4"
  MIDIEvent.toNoteString = function (d, skip_octave) {
    d = Math.round(d); //in case it has decimals
    var note = d - 21;
    var octave = Math.floor((d - 24) / 12 + 1);
    note = note % 12;
    if (note < 0) {
      note = 12 + note;
    }
    return MIDIEvent.notes[note] + (skip_octave ? '' : octave);
  };

  MIDIEvent.NoteStringToPitch = function (str) {
    str = str.toUpperCase();
    var note = str[0];
    var octave = 4;

    if (str[1] == '#') {
      note += '#';
      if (str.length > 2) {
        octave = Number(str[2]);
      }
    } else {
      if (str.length > 1) {
        octave = Number(str[1]);
      }
    }
    var pitch = MIDIEvent.note_to_index[note];
    if (pitch == null) {
      return null;
    }
    return (octave - 1) * 12 + pitch + 21;
  };

  MIDIEvent.prototype.toString = function () {
    var str = '' + this.channel + '. ';
    switch (this.cmd) {
      case MIDIEvent.NOTEON:
        str += 'NOTEON ' + MIDIEvent.toNoteString(this.data[1]);
        break;
      case MIDIEvent.NOTEOFF:
        str += 'NOTEOFF ' + MIDIEvent.toNoteString(this.data[1]);
        break;
      case MIDIEvent.CONTROLLERCHANGE:
        str += 'CC ' + this.data[1] + ' ' + this.data[2];
        break;
      case MIDIEvent.PROGRAMCHANGE:
        str += 'PC ' + this.data[1];
        break;
      case MIDIEvent.PITCHBEND:
        str += 'PITCHBEND ' + this.getPitchBend();
        break;
      case MIDIEvent.KEYPRESSURE:
        str += 'KEYPRESS ' + this.data[1];
        break;
    }

    return str;
  };

  MIDIEvent.prototype.toHexString = function () {
    var str = '';
    for (var i = 0; i < this.data.length; i++) {
      str += this.data[i].toString(16) + ' ';
    }
  };

  MIDIEvent.prototype.toJSON = function () {
    return {
      data: [this.data[0], this.data[1], this.data[2]],
      object_class: 'MIDIEvent',
    };
  };

  MIDIEvent.NOTEOFF = 0x80;
  MIDIEvent.NOTEON = 0x90;
  MIDIEvent.KEYPRESSURE = 0xa0;
  MIDIEvent.CONTROLLERCHANGE = 0xb0;
  MIDIEvent.PROGRAMCHANGE = 0xc0;
  MIDIEvent.CHANNELPRESSURE = 0xd0;
  MIDIEvent.PITCHBEND = 0xe0;
  MIDIEvent.TIMETICK = 0xf8;

  MIDIEvent.commands = {
    0x80: 'note off',
    0x90: 'note on',
    0xa0: 'key pressure',
    0xb0: 'controller change',
    0xc0: 'program change',
    0xd0: 'channel pressure',
    0xe0: 'pitch bend',
    0xf0: 'system',
    0xf2: 'Song pos',
    0xf3: 'Song select',
    0xf6: 'Tune request',
    0xf8: 'time tick',
    0xfa: 'Start Song',
    0xfb: 'Continue Song',
    0xfc: 'Stop Song',
    0xfe: 'Sensing',
    0xff: 'Reset',
  };

  MIDIEvent.commands_short = {
    0x80: 'NOTEOFF',
    0x90: 'NOTEOFF',
    0xa0: 'KEYP',
    0xb0: 'CC',
    0xc0: 'PC',
    0xd0: 'CP',
    0xe0: 'PB',
    0xf0: 'SYS',
    0xf2: 'POS',
    0xf3: 'SELECT',
    0xf6: 'TUNEREQ',
    0xf8: 'TT',
    0xfa: 'START',
    0xfb: 'CONTINUE',
    0xfc: 'STOP',
    0xfe: 'SENS',
    0xff: 'RESET',
  };

  MIDIEvent.commands_reversed = {};
  for (var i in MIDIEvent.commands) {
    MIDIEvent.commands_reversed[MIDIEvent.commands[i]] = i;
  }

  //MIDI wrapper, instantiate by MIDIIn and MIDIOut
  function MIDIInterface(on_ready, on_error) {
    if (!navigator.requestMIDIAccess) {
      this.error = 'not suppoorted';
      if (on_error) {
        on_error('Not supported');
      } else {
        console.error('MIDI NOT SUPPORTED, enable by chrome://flags');
      }
      return;
    }

    this.on_ready = on_ready;

    this.state = {
      note: [],
      cc: [],
    };

    this.input_ports = null;
    this.input_ports_info = [];
    this.output_ports = null;
    this.output_ports_info = [];

    navigator
      .requestMIDIAccess()
      .then(this.onMIDISuccess.bind(this), this.onMIDIFailure.bind(this));
  }

  MIDIInterface.input = null;

  MIDIInterface.MIDIEvent = MIDIEvent;

  MIDIInterface.prototype.onMIDISuccess = function (midiAccess) {
    console.log('MIDI ready!');
    console.log(midiAccess);
    this.midi = midiAccess; // store in the global (in real usage, would probably keep in an object instance)
    this.updatePorts();

    if (this.on_ready) {
      this.on_ready(this);
    }
  };

  MIDIInterface.prototype.updatePorts = function () {
    var midi = this.midi;
    this.input_ports = midi.inputs;
    this.input_ports_info = [];
    this.output_ports = midi.outputs;
    this.output_ports_info = [];

    var num = 0;

    var it = this.input_ports.values();
    var it_value = it.next();
    while (it_value && it_value.done === false) {
      var port_info = it_value.value;
      this.input_ports_info.push(port_info);
      console.log(
        "Input port [type:'" +
          port_info.type +
          "'] id:'" +
          port_info.id +
          "' manufacturer:'" +
          port_info.manufacturer +
          "' name:'" +
          port_info.name +
          "' version:'" +
          port_info.version +
          "'",
      );
      num++;
      it_value = it.next();
    }
    this.num_input_ports = num;

    num = 0;
    var it = this.output_ports.values();
    var it_value = it.next();
    while (it_value && it_value.done === false) {
      var port_info = it_value.value;
      this.output_ports_info.push(port_info);
      console.log(
        "Output port [type:'" +
          port_info.type +
          "'] id:'" +
          port_info.id +
          "' manufacturer:'" +
          port_info.manufacturer +
          "' name:'" +
          port_info.name +
          "' version:'" +
          port_info.version +
          "'",
      );
      num++;
      it_value = it.next();
    }
    this.num_output_ports = num;
  };

  MIDIInterface.prototype.onMIDIFailure = function (msg) {
    console.error('Failed to get MIDI access - ' + msg);
  };

  MIDIInterface.prototype.openInputPort = function (port, callback) {
    var input_port = this.input_ports.get('input-' + port);
    if (!input_port) {
      return false;
    }
    MIDIInterface.input = this;
    var that = this;

    input_port.onmidimessage = function (a) {
      var midi_event = new MIDIEvent(a.data);
      that.updateState(midi_event);
      if (callback) {
        callback(a.data, midi_event);
      }
      if (MIDIInterface.on_message) {
        MIDIInterface.on_message(a.data, midi_event);
      }
    };
    console.log('port open: ', input_port);
    return true;
  };

  MIDIInterface.parseMsg = function (data) {};

  MIDIInterface.prototype.updateState = function (midi_event) {
    switch (midi_event.cmd) {
      case MIDIEvent.NOTEON:
        this.state.note[midi_event.value1 | 0] = midi_event.value2;
        break;
      case MIDIEvent.NOTEOFF:
        this.state.note[midi_event.value1 | 0] = 0;
        break;
      case MIDIEvent.CONTROLLERCHANGE:
        this.state.cc[midi_event.getCC()] = midi_event.getCCValue();
        break;
    }
  };

  MIDIInterface.prototype.sendMIDI = function (port, midi_data) {
    if (!midi_data) {
      return;
    }

    var output_port = this.output_ports_info[port]; //this.output_ports.get("output-" + port);
    if (!output_port) {
      return;
    }

    MIDIInterface.output = this;

    if (midi_data.constructor === MIDIEvent) {
      output_port.send(midi_data.data);
    } else {
      output_port.send(midi_data);
    }
  };

  function LGMIDIIn() {
    this.addOutput('on_midi', LiteGraph.EVENT);
    this.addOutput('out', 'midi');
    this.properties = { port: 0 };
    this._last_midi_event = null;
    this._current_midi_event = null;
    this.boxcolor = '#AAA';
    this._last_time = 0;

    var that = this;
    new MIDIInterface(function (midi) {
      //open
      that._midi = midi;
      if (that._waiting) {
        that.onStart();
      }
      that._waiting = false;
    });
  }

  LGMIDIIn.MIDIInterface = MIDIInterface;

  LGMIDIIn.title = 'MIDI Input';
  LGMIDIIn.desc = 'Reads MIDI from a input port';
  LGMIDIIn.color = MIDI_COLOR;

  LGMIDIIn.prototype.getPropertyInfo = function (name) {
    if (!this._midi) {
      return;
    }

    if (name == 'port') {
      var values = {};
      for (var i = 0; i < this._midi.input_ports_info.length; ++i) {
        var input = this._midi.input_ports_info[i];
        values[i] = i + '.- ' + input.name + ' version:' + input.version;
      }
      return { type: 'enum', values: values };
    }
  };

  LGMIDIIn.prototype.onStart = function () {
    if (this._midi) {
      this._midi.openInputPort(
        this.properties.port,
        this.onMIDIEvent.bind(this),
      );
    } else {
      this._waiting = true;
    }
  };

  LGMIDIIn.prototype.onMIDIEvent = function (data, midi_event) {
    this._last_midi_event = midi_event;
    this.boxcolor = '#AFA';
    this._last_time = LiteGraph.getTime();
    this.trigger('on_midi', midi_event);
    if (midi_event.cmd == MIDIEvent.NOTEON) {
      this.trigger('on_noteon', midi_event);
    } else if (midi_event.cmd == MIDIEvent.NOTEOFF) {
      this.trigger('on_noteoff', midi_event);
    } else if (midi_event.cmd == MIDIEvent.CONTROLLERCHANGE) {
      this.trigger('on_cc', midi_event);
    } else if (midi_event.cmd == MIDIEvent.PROGRAMCHANGE) {
      this.trigger('on_pc', midi_event);
    } else if (midi_event.cmd == MIDIEvent.PITCHBEND) {
      this.trigger('on_pitchbend', midi_event);
    }
  };

  LGMIDIIn.prototype.onDrawBackground = function (ctx) {
    this.boxcolor = '#AAA';
    if (!this.flags.collapsed && this._last_midi_event) {
      ctx.fillStyle = 'white';
      var now = LiteGraph.getTime();
      var f = 1.0 - Math.max(0, (now - this._last_time) * 0.001);
      if (f > 0) {
        var t = ctx.globalAlpha;
        ctx.globalAlpha *= f;
        ctx.font = '12px Tahoma';
        ctx.fillText(
          this._last_midi_event.toString(),
          2,
          this.size[1] * 0.5 + 3,
        );
        //ctx.fillRect(0,0,this.size[0],this.size[1]);
        ctx.globalAlpha = t;
      }
    }
  };

  LGMIDIIn.prototype.onExecute = function () {
    if (this.outputs) {
      var last = this._last_midi_event;
      for (var i = 0; i < this.outputs.length; ++i) {
        var output = this.outputs[i];
        var v = null;
        switch (output.name) {
          case 'midi':
            v = this._midi;
            break;
          case 'last_midi':
            v = last;
            break;
          default:
            continue;
        }
        this.setOutputData(i, v);
      }
    }
  };

  LGMIDIIn.prototype.onGetOutputs = function () {
    return [
      ['last_midi', 'midi'],
      ['on_midi', LiteGraph.EVENT],
      ['on_noteon', LiteGraph.EVENT],
      ['on_noteoff', LiteGraph.EVENT],
      ['on_cc', LiteGraph.EVENT],
      ['on_pc', LiteGraph.EVENT],
      ['on_pitchbend', LiteGraph.EVENT],
    ];
  };

  LiteGraph.registerNodeType('midi/input', LGMIDIIn);

  function LGMIDIOut() {
    this.addInput('send', LiteGraph.EVENT);
    this.properties = { port: 0 };

    var that = this;
    new MIDIInterface(function (midi) {
      that._midi = midi;
      that.widget.options.values = that.getMIDIOutputs();
    });
    this.widget = this.addWidget('combo', 'Device', this.properties.port, {
      property: 'port',
      values: this.getMIDIOutputs.bind(this),
    });
    this.size = [340, 60];
  }

  LGMIDIOut.MIDIInterface = MIDIInterface;

  LGMIDIOut.title = 'MIDI Output';
  LGMIDIOut.desc = 'Sends MIDI to output channel';
  LGMIDIOut.color = MIDI_COLOR;

  LGMIDIOut.prototype.onGetPropertyInfo = function (name) {
    if (!this._midi) {
      return;
    }

    if (name == 'port') {
      var values = this.getMIDIOutputs();
      return { type: 'enum', values: values };
    }
  };
  LGMIDIOut.default_ports = { 0: 'unknown' };

  LGMIDIOut.prototype.getMIDIOutputs = function () {
    var values = {};
    if (!this._midi) return LGMIDIOut.default_ports;
    if (this._midi.output_ports_info)
      for (var i = 0; i < this._midi.output_ports_info.length; ++i) {
        var output = this._midi.output_ports_info[i];
        if (!output) continue;
        var name = i + '.- ' + output.name + ' version:' + output.version;
        values[i] = name;
      }
    return values;
  };

  LGMIDIOut.prototype.onAction = function (event, midi_event) {
    //console.log(midi_event);
    if (!this._midi) {
      return;
    }
    if (event == 'send') {
      this._midi.sendMIDI(this.properties.port, midi_event);
    }
    this.trigger('midi', midi_event);
  };

  LGMIDIOut.prototype.onGetInputs = function () {
    return [['send', LiteGraph.ACTION]];
  };

  LGMIDIOut.prototype.onGetOutputs = function () {
    return [['on_midi', LiteGraph.EVENT]];
  };

  LiteGraph.registerNodeType('midi/output', LGMIDIOut);

  function LGMIDIShow() {
    this.addInput('on_midi', LiteGraph.EVENT);
    this._str = '';
    this.size = [200, 40];
  }

  LGMIDIShow.title = 'MIDI Show';
  LGMIDIShow.desc = 'Shows MIDI in the graph';
  LGMIDIShow.color = MIDI_COLOR;

  LGMIDIShow.prototype.getTitle = function () {
    if (this.flags.collapsed) {
      return this._str;
    }
    return this.title;
  };

  LGMIDIShow.prototype.onAction = function (event, midi_event) {
    if (!midi_event) {
      return;
    }
    if (midi_event.constructor === MIDIEvent) {
      this._str = midi_event.toString();
    } else {
      this._str = '???';
    }
  };

  LGMIDIShow.prototype.onDrawForeground = function (ctx) {
    if (!this._str || this.flags.collapsed) {
      return;
    }

    ctx.font = '30px Arial';
    ctx.fillText(this._str, 10, this.size[1] * 0.8);
  };

  LGMIDIShow.prototype.onGetInputs = function () {
    return [['in', LiteGraph.ACTION]];
  };

  LGMIDIShow.prototype.onGetOutputs = function () {
    return [['on_midi', LiteGraph.EVENT]];
  };

  LiteGraph.registerNodeType('midi/show', LGMIDIShow);

  function LGMIDIFilter() {
    this.properties = {
      channel: -1,
      cmd: -1,
      min_value: -1,
      max_value: -1,
    };

    var that = this;
    this._learning = false;
    this.addWidget('button', 'Learn', '', function () {
      that._learning = true;
      that.boxcolor = '#FA3';
    });

    this.addInput('in', LiteGraph.EVENT);
    this.addOutput('on_midi', LiteGraph.EVENT);
    this.boxcolor = '#AAA';
  }

  LGMIDIFilter.title = 'MIDI Filter';
  LGMIDIFilter.desc = 'Filters MIDI messages';
  LGMIDIFilter.color = MIDI_COLOR;

  LGMIDIFilter['@cmd'] = {
    type: 'enum',
    title: 'Command',
    values: MIDIEvent.commands_reversed,
  };

  LGMIDIFilter.prototype.getTitle = function () {
    var str = null;
    if (this.properties.cmd == -1) {
      str = 'Nothing';
    } else {
      str = MIDIEvent.commands_short[this.properties.cmd] || 'Unknown';
    }

    if (this.properties.min_value != -1 && this.properties.max_value != -1) {
      str +=
        ' ' +
        (this.properties.min_value == this.properties.max_value
          ? this.properties.max_value
          : this.properties.min_value + '..' + this.properties.max_value);
    }

    return 'Filter: ' + str;
  };

  LGMIDIFilter.prototype.onPropertyChanged = function (name, value) {
    if (name == 'cmd') {
      var num = Number(value);
      if (isNaN(num)) {
        num = MIDIEvent.commands[value] || 0;
      }
      this.properties.cmd = num;
    }
  };

  LGMIDIFilter.prototype.onAction = function (event, midi_event) {
    if (!midi_event || midi_event.constructor !== MIDIEvent) {
      return;
    }

    if (this._learning) {
      this._learning = false;
      this.boxcolor = '#AAA';
      this.properties.channel = midi_event.channel;
      this.properties.cmd = midi_event.cmd;
      this.properties.min_value = this.properties.max_value =
        midi_event.data[1];
    } else {
      if (
        this.properties.channel != -1 &&
        midi_event.channel != this.properties.channel
      ) {
        return;
      }
      if (this.properties.cmd != -1 && midi_event.cmd != this.properties.cmd) {
        return;
      }
      if (
        this.properties.min_value != -1 &&
        midi_event.data[1] < this.properties.min_value
      ) {
        return;
      }
      if (
        this.properties.max_value != -1 &&
        midi_event.data[1] > this.properties.max_value
      ) {
        return;
      }
    }

    this.trigger('on_midi', midi_event);
  };

  LiteGraph.registerNodeType('midi/filter', LGMIDIFilter);

  function LGMIDIEvent() {
    this.properties = {
      channel: 0,
      cmd: 144, //0x90
      value1: 1,
      value2: 1,
    };

    this.addInput('send', LiteGraph.EVENT);
    this.addInput('assign', LiteGraph.EVENT);
    this.addOutput('on_midi', LiteGraph.EVENT);

    this.midi_event = new MIDIEvent();
    this.gate = false;
  }

  LGMIDIEvent.title = 'MIDIEvent';
  LGMIDIEvent.desc = 'Create a MIDI Event';
  LGMIDIEvent.color = MIDI_COLOR;

  LGMIDIEvent.prototype.onAction = function (event, midi_event) {
    if (event == 'assign') {
      this.properties.channel = midi_event.channel;
      this.properties.cmd = midi_event.cmd;
      this.properties.value1 = midi_event.data[1];
      this.properties.value2 = midi_event.data[2];
      if (midi_event.cmd == MIDIEvent.NOTEON) {
        this.gate = true;
      } else if (midi_event.cmd == MIDIEvent.NOTEOFF) {
        this.gate = false;
      }
      return;
    }

    //send
    var midi_event = this.midi_event;
    midi_event.channel = this.properties.channel;
    if (this.properties.cmd && this.properties.cmd.constructor === String) {
      midi_event.setCommandFromString(this.properties.cmd);
    } else {
      midi_event.cmd = this.properties.cmd;
    }
    midi_event.data[0] = midi_event.cmd | midi_event.channel;
    midi_event.data[1] = Number(this.properties.value1);
    midi_event.data[2] = Number(this.properties.value2);

    this.trigger('on_midi', midi_event);
  };

  LGMIDIEvent.prototype.onExecute = function () {
    var props = this.properties;

    if (this.inputs) {
      for (var i = 0; i < this.inputs.length; ++i) {
        var input = this.inputs[i];
        if (input.link == -1) {
          continue;
        }
        switch (input.name) {
          case 'note':
            var v = this.getInputData(i);
            if (v != null) {
              if (v.constructor === String) {
                v = MIDIEvent.NoteStringToPitch(v);
              }
              this.properties.value1 = (v | 0) % 255;
            }
            break;
          case 'cmd':
            var v = this.getInputData(i);
            if (v != null) {
              this.properties.cmd = v;
            }
            break;
          case 'value1':
            var v = this.getInputData(i);
            if (v != null) {
              this.properties.value1 = clamp(v | 0, 0, 127);
            }
            break;
          case 'value2':
            var v = this.getInputData(i);
            if (v != null) {
              this.properties.value2 = clamp(v | 0, 0, 127);
            }
            break;
        }
      }
    }

    if (this.outputs) {
      for (var i = 0; i < this.outputs.length; ++i) {
        var output = this.outputs[i];
        var v = null;
        switch (output.name) {
          case 'midi':
            v = new MIDIEvent();
            v.setup([props.cmd, props.value1, props.value2]);
            v.channel = props.channel;
            break;
          case 'command':
            v = props.cmd;
            break;
          case 'cc':
            v = props.value1;
            break;
          case 'cc_value':
            v = props.value2;
            break;
          case 'note':
            v =
              props.cmd == MIDIEvent.NOTEON || props.cmd == MIDIEvent.NOTEOFF
                ? props.value1
                : null;
            break;
          case 'velocity':
            v = props.cmd == MIDIEvent.NOTEON ? props.value2 : null;
            break;
          case 'pitch':
            v =
              props.cmd == MIDIEvent.NOTEON
                ? MIDIEvent.computePitch(props.value1)
                : null;
            break;
          case 'pitchbend':
            v =
              props.cmd == MIDIEvent.PITCHBEND
                ? MIDIEvent.computePitchBend(props.value1, props.value2)
                : null;
            break;
          case 'gate':
            v = this.gate;
            break;
          default:
            continue;
        }
        if (v !== null) {
          this.setOutputData(i, v);
        }
      }
    }
  };

  LGMIDIEvent.prototype.onPropertyChanged = function (name, value) {
    if (name == 'cmd') {
      this.properties.cmd = MIDIEvent.computeCommandFromString(value);
    }
  };

  LGMIDIEvent.prototype.onGetInputs = function () {
    return [
      ['cmd', 'number'],
      ['note', 'number'],
      ['value1', 'number'],
      ['value2', 'number'],
    ];
  };

  LGMIDIEvent.prototype.onGetOutputs = function () {
    return [
      ['midi', 'midi'],
      ['on_midi', LiteGraph.EVENT],
      ['command', 'number'],
      ['note', 'number'],
      ['velocity', 'number'],
      ['cc', 'number'],
      ['cc_value', 'number'],
      ['pitch', 'number'],
      ['gate', 'bool'],
      ['pitchbend', 'number'],
    ];
  };

  LiteGraph.registerNodeType('midi/event', LGMIDIEvent);

  function LGMIDICC() {
    this.properties = {
      //		channel: 0,
      cc: 1,
      value: 0,
    };

    this.addOutput('value', 'number');
  }

  LGMIDICC.title = 'MIDICC';
  LGMIDICC.desc = 'gets a Controller Change';
  LGMIDICC.color = MIDI_COLOR;

  LGMIDICC.prototype.onExecute = function () {
    var props = this.properties;
    if (MIDIInterface.input) {
      this.properties.value = MIDIInterface.input.state.cc[this.properties.cc];
    }
    this.setOutputData(0, this.properties.value);
  };

  LiteGraph.registerNodeType('midi/cc', LGMIDICC);

  function LGMIDIGenerator() {
    this.addInput('generate', LiteGraph.ACTION);
    this.addInput('scale', 'string');
    this.addInput('octave', 'number');
    this.addOutput('note', LiteGraph.EVENT);
    this.properties = {
      notes: 'A,A#,B,C,C#,D,D#,E,F,F#,G,G#',
      octave: 2,
      duration: 0.5,
      mode: 'sequence',
    };

    this.notes_pitches = LGMIDIGenerator.processScale(this.properties.notes);
    this.sequence_index = 0;
  }

  LGMIDIGenerator.title = 'MIDI Generator';
  LGMIDIGenerator.desc = 'Generates a random MIDI note';
  LGMIDIGenerator.color = MIDI_COLOR;

  LGMIDIGenerator.processScale = function (scale) {
    var notes = scale.split(',');
    for (var i = 0; i < notes.length; ++i) {
      var n = notes[i];
      if ((n.length == 2 && n[1] != '#') || n.length > 2) {
        notes[i] = -LiteGraph.MIDIEvent.NoteStringToPitch(n);
      } else {
        notes[i] = MIDIEvent.note_to_index[n] || 0;
      }
    }
    return notes;
  };

  LGMIDIGenerator.prototype.onPropertyChanged = function (name, value) {
    if (name == 'notes') {
      this.notes_pitches = LGMIDIGenerator.processScale(value);
    }
  };

  LGMIDIGenerator.prototype.onExecute = function () {
    var octave = this.getInputData(2);
    if (octave != null) {
      this.properties.octave = octave;
    }

    var scale = this.getInputData(1);
    if (scale) {
      this.notes_pitches = LGMIDIGenerator.processScale(scale);
    }
  };

  LGMIDIGenerator.prototype.onAction = function (event, midi_event) {
    //var range = this.properties.max - this.properties.min;
    //var pitch = this.properties.min + ((Math.random() * range)|0);
    var pitch = 0;
    var range = this.notes_pitches.length;
    var index = 0;

    if (this.properties.mode == 'sequence') {
      index = this.sequence_index = (this.sequence_index + 1) % range;
    } else if (this.properties.mode == 'random') {
      index = Math.floor(Math.random() * range);
    }

    var note = this.notes_pitches[index];
    if (note >= 0) {
      pitch = note + (this.properties.octave - 1) * 12 + 33;
    } else {
      pitch = -note;
    }

    var midi_event = new MIDIEvent();
    midi_event.setup([MIDIEvent.NOTEON, pitch, 10]);
    var duration = this.properties.duration || 1;
    this.trigger('note', midi_event);

    //noteoff
    setTimeout(
      function () {
        var midi_event = new MIDIEvent();
        midi_event.setup([MIDIEvent.NOTEOFF, pitch, 0]);
        this.trigger('note', midi_event);
      }.bind(this),
      duration * 1000,
    );
  };

  LiteGraph.registerNodeType('midi/generator', LGMIDIGenerator);

  function LGMIDITranspose() {
    this.properties = {
      amount: 0,
    };
    this.addInput('in', LiteGraph.ACTION);
    this.addInput('amount', 'number');
    this.addOutput('out', LiteGraph.EVENT);

    this.midi_event = new MIDIEvent();
  }

  LGMIDITranspose.title = 'MIDI Transpose';
  LGMIDITranspose.desc = 'Transpose a MIDI note';
  LGMIDITranspose.color = MIDI_COLOR;

  LGMIDITranspose.prototype.onAction = function (event, midi_event) {
    if (!midi_event || midi_event.constructor !== MIDIEvent) {
      return;
    }

    if (
      midi_event.data[0] == MIDIEvent.NOTEON ||
      midi_event.data[0] == MIDIEvent.NOTEOFF
    ) {
      this.midi_event = new MIDIEvent();
      this.midi_event.setup(midi_event.data);
      this.midi_event.data[1] = Math.round(
        this.midi_event.data[1] + this.properties.amount,
      );
      this.trigger('out', this.midi_event);
    } else {
      this.trigger('out', midi_event);
    }
  };

  LGMIDITranspose.prototype.onExecute = function () {
    var amount = this.getInputData(1);
    if (amount != null) {
      this.properties.amount = amount;
    }
  };

  LiteGraph.registerNodeType('midi/transpose', LGMIDITranspose);

  function LGMIDIQuantize() {
    this.properties = {
      scale: 'A,A#,B,C,C#,D,D#,E,F,F#,G,G#',
    };
    this.addInput('note', LiteGraph.ACTION);
    this.addInput('scale', 'string');
    this.addOutput('out', LiteGraph.EVENT);

    this.valid_notes = new Array(12);
    this.offset_notes = new Array(12);
    this.processScale(this.properties.scale);
  }

  LGMIDIQuantize.title = 'MIDI Quantize Pitch';
  LGMIDIQuantize.desc = 'Transpose a MIDI note tp fit an scale';
  LGMIDIQuantize.color = MIDI_COLOR;

  LGMIDIQuantize.prototype.onPropertyChanged = function (name, value) {
    if (name == 'scale') {
      this.processScale(value);
    }
  };

  LGMIDIQuantize.prototype.processScale = function (scale) {
    this._current_scale = scale;
    this.notes_pitches = LGMIDIGenerator.processScale(scale);
    for (var i = 0; i < 12; ++i) {
      this.valid_notes[i] = this.notes_pitches.indexOf(i) != -1;
    }
    for (var i = 0; i < 12; ++i) {
      if (this.valid_notes[i]) {
        this.offset_notes[i] = 0;
        continue;
      }
      for (var j = 1; j < 12; ++j) {
        if (this.valid_notes[(i - j) % 12]) {
          this.offset_notes[i] = -j;
          break;
        }
        if (this.valid_notes[(i + j) % 12]) {
          this.offset_notes[i] = j;
          break;
        }
      }
    }
  };

  LGMIDIQuantize.prototype.onAction = function (event, midi_event) {
    if (!midi_event || midi_event.constructor !== MIDIEvent) {
      return;
    }

    if (
      midi_event.data[0] == MIDIEvent.NOTEON ||
      midi_event.data[0] == MIDIEvent.NOTEOFF
    ) {
      this.midi_event = new MIDIEvent();
      this.midi_event.setup(midi_event.data);
      var note = midi_event.note;
      var index = MIDIEvent.note_to_index[note];
      var offset = this.offset_notes[index];
      this.midi_event.data[1] += offset;
      this.trigger('out', this.midi_event);
    } else {
      this.trigger('out', midi_event);
    }
  };

  LGMIDIQuantize.prototype.onExecute = function () {
    var scale = this.getInputData(1);
    if (scale != null && scale != this._current_scale) {
      this.processScale(scale);
    }
  };

  LiteGraph.registerNodeType('midi/quantize', LGMIDIQuantize);

  function LGMIDIFromFile() {
    this.properties = {
      url: '',
      autoplay: true,
    };

    this.addInput('play', LiteGraph.ACTION);
    this.addInput('pause', LiteGraph.ACTION);
    this.addOutput('note', LiteGraph.EVENT);
    this._midi = null;
    this._current_time = 0;
    this._playing = false;

    if (typeof MidiParser == 'undefined') {
      console.error(
        'midi-parser.js not included, LGMidiPlay requires that library: https://raw.githubusercontent.com/colxi/midi-parser-js/master/src/main.js',
      );
      this.boxcolor = 'red';
    }
  }

  LGMIDIFromFile.title = 'MIDI fromFile';
  LGMIDIFromFile.desc = 'Plays a MIDI file';
  LGMIDIFromFile.color = MIDI_COLOR;

  LGMIDIFromFile.prototype.onAction = function (name) {
    if (name == 'play') this.play();
    else if (name == 'pause') this._playing = !this._playing;
  };

  LGMIDIFromFile.prototype.onPropertyChanged = function (name, value) {
    if (name == 'url') this.loadMIDIFile(value);
  };

  LGMIDIFromFile.prototype.onExecute = function () {
    if (!this._midi) return;

    if (!this._playing) return;

    this._current_time += this.graph.elapsed_time;
    var current_time = this._current_time * 100;

    for (var i = 0; i < this._midi.tracks; ++i) {
      var track = this._midi.track[i];
      if (!track._last_pos) {
        track._last_pos = 0;
        track._time = 0;
      }

      var elem = track.event[track._last_pos];
      if (elem && track._time + elem.deltaTime <= current_time) {
        track._last_pos++;
        track._time += elem.deltaTime;

        if (elem.data) {
          var midi_cmd = elem.type << (4 + elem.channel);
          var midi_event = new MIDIEvent();
          midi_event.setup([midi_cmd, elem.data[0], elem.data[1]]);
          this.trigger('note', midi_event);
        }
      }
    }
  };

  LGMIDIFromFile.prototype.play = function () {
    this._playing = true;
    this._current_time = 0;
    if (!this._midi) return;

    for (var i = 0; i < this._midi.tracks; ++i) {
      var track = this._midi.track[i];
      track._last_pos = 0;
      track._time = 0;
    }
  };

  LGMIDIFromFile.prototype.loadMIDIFile = function (url) {
    var that = this;
    LiteGraph.fetchFile(
      url,
      'arraybuffer',
      function (data) {
        that.boxcolor = '#AFA';
        that._midi = MidiParser.parse(new Uint8Array(data));
        if (that.properties.autoplay) that.play();
      },
      function (err) {
        that.boxcolor = '#FAA';
        that._midi = null;
      },
    );
  };

  LGMIDIFromFile.prototype.onDropFile = function (file) {
    this.properties.url = '';
    this.loadMIDIFile(file);
  };

  LiteGraph.registerNodeType('midi/fromFile', LGMIDIFromFile);

  function LGMIDIPlay() {
    this.properties = {
      volume: 0.5,
      duration: 1,
    };
    this.addInput('note', LiteGraph.ACTION);
    this.addInput('volume', 'number');
    this.addInput('duration', 'number');
    this.addOutput('note', LiteGraph.EVENT);

    if (typeof AudioSynth == 'undefined') {
      console.error(
        'Audiosynth.js not included, LGMidiPlay requires that library',
      );
      this.boxcolor = 'red';
    } else {
      var Synth = (this.synth = new AudioSynth());
      this.instrument = Synth.createInstrument('piano');
    }
  }

  LGMIDIPlay.title = 'MIDI Play';
  LGMIDIPlay.desc = 'Plays a MIDI note';
  LGMIDIPlay.color = MIDI_COLOR;

  LGMIDIPlay.prototype.onAction = function (event, midi_event) {
    if (!midi_event || midi_event.constructor !== MIDIEvent) {
      return;
    }

    if (this.instrument && midi_event.data[0] == MIDIEvent.NOTEON) {
      var note = midi_event.note; //C#
      if (!note || note == 'undefined' || note.constructor !== String) {
        return;
      }
      this.instrument.play(
        note,
        midi_event.octave,
        this.properties.duration,
        this.properties.volume,
      );
    }
    this.trigger('note', midi_event);
  };

  LGMIDIPlay.prototype.onExecute = function () {
    var volume = this.getInputData(1);
    if (volume != null) {
      this.properties.volume = volume;
    }

    var duration = this.getInputData(2);
    if (duration != null) {
      this.properties.duration = duration;
    }
  };

  LiteGraph.registerNodeType('midi/play', LGMIDIPlay);

  function LGMIDIKeys() {
    this.properties = {
      num_octaves: 2,
      start_octave: 2,
    };
    this.addInput('note', LiteGraph.ACTION);
    this.addInput('reset', LiteGraph.ACTION);
    this.addOutput('note', LiteGraph.EVENT);
    this.size = [400, 100];
    this.keys = [];
    this._last_key = -1;
  }

  LGMIDIKeys.title = 'MIDI Keys';
  LGMIDIKeys.desc = 'Keyboard to play notes';
  LGMIDIKeys.color = MIDI_COLOR;

  LGMIDIKeys.keys = [
    { x: 0, w: 1, h: 1, t: 0 },
    { x: 0.75, w: 0.5, h: 0.6, t: 1 },
    { x: 1, w: 1, h: 1, t: 0 },
    { x: 1.75, w: 0.5, h: 0.6, t: 1 },
    { x: 2, w: 1, h: 1, t: 0 },
    { x: 2.75, w: 0.5, h: 0.6, t: 1 },
    { x: 3, w: 1, h: 1, t: 0 },
    { x: 4, w: 1, h: 1, t: 0 },
    { x: 4.75, w: 0.5, h: 0.6, t: 1 },
    { x: 5, w: 1, h: 1, t: 0 },
    { x: 5.75, w: 0.5, h: 0.6, t: 1 },
    { x: 6, w: 1, h: 1, t: 0 },
  ];

  LGMIDIKeys.prototype.onDrawForeground = function (ctx) {
    if (this.flags.collapsed) {
      return;
    }

    var num_keys = this.properties.num_octaves * 12;
    this.keys.length = num_keys;
    var key_width = this.size[0] / (this.properties.num_octaves * 7);
    var key_height = this.size[1];

    ctx.globalAlpha = 1;

    for (
      var k = 0;
      k < 2;
      k++ //draw first whites (0) then blacks (1)
    ) {
      for (var i = 0; i < num_keys; ++i) {
        var key_info = LGMIDIKeys.keys[i % 12];
        if (key_info.t != k) {
          continue;
        }
        var octave = Math.floor(i / 12);
        var x = octave * 7 * key_width + key_info.x * key_width;
        if (k == 0) {
          ctx.fillStyle = this.keys[i] ? '#CCC' : 'white';
        } else {
          ctx.fillStyle = this.keys[i] ? '#333' : 'black';
        }
        ctx.fillRect(
          x + 1,
          0,
          key_width * key_info.w - 2,
          key_height * key_info.h,
        );
      }
    }
  };

  LGMIDIKeys.prototype.getKeyIndex = function (pos) {
    var num_keys = this.properties.num_octaves * 12;
    var key_width = this.size[0] / (this.properties.num_octaves * 7);
    var key_height = this.size[1];

    for (
      var k = 1;
      k >= 0;
      k-- //test blacks first (1) then whites (0)
    ) {
      for (var i = 0; i < this.keys.length; ++i) {
        var key_info = LGMIDIKeys.keys[i % 12];
        if (key_info.t != k) {
          continue;
        }
        var octave = Math.floor(i / 12);
        var x = octave * 7 * key_width + key_info.x * key_width;
        var w = key_width * key_info.w;
        var h = key_height * key_info.h;
        if (pos[0] < x || pos[0] > x + w || pos[1] > h) {
          continue;
        }
        return i;
      }
    }
    return -1;
  };

  LGMIDIKeys.prototype.onAction = function (event, params) {
    if (event == 'reset') {
      for (var i = 0; i < this.keys.length; ++i) {
        this.keys[i] = false;
      }
      return;
    }

    if (!params || params.constructor !== MIDIEvent) {
      return;
    }
    var midi_event = params;
    var start_note = (this.properties.start_octave - 1) * 12 + 29;
    var index = midi_event.data[1] - start_note;
    if (index >= 0 && index < this.keys.length) {
      if (midi_event.data[0] == MIDIEvent.NOTEON) {
        this.keys[index] = true;
      } else if (midi_event.data[0] == MIDIEvent.NOTEOFF) {
        this.keys[index] = false;
      }
    }

    this.trigger('note', midi_event);
  };

  LGMIDIKeys.prototype.onMouseDown = function (e, pos) {
    if (pos[1] < 0) {
      return;
    }
    var index = this.getKeyIndex(pos);
    this.keys[index] = true;
    this._last_key = index;
    var pitch = (this.properties.start_octave - 1) * 12 + 29 + index;
    var midi_event = new MIDIEvent();
    midi_event.setup([MIDIEvent.NOTEON, pitch, 100]);
    this.trigger('note', midi_event);
    return true;
  };

  LGMIDIKeys.prototype.onMouseMove = function (e, pos) {
    if (pos[1] < 0 || this._last_key == -1) {
      return;
    }
    this.setDirtyCanvas(true);
    var index = this.getKeyIndex(pos);
    if (this._last_key == index) {
      return true;
    }
    this.keys[this._last_key] = false;
    var pitch = (this.properties.start_octave - 1) * 12 + 29 + this._last_key;
    var midi_event = new MIDIEvent();
    midi_event.setup([MIDIEvent.NOTEOFF, pitch, 100]);
    this.trigger('note', midi_event);

    this.keys[index] = true;
    var pitch = (this.properties.start_octave - 1) * 12 + 29 + index;
    var midi_event = new MIDIEvent();
    midi_event.setup([MIDIEvent.NOTEON, pitch, 100]);
    this.trigger('note', midi_event);

    this._last_key = index;
    return true;
  };

  LGMIDIKeys.prototype.onMouseUp = function (e, pos) {
    if (pos[1] < 0) {
      return;
    }
    var index = this.getKeyIndex(pos);
    this.keys[index] = false;
    this._last_key = -1;
    var pitch = (this.properties.start_octave - 1) * 12 + 29 + index;
    var midi_event = new MIDIEvent();
    midi_event.setup([MIDIEvent.NOTEOFF, pitch, 100]);
    this.trigger('note', midi_event);
    return true;
  };

  LiteGraph.registerNodeType('midi/keys', LGMIDIKeys);

  function now() {
    return window.performance.now();
  }
})(this);

(function (global) {
  var LiteGraph = global.LiteGraph;

  var LGAudio = {};
  global.LGAudio = LGAudio;

  LGAudio.getAudioContext = function () {
    if (!this._audio_context) {
      window.AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!window.AudioContext) {
        console.error('AudioContext not supported by browser');
        return null;
      }
      this._audio_context = new AudioContext();
      this._audio_context.onmessage = function (msg) {
        console.log('msg', msg);
      };
      this._audio_context.onended = function (msg) {
        console.log('ended', msg);
      };
      this._audio_context.oncomplete = function (msg) {
        console.log('complete', msg);
      };
    }

    //in case it crashes
    //if(this._audio_context.state == "suspended")
    //	this._audio_context.resume();
    return this._audio_context;
  };

  LGAudio.connect = function (audionodeA, audionodeB) {
    try {
      audionodeA.connect(audionodeB);
    } catch (err) {
      console.warn('LGraphAudio:', err);
    }
  };

  LGAudio.disconnect = function (audionodeA, audionodeB) {
    try {
      audionodeA.disconnect(audionodeB);
    } catch (err) {
      console.warn('LGraphAudio:', err);
    }
  };

  LGAudio.changeAllAudiosConnections = function (node, connect) {
    if (node.inputs) {
      for (var i = 0; i < node.inputs.length; ++i) {
        var input = node.inputs[i];
        var link_info = node.graph.links[input.link];
        if (!link_info) {
          continue;
        }

        var origin_node = node.graph.getNodeById(link_info.origin_id);
        var origin_audionode = null;
        if (origin_node.getAudioNodeInOutputSlot) {
          origin_audionode = origin_node.getAudioNodeInOutputSlot(
            link_info.origin_slot,
          );
        } else {
          origin_audionode = origin_node.audionode;
        }

        var target_audionode = null;
        if (node.getAudioNodeInInputSlot) {
          target_audionode = node.getAudioNodeInInputSlot(i);
        } else {
          target_audionode = node.audionode;
        }

        if (connect) {
          LGAudio.connect(origin_audionode, target_audionode);
        } else {
          LGAudio.disconnect(origin_audionode, target_audionode);
        }
      }
    }

    if (node.outputs) {
      for (var i = 0; i < node.outputs.length; ++i) {
        var output = node.outputs[i];
        for (var j = 0; j < output.links.length; ++j) {
          var link_info = node.graph.links[output.links[j]];
          if (!link_info) {
            continue;
          }

          var origin_audionode = null;
          if (node.getAudioNodeInOutputSlot) {
            origin_audionode = node.getAudioNodeInOutputSlot(i);
          } else {
            origin_audionode = node.audionode;
          }

          var target_node = node.graph.getNodeById(link_info.target_id);
          var target_audionode = null;
          if (target_node.getAudioNodeInInputSlot) {
            target_audionode = target_node.getAudioNodeInInputSlot(
              link_info.target_slot,
            );
          } else {
            target_audionode = target_node.audionode;
          }

          if (connect) {
            LGAudio.connect(origin_audionode, target_audionode);
          } else {
            LGAudio.disconnect(origin_audionode, target_audionode);
          }
        }
      }
    }
  };

  //used by many nodes
  LGAudio.onConnectionsChange = function (
    connection,
    slot,
    connected,
    link_info,
  ) {
    //only process the outputs events
    if (connection != LiteGraph.OUTPUT) {
      return;
    }

    var target_node = null;
    if (link_info) {
      target_node = this.graph.getNodeById(link_info.target_id);
    }

    if (!target_node) {
      return;
    }

    //get origin audionode
    var local_audionode = null;
    if (this.getAudioNodeInOutputSlot) {
      local_audionode = this.getAudioNodeInOutputSlot(slot);
    } else {
      local_audionode = this.audionode;
    }

    //get target audionode
    var target_audionode = null;
    if (target_node.getAudioNodeInInputSlot) {
      target_audionode = target_node.getAudioNodeInInputSlot(
        link_info.target_slot,
      );
    } else {
      target_audionode = target_node.audionode;
    }

    //do the connection/disconnection
    if (connected) {
      LGAudio.connect(local_audionode, target_audionode);
    } else {
      LGAudio.disconnect(local_audionode, target_audionode);
    }
  };

  //this function helps creating wrappers to existing classes
  LGAudio.createAudioNodeWrapper = function (class_object) {
    var old_func = class_object.prototype.onPropertyChanged;

    class_object.prototype.onPropertyChanged = function (name, value) {
      if (old_func) {
        old_func.call(this, name, value);
      }

      if (!this.audionode) {
        return;
      }

      if (this.audionode[name] === undefined) {
        return;
      }

      if (this.audionode[name].value !== undefined) {
        this.audionode[name].value = value;
      } else {
        this.audionode[name] = value;
      }
    };

    class_object.prototype.onConnectionsChange = LGAudio.onConnectionsChange;
  };

  //contains the samples decoded of the loaded audios in AudioBuffer format
  LGAudio.cached_audios = {};

  LGAudio.loadSound = function (url, on_complete, on_error) {
    if (LGAudio.cached_audios[url] && url.indexOf('blob:') == -1) {
      if (on_complete) {
        on_complete(LGAudio.cached_audios[url]);
      }
      return;
    }

    if (LGAudio.onProcessAudioURL) {
      url = LGAudio.onProcessAudioURL(url);
    }

    //load new sample
    var request = new XMLHttpRequest();
    request.open('GET', url, true);
    request.responseType = 'arraybuffer';

    var context = LGAudio.getAudioContext();

    // Decode asynchronously
    request.onload = function () {
      console.log('AudioSource loaded');
      context.decodeAudioData(
        request.response,
        function (buffer) {
          console.log('AudioSource decoded');
          LGAudio.cached_audios[url] = buffer;
          if (on_complete) {
            on_complete(buffer);
          }
        },
        onError,
      );
    };
    request.send();

    function onError(err) {
      console.log('Audio loading sample error:', err);
      if (on_error) {
        on_error(err);
      }
    }

    return request;
  };

  //****************************************************

  function LGAudioSource() {
    this.properties = {
      src: '',
      gain: 0.5,
      loop: true,
      autoplay: true,
      playbackRate: 1,
    };

    this._loading_audio = false;
    this._audiobuffer = null; //points to AudioBuffer with the audio samples decoded
    this._audionodes = [];
    this._last_sourcenode = null; //the last AudioBufferSourceNode (there could be more if there are several sounds playing)

    this.addOutput('out', 'audio');
    this.addInput('gain', 'number');

    //init context
    var context = LGAudio.getAudioContext();

    //create gain node to control volume
    this.audionode = context.createGain();
    this.audionode.graphnode = this;
    this.audionode.gain.value = this.properties.gain;

    //debug
    if (this.properties.src) {
      this.loadSound(this.properties.src);
    }
  }

  LGAudioSource.desc = 'Plays an audio file';
  LGAudioSource['@src'] = { widget: 'resource' };
  LGAudioSource.supported_extensions = ['wav', 'ogg', 'mp3'];

  LGAudioSource.prototype.onAdded = function (graph) {
    if (graph.status === LGraph.STATUS_RUNNING) {
      this.onStart();
    }
  };

  LGAudioSource.prototype.onStart = function () {
    if (!this._audiobuffer) {
      return;
    }

    if (this.properties.autoplay) {
      this.playBuffer(this._audiobuffer);
    }
  };

  LGAudioSource.prototype.onStop = function () {
    this.stopAllSounds();
  };

  LGAudioSource.prototype.onPause = function () {
    this.pauseAllSounds();
  };

  LGAudioSource.prototype.onUnpause = function () {
    this.unpauseAllSounds();
    //this.onStart();
  };

  LGAudioSource.prototype.onRemoved = function () {
    this.stopAllSounds();
    if (this._dropped_url) {
      URL.revokeObjectURL(this._url);
    }
  };

  LGAudioSource.prototype.stopAllSounds = function () {
    //iterate and stop
    for (var i = 0; i < this._audionodes.length; ++i) {
      if (this._audionodes[i].started) {
        this._audionodes[i].started = false;
        this._audionodes[i].stop();
      }
      //this._audionodes[i].disconnect( this.audionode );
    }
    this._audionodes.length = 0;
  };

  LGAudioSource.prototype.pauseAllSounds = function () {
    LGAudio.getAudioContext().suspend();
  };

  LGAudioSource.prototype.unpauseAllSounds = function () {
    LGAudio.getAudioContext().resume();
  };

  LGAudioSource.prototype.onExecute = function () {
    if (this.inputs) {
      for (var i = 0; i < this.inputs.length; ++i) {
        var input = this.inputs[i];
        if (input.link == null) {
          continue;
        }
        var v = this.getInputData(i);
        if (v === undefined) {
          continue;
        }
        if (input.name == 'gain') this.audionode.gain.value = v;
        else if (input.name == 'src') {
          this.setProperty('src', v);
        } else if (input.name == 'playbackRate') {
          this.properties.playbackRate = v;
          for (var j = 0; j < this._audionodes.length; ++j) {
            this._audionodes[j].playbackRate.value = v;
          }
        }
      }
    }

    if (this.outputs) {
      for (var i = 0; i < this.outputs.length; ++i) {
        var output = this.outputs[i];
        if (output.name == 'buffer' && this._audiobuffer) {
          this.setOutputData(i, this._audiobuffer);
        }
      }
    }
  };

  LGAudioSource.prototype.onAction = function (event) {
    if (this._audiobuffer) {
      if (event == 'Play') {
        this.playBuffer(this._audiobuffer);
      } else if (event == 'Stop') {
        this.stopAllSounds();
      }
    }
  };

  LGAudioSource.prototype.onPropertyChanged = function (name, value) {
    if (name == 'src') {
      this.loadSound(value);
    } else if (name == 'gain') {
      this.audionode.gain.value = value;
    } else if (name == 'playbackRate') {
      for (var j = 0; j < this._audionodes.length; ++j) {
        this._audionodes[j].playbackRate.value = value;
      }
    }
  };

  LGAudioSource.prototype.playBuffer = function (buffer) {
    var that = this;
    var context = LGAudio.getAudioContext();

    //create a new audionode (this is mandatory, AudioAPI doesnt like to reuse old ones)
    var audionode = context.createBufferSource(); //create a AudioBufferSourceNode
    this._last_sourcenode = audionode;
    audionode.graphnode = this;
    audionode.buffer = buffer;
    audionode.loop = this.properties.loop;
    audionode.playbackRate.value = this.properties.playbackRate;
    this._audionodes.push(audionode);
    audionode.connect(this.audionode); //connect to gain

    this._audionodes.push(audionode);

    this.trigger('start');

    audionode.onended = function () {
      //console.log("ended!");
      that.trigger('ended');
      //remove
      var index = that._audionodes.indexOf(audionode);
      if (index != -1) {
        that._audionodes.splice(index, 1);
      }
    };

    if (!audionode.started) {
      audionode.started = true;
      audionode.start();
    }
    return audionode;
  };

  LGAudioSource.prototype.loadSound = function (url) {
    var that = this;

    //kill previous load
    if (this._request) {
      this._request.abort();
      this._request = null;
    }

    this._audiobuffer = null; //points to the audiobuffer once the audio is loaded
    this._loading_audio = false;

    if (!url) {
      return;
    }

    this._request = LGAudio.loadSound(url, inner);

    this._loading_audio = true;
    this.boxcolor = '#AA4';

    function inner(buffer) {
      this.boxcolor = LiteGraph.NODE_DEFAULT_BOXCOLOR;
      that._audiobuffer = buffer;
      that._loading_audio = false;
      //if is playing, then play it
      if (that.graph && that.graph.status === LGraph.STATUS_RUNNING) {
        that.onStart();
      } //this controls the autoplay already
    }
  };

  //Helps connect/disconnect AudioNodes when new connections are made in the node
  LGAudioSource.prototype.onConnectionsChange = LGAudio.onConnectionsChange;

  LGAudioSource.prototype.onGetInputs = function () {
    return [
      ['playbackRate', 'number'],
      ['src', 'string'],
      ['Play', LiteGraph.ACTION],
      ['Stop', LiteGraph.ACTION],
    ];
  };

  LGAudioSource.prototype.onGetOutputs = function () {
    return [
      ['buffer', 'audiobuffer'],
      ['start', LiteGraph.EVENT],
      ['ended', LiteGraph.EVENT],
    ];
  };

  LGAudioSource.prototype.onDropFile = function (file) {
    if (this._dropped_url) {
      URL.revokeObjectURL(this._dropped_url);
    }
    var url = URL.createObjectURL(file);
    this.properties.src = url;
    this.loadSound(url);
    this._dropped_url = url;
  };

  LGAudioSource.title = 'Source';
  LGAudioSource.desc = 'Plays audio';
  LiteGraph.registerNodeType('audio/source', LGAudioSource);

  //****************************************************

  function LGAudioMediaSource() {
    this.properties = {
      gain: 0.5,
    };

    this._audionodes = [];
    this._media_stream = null;

    this.addOutput('out', 'audio');
    this.addInput('gain', 'number');

    //create gain node to control volume
    var context = LGAudio.getAudioContext();
    this.audionode = context.createGain();
    this.audionode.graphnode = this;
    this.audionode.gain.value = this.properties.gain;
  }

  LGAudioMediaSource.prototype.onAdded = function (graph) {
    if (graph.status === LGraph.STATUS_RUNNING) {
      this.onStart();
    }
  };

  LGAudioMediaSource.prototype.onStart = function () {
    if (this._media_stream == null && !this._waiting_confirmation) {
      this.openStream();
    }
  };

  LGAudioMediaSource.prototype.onStop = function () {
    this.audionode.gain.value = 0;
  };

  LGAudioMediaSource.prototype.onPause = function () {
    this.audionode.gain.value = 0;
  };

  LGAudioMediaSource.prototype.onUnpause = function () {
    this.audionode.gain.value = this.properties.gain;
  };

  LGAudioMediaSource.prototype.onRemoved = function () {
    this.audionode.gain.value = 0;
    if (this.audiosource_node) {
      this.audiosource_node.disconnect(this.audionode);
      this.audiosource_node = null;
    }
    if (this._media_stream) {
      var tracks = this._media_stream.getTracks();
      if (tracks.length) {
        tracks[0].stop();
      }
    }
  };

  LGAudioMediaSource.prototype.openStream = function () {
    if (!navigator.mediaDevices) {
      console.log(
        'getUserMedia() is not supported in your browser, use chrome and enable WebRTC from about://flags',
      );
      return;
    }

    this._waiting_confirmation = true;

    // Not showing vendor prefixes.
    navigator.mediaDevices
      .getUserMedia({ audio: true, video: false })
      .then(this.streamReady.bind(this))
      .catch(onFailSoHard);

    var that = this;
    function onFailSoHard(err) {
      console.log('Media rejected', err);
      that._media_stream = false;
      that.boxcolor = 'red';
    }
  };

  LGAudioMediaSource.prototype.streamReady = function (localMediaStream) {
    this._media_stream = localMediaStream;
    //this._waiting_confirmation = false;

    //init context
    if (this.audiosource_node) {
      this.audiosource_node.disconnect(this.audionode);
    }
    var context = LGAudio.getAudioContext();
    this.audiosource_node = context.createMediaStreamSource(localMediaStream);
    this.audiosource_node.graphnode = this;
    this.audiosource_node.connect(this.audionode);
    this.boxcolor = 'white';
  };

  LGAudioMediaSource.prototype.onExecute = function () {
    if (this._media_stream == null && !this._waiting_confirmation) {
      this.openStream();
    }

    if (this.inputs) {
      for (var i = 0; i < this.inputs.length; ++i) {
        var input = this.inputs[i];
        if (input.link == null) {
          continue;
        }
        var v = this.getInputData(i);
        if (v === undefined) {
          continue;
        }
        if (input.name == 'gain') {
          this.audionode.gain.value = this.properties.gain = v;
        }
      }
    }
  };

  LGAudioMediaSource.prototype.onAction = function (event) {
    if (event == 'Play') {
      this.audionode.gain.value = this.properties.gain;
    } else if (event == 'Stop') {
      this.audionode.gain.value = 0;
    }
  };

  LGAudioMediaSource.prototype.onPropertyChanged = function (name, value) {
    if (name == 'gain') {
      this.audionode.gain.value = value;
    }
  };

  //Helps connect/disconnect AudioNodes when new connections are made in the node
  LGAudioMediaSource.prototype.onConnectionsChange =
    LGAudio.onConnectionsChange;

  LGAudioMediaSource.prototype.onGetInputs = function () {
    return [
      ['playbackRate', 'number'],
      ['Play', LiteGraph.ACTION],
      ['Stop', LiteGraph.ACTION],
    ];
  };

  LGAudioMediaSource.title = 'MediaSource';
  LGAudioMediaSource.desc = 'Plays microphone';
  LiteGraph.registerNodeType('audio/media_source', LGAudioMediaSource);

  //*****************************************************

  function LGAudioAnalyser() {
    this.properties = {
      fftSize: 2048,
      minDecibels: -100,
      maxDecibels: -10,
      smoothingTimeConstant: 0.5,
    };

    var context = LGAudio.getAudioContext();

    this.audionode = context.createAnalyser();
    this.audionode.graphnode = this;
    this.audionode.fftSize = this.properties.fftSize;
    this.audionode.minDecibels = this.properties.minDecibels;
    this.audionode.maxDecibels = this.properties.maxDecibels;
    this.audionode.smoothingTimeConstant =
      this.properties.smoothingTimeConstant;

    this.addInput('in', 'audio');
    this.addOutput('freqs', 'array');
    this.addOutput('samples', 'array');

    this._freq_bin = null;
    this._time_bin = null;
  }

  LGAudioAnalyser.prototype.onPropertyChanged = function (name, value) {
    this.audionode[name] = value;
  };

  LGAudioAnalyser.prototype.onExecute = function () {
    if (this.isOutputConnected(0)) {
      //send FFT
      var bufferLength = this.audionode.frequencyBinCount;
      if (!this._freq_bin || this._freq_bin.length != bufferLength) {
        this._freq_bin = new Uint8Array(bufferLength);
      }
      this.audionode.getByteFrequencyData(this._freq_bin);
      this.setOutputData(0, this._freq_bin);
    }

    //send analyzer
    if (this.isOutputConnected(1)) {
      //send Samples
      var bufferLength = this.audionode.frequencyBinCount;
      if (!this._time_bin || this._time_bin.length != bufferLength) {
        this._time_bin = new Uint8Array(bufferLength);
      }
      this.audionode.getByteTimeDomainData(this._time_bin);
      this.setOutputData(1, this._time_bin);
    }

    //properties
    for (var i = 1; i < this.inputs.length; ++i) {
      var input = this.inputs[i];
      if (input.link == null) {
        continue;
      }
      var v = this.getInputData(i);
      if (v !== undefined) {
        this.audionode[input.name].value = v;
      }
    }

    //time domain
    //this.audionode.getFloatTimeDomainData( dataArray );
  };

  LGAudioAnalyser.prototype.onGetInputs = function () {
    return [
      ['minDecibels', 'number'],
      ['maxDecibels', 'number'],
      ['smoothingTimeConstant', 'number'],
    ];
  };

  LGAudioAnalyser.prototype.onGetOutputs = function () {
    return [
      ['freqs', 'array'],
      ['samples', 'array'],
    ];
  };

  LGAudioAnalyser.title = 'Analyser';
  LGAudioAnalyser.desc = 'Audio Analyser';
  LiteGraph.registerNodeType('audio/analyser', LGAudioAnalyser);

  //*****************************************************

  function LGAudioGain() {
    //default
    this.properties = {
      gain: 1,
    };

    this.audionode = LGAudio.getAudioContext().createGain();
    this.addInput('in', 'audio');
    this.addInput('gain', 'number');
    this.addOutput('out', 'audio');
  }

  LGAudioGain.prototype.onExecute = function () {
    if (!this.inputs || !this.inputs.length) {
      return;
    }

    for (var i = 1; i < this.inputs.length; ++i) {
      var input = this.inputs[i];
      var v = this.getInputData(i);
      if (v !== undefined) {
        this.audionode[input.name].value = v;
      }
    }
  };

  LGAudio.createAudioNodeWrapper(LGAudioGain);

  LGAudioGain.title = 'Gain';
  LGAudioGain.desc = 'Audio gain';
  LiteGraph.registerNodeType('audio/gain', LGAudioGain);

  function LGAudioConvolver() {
    //default
    this.properties = {
      impulse_src: '',
      normalize: true,
    };

    this.audionode = LGAudio.getAudioContext().createConvolver();
    this.addInput('in', 'audio');
    this.addOutput('out', 'audio');
  }

  LGAudio.createAudioNodeWrapper(LGAudioConvolver);

  LGAudioConvolver.prototype.onRemove = function () {
    if (this._dropped_url) {
      URL.revokeObjectURL(this._dropped_url);
    }
  };

  LGAudioConvolver.prototype.onPropertyChanged = function (name, value) {
    if (name == 'impulse_src') {
      this.loadImpulse(value);
    } else if (name == 'normalize') {
      this.audionode.normalize = value;
    }
  };

  LGAudioConvolver.prototype.onDropFile = function (file) {
    if (this._dropped_url) {
      URL.revokeObjectURL(this._dropped_url);
    }
    this._dropped_url = URL.createObjectURL(file);
    this.properties.impulse_src = this._dropped_url;
    this.loadImpulse(this._dropped_url);
  };

  LGAudioConvolver.prototype.loadImpulse = function (url) {
    var that = this;

    //kill previous load
    if (this._request) {
      this._request.abort();
      this._request = null;
    }

    this._impulse_buffer = null;
    this._loading_impulse = false;

    if (!url) {
      return;
    }

    //load new sample
    this._request = LGAudio.loadSound(url, inner);
    this._loading_impulse = true;

    // Decode asynchronously
    function inner(buffer) {
      that._impulse_buffer = buffer;
      that.audionode.buffer = buffer;
      console.log('Impulse signal set');
      that._loading_impulse = false;
    }
  };

  LGAudioConvolver.title = 'Convolver';
  LGAudioConvolver.desc = 'Convolves the signal (used for reverb)';
  LiteGraph.registerNodeType('audio/convolver', LGAudioConvolver);

  function LGAudioDynamicsCompressor() {
    //default
    this.properties = {
      threshold: -50,
      knee: 40,
      ratio: 12,
      reduction: -20,
      attack: 0,
      release: 0.25,
    };

    this.audionode = LGAudio.getAudioContext().createDynamicsCompressor();
    this.addInput('in', 'audio');
    this.addOutput('out', 'audio');
  }

  LGAudio.createAudioNodeWrapper(LGAudioDynamicsCompressor);

  LGAudioDynamicsCompressor.prototype.onExecute = function () {
    if (!this.inputs || !this.inputs.length) {
      return;
    }
    for (var i = 1; i < this.inputs.length; ++i) {
      var input = this.inputs[i];
      if (input.link == null) {
        continue;
      }
      var v = this.getInputData(i);
      if (v !== undefined) {
        this.audionode[input.name].value = v;
      }
    }
  };

  LGAudioDynamicsCompressor.prototype.onGetInputs = function () {
    return [
      ['threshold', 'number'],
      ['knee', 'number'],
      ['ratio', 'number'],
      ['reduction', 'number'],
      ['attack', 'number'],
      ['release', 'number'],
    ];
  };

  LGAudioDynamicsCompressor.title = 'DynamicsCompressor';
  LGAudioDynamicsCompressor.desc = 'Dynamics Compressor';
  LiteGraph.registerNodeType(
    'audio/dynamicsCompressor',
    LGAudioDynamicsCompressor,
  );

  function LGAudioWaveShaper() {
    //default
    this.properties = {};

    this.audionode = LGAudio.getAudioContext().createWaveShaper();
    this.addInput('in', 'audio');
    this.addInput('shape', 'waveshape');
    this.addOutput('out', 'audio');
  }

  LGAudioWaveShaper.prototype.onExecute = function () {
    if (!this.inputs || !this.inputs.length) {
      return;
    }
    var v = this.getInputData(1);
    if (v === undefined) {
      return;
    }
    this.audionode.curve = v;
  };

  LGAudioWaveShaper.prototype.setWaveShape = function (shape) {
    this.audionode.curve = shape;
  };

  LGAudio.createAudioNodeWrapper(LGAudioWaveShaper);

  /* disabled till I dont find a way to do a wave shape
LGAudioWaveShaper.title = "WaveShaper";
LGAudioWaveShaper.desc = "Distortion using wave shape";
LiteGraph.registerNodeType("audio/waveShaper", LGAudioWaveShaper);
*/

  function LGAudioMixer() {
    //default
    this.properties = {
      gain1: 0.5,
      gain2: 0.5,
    };

    this.audionode = LGAudio.getAudioContext().createGain();

    this.audionode1 = LGAudio.getAudioContext().createGain();
    this.audionode1.gain.value = this.properties.gain1;
    this.audionode2 = LGAudio.getAudioContext().createGain();
    this.audionode2.gain.value = this.properties.gain2;

    this.audionode1.connect(this.audionode);
    this.audionode2.connect(this.audionode);

    this.addInput('in1', 'audio');
    this.addInput('in1 gain', 'number');
    this.addInput('in2', 'audio');
    this.addInput('in2 gain', 'number');

    this.addOutput('out', 'audio');
  }

  LGAudioMixer.prototype.getAudioNodeInInputSlot = function (slot) {
    if (slot == 0) {
      return this.audionode1;
    } else if (slot == 2) {
      return this.audionode2;
    }
  };

  LGAudioMixer.prototype.onPropertyChanged = function (name, value) {
    if (name == 'gain1') {
      this.audionode1.gain.value = value;
    } else if (name == 'gain2') {
      this.audionode2.gain.value = value;
    }
  };

  LGAudioMixer.prototype.onExecute = function () {
    if (!this.inputs || !this.inputs.length) {
      return;
    }

    for (var i = 1; i < this.inputs.length; ++i) {
      var input = this.inputs[i];

      if (input.link == null || input.type == 'audio') {
        continue;
      }

      var v = this.getInputData(i);
      if (v === undefined) {
        continue;
      }

      if (i == 1) {
        this.audionode1.gain.value = v;
      } else if (i == 3) {
        this.audionode2.gain.value = v;
      }
    }
  };

  LGAudio.createAudioNodeWrapper(LGAudioMixer);

  LGAudioMixer.title = 'Mixer';
  LGAudioMixer.desc = 'Audio mixer';
  LiteGraph.registerNodeType('audio/mixer', LGAudioMixer);

  function LGAudioADSR() {
    //default
    this.properties = {
      A: 0.1,
      D: 0.1,
      S: 0.1,
      R: 0.1,
    };

    this.audionode = LGAudio.getAudioContext().createGain();
    this.audionode.gain.value = 0;
    this.addInput('in', 'audio');
    this.addInput('gate', 'boolean');
    this.addOutput('out', 'audio');
    this.gate = false;
  }

  LGAudioADSR.prototype.onExecute = function () {
    var audioContext = LGAudio.getAudioContext();
    var now = audioContext.currentTime;
    var node = this.audionode;
    var gain = node.gain;
    var current_gate = this.getInputData(1);

    var A = this.getInputOrProperty('A');
    var D = this.getInputOrProperty('D');
    var S = this.getInputOrProperty('S');
    var R = this.getInputOrProperty('R');

    if (!this.gate && current_gate) {
      gain.cancelScheduledValues(0);
      gain.setValueAtTime(0, now);
      gain.linearRampToValueAtTime(1, now + A);
      gain.linearRampToValueAtTime(S, now + A + D);
    } else if (this.gate && !current_gate) {
      gain.cancelScheduledValues(0);
      gain.setValueAtTime(gain.value, now);
      gain.linearRampToValueAtTime(0, now + R);
    }

    this.gate = current_gate;
  };

  LGAudioADSR.prototype.onGetInputs = function () {
    return [
      ['A', 'number'],
      ['D', 'number'],
      ['S', 'number'],
      ['R', 'number'],
    ];
  };

  LGAudio.createAudioNodeWrapper(LGAudioADSR);

  LGAudioADSR.title = 'ADSR';
  LGAudioADSR.desc = 'Audio envelope';
  LiteGraph.registerNodeType('audio/adsr', LGAudioADSR);

  function LGAudioDelay() {
    //default
    this.properties = {
      delayTime: 0.5,
    };

    this.audionode = LGAudio.getAudioContext().createDelay(10);
    this.audionode.delayTime.value = this.properties.delayTime;
    this.addInput('in', 'audio');
    this.addInput('time', 'number');
    this.addOutput('out', 'audio');
  }

  LGAudio.createAudioNodeWrapper(LGAudioDelay);

  LGAudioDelay.prototype.onExecute = function () {
    var v = this.getInputData(1);
    if (v !== undefined) {
      this.audionode.delayTime.value = v;
    }
  };

  LGAudioDelay.title = 'Delay';
  LGAudioDelay.desc = 'Audio delay';
  LiteGraph.registerNodeType('audio/delay', LGAudioDelay);

  function LGAudioBiquadFilter() {
    //default
    this.properties = {
      frequency: 350,
      detune: 0,
      Q: 1,
    };
    this.addProperty('type', 'lowpass', 'enum', {
      values: [
        'lowpass',
        'highpass',
        'bandpass',
        'lowshelf',
        'highshelf',
        'peaking',
        'notch',
        'allpass',
      ],
    });

    //create node
    this.audionode = LGAudio.getAudioContext().createBiquadFilter();

    //slots
    this.addInput('in', 'audio');
    this.addOutput('out', 'audio');
  }

  LGAudioBiquadFilter.prototype.onExecute = function () {
    if (!this.inputs || !this.inputs.length) {
      return;
    }

    for (var i = 1; i < this.inputs.length; ++i) {
      var input = this.inputs[i];
      if (input.link == null) {
        continue;
      }
      var v = this.getInputData(i);
      if (v !== undefined) {
        this.audionode[input.name].value = v;
      }
    }
  };

  LGAudioBiquadFilter.prototype.onGetInputs = function () {
    return [
      ['frequency', 'number'],
      ['detune', 'number'],
      ['Q', 'number'],
    ];
  };

  LGAudio.createAudioNodeWrapper(LGAudioBiquadFilter);

  LGAudioBiquadFilter.title = 'BiquadFilter';
  LGAudioBiquadFilter.desc = 'Audio filter';
  LiteGraph.registerNodeType('audio/biquadfilter', LGAudioBiquadFilter);

  function LGAudioOscillatorNode() {
    //default
    this.properties = {
      frequency: 440,
      detune: 0,
      type: 'sine',
    };
    this.addProperty('type', 'sine', 'enum', {
      values: ['sine', 'square', 'sawtooth', 'triangle', 'custom'],
    });

    //create node
    this.audionode = LGAudio.getAudioContext().createOscillator();

    //slots
    this.addOutput('out', 'audio');
  }

  LGAudioOscillatorNode.prototype.onStart = function () {
    if (!this.audionode.started) {
      this.audionode.started = true;
      try {
        this.audionode.start();
      } catch (err) {}
    }
  };

  LGAudioOscillatorNode.prototype.onStop = function () {
    if (this.audionode.started) {
      this.audionode.started = false;
      this.audionode.stop();
    }
  };

  LGAudioOscillatorNode.prototype.onPause = function () {
    this.onStop();
  };

  LGAudioOscillatorNode.prototype.onUnpause = function () {
    this.onStart();
  };

  LGAudioOscillatorNode.prototype.onExecute = function () {
    if (!this.inputs || !this.inputs.length) {
      return;
    }

    for (var i = 0; i < this.inputs.length; ++i) {
      var input = this.inputs[i];
      if (input.link == null) {
        continue;
      }
      var v = this.getInputData(i);
      if (v !== undefined) {
        this.audionode[input.name].value = v;
      }
    }
  };

  LGAudioOscillatorNode.prototype.onGetInputs = function () {
    return [
      ['frequency', 'number'],
      ['detune', 'number'],
      ['type', 'string'],
    ];
  };

  LGAudio.createAudioNodeWrapper(LGAudioOscillatorNode);

  LGAudioOscillatorNode.title = 'Oscillator';
  LGAudioOscillatorNode.desc = 'Oscillator';
  LiteGraph.registerNodeType('audio/oscillator', LGAudioOscillatorNode);

  //*****************************************************

  //EXTRA

  function LGAudioVisualization() {
    this.properties = {
      continuous: true,
      mark: -1,
    };

    this.addInput('data', 'array');
    this.addInput('mark', 'number');
    this.size = [300, 200];
    this._last_buffer = null;
  }

  LGAudioVisualization.prototype.onExecute = function () {
    this._last_buffer = this.getInputData(0);
    var v = this.getInputData(1);
    if (v !== undefined) {
      this.properties.mark = v;
    }
    this.setDirtyCanvas(true, false);
  };

  LGAudioVisualization.prototype.onDrawForeground = function (ctx) {
    if (!this._last_buffer) {
      return;
    }

    var buffer = this._last_buffer;

    //delta represents how many samples we advance per pixel
    var delta = buffer.length / this.size[0];
    var h = this.size[1];

    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, this.size[0], this.size[1]);
    ctx.strokeStyle = 'white';
    ctx.beginPath();
    var x = 0;

    if (this.properties.continuous) {
      ctx.moveTo(x, h);
      for (var i = 0; i < buffer.length; i += delta) {
        ctx.lineTo(x, h - (buffer[i | 0] / 255) * h);
        x++;
      }
    } else {
      for (var i = 0; i < buffer.length; i += delta) {
        ctx.moveTo(x + 0.5, h);
        ctx.lineTo(x + 0.5, h - (buffer[i | 0] / 255) * h);
        x++;
      }
    }
    ctx.stroke();

    if (this.properties.mark >= 0) {
      var samplerate = LGAudio.getAudioContext().sampleRate;
      var binfreq = samplerate / buffer.length;
      var x = (2 * (this.properties.mark / binfreq)) / delta;
      if (x >= this.size[0]) {
        x = this.size[0] - 1;
      }
      ctx.strokeStyle = 'red';
      ctx.beginPath();
      ctx.moveTo(x, h);
      ctx.lineTo(x, 0);
      ctx.stroke();
    }
  };

  LGAudioVisualization.title = 'Visualization';
  LGAudioVisualization.desc = 'Audio Visualization';
  LiteGraph.registerNodeType('audio/visualization', LGAudioVisualization);

  function LGAudioBandSignal() {
    //default
    this.properties = {
      band: 440,
      amplitude: 1,
    };

    this.addInput('freqs', 'array');
    this.addOutput('signal', 'number');
  }

  LGAudioBandSignal.prototype.onExecute = function () {
    this._freqs = this.getInputData(0);
    if (!this._freqs) {
      return;
    }

    var band = this.properties.band;
    var v = this.getInputData(1);
    if (v !== undefined) {
      band = v;
    }

    var samplerate = LGAudio.getAudioContext().sampleRate;
    var binfreq = samplerate / this._freqs.length;
    var index = 2 * (band / binfreq);
    var v = 0;
    if (index < 0) {
      v = this._freqs[0];
    }
    if (index >= this._freqs.length) {
      v = this._freqs[this._freqs.length - 1];
    } else {
      var pos = index | 0;
      var v0 = this._freqs[pos];
      var v1 = this._freqs[pos + 1];
      var f = index - pos;
      v = v0 * (1 - f) + v1 * f;
    }

    this.setOutputData(0, (v / 255) * this.properties.amplitude);
  };

  LGAudioBandSignal.prototype.onGetInputs = function () {
    return [['band', 'number']];
  };

  LGAudioBandSignal.title = 'Signal';
  LGAudioBandSignal.desc = 'extract the signal of some frequency';
  LiteGraph.registerNodeType('audio/signal', LGAudioBandSignal);

  function LGAudioScript() {
    if (!LGAudioScript.default_code) {
      var code = LGAudioScript.default_function.toString();
      var index = code.indexOf('{') + 1;
      var index2 = code.lastIndexOf('}');
      LGAudioScript.default_code = code.substr(index, index2 - index);
    }

    //default
    this.properties = {
      code: LGAudioScript.default_code,
    };

    //create node
    var ctx = LGAudio.getAudioContext();
    if (ctx.createScriptProcessor) {
      this.audionode = ctx.createScriptProcessor(4096, 1, 1);
    }
    //buffer size, input channels, output channels
    else {
      console.warn('ScriptProcessorNode deprecated');
      this.audionode = ctx.createGain(); //bypass audio
    }

    this.processCode();
    if (!LGAudioScript._bypass_function) {
      LGAudioScript._bypass_function = this.audionode.onaudioprocess;
    }

    //slots
    this.addInput('in', 'audio');
    this.addOutput('out', 'audio');
  }

  LGAudioScript.prototype.onAdded = function (graph) {
    if (graph.status == LGraph.STATUS_RUNNING) {
      this.audionode.onaudioprocess = this._callback;
    }
  };

  LGAudioScript['@code'] = { widget: 'code', type: 'code' };

  LGAudioScript.prototype.onStart = function () {
    this.audionode.onaudioprocess = this._callback;
  };

  LGAudioScript.prototype.onStop = function () {
    this.audionode.onaudioprocess = LGAudioScript._bypass_function;
  };

  LGAudioScript.prototype.onPause = function () {
    this.audionode.onaudioprocess = LGAudioScript._bypass_function;
  };

  LGAudioScript.prototype.onUnpause = function () {
    this.audionode.onaudioprocess = this._callback;
  };

  LGAudioScript.prototype.onExecute = function () {
    //nothing! because we need an onExecute to receive onStart... fix that
  };

  LGAudioScript.prototype.onRemoved = function () {
    this.audionode.onaudioprocess = LGAudioScript._bypass_function;
  };

  LGAudioScript.prototype.processCode = function () {
    try {
      var func = new Function('properties', this.properties.code);
      this._script = new func(this.properties);
      this._old_code = this.properties.code;
      this._callback = this._script.onaudioprocess;
    } catch (err) {
      console.error('Error in onaudioprocess code', err);
      this._callback = LGAudioScript._bypass_function;
      this.audionode.onaudioprocess = this._callback;
    }
  };

  LGAudioScript.prototype.onPropertyChanged = function (name, value) {
    if (name == 'code') {
      this.properties.code = value;
      this.processCode();
      if (this.graph && this.graph.status == LGraph.STATUS_RUNNING) {
        this.audionode.onaudioprocess = this._callback;
      }
    }
  };

  LGAudioScript.default_function = function () {
    this.onaudioprocess = function (audioProcessingEvent) {
      // The input buffer is the song we loaded earlier
      var inputBuffer = audioProcessingEvent.inputBuffer;

      // The output buffer contains the samples that will be modified and played
      var outputBuffer = audioProcessingEvent.outputBuffer;

      // Loop through the output channels (in this case there is only one)
      for (
        var channel = 0;
        channel < outputBuffer.numberOfChannels;
        channel++
      ) {
        var inputData = inputBuffer.getChannelData(channel);
        var outputData = outputBuffer.getChannelData(channel);

        // Loop through the 4096 samples
        for (var sample = 0; sample < inputBuffer.length; sample++) {
          // make output equal to the same as the input
          outputData[sample] = inputData[sample];
        }
      }
    };
  };

  LGAudio.createAudioNodeWrapper(LGAudioScript);

  LGAudioScript.title = 'Script';
  LGAudioScript.desc = 'apply script to signal';
  LiteGraph.registerNodeType('audio/script', LGAudioScript);

  function LGAudioDestination() {
    this.audionode = LGAudio.getAudioContext().destination;
    this.addInput('in', 'audio');
  }

  LGAudioDestination.title = 'Destination';
  LGAudioDestination.desc = 'Audio output';
  LiteGraph.registerNodeType('audio/destination', LGAudioDestination);
})(this);

//event related nodes
(function (global) {
  var LiteGraph = global.LiteGraph;

  function LGWebSocket() {
    this.size = [60, 20];
    this.addInput('send', LiteGraph.ACTION);
    this.addOutput('received', LiteGraph.EVENT);
    this.addInput('in', 0);
    this.addOutput('out', 0);
    this.properties = {
      url: '',
      room: 'lgraph', //allows to filter messages,
      only_send_changes: true,
    };
    this._ws = null;
    this._last_sent_data = [];
    this._last_received_data = [];
  }

  LGWebSocket.title = 'WebSocket';
  LGWebSocket.desc = 'Send data through a websocket';

  LGWebSocket.prototype.onPropertyChanged = function (name, value) {
    if (name == 'url') {
      this.connectSocket();
    }
  };

  LGWebSocket.prototype.onExecute = function () {
    if (!this._ws && this.properties.url) {
      this.connectSocket();
    }

    if (!this._ws || this._ws.readyState != WebSocket.OPEN) {
      return;
    }

    var room = this.properties.room;
    var only_changes = this.properties.only_send_changes;

    for (var i = 1; i < this.inputs.length; ++i) {
      var data = this.getInputData(i);
      if (data == null) {
        continue;
      }
      var json;
      try {
        json = JSON.stringify({
          type: 0,
          room: room,
          channel: i,
          data: data,
        });
      } catch (err) {
        continue;
      }
      if (only_changes && this._last_sent_data[i] == json) {
        continue;
      }

      this._last_sent_data[i] = json;
      this._ws.send(json);
    }

    for (var i = 1; i < this.outputs.length; ++i) {
      this.setOutputData(i, this._last_received_data[i]);
    }

    if (this.boxcolor == '#AFA') {
      this.boxcolor = '#6C6';
    }
  };

  LGWebSocket.prototype.connectSocket = function () {
    var that = this;
    var url = this.properties.url;
    if (url.substr(0, 2) != 'ws') {
      url = 'ws://' + url;
    }
    this._ws = new WebSocket(url);
    this._ws.onopen = function () {
      console.log('ready');
      that.boxcolor = '#6C6';
    };
    this._ws.onmessage = function (e) {
      that.boxcolor = '#AFA';
      var data = JSON.parse(e.data);
      if (data.room && data.room != that.properties.room) {
        return;
      }
      if (data.type == 1) {
        if (data.data.object_class && LiteGraph[data.data.object_class]) {
          var obj = null;
          try {
            obj = new LiteGraph[data.data.object_class](data.data);
            that.triggerSlot(0, obj);
          } catch (err) {
            return;
          }
        } else {
          that.triggerSlot(0, data.data);
        }
      } else {
        that._last_received_data[data.channel || 0] = data.data;
      }
    };
    this._ws.onerror = function (e) {
      console.log('couldnt connect to websocket');
      that.boxcolor = '#E88';
    };
    this._ws.onclose = function (e) {
      console.log('connection closed');
      that.boxcolor = '#000';
    };
  };

  LGWebSocket.prototype.send = function (data) {
    if (!this._ws || this._ws.readyState != WebSocket.OPEN) {
      return;
    }
    this._ws.send(JSON.stringify({ type: 1, msg: data }));
  };

  LGWebSocket.prototype.onAction = function (action, param) {
    if (!this._ws || this._ws.readyState != WebSocket.OPEN) {
      return;
    }
    this._ws.send({
      type: 1,
      room: this.properties.room,
      action: action,
      data: param,
    });
  };

  LGWebSocket.prototype.onGetInputs = function () {
    return [['in', 0]];
  };

  LGWebSocket.prototype.onGetOutputs = function () {
    return [['out', 0]];
  };

  LiteGraph.registerNodeType('network/websocket', LGWebSocket);

  //It is like a websocket but using the SillyServer.js server that bounces packets back to all clients connected:
  //For more information: https://github.com/jagenjo/SillyServer.js

  function LGSillyClient() {
    //this.size = [60,20];
    this.room_widget = this.addWidget(
      'text',
      'Room',
      'lgraph',
      this.setRoom.bind(this),
    );
    this.addWidget('button', 'Reconnect', null, this.connectSocket.bind(this));

    this.addInput('send', LiteGraph.ACTION);
    this.addOutput('received', LiteGraph.EVENT);
    this.addInput('in', 0);
    this.addOutput('out', 0);
    this.properties = {
      url: 'tamats.com:55000',
      room: 'lgraph',
      only_send_changes: true,
    };

    this._server = null;
    this.connectSocket();
    this._last_sent_data = [];
    this._last_received_data = [];

    if (typeof SillyClient == 'undefined')
      console.warn(
        'remember to add SillyClient.js to your project: https://tamats.com/projects/sillyserver/src/sillyclient.js',
      );
  }

  LGSillyClient.title = 'SillyClient';
  LGSillyClient.desc = 'Connects to SillyServer to broadcast messages';

  LGSillyClient.prototype.onPropertyChanged = function (name, value) {
    if (name == 'room') {
      this.room_widget.value = value;
    }
    this.connectSocket();
  };

  LGSillyClient.prototype.setRoom = function (room_name) {
    this.properties.room = room_name;
    this.room_widget.value = room_name;
    this.connectSocket();
  };

  //force label names
  LGSillyClient.prototype.onDrawForeground = function () {
    for (var i = 1; i < this.inputs.length; ++i) {
      var slot = this.inputs[i];
      slot.label = 'in_' + i;
    }
    for (var i = 1; i < this.outputs.length; ++i) {
      var slot = this.outputs[i];
      slot.label = 'out_' + i;
    }
  };

  LGSillyClient.prototype.onExecute = function () {
    if (!this._server || !this._server.is_connected) {
      return;
    }

    var only_send_changes = this.properties.only_send_changes;

    for (var i = 1; i < this.inputs.length; ++i) {
      var data = this.getInputData(i);
      var prev_data = this._last_sent_data[i];
      if (data != null) {
        if (only_send_changes) {
          var is_equal = true;
          if (
            data &&
            data.length &&
            prev_data &&
            prev_data.length == data.length &&
            data.constructor !== String
          ) {
            for (var j = 0; j < data.length; ++j)
              if (prev_data[j] != data[j]) {
                is_equal = false;
                break;
              }
          } else if (this._last_sent_data[i] != data) is_equal = false;
          if (is_equal) continue;
        }
        this._server.sendMessage({ type: 0, channel: i, data: data });
        if (data.length && data.constructor !== String) {
          if (this._last_sent_data[i]) {
            this._last_sent_data[i].length = data.length;
            for (var j = 0; j < data.length; ++j)
              this._last_sent_data[i][j] = data[j];
          } //create
          else {
            if (data.constructor === Array)
              this._last_sent_data[i] = data.concat();
            else this._last_sent_data[i] = new data.constructor(data);
          }
        } else this._last_sent_data[i] = data; //should be cloned
      }
    }

    for (var i = 1; i < this.outputs.length; ++i) {
      this.setOutputData(i, this._last_received_data[i]);
    }

    if (this.boxcolor == '#AFA') {
      this.boxcolor = '#6C6';
    }
  };

  LGSillyClient.prototype.connectSocket = function () {
    var that = this;
    if (typeof SillyClient == 'undefined') {
      if (!this._error) {
        console.error(
          'SillyClient node cannot be used, you must include SillyServer.js',
        );
      }
      this._error = true;
      return;
    }

    this._server = new SillyClient();
    this._server.on_ready = function () {
      console.log('ready');
      that.boxcolor = '#6C6';
    };
    this._server.on_message = function (id, msg) {
      var data = null;
      try {
        data = JSON.parse(msg);
      } catch (err) {
        return;
      }

      if (data.type == 1) {
        //EVENT slot
        if (data.data.object_class && LiteGraph[data.data.object_class]) {
          var obj = null;
          try {
            obj = new LiteGraph[data.data.object_class](data.data);
            that.triggerSlot(0, obj);
          } catch (err) {
            return;
          }
        } else {
          that.triggerSlot(0, data.data);
        }
      } //for FLOW slots
      else {
        that._last_received_data[data.channel || 0] = data.data;
      }
      that.boxcolor = '#AFA';
    };
    this._server.on_error = function (e) {
      console.log('couldnt connect to websocket');
      that.boxcolor = '#E88';
    };
    this._server.on_close = function (e) {
      console.log('connection closed');
      that.boxcolor = '#000';
    };

    if (this.properties.url && this.properties.room) {
      try {
        this._server.connect(this.properties.url, this.properties.room);
      } catch (err) {
        console.error('SillyServer error: ' + err);
        this._server = null;
        return;
      }
      this._final_url = this.properties.url + '/' + this.properties.room;
    }
  };

  LGSillyClient.prototype.send = function (data) {
    if (!this._server || !this._server.is_connected) {
      return;
    }
    this._server.sendMessage({ type: 1, data: data });
  };

  LGSillyClient.prototype.onAction = function (action, param) {
    if (!this._server || !this._server.is_connected) {
      return;
    }
    this._server.sendMessage({ type: 1, action: action, data: param });
  };

  LGSillyClient.prototype.onGetInputs = function () {
    return [['in', 0]];
  };

  LGSillyClient.prototype.onGetOutputs = function () {
    return [['out', 0]];
  };

  LiteGraph.registerNodeType('network/sillyclient', LGSillyClient);

  //HTTP Request
  function HTTPRequestNode() {
    var that = this;
    this.addInput('request', LiteGraph.ACTION);
    this.addInput('url', 'string');
    this.addProperty('url', '');
    this.addOutput('ready', LiteGraph.EVENT);
    this.addOutput('data', 'string');
    this.addWidget('button', 'Fetch', null, this.fetch.bind(this));
    this._data = null;
    this._fetching = null;
  }

  HTTPRequestNode.title = 'HTTP Request';
  HTTPRequestNode.desc = 'Fetch data through HTTP';

  HTTPRequestNode.prototype.fetch = function () {
    var url = this.properties.url;
    if (!url) return;

    this.boxcolor = '#FF0';
    var that = this;
    this._fetching = fetch(url)
      .then((resp) => {
        if (!resp.ok) {
          this.boxcolor = '#F00';
          that.trigger('error');
        } else {
          this.boxcolor = '#0F0';
          return resp.text();
        }
      })
      .then((data) => {
        that._data = data;
        that._fetching = null;
        that.trigger('ready');
      });
  };

  HTTPRequestNode.prototype.onAction = function (evt) {
    if (evt == 'request') this.fetch();
  };

  HTTPRequestNode.prototype.onExecute = function () {
    this.setOutputData(1, this._data);
  };

  HTTPRequestNode.prototype.onGetOutputs = function () {
    return [['error', LiteGraph.EVENT]];
  };

  LiteGraph.registerNodeType('network/httprequest', HTTPRequestNode);
})(this);
