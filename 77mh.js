var webpage = require('webpage'),
    system = require('system'),
    page, address;

address = system.args[1];
// address = 'http://www.77mh.com/colist_237987.html';
// address = 'http://www.77mh.com/201603/330426.html';

page = webpage.create();

function page_handler(status) {
    if (status !== 'success') {
	console.log('Unable to access network');
	phantom.exit();
    }

    var url = page.evaluate(function() {
	return document.getElementById('dracga').src;
    });
    console.log(url);

    var nextpage = page.evaluate(function () {
	var nextobj = document.getElementsByClassName('nextPage')[0];
	if (nextobj.textContent == '下一页') {
	    return nextobj.href;
	} else {
	    return '';
	}
    });

    if (nextpage == '') {
	phantom.exit();
    } else {
	page.open(nextpage, page_handler);
    }
}

page.open(address, page_handler);
