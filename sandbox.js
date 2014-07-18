var Sandbox = require('sandbox');
var s = new Sandbox();

s.run(process.argv[2], function(output) {
    console.log(output.console.join('\n'));
    //console.log(output.result);
});




/*var vm = require('vm');
var util = require('util');

String.prototype.replaceAt = function(index, subs){
    return this.substr(0, index) + subs + this.substr(index+subs.length);
}

function handle_TypeError (code, context, err){
    if (err.message.indexOf("$") > -1){
        code = "$ = this;".concat(code);
        return evaluate(code, context, err);
    }
    else if (err.message.indexOf("called on null or undefined") > -1){
        //TODO
        console.log("called on null or undefined");
        var line = err.stack.match(/at evalmachine.<anonymous>:(\d):(\d)/);
        lines = code.split('\n');
        oldline = lines[parseInt(line[1])-2];
        newline = oldline.replace(/=\s?.\(.*?\)/, "=app");
        if (newline == oldline){
            newline = oldline.replace(/=.*//*, "=app;");
        }
        //newline = oldline.replaceAt(parseInt(line[2])-1, "app");
        code = code.replace(oldline, newline);
        return evaluate(code, context, err.message);
    }
    else {
        return context.eval_code;
    }
}

function evaluate(code, context, old_msg) {
    console.log('evaluate');
    try {
        vm.runInNewContext(eval_string, context);
    }
    catch(ex){
        console.log("In catch");
        console.log(ex);
        if (ex.message == old_msg){
            return context.eval_code;
        }
        if (ex.name == "ReferenceError"){
            console.log("ReferenceError!");
            return;
        }
        else if (ex.name == "TypeError"){
            return handle_TypeError(code, context, ex);
        }
        else if (ex.name == "SyntaxError"){
            console.log("SyntaxError!");
            return;
        }
        else {
            console.log("Unknown exception: " + ex);
            return;
        }
        return;
    }
    finally{
        console.log(context.eval_code);
        return context.eval_code;
    }
}

var eval_string = 'eval = function evalOverride(text) { eval_code += text; return;};'
eval_string += process.argv[2];
var context = {
    eval_code: ''    
};
console.log(evaluate(eval_string, context, ''));
//return 'bweeeee';*/

