// note: utility script should be placed before scripts that use functions in utility script
// node title width
var textMaxWidth = '100';

function getCustomNodeStyle(style) {
    var nodeStyle = {
        'width': 20,
        'height': 20,
        'background-color': '#39acff',
        'label': 'data(title)',
        'text-opacity': 1,
        'text-wrap': 'ellipsis',
        'text-max-width': textMaxWidth,
        'text-background-color': '#FFFFFF',
        'text-outline-opacity': 1,
        'text-outline-color': '#FFFFFF',
        'text-outline-width': '1px',
        'font-size': '10px',
        'border-width': '1.5px',
        'border-color': "#9d8b71",
        'visibility': 'visible'
    };
    for (var key in style) {
        if (style.hasOwnProperty(key)) {
            nodeStyle[key] = style[key];
        }
    }
    return nodeStyle;
}

function getCustomEdgeStyle(style) {
    var edgeStyle = {
        'width': 2,
        'label': 'data(label)',
        'line-color': '#2bd6ad',
        'line-style': 'data(line)',
        'curve-style': 'bezier',
        'target-arrow-color': '#2bd6ad',
        'target-arrow-shape': 'triangle',
        'text-opacity': 1,
        'text-outline-opacity': 1,
        'text-outline-color': '#FFFFFF',
        'text-outline-width': '1px',
        'font-size': '9px',
        'visibility': 'visible'

    };
    for (var key in style) {
        if (style.hasOwnProperty(key)) {
            edgeStyle[key] = style[key];
        }
    }
    return edgeStyle;
}