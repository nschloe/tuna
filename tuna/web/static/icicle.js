class Icicle extends HTMLElement {
  connectedCallback () {
    // this.createShadowRoot()
    this.data = JSON.parse(this.getAttribute('data'));
    this.width = this.getAttribute('width');
    this.rowHeight = this.getAttribute('row-height');
    this.render();
  }

  render () {
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // TODO some interesting test cases

    const root = d3.hierarchy(this.data)
      .sum(function(d) { return d.value; })
      .sort(function(a, b) { return b.value - a.value; });

    const numLevels = root.height + 1;
    const height = numLevels * this.rowHeight;

    var x = d3.scaleLinear()
      .range([0, this.width]);

    var y = d3.scaleLinear()
      .range([0, height]);

    const svg = d3.select("body").append("svg")
      .attr("width", this.width)
      .attr("height", height);

    const totalRuntime = root.value;

    const partition = d3.partition();
    // .size([this.width, height])
    // .round(true);
    partition(root);

    // Put text and rectangle into a group;
    // cf. <https://stackoverflow.com/a/6732550/353337>.
    const g = svg.selectAll("g").data(
      // Only get the blocks above a certain threshold width
      root.descendants().filter(d => x(d.x1 - d.x0) > 1.0)
    )
    .enter().append("g");

    const rect = g.append("rect")
      .attr("x", function(d) { return x(d.x0); })
      .attr("y", function(d) { return y(d.y0); })
      .attr("width", function(d) { return x(d.x1 - d.x0); })
      .attr("height", this.rowHeight)
      .on("click", clicked);
      // .attr("fill", function(d) { return color((d.children ? d : d.parent).key); })

    // title, typically rendered as tooltip
    rect.append("title")
      .text(function(d) {
        return d.data.name + "\n" + d.value + " s  (" + d3.format(".2f")(d.value / totalRuntime * 100) + "%)"
      });

    // Now add the text. First, the clip path.
    const clipPath = g.append("clipPath")
      .attr("id", function(d) { return "cp_" + Math.round(x(d.x0)) + "_" + Math.round(x(d.x1)) + "_" + Math.round(y(d.y0)) + "_" + Math.round(y(d.y1)); })
    const clipRect = clipPath.append("rect")
      .attr("x", function(d) { return x(d.x0); })
      .attr("y", function(d) { return y(d.y0); })
      .attr("width", function(d) { return x(d.x1) - x(d.x0); })
      .attr("height", this.rowHeight);
    // Now the text. Multiline text is realized with <tspan> in SVG.
    const text = g.append("text")
      .attr("y", function(d) { return y(d.y0 + d.y1)/2; })
      .attr("alignment-baseline", "middle")
      .attr("text-anchor", "middle")
      .attr("fill", "white")
      .attr("clip-path", function(d) { return "url(#" + "cp_" + Math.round(x(d.x0)) + "_" + Math.round(x(d.x1)) + "_" + Math.round(y(d.y0)) + "_" + Math.round(y(d.y1)) + ")"; });
    const tspan1 = text.append("tspan")
      .text(function(d) {
        let arr = d.data.name.split("::");
        console.log(arr[0].split("/")[-1]);
        arr[0] = arr[0].split("/").pop();
        return arr.join("::");
      })
      .attr("font-family", "sans-serif")
      .attr("x", function(d) { return x(d.x0 + d.x1)/2; });
    const tspan2 = text.append("tspan")
      .text(function(d) { return d3.format(".3f")(d.value) + " s  (" + d3.format(".1f")(d.value / totalRuntime * 100) + "%)" })
      .attr("font-family", "sans-serif")
      .attr("x", function(d) { return x(d.x0 + d.x1)/2; })
      .attr("dy", "1.5em");

    // make height available in clicked()
    function clicked(d) {
      x.domain([d.x0, d.x1]);
      y.domain([d.y0, 1]).range([d.y0 ? 20 : 0, height]);

      rect.transition()
        .duration(750)
        .attr("x", function(d) { return x(d.x0); })
        .attr("y", function(d) { return y(d.y0); })
        .attr("width", function(d) { return x(d.x1) - x(d.x0); });

      clipRect.transition()
        .duration(750)
        .attr("x", function(d) { return x(d.x0); })
        .attr("y", function(d) { return y(d.y0); })
        .attr("width", function(d) { return x(d.x1) - x(d.x0); });

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
