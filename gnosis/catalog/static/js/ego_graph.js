/************** resizable graph **************/
// simulate stop resizing using timer
var resizeTimer;

var $cy = $('#cy');

// centering only happens after 250ms each time resize stops
$(window).on('resize', function (e) {
    clearTimeout(resizeTimer);
    $cy.css('height', $cy.css('width'));
    resizeTimer = setTimeout(function () {
        center();
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

var $graphfilter = $('.graphfilter');

var $buttons = $('.filter_btn');

function reset_nodes() {
    collection = cy.elements();
    cy.style().selector('node').style('visibility', 'visible').update();
    cy.style().selector('edge').style('visibility', 'visible').update();
    collection.layout(cy_layout).run();

    center();

    $buttons.attr('data-pressed', 'true').addClass('active');
    // sync select menu option to 'all'
    $graphfilter.val('all');
}

$('.ego_button_reset').click(function () {
    reset_nodes();
});

$('.ego_button_toggle').click(function () {
    toggle_relas();
});


/************** graph filtering function **************/
// filter for single node type or relationship type
// labels indicated relas, types indicate nodes
function show_relas(relas) {
    if (relas === "all") {
        collection = cy.elements();
        cy.style().selector('node').style('visibility', 'visible').update();
        cy.style().selector('edge').style('visibility', 'visible').update();
    } else {
        // get all elements on the graph
        collection = cy.filter((element) => {
            return element.data('label') === relas
                || element.data('label') === "origin"
        });
        cy.style().selector('node').style('visibility', 'hidden').update();
        cy.style().selector('edge').style('visibility', 'hidden').update();
        cy.style().selector('[label="' + relas + '"]').style('visibility', 'visible').update();
        cy.style().selector('node[label="origin"]').style('visibility', 'visible').update();
    }

    collection.layout(cy_layout).run();
    center();
}

$buttons.click(function () {
    var type = $(this).attr('data-type');
    var data_name = $(this).attr('data-name');
    // get buttons in mobile view and desk view.
    var $these = $('[data-name="' + data_name + '"]');

    if ($(this).attr('data-pressed') === 'false') {

        // update the graph
        cy.style().selector('[type="' + type + '"]').style('visibility', 'visible').update();

        // set the state of the buttons to 'pressed'
        $these.attr('data-pressed', 'true');
        // update the button style
        $these.addClass('active')
    } else {
        //update the graph
        cy.style().selector('[type="' + type + '"]').style('visibility', 'hidden').update();
        cy.style().selector('[label="origin"]').style('visibility', 'visible').update();

        // set the state of the buttons to 'not pressed'
        $these.attr('data-pressed', 'false');
        // update the button style
        $these.removeClass('active')

    }

    collection = cy.filter((element) => {
        return element.visible();
    });
    collection.layout(cy_layout).run();

    center();
});

$graphfilter.change(function () {
    show_relas(this.value, 'all');
    var data_type = $('option:selected', this).attr('data-type');

    $buttons.each(function (index, element) {
        if (data_type === 'all') {
            $(element).addClass('active')
        } else if (data_type !== $(element).attr('data-type')) {
            $(element).removeClass('active')
        } else {
            $(element).addClass('active')
        }
    })
});


/************** collapse ego-graph **************/
// stores state of the collapse target
var hidden = false;

var ego_header = $('#ego_header');

$(ego_header).click(function () {
    hidden = !hidden;
    if (hidden) {
        $(this).children('.drop_indicator').text('arrow_drop_down');
        $('#ego_graph_content').hide(200);

    } else {
        $(this).children('.drop_indicator').text('arrow_drop_up');
        $('#ego_graph_content').show(200);
    }
});

// collapse initially if device width is < 600
// device widths reference: https://www.w3schools.com/css/css_rwd_mediaqueries.asp
if ($(window).width() < 600) {
    $(ego_header).click()
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
                tip_item = node.data('name');
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
