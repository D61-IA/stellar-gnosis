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

// /************** show/hide graph add-ons **************/
// var hide_opt = false;
//
// function toggle_options() {
//     hide_opt = !hide_opt;
//     if (hide_opt) {
//         $(".graph-adder").hide(300);
//         $("#menu-button").text("Show").attr("title", "Show add-ons");
//
//     } else {
//         $(".graph-adder").show(300);
//         $("#menu-button").text("Hide").attr("title", "Hide add-ons");
//     }
// }

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

function reset_nodes() {
    collection = cy.elements();
    cy.style().selector('node').style('visibility', 'visible').update();
    cy.style().selector('edge').style('visibility', 'visible').update();
    reset_layout();

    // sync select menu option to 'all'
    $('#graphfilter').val('all');
}

/************** graph filtering function **************/
function show_cites(label, type) {

    if (label === "all" && type === "all") {
        collection = cy.elements();
        cy.style().selector('node').style('visibility', 'visible').update();
        cy.style().selector('edge').style('visibility', 'visible').update();
    } else {
        // get all elements on the graph
        collection = cy.filter((element) => {
            return element.data('label') === label || element.data('type') === type
                || element.data('label') === "origin"
        });
        cy.style().selector('node').style('visibility', 'hidden').update();
        cy.style().selector('edge').style('visibility', 'hidden').update();
        cy.style().selector('[type="' + type + '"]').style('visibility', 'visible').update();
        cy.style().selector('[label="' + label + '"]').style('visibility', 'visible').update();
        cy.style().selector('node[label="origin"]').style('visibility', 'visible').update();
    }

    center();
}

/************** collapse ego-graph **************/
// stores state of the collapse target
var hidden = false;

function collapse_toggle(ele, that) {
    hidden = !hidden;
    if (hidden) {
        $(that).children('.drop_indicator').text('arrow_drop_down');
        $('#' + ele).hide(200);

    } else {
        $(that).children('.drop_indicator').text('arrow_drop_up');
        $('#' + ele).show(200);

    }
}

// collapse initially if device width is < 600
// device widths reference: https://www.w3schools.com/css/css_rwd_mediaqueries.asp
if ($(window).width() < 600){
    collapse_toggle('ego-graph-content', $('#ego-header'));
}

/************** tooltip **************/
// interactivity with the ego graph
// timeout for delaying tooltip
var time_out = 300;
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

            // what is shown on the tooltip
            if (node.data('type') === 'Person') {
                // combine individual names to one
                tip_item = node.data('first_name') + node.data('middle_name') + ' ' + node.data('last_name');
            }
            // for paper showing title only
            if (node.data('type') === 'Paper' || node.data('type') === 'Venue' || node.data('type') === 'Dataset') {
                tip_item = node.data('title')
            }

            if (tip_item.length > 0) {
                // css for tooltip
                $('#tooltip').attr('hidden', false);

                $('#tooltip span').text(tip_item).css({
                    "left": px + 15,
                    "top": py + 15,
                });
            }

        }, time_out);

    })
    .on('mousedown', 'node', function (evt) {
        clearTimeout(hoverTimeout);
        var node = evt.target;
        node.style('opacity', 1);
        $('#tooltip').attr('hidden', true);
    })

    // remove tooltip on mouseout
    .on('mouseout', 'node', function (evt) {
        clearTimeout(hoverTimeout);
        var node = evt.target;
        node.style('opacity', 1);
        $('#tooltip').attr('hidden', true);

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