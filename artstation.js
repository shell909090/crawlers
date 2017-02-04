var webpage = require('webpage'),
    system = require('system'),
    page, address;

// address = system.args[1];
address = 'https://www.artstation.com/artist/jcpark';

page = webpage.create();
page.onConsoleMessage = function(msg) {
    console.log(msg);
};

page.open(address, function (status) {
    if (status !== 'success') {
    	console.log('Unable to access network');
    	phantom.exit();
    }

    page.evaluate(function () {
    	$("a.project-image img.image").each(function () {
	    console.log(this.src.replace('/smaller_square/', '/large/'));
    	});
    });
    phantom.exit();
});
