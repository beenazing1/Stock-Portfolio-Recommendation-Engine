// Create pie chart of portfolio weights


// Initialize svg
var w = 400;
var h = 400;
var r = h/2;

var vis = d3.select("#piechart").append("svg:svg")
            .data([piedata])
            .attr("width", w)
            .attr("height", h)
            .append("svg:g")
            .attr("transform", "translate(" + r + "," + r + ")");

// Initialize pie chart objects
var pie = d3.layout.pie().value(function(d) { return d.value; });
var arc = d3.svg.arc().outerRadius(r);

// Initialize arcs of pie chart
var arcs = vis.selectAll("g.slice")
              .data(pie)
              .enter()
              .append("svg:g")
              .attr("class", "slice");

// Add different colors for each segment
arcs.append("svg:path")
    .attr("fill", function(d, i) { return piecolors[i]; })
    .attr("d", function(d) {return arc(d);});

// Name text
arcs.append("svg:text")
    .attr("transform", function(d) {
        d.innerRadius = 100;
        d.outerRadius = r;
        return "translate(" + arc.centroid(d) + ")";}
    )
    .attr("text-anchor", "middle")
    .attr("font-size", function(d,i) { if (piedata[i].value < 0.05) { return "8px"; } else { return "14px"; }})
    .attr("font-family", "sans-serif")
    .text(function(d, i) {return piedata[i].label;});


// Percentage text
arcs.append("svg:text")
    .attr("transform", function(d) {
        d.innerRadius = 20;
        d.outerRadius = r;
        return "translate(" + arc.centroid(d) + ")";}
    )
    .attr("text-anchor", "middle")
    .attr("font-size", function(d,i) { if (piedata[i].value < 0.04) { return "6px"; } else { return "12px"; }})
    .attr("font-family", "sans-serif")
    .text(function(d, i) {return 100*Math.round(1000*piedata[i].value)/1000 + '%';});



// Create plot of portfolio performance


// Initialize svg
var width = 600;
var height = 300;
var margin = {top: 30, right: 30, bottom: 30, left: 80};

var svg = d3.select("#performanceplot")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// Parser for date labels
var dateparse = d3.time.format("%Y-%m-%d").parse;

// X and Y scales
var x = d3.time.scale().range([0,width]);
var y = d3.scale.linear().range([height, 0]);

// Line plotting portfolio value
var portline = d3.svg.line()
                 .x(function(d) { return x(dateparse(d[0])); })
                 .y(function(d) { return y(d[1]); });

// Domain and range of plot
x.domain(d3.extent(portvals, function(d) { return dateparse(d[0]); }));
y.domain([d3.min(portvals, function(d) { return d[1]*0.95; }), d3.max(portvals, function(d) { return d[1]*1.05; })]);

var dates = portvals.map(function(item) { return dateparse(item[0]); });

// X axis of plot
var xaxis = d3.svg.axis()
              .scale(x)
              .orient("bottom")
              .tickFormat(d3.time.format("%m/%d/%y"))
              .tickValues(dates);

// Y axis of plot
var yaxis = d3.svg.axis()
              .scale(y)
              .orient("left");

// Plot line
svg.append("path")
   .attr("class", "line")
   .attr("d", portline(portvals))
   .attr("stroke", "steelblue")
   .attr("stroke-width", 2)
   .attr("fill", "none");

// Add axes
svg.append("g")
   .attr("class", "axis")
   .attr("transform", "translate(0," + height + ")")
   .call(xaxis);

svg.append("g")
   .attr("class", "axis")
   .call(yaxis);

// Axis labels
svg.append("svg:text")
       .text("Date")
       .attr("x", width/2)
       .attr("y", height-margin.bottom + 60)
       .style("text-anchor", "middle")
       .attr("font-size", "12px")
       .attr("font-family", "sans-serif");

svg.append("svg:text")
       .attr("transform", "rotate(-90)")
       .attr("x", 0-height/2)
       .attr("y", margin.left - 150)
       .style("text-anchor", "middle")
       .attr("font-size", "12px")
       .attr("font-family", "sans-serif")
       .text("Portfolio Value ($)");

