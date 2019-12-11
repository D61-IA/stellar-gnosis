var hostList = {
    arxiv: 'arxiv.org',
    nips: 'papers.nips.cc',
    jmlr: 'www.jmlr.org',
    pmlr: 'proceedings.mlr.press',
    cvf: 'openaccess.thecvf.com',
    springer: 'link.springer.com',
    robotics: 'www.roboticsproceedings.org',
};

// get the html of that url
function importHTML(url) {
    var responseType = 'document';

    return new Promise(function (resolve, reject) {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", url); // url/address is prefixed with where the js file is listed
        xhr.responseType = responseType;

        xhr.onload = function () {
            if (this.status === 200 && this.status < 300) {
                resolve(xhr.response)
            } else {
                reject({
                    status: this.status,
                    statusText: xhr.statusText
                });
            }
        };

        xhr.onerror = function () {
            reject({
                status: this.status,
                statusText: xhr.statusText
            });
        };
        xhr.send();
    })
}

function importPaper(url) {
    // check if url is importable
    var a = document.createElement('a');
    a.href = url;
    var hostName = a.hostname;

    var host = null;
    for (let key in hostList) {
        if (hostList[key] === hostName) {
            host = key;
        }
    }

    // if yes get necessary info from url using scrapper function
    if (host != null) {
        $('#paper_import').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Loading');
        importHTML(url).then(function (html) {
            var content = scrapper(host, html);

            // id='id_title'
            $('#id_title').val(content['title']);
            // id='id_abstract'
            $('#id_abstract').val(content['abstract']);
            // id='id_download_link
            $('#id_download_link').val(content['download']);
            // id='id_authors'
            $('#id_authors').val(content['authors']);

            $('#paper_import').html('Import');
            $('#paper_submit').attr('disabled', false);

            // console.log("ABSTRACT:", content['abstract']);
            // console.log("TITLE:", content['title']);
            // console.log("AUTHORS:", content['authors']);
            // console.log("URL:", content['download']);

        }).catch(function (err) {
            console.log("There was an error!", err.statusText)
        });
    } else {
        alert("Resource not available.")
    }
}

// takes in a url, sets host and html variables.
function scrapper(host, html) {

    var getAbstract = function () {
        var raw;

        if (host === 'arxiv') {
            raw = $("meta[property='og:description']", html).attr('content');
        }
        if (host === 'nips') {
            raw = $('p.abstract', html).prop('innerHTML');
        }
        if (host === 'jmlr') {
            var html_str = $("#content", html).prop('innerHTML');
            var i = html_str.indexOf("</h3>");
            var j = html_str.indexOf("<font");
            raw = $.trim(html_str.substring(i + 5, j));
        }
        if (host === 'pmlr') {
            raw = $("#abstract", html).prop('innerHTML');
        }
        if (host === 'cvf') {
            raw = $('#abstract', html).prop('innerHTML');
        }
        if (host === 'springer') {
            raw = $("#Par1", html).prop('innerHTML');
        }
        if (host === 'robotics') {
            // get the second p element inside .content parent
            raw = $('.content p', html).eq(1).prop('innerHTML');
        }

        return $.trim(raw);
    };

    var getTitle = function () {
        var raw;
        raw = $("meta[name='citation_title']", html).attr('content');
        return $.trim(raw);
    };

    // returns a list of author names seperated with space. e.g. ["zhenghao zhao", ...]
    var getAuthors = function () {
        var author_list = [];
        var name;
        // first name and next name are seperated with ', '
        if (host === 'arxiv' || host === 'jmlr' || host === 'cvf') {
            $("meta[name='citation_author']", html).each(function (i, obj) {
                name = $(this).attr('content').replace(",", "");
                // returns an array in an object (json purposes)
                author_list.push($.trim(name));
            });
        }

        // separated with ' '
        if (host === 'pmlr' || host === 'nips' || host === 'springer' || host === 'robotics') {
            $("meta[name='citation_author']", html).each(function (i, obj) {
                name = $(this).attr('content');
                author_list.push($.trim(name));
            });
        }
        return author_list;
    };

    var getDownloadLink = function () {
        var raw;
        raw = $("meta[name=citation_pdf_url", html).attr('content');
        if (host === 'robotics') {
            raw = $(".content a[target='_blank']", html).prop('href');
        }
        return $.trim(raw);
    };

    return {
        abstract: getAbstract(),
        title: getTitle(),
        authors: getAuthors(),
        download: getDownloadLink()
    }
}

$('#paper_import').click(function (e) {
    e.preventDefault();
    importPaper($('#id_url').val())
});

