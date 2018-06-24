class Icicle extends HTMLElement {
  connectedCallback () {
    this.createShadowRoot()
    this.filename = this.getAttribute('filename')
    this.width = this.getAttribute('width')
    this.height = this.getAttribute('height')
    this.render()
  }

  // addStyle () {
  //   const styleTag = document.createElement('style')
  //   styleTag.textContent = getStyle(this.size)
  //   this.shadowRoot.appendChild(styleTag)
  // }

  // addSpanEventListeners (span) {
  //   span.addEventListener('mouseover', () => { span.classList.add('hovered') })
  //   span.addEventListener('animationend', () => { span.classList.remove('hovered') })
  // }

  // createSpan (letter) {
  //   const span = document.createElement('span')
  //   span.classList.add('letter')
  //   span.innerHTML = letter
  //   this.addSpanEventListeners(span)
  //   return span
  // }

  // addSpans (div) {
  //   Array.from(this.text).forEach(letter => {
  //     let span = this.createSpan(letter)
  //     div.appendChild(span)
  //   })
  // }

  render () {
    // const div = document.createElement('div')
    // div.classList.add('header')
    // this.shadowRoot.appendChild(div)
    // this.addSpans(div)
    // this.addStyle()
    //
  // const color = d3.scaleOrdinal(d3.schemeCategory20c);
  const color = d3.scaleOrdinal(d3.schemeCategory10);

  const partition = d3.partition()
     .size([this.width, this.height]);

  const svg = d3.select("body").append("svg")
      .attr("width", this.width)
      .attr("height", this.height);

  d3.json(this.filename).then(function(data) {
    const root = d3.hierarchy(data);
    root.sum( function(d) { return d.value; });
    root.sort();

    partition(root);

    const rect = svg.selectAll("rect");
    rect = rect
        .data(root.descendants())
        .enter().append("rect")
          .attr("x", function(d) { return d.x0; })
          .attr("y", function(d) { return d.y0; })
          .attr("width", function(d) { return d.x1 - d.x0; })
          .attr("height", function(d) { return d.y1 - d.y0; })
          .attr("fill", function(d) { return color((d.children ? d : d.parent).key); });
          // .on("click", clicked);
});

// function clicked(d) {
//   // x.domain([d.x0, d.x1]);
//   // y.domain([d.y0, 1]).range([d.y0 ? 20 : 0, height]);
//
//   rect.transition()
//       .duration(750)
//       .attr("x", function(d) { return d.x0; })
//       .attr("y", function(d) { return d.y0; })
//       .attr("width", function(d) { return d.x1 - d.x0; })
//       .attr("height", function(d) { return d.y1 - d.y0; });
// }

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
