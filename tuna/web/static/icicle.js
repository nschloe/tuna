class Icicle extends HTMLElement {
  connectedCallback () {
    // this.createShadowRoot()
    this.data = JSON.parse(this.getAttribute('data'));
    this.width = this.getAttribute('width');
    this.height = this.getAttribute('height');
    this.myheight = this.getAttribute('height');
    this.render();
  }

  render () {
    // const color = d3.scaleOrdinal(d3.schemeCategory20c);
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // TODO filter width 0
    // some interesting test cases

    var x = d3.scaleLinear()
      .range([0, this.width]);

    var y = d3.scaleLinear()
      .range([0, this.height]);

    const partition = d3.partition();
    // .size([this.width, this.height])
    // .round(true);

    const svg = d3.select("body").append("svg")
      .attr("width", this.width)
      .attr("height", this.height);

    const root = d3.hierarchy(this.data)
      .sum( function(d) { return d.value; })
      .sort(function(a, b) { return b.value - a.value; });

    partition(root);

    // Put text and rectangle into a group;
    // cf. <https://stackoverflow.com/a/6732550/353337>.
    const g = svg.selectAll("g").data(root.descendants())
      .enter().append("g");

    const rect = g.append("rect")
      .attr("x", function(d) { return x(d.x0); })
      .attr("y", function(d) { return y(d.y0); })
      .attr("width", function(d) { return x(d.x1 - d.x0); })
      .attr("height", function(d) { return y(d.y1 - d.y0); })
      .attr("fill", function(d) { return color((d.children ? d : d.parent).key); })
      .on("click", clicked);

    // title, typically rendered as tooltip
    rect.append("title")
      .text(function(d) { return d.data.name + "\n" + d.value + " s"; });

    // Now add the text. First, the clip path.
    const clipPath = g.append("clipPath")
      .attr("id", function(d) { return "cp_" + Math.round(x(d.x0)) + "_" + Math.round(x(d.x1)) + "_" + Math.round(y(d.y0)) + "_" + Math.round(y(d.y1)); })
    const clipRect = clipPath.append("rect")
      .attr("x", function(d) { return x(d.x0); })
      .attr("y", function(d) { return y(d.y0); })
      .attr("width", function(d) { return x(d.x1) - x(d.x0); })
      .attr("height", function(d) { return y(d.y1) - y(d.y0); });
    // Now the text. Multiline text is realized with <tspan> in SVG.
    const text = g.append("text")
      .attr("y", function(d) { return y(d.y0 + d.y1)/2; })
      .attr("alignment-baseline", "middle")
      .attr("text-anchor", "middle")
      .attr("fill", "white")
      .attr("clip-path", function(d) { return "url(#" + "cp_" + Math.round(x(d.x0)) + "_" + Math.round(x(d.x1)) + "_" + Math.round(y(d.y0)) + "_" + Math.round(y(d.y1)) + ")"; });
    const tspan1 = text.append("tspan")
      .text(function(d) { return d.data.name })
      .attr("font-family", "sans-serif")
      .attr("x", function(d) { return x(d.x0 + d.x1)/2; });
    const tspan2 = text.append("tspan")
      .text(function(d) { return d3.format(".3e")(d.value) + " s" })
      .attr("font-family", "sans-serif")
      .attr("x", function(d) { return x(d.x0 + d.x1)/2; })
      .attr("dy", "1.5em");

    // make height available in clicked()
    const height = this.height;

    function clicked(d) {
      x.domain([d.x0, d.x1]);
      y.domain([d.y0, 1]).range([d.y0 ? 20 : 0, height]);

      rect.transition()
        .duration(750)
        .attr("x", function(d) { return x(d.x0); })
        .attr("y", function(d) { return y(d.y0); })
        .attr("width", function(d) { return x(d.x1) - x(d.x0); })
        .attr("height", function(d) { return y(d.y1) - y(d.y0); });

      clipRect.transition()
        .duration(750)
        .attr("x", function(d) { return x(d.x0); })
        .attr("y", function(d) { return y(d.y0); })
        .attr("width", function(d) { return x(d.x1) - x(d.x0); })
        .attr("height", function(d) { return y(d.y1) - y(d.y0); });

      text.transition()
        .duration(750)
        .attr("y", function(d) { return y((d.y0 + d.y1)/2); });

      tspan1.transition()
        .duration(750)
        .attr("x", function(d) { return x((d.x0 + d.x1)/2); });

      tspan2.transition()
        .duration(750)
        .attr("x", function(d) { return x((d.x0 + d.x1)/2); });
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
