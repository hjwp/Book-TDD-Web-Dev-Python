var system = require('system');
// var env = system.env;
// Object.keys(env).forEach(function(key) {
//     console.log(key + '=' + env[key]);
// });

var path = system.env.PWD + '/' + system.args[1];
console.log(path);

if (!system.args[1]){
    console.log('Pass path to test file as second arg');
    phantom.exit();
}

var page = require('webpage').create();
page.open('file://' + path, function () {
    setTimeout(function() {
        var output = page.evaluate( function () {
            var results = '';

            var headline = $('#qunit-testresult').text().split('.')[1];
            results += headline + '\n';

            var counter = 0;
            $('#qunit-tests li').each(function() {
                var li = $(this);
                if (li.prop('id').indexOf('qunit-test-output') !== -1){
                    counter += 1;
                    var resultLine = '';
                    resultLine += counter + '. ';
                    resultLine += li.find('.test-name').text();
                    resultLine += ' ' + li.find('.counts').text();
                    resultLine = resultLine.replace('Rerun', '');
                    var fails = li.find('.fail');
                    if (fails.text()) {
                        resultLine += '\n';
                        resultLine += fails.find('tr.test-expected').text();
                        resultLine += '\n';
                        resultLine += fails.find('tr.test-actual').text();
                        resultLine += '\n';
                        resultLine += fails.find('tr.test-diff').text();
                        resultLine += '\n';
                        resultLine += fails.find('tr.test-source').text();
                    }
                    results += resultLine + '\n';
                }
            });

            return results;

            //return document.getElementById('qunit-testresult').textContent;
        });
        console.log(output);
        phantom.exit();

    }, 100);
});

