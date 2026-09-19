/* Mobile navigation.
   Below 700px the link row is too long to sit on one line — seven items on the
   homepage — so it wraps into two rows and pushes the wordmark down the page.
   This turns it into a sheet behind a Menu button at that width and leaves it
   alone above it.

   Progressive enhancement on purpose: the button is built here rather than
   written into twenty-two files, and with JavaScript off the links stay exactly
   as they are now, which is ugly but not broken. The sheet takes its colours
   from --nav-bg and --nav-ink, which each page sets to whatever its header is
   sitting on. */
(function () {
  var bar = document.querySelector(".nav");
  if (!bar) return;
  var list = bar.querySelector("nav");
  if (!list) return;
  if (!list.id) list.id = "sitenav";

  var btn = document.createElement("button");
  btn.type = "button";
  btn.className = "nav-toggle";
  btn.setAttribute("aria-expanded", "false");
  btn.setAttribute("aria-controls", list.id);
  btn.innerHTML = '<span class="nav-bars" aria-hidden="true"></span><span class="nav-word">Menu</span>';
  list.parentNode.insertBefore(btn, list);
  bar.classList.add("has-toggle");

  var word = btn.querySelector(".nav-word");

  function set(open) {
    bar.classList.toggle("nav-open", open);
    btn.setAttribute("aria-expanded", String(open));
    word.textContent = open ? "Close" : "Menu";
    // the sheet covers the viewport; letting the page scroll behind it means
    // closing the menu drops you somewhere you did not choose
    document.documentElement.style.overflow = open ? "hidden" : "";
    if (open) {
      var first = list.querySelector("a");
      if (first) first.focus();
    }
  }

  btn.addEventListener("click", function () {
    set(!bar.classList.contains("nav-open"));
  });

  // every link either navigates or jumps to an anchor on this page; both want
  // the sheet gone
  list.addEventListener("click", function (e) {
    if (e.target.closest("a")) set(false);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && bar.classList.contains("nav-open")) {
      set(false);
      btn.focus();
    }
  });

  // a rotate to landscape past the breakpoint would otherwise leave the sheet
  // open over a nav that is already visible
  var wide = window.matchMedia("(min-width:701px)");
  function onChange() { if (wide.matches) set(false); }
  if (wide.addEventListener) wide.addEventListener("change", onChange);
  else if (wide.addListener) wide.addListener(onChange);
})();
