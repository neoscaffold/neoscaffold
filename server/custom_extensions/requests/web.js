// class NeoScaffoldNetwork {
//   // graph level

//   constructor(neoscaffold) {
//     console.log(`ext nsr, ${neoscaffold}`);
//   }

// }
// this.NeoScaffoldNetwork = NeoScaffoldNetwork;

// class ConsoleLog {
//   title = "ConsoleLog";
//   description = "Logs to the console";
//   category = "utils";
//   subcategory = "logging";
//   serialize_widgets = true;

//   color=LGraphCanvas.node_colors.yellow.color;
//   bgcolor=LGraphCanvas.node_colors.yellow.bgcolor;
//   groupcolor = LGraphCanvas.node_colors.yellow.groupcolor;

//   constructor() {
//     this.addInput('in_rules', 'rule_group', { pos: [10, 10] });
//     this.addInput('out_rules', 'rule_group', { pos: [10, 25] });
//     this.addInput('any', '*');
//     this.addOutput('any', '*');
//   }

//   onDrawBackground(ctx) {
//     this.outputs[0].label = this.inputs[0].value;
//   }
// }
// this.ConsoleLog = ConsoleLog;

// class TextLength {
//   title = "TextLength";
//   description = "Logs to the console";
//   category = "utils";
//   subcategory = "logging";
//   serialize_widgets = true;

//   color=LGraphCanvas.node_colors.black.color;
//   bgcolor=LGraphCanvas.node_colors.black.bgcolor;
//   groupcolor = LGraphCanvas.node_colors.black.groupcolor;

//   constructor() {
//     this.addInput('rule_group', 'rule_group', { pos: [10, 10] });
//     this.addOutput('rule_group', 'rule_group');

//     this.addInput('value_path', '*');
//     this.addInput('min_length', '*');
//     this.addInput('max_length', '*');

//     this.addProperty('value_path');
//     this.addProperty('min_length');
//     this.addProperty('max_length');

//     this.addWidget(
//       'string',
//       'value_path',
//       '',
//       'value_path', // modify the uri property
//       undefined // no special options
//     );
//     this.addWidget(
//       'number',
//       'min_length',
//       0,
//       'min_length', // modify the min_length property
//       undefined // no special options
//     );
//     this.addWidget(
//       'number',
//       'max_length',
//       0,
//       'max_length', // modify the body property
//       undefined // no special options
//     );

//   }
// }
// this.TextLength = TextLength;