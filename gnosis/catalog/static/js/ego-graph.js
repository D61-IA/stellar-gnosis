/************** resizable graph **************/
// simulate stop resizing using timer
var resizeTimer;

// centering only happens after 250ms each time resize stops (mouse is released)
$(window).on('resize', function (e) {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
        center()
        // Run code here, resizing has "stopped"
    }, 250);

});

/************** show/not show relationships **************/
// initial toggle state
var hide_rela = false;

// function for toggle relationships button
function toggle_relas() {
    hide_rela = !hide_rela;
    if (hide_rela) {
        cy.style().selector('edge').style('label', '').update();
        $(".toggle").text("Show relationships");
    } else {
        cy.style().selector('edge').style('label', 'data(label)').update();
        $(".toggle").text("Hide relationships");
    }
}

/************** center graph **************/
// center button
function center() {
    cy.animate({
        center: cy.nodes(),
        fit: {eles: cy.nodes(), padding: 20},
        duration: 50,
    });
}

/************** reset and re-render layout **************/
// reset layout (reload initial layout)
function reset_layout() {
    cy.layout(layout).run();
}

/************** dropdown menu **************/
function show_cites(value) {

    var cat = value;
    //document.write('node[label="'+cat+'"]');
    if (cat === "all relationships") {
        cy.style().selector('node').style('visibility', 'visible').update();
        cy.style().selector('edge').style('visibility', 'visible').update();
    } else {
        cy.style().selector('node').style('visibility', 'hidden').update();
        cy.style().selector('edge').style('visibility', 'hidden').update();
        cy.style().selector('node[label="' + cat + '"]').style('visibility', 'visible').update();
        cy.style().selector('edge[label="' + cat + '"]').style('visibility', 'visible').update();
        cy.style().selector('node[label="origin"]').style('visibility', 'visible').update();
    }

}

/************** tooltip **************/
// interactivity with the ego graph
// timeout for delaying tooltip
var time_out = 1000;
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