class Icicle extends HTMLElement {
  connectedCallback () {
    // this.shadow = this.createShadowRoot();
    this.data = JSON.parse(this.getAttribute('data'));

    const paddingLeft = parseFloat(getComputedStyle(this.parentElement).paddingLeft);
    const paddingRight = parseFloat(getComputedStyle(this.parentElement).paddingRight);
    this.width = this.parentElement.offsetWidth - paddingLeft - paddingRight;

    this.rowHeight = this.getAttribute('row-height');
    this.render();
  }

  render () {
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    const root = d3.hierarchy(this.data)
      .sum(d => d.value)
      .sort((a, b) => b.value - a.value);

    // Give each node a unique id (used for clip paths)
    let id = 0;
    root.descendants().forEach(function(d) {d.id = id; id++;});

    const strokeWidth = 1;
    const numLevels = root.height + 1;
    const height = numLevels * this.rowHeight + numLevels * strokeWidth;

    const x = d3.scaleLinear()
      .range([0, this.width]);

    const y = d3.scaleLinear()
      .range([0, height]);

    const svg = d3.select(this).append("svg")
      .attr("width", this.width)
      .attr("height", height);

    const totalRuntime = root.value;

    const partition = d3.partition();
    // .size([this.width, height])
    // .round(true);
    partition(root);

    // array for storing all entities that are animated upon transition
    const to_anim = {};

    // Put text and rectangle into a group;
    // cf. <https://stackoverflow.com/a/6732550/353337>.
    const g = svg.selectAll("g").data(
      // Only get the blocks above a certain threshold width
      root.descendants().filter(d => x(d.x1 - d.x0) > 1.0)
    )
    .enter()
    .call(el => el.append("g")
      .call(el => el.append("rect")
        .call(rect => { to_anim.rect = rect; })
        .attr("x", d => x(d.x0))
        .attr("y", d => y(d.y0))
        .attr("width", d => x(d.x1 - d.x0))
        .attr("height", this.rowHeight)
        .on("click", clicked)
        // .attr("fill", d => color((d.children ? d : d.parent).key))

        // title, typically rendered as tooltip
        .call(el => el.append("title")
          .text(d => (
            d.data.name + "\n" +
            d.value + " s  (" + d3.format(".2f")(d.value / totalRuntime * 100) + "%)"
          ))
        )
      )
      // Now add the text. First, the clip path.
      .call(el => el.append("clipPath")
        .attr("id", d => "cp" + d.id)
        .call(el => el.append("rect")
          .call(clipRect => { to_anim.clipRect = clipRect; })
          .attr("x", d => x(d.x0))
          .attr("y", d => y(d.y0))
          .attr("width", d => x(d.x1) - x(d.x0))
          .attr("height", this.rowHeight)
        )
      )
      // Now the text. Multiline text is realized with <tspan> in SVG.
      .call(el => el.append("text")
        .call(text => { to_anim.text = text; })
        .attr("y", d => y(d.y0 + d.y1)/2)
        .attr("alignment-baseline", "middle")
        .attr("text-anchor", "middle")
        .attr("fill", "white")
        .attr("clip-path", d => "url(#" + "cp" + d.id + ")")
        .call(el => el.append("tspan")
          .call(tspan1 => { to_anim.tspan1 = tspan1; })
          .text(d => {
            let arr = d.data.name.split("::");
            arr[0] = arr[0].split("/").pop();
            return arr.join("::");
          })
          .attr("x", d => x(d.x0 + d.x1)/2)
        )
        .call(el => el.append("tspan")
          .call(tspan2 => { to_anim.tspan2 = tspan2; })
          .text(d => d3.format(".3f")(d.value) + " s  (" + d3.format(".1f")(d.value / totalRuntime * 100) + "%)")
          .attr("x", d => x(d.x0 + d.x1)/2)
          .attr("dy", "1.5em")
        )
      )
    );

    // Make rowHeight available in clicked()
    const rowHeight = this.rowHeight;

    function clicked(d) {
      const offset = d.y0 ? 20 : 0;
      const height = root.height - d.depth;
      const newHeight = (height+1) * rowHeight + (height+1) * strokeWidth;
      x.domain([d.x0, d.x1]);
      y.domain([d.y0, 1]).range([offset, newHeight + offset]);

      to_anim.rect.transition()
        .duration(750)
        .attr("x", d => x(d.x0))
        .attr("y", d => y(d.y0))
        .attr("width", d => x(d.x1) - x(d.x0));

      to_anim.clipRect.transition()
        .duration(750)
        .attr("x", d => x(d.x0))
        .attr("y", d => y(d.y0))
        .attr("width", d => x(d.x1) - x(d.x0));

      to_anim.text.transition()
        .duration(750)
        .attr("y", d => y((d.y0 + d.y1)/2));

      to_anim.tspan1.transition()
        .duration(750)
        .attr("x", d => x((d.x0 + d.x1)/2));

      to_anim.tspan2.transition()
        .duration(750)
        .attr("x", d => x((d.x0 + d.x1)/2));
    }
  }
}

try {
  customElements.define('x-icicle', Icicle);
} catch (err) {
  console.log(err);
  const h3 = document.createElement('h3');
  h3.innerHTML = "This site uses webcomponents which don't work in all browsers. Try this site in a browser that supports them.";
  document.body.appendChild(h3);
}
