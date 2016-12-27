/*global require, phantom */
var system = require('system');

if (!system.args[1]){
    console.log('Pass path to test file as second arg');
    phantom.exit();
}

var path = system.args[1];
if (path.indexOf('/') !== 0) {
    path = system.env.PWD + '/' + path;
}

var page = require('webpage').create();
var logs = '';

page.onConsoleMessage = function (msg) {
  logs += msg + '\n';
};

page.open('file://' + path, function () {
    setTimeout(function() {
        var output = page.evaluate( function () {
            var results = '';

            var headline = $('#qunit-testresult').text().split('.')[1] + '.';
            results += headline + '\n';

            var testCounter = 0;
            $('#qunit-tests li').each(function() {
                var li = $(this);
                if (li.prop('id').indexOf('qunit-test-output') !== -1){
                    testCounter += 1;
                    var resultLine = '';
                    resultLine += testCounter + '. ';
                    if (li.find('.module-name').length > 0) {
                        resultLine += li.find('.module-name').text() + ': ';
                    }
                    resultLine += li.find('.test-name').text();
                    resultLine += ' ' + li.find('.counts').text();
                    resultLine = resultLine.replace('Rerun', '');
                    var fails = li.find('.fail');
                    if (fails.text()) {
                        li.find('.qunit-assert-list li').each(function (assertCounter) {
                            var assert = $(this);
                            resultLine += '\n';
                            resultLine += '    ' + (assertCounter + 1) + '. ';
                            resultLine += assert.find('.test-message').text();
                            if (assert.find('.fail')) {
                                assert.find('tr').each(function () {
                                    resultLine += '\n';
                                    resultLine += '        ' + $(this).text();
                                });
                            }
                        });
                    }
                    results += resultLine + '\n';
                }
            });

            return results;
        });
        console.log(output);
        console.log(logs);
        phantom.exit();

    }, 100);
});

