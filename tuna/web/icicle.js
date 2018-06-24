class Icicle extends HTMLElement {
  connectedCallback () {
    // this.createShadowRoot()
    this.filename = this.getAttribute('filename')
    this.width = this.getAttribute('width')
    this.height = this.getAttribute('height')
    this.render()
  }

  render () {
    // const color = d3.scaleOrdinal(d3.schemeCategory20c);
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // TODO filter width 0
    // zoom
    // unzoom
    // some interesting test cases

    const partition = d3.partition()
      .size([this.width, this.height])
      .round(true);

    const svg = d3.select("body").append("svg")
      .attr("width", this.width)
      .attr("height", this.height);

    d3.json(this.filename).then(function(data) {
      const root = d3.hierarchy(data)
        .sum( function(d) { return d.value; })
        .sort(function(a, b) { return b.value - a.value; });

      partition(root);

      // Put text and rectangle into a group;
      // cf. <https://stackoverflow.com/a/6732550/353337>.
      const g = svg.selectAll("g").data(root.descendants())
        .enter().append("g");

      const rect = g.append("rect")
        .attr("x", function(d) { return d.x0; })
        .attr("y", function(d) { return d.y0; })
        .attr("width", function(d) { return d.x1 - d.x0; })
        .attr("height", function(d) { return d.y1 - d.y0; })
        .attr("fill", function(d) { return color((d.children ? d : d.parent).key); })
        .on("click", clicked);

      // title, typically rendered as tooltip
      rect.append("title")
        .text(function(d) { return d.data.name + "\n" + d.value + " s"; });

      // Now add the text. First, the clip path.
      const clipPath = g.append("clipPath")
        .attr("id", function(d) { return "cp_" + d.x0 + "_" + d.x1 + "_" + d.y0 + "_" + d.y1; })
      clipPath.append("rect")
        .attr("x", function(d) { return d.x0; })
        .attr("y", function(d) { return d.y0; })
        .attr("width", function(d) { return d.x1 - d.x0; })
        .attr("height", function(d) { return d.y1 - d.y0; });
      // Now the text. Multiline text is realized with <tspan> in SVG.
      const text = g.append("text")
        .attr("y", function(d) { return (d.y0 + d.y1)/2; })
        .attr("alignment-baseline", "middle")
        .attr("text-anchor", "middle")
        .attr("fill", "white")
        .attr("clip-path", function(d) { return "url(#" + "cp_" + d.x0 + "_" + d.x1 + "_" + d.y0 + "_" + d.y1 + ")"; });
      text.append("tspan")
        .text(function(d) { return d.data.name })
        .attr("font-family", "sans-serif")
        .attr("x", function(d) { return (d.x0 + d.x1)/2; });
      text.append("tspan")
        .text(function(d) { return d3.format(".3e")(d.value) + " s" })
        .attr("font-family", "sans-serif")
        .attr("x", function(d) { return (d.x0 + d.x1)/2; })
        .attr("dy", "1.5em");
    });

    function clicked(d) {
      console.log("clicked");
      // x.domain([d.x0, d.x1]);
      // y.domain([d.y0, 1]).range([d.y0 ? 20 : 0, height]);

      // rect.transition()
      //     .duration(750)
      //     .attr("x", function(d) { return d.x0; })
      //     .attr("y", function(d) { return d.y0; })
      //     .attr("width", function(d) { return d.x1 - d.x0; })
      //     .attr("height", function(d) { return d.y1 - d.y0; });
    }
  }
}

try {
  customElements.define('x-icicle', Icicle)
} catch (err) {
  console.log(err);
  const h3 = document.createElement('h3')
  h3.innerHTML = "This site uses webcomponents which don't work in all browsers. Try this site in a browser that supports them."
  document.body.appendChild(h3)
}
