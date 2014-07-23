var Sandbox = require('sandbox');
var s = new Sandbox();

s.run(process.argv[2], function(output) {
    console.log(output.console.join('\n'));
    //console.log(output.result);
});




