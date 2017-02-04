var webpage = require('webpage'),
    system = require('system'),
    page, address;

// address = system.args[1];
address = 'https://www.artstation.com/artist/jcpark';

page = webpage.create();
page.onConsoleMessage = function(msg) {
    console.log(msg);
};

page.onClosing = function() {
    phantom.exit();
};

page.open(address, function (status) {
    if (status !== 'success') {
    	console.log('Unable to access network');
    	phantom.exit();
    }

    page.evaluate(function () {
	var loop_count = 0;

	function dump_urls () {
    	    $("a.project-image img.image").each(function () {
		console.log(this.src.replace(/\d{14}\/smaller_square/i, 'large').replace('/smaller_square/', '/large/'));
    	    });
	    window.close();
	}

	function scrollBottom () {
	    window.scrollTo(0, document.body.scrollHeight);
	    loop_count++;

	    if (loop_count > 10) {
		setTimeout(dump_urls, 2000);
	    } else {
		setTimeout(scrollBottom, 2000);
	    }
	}

	scrollBottom();
    });
});
