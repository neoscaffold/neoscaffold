// class NeoScaffoldIteration {
//   // graph level

//   constructor(neoscaffold) {
//     console.log(`ext nsu, ${neoscaffold}`);
//   }

// }
// this.NeoScaffoldIteration = NeoScaffoldIteration;

// class DisplayText {
//   title = "DisplayText";
//   description = "Displays text directly in the node";
//   category = "utils";
//   subcategory = "logging";
//   serialize_widgets = true;

//   constructor() {
//     this.addInput('in_rules', 'rule_group', { pos: [10, 10] });
//     this.addInput('out_rules', 'rule_group', { pos: [10, 25] });
//     this.addInput('any', '*');
//     this.addOutput('any', '*');
//   }

//   onSerialize() {
//     if (this.flags.collapsed) {
//       return;
//     }
//     let textInput = this.inputs[0].value;
//     if (textInput) {
//       // let textarea = document.createElement('textarea');
//     }
//   }
// }
// this.DisplayText = DisplayText;