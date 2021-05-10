class Icicle extends HTMLElement {
  connectedCallback() {
    // this.shadow = this.createShadowRoot();
    this.data = JSON.parse(this.getAttribute("data"));
    this.rowHeight = this.getAttribute("row-height");
    this.svg = d3.select(this).append("svg");
    this.svg.style("width", "100%");
    this.render();
  }

  get width() {
    return this.svg.node().getBoundingClientRect().width;
  }

  render() {
    // const color = d3.scaleOrdinal(d3.schemeCategory10);
    //
    const root = d3
      .hierarchy(this.data)
      .sum((d) => d.value)
      .sort((a, b) => b.value - a.value);

    // Give each node a unique id (used for clip paths)
    let id = 0;
    root.descendants().forEach(function (d) {
      d.id = id;
      id++;
    });

    // Find the resetZoomButton and call clicked() with root
    const button = document.getElementById("resetZoomButton");
    button.addEventListener("click", (evt) => {
      clicked.bind(this)(evt, root);
    });

    const strokeWidth = 1;
    const numLevels = root.height + 1;
    const height = numLevels * this.rowHeight + numLevels * strokeWidth;

    this.svg.attr("height", height);

    const x = d3.scaleLinear().range([0, this.width]);
    const y = d3.scaleLinear().range([0, height]);

    const totalRuntime = root.value;

    const partition = d3.partition();
    // .size([this.width, height])
    // .round(true);
    partition(root);

    // Put text and rectangle into a group;
    // cf. <https://stackoverflow.com/a/6732550/353337>.
    const all_g = this.svg.selectAll("g");
    const g = all_g
      .data(
        // Only get the blocks above a certain threshold width
        root.descendants().filter((d) => x(d.x1 - d.x0) > 1.0)
      )
      .enter()
      .append("g")
      .attr("class", (d) => "color" + d.data.color)
      // binding ensures `this` is correct in clicked:
      .on("click", clicked.bind(this));

    // append <title>, rendered as tooltip
    g.append("title").text((d) => {
      let out = d.data.text[0] + " ";
      if (d.data.text.length > 1) {
        out += d.data.text[1];
      } else {
        out +=
          d3.format(".3f")(d.value) +
          " s  (" +
          d3.format(".1%")(d.value / totalRuntime) +
          ")";
      }
      return out;
    });

    const rect = g
      .append("rect")
      .attr("x", (d) => x(d.x0))
      .attr("y", (d) => y(d.y0))
      .attr("width", (d) => x(d.x1 - d.x0))
      .attr("height", this.rowHeight);
    // .attr("fill", d => color((d.children ? d : d.parent).key))

    // First, the clip path, same as the rect.
    // It'd be nice to having to repeat outselves here, but the <use> suggestion from
    // <https://stackoverflow.com/q/23998457/353337> doesn't work.
    const cp = g.append("clipPath").attr("id", (d) => "cp" + d.id);
    const clipRect = cp
      .append("rect")
      .attr("x", (d) => x(d.x0))
      .attr("y", (d) => y(d.y0))
      .attr("width", (d) => x(d.x1) - x(d.x0))
      .attr("height", this.rowHeight);

    // Now the text. Multiline text is realized with <tspan> in SVG.
    const text = g
      .append("text")
      .attr("y", (d) => y(d.y0 + d.y1) / 2)
      .attr("alignment-baseline", "middle")
      .attr("text-anchor", "middle")
      .attr("fill", "white")
      .attr("clip-path", (d) => "url(#" + "cp" + d.id + ")");

    const tspan1 = text
      .append("tspan")
      .text((d) => d.data.text[0])
      .attr("x", (d) => x(d.x0 + d.x1) / 2);

    const tspan2 = text
      .append("tspan")
      .text((d) => {
        if (d.data.text.length > 1) {
          return d.data.text[1];
        }
        return (
          d3.format(".3f")(d.value) +
          " s  (" +
          d3.format(".1%")(d.value / totalRuntime) +
          ")"
        );
      })
      .attr("x", (d) => x(d.x0 + d.x1) / 2)
      .attr("dy", "1.5em");

    function clicked(evt, d) {
      const offset = d.y0 ? 20 : 0;
      const height = root.height - d.depth;
      const newHeight =
        (height + 1) * this.rowHeight + (height + 1) * strokeWidth;
      x.domain([d.x0, d.x1]).range([0, this.width]);
      y.domain([d.y0, 1]).range([offset, newHeight + offset]);
      const trans = d3.transition().duration(300);
      rect
        .transition(trans)
        .attr("x", (d) => x(d.x0))
        .attr("y", (d) => y(d.y0))
        .attr("width", (d) => x(d.x1) - x(d.x0));
      clipRect
        .transition(trans)
        .attr("x", (d) => x(d.x0))
        .attr("y", (d) => y(d.y0))
        .attr("width", (d) => x(d.x1) - x(d.x0));
      text.transition(trans).attr("y", (d) => y((d.y0 + d.y1) / 2));
      tspan1.transition(trans).attr("x", (d) => x((d.x0 + d.x1) / 2));
      tspan2.transition(trans).attr("x", (d) => x((d.x0 + d.x1) / 2));
    }

    // TODO: This repeats much of the content of `clicked`
    window.addEventListener("resize", (e) => {
      x.range([0, this.width]);
      rect
        .attr("x", (d) => x(d.x0))
        .attr("y", (d) => y(d.y0))
        .attr("width", (d) => x(d.x1) - x(d.x0));
      clipRect
        .attr("x", (d) => x(d.x0))
        .attr("y", (d) => y(d.y0))
        .attr("width", (d) => x(d.x1) - x(d.x0));
      text.attr("y", (d) => y((d.y0 + d.y1) / 2));
      tspan1.attr("x", (d) => x((d.x0 + d.x1) / 2));
      tspan2.attr("x", (d) => x((d.x0 + d.x1) / 2));
    });
  }
}

try {
  customElements.define("x-icicle", Icicle);
} catch (err) {
  console.log(err);
  const h3 = document.createElement("h3");
  h3.innerHTML =
    "This site uses webcomponents which don't work in all browsers. Try this site in a browser that supports them.";
  document.body.appendChild(h3);
}
