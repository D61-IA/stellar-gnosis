
/************** resizable graph **************/
// simulate stop resizing using timer
var resizeTimer;

// centering only happens after 250ms each time resize stops (mouse is released)
$(window).on('resize', function (e) {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
        center();
        // Run code here, resizing has "stopped"
    }, 250);

});

/************** show/hide relationships **************/
// initial toggle state
var hide_rela = false;

// function for toggle relationships button
function toggle_relas() {
    hide_rela = !hide_rela;
    if (hide_rela) {
        cy.style().selector('edge').style('label', '').update();
        $("#rela_toggle").text("visibility_off").attr("title", "Show relationships");
    } else {
        cy.style().selector('edge').style('label', 'data(label)').update();
        $("#rela_toggle").text("visibility").attr("title", "Hide relationships");
    }
}

/************** show/hide graph add-ons **************/
var hide_opt = false;

function toggle_options() {
    hide_opt = !hide_opt;
    if (hide_opt) {
        $(".graph-adder").hide(300);
        $("#menu-button").text("Show").attr("title", "Show add-ons");

    } else {
        $(".graph-adder").show(300);
        $("#menu-button").text("Hide").attr("title", "Hide add-ons");
    }
}

/************** double click toggle **************/
// $(".graph-canvas").dblclick(
//     function () {
//         toggle_options();
//     }
// );

// collection of all elements (nodes + edges) in the graph currently
var collection = cy.elements();

/************** center graph **************/
// combines center and fit
function center() {
    cy.animate({
        center: collection,
        fit: {eles: collection, padding: 20},
        duration: 0,
    });
}

/************** reset and re-render layout **************/
// reset layout, all nodes return to initial positions
function reset_layout() {
    cy.layout(layout).run();
    center();
}

/************** dropdown menu **************/
function show_cites(value) {
    var cat = value;

    if (cat === "all relationships") {
        collection = cy.elements();
        cy.style().selector('node').style('visibility', 'visible').update();
        cy.style().selector('edge').style('visibility', 'visible').update();
    } else {
        // get all elements currently on the graph
        collection = cy.filter((element) => {
            return element.data('label') === cat || element.data('label') === "origin"
        });

        cy.style().selector('node').style('visibility', 'hidden').update();
        cy.style().selector('edge').style('visibility', 'hidden').update();
        cy.style().selector('[label="' + cat + '"]').style('visibility', 'visible').update();
        cy.style().selector('node[label="origin"]').style('visibility', 'visible').update();
    }

    center();
}

/************** tooltip **************/
// interactivity with the ego graph
// timeout for delaying tooltip
var time_out = 1000;
var hoverTimeout;
cy.on('click', 'node', function (evt) {
    var node = evt.target;
    console.log('tapped ' + node.data('href'));
    try {
        window.open(node.data('href'), '_self');
    } catch (e) {
        window.location.href = node.data('href');
    }
})

// drawing tooltip upon mouseover
    .on('mouseover', 'node', function (evt) {
        var node = evt.target;
        node.style('opacity', 0.8);

        hoverTimeout = setTimeout(function () {
            var px = node.renderedPosition('x');
            var py = node.renderedPosition('y');

            var tip_item = "";

            var span = document.createElement("span");
            // what is shown on the tooltip
            if (node.data('type') === 'Person') {
                // combine individual names to one
                tip_item = node.data('first_name') + node.data('middle_name') + ' ' + node.data('last_name');
            }
            // for paper showing title only
            if (node.data('type') === 'Paper' || node.data('type') === 'Venue' || node.data('type') === 'Dataset') {
                tip_item = node.data('title')
            }

            span.innerHTML = tip_item;
            if (tip_item.length > 0) {

                $("#cy").append("<div id='tooltip'></div>");

                // css for tooltip
                $('#tooltip').append(span).css({
                    "display": "block",
                    "max-width": "200px",
                    "margin": 0,
                    "height": "auto",
                    "position": "absolute",
                    "padding": "5px",
                    "left": px,
                    "top": py,
                    "background-color": "#f2e5b8",
                    "z-index": 1000,
                    "border-radius": "6px",
                    "opacity": 0.9,
                    "text-align": "left"
                });
            }
            $('#tooltip span').css({
                "margin": 0,
            })

        }, time_out);

    })

    // remove tooltip on mouseout
    .on('mouseout', 'node', function (evt) {
        clearTimeout(hoverTimeout);
        var node = evt.target;
        node.style('opacity', 1);
        $('#tooltip').remove();

    })

    // graph components changes color to reflect hovering
    .on('mouseover', 'edge', function (evt) {
        var edge = evt.target;
        edge.style('opacity', 0.8);

    })
    .on('mouseout', 'edge', function (evt) {
        var edge = evt.target;
        edge.style('opacity', 1);

    });