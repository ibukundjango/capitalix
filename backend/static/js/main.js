/* Capitalix — global UI behaviour
   Vanilla JS, no dependencies
   Django-ready
*/

(function () {
  "use strict";

  /* =========================================================
     THEME
  ========================================================= */

  var STORAGE_KEY = "capitalix-theme";

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);

    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      btn.setAttribute(
        "aria-pressed",
        theme === "dark" ? "true" : "false"
      );

      btn.setAttribute(
        "aria-label",
        theme === "dark"
          ? "Switch to light mode"
          : "Switch to dark mode"
      );
    });
  }

  function initTheme() {
    var stored = null;

    try {
      stored = localStorage.getItem(STORAGE_KEY);
    } catch (e) {}

    var prefersDark =
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches;

    applyTheme(stored || (prefersDark ? "dark" : "light"));

    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var current =
          document.documentElement.getAttribute("data-theme");

        var next = current === "dark" ? "light" : "dark";

        applyTheme(next);

        try {
          localStorage.setItem(STORAGE_KEY, next);
        } catch (e) {}
      });
    });
  }


  /* =========================================================
     MOBILE NAVIGATION
  ========================================================= */

  function initMobileNav() {
    var toggle = document.querySelector("[data-nav-toggle]");
    var menu = document.getElementById("mobile-menu");

    if (!toggle || !menu) return;

    function setOpen(open) {
      menu.classList.toggle("is-open", open);

      toggle.setAttribute(
        "aria-expanded",
        open ? "true" : "false"
      );

      toggle.setAttribute(
        "aria-label",
        open ? "Close navigation menu" : "Open navigation menu"
      );

      document.body.classList.toggle("mobile-menu-open", open);
    }

    toggle.addEventListener("click", function () {
      var isOpen = menu.classList.contains("is-open");

      setOpen(!isOpen);
    });

    menu.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        setOpen(false);
      });
    });

    document.addEventListener("keydown", function (e) {
      if (
        e.key === "Escape" &&
        menu.classList.contains("is-open")
      ) {
        setOpen(false);
        toggle.focus();
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 1080) {
        setOpen(false);
      }
    });
  }


  /* =========================================================
     STICKY HEADER
  ========================================================= */

  function initHeaderScroll() {
    var header = document.querySelector(".site-header");

    if (!header) return;

    function update() {
      header.classList.toggle(
        "is-scrolled",
        window.scrollY > 8
      );
    }

    update();

    window.addEventListener("scroll", update, {
      passive: true
    });
  }


  /* =========================================================
     ACCORDIONS / FAQ
  ========================================================= */

  function initAccordions() {
    document.querySelectorAll(".acc-trigger").forEach(function (trigger) {
      var panel = document.getElementById(
        trigger.getAttribute("aria-controls")
      );

      if (!panel) return;

      trigger.addEventListener("click", function () {
        var open =
          trigger.getAttribute("aria-expanded") === "true";

        trigger.setAttribute(
          "aria-expanded",
          open ? "false" : "true"
        );

        panel.hidden = open;
      });
    });
  }


  /* =========================================================
     PASSWORD VISIBILITY
  ========================================================= */

  function initPasswordToggles() {
    document
      .querySelectorAll("[data-password-toggle]")
      .forEach(function (btn) {

        var input = document.getElementById(
          btn.getAttribute("data-password-toggle")
        );

        if (!input) return;

        btn.addEventListener("click", function () {
          var hidden = input.type === "password";

          input.type = hidden ? "text" : "password";

          btn.textContent = hidden ? "Hide" : "Show";

          btn.setAttribute(
            "aria-label",
            hidden ? "Hide password" : "Show password"
          );
        });
      });
  }


  /* =========================================================
     ACCOUNT TYPE SELECTION
  ========================================================= */

  function initAccountSelection() {
    var cards = document.querySelectorAll(
      "[data-account-option]"
    );

    if (!cards.length) return;

    var form = document.getElementById("application-form");
    var typeField = document.getElementById("account_type");
    var chosenLabel = document.getElementById("chosen-account");

    cards.forEach(function (card) {
      card.addEventListener("click", function () {

        cards.forEach(function (c) {
          c.setAttribute("aria-pressed", "false");
        });

        card.setAttribute("aria-pressed", "true");

        var value = card.getAttribute(
          "data-account-option"
        );

        if (typeField) {
          typeField.value = value;
        }

        if (chosenLabel) {
          chosenLabel.textContent = value;
        }

        if (form) {
          form.hidden = false;

          form.scrollIntoView({
            behavior: "smooth",
            block: "start"
          });

          var first = form.querySelector(
            "input, select, textarea"
          );

          if (first) {
            window.setTimeout(function () {
              first.focus();
            }, 420);
          }
        }
      });
    });
  }


  /* =========================================================
     SCROLL REVEAL
  ========================================================= */

  function initReveal() {
    var items = document.querySelectorAll(".reveal");

    if (!items.length) return;

    if (!("IntersectionObserver" in window)) {
      items.forEach(function (el) {
        el.classList.add("is-visible");
      });

      return;
    }

    var io = new IntersectionObserver(
      function (entries) {

        entries.forEach(function (entry) {

          if (entry.isIntersecting) {

            entry.target.classList.add("is-visible");

            io.unobserve(entry.target);
          }
        });
      },
      {
        rootMargin: "0px 0px -8% 0px",
        threshold: 0.08
      }
    );

    items.forEach(function (el) {
      io.observe(el);
    });
  }


  /* =========================================================
     GLOBAL LOADING SPINNER
  ========================================================= */

  function showSpinner() {
    var spinner = document.getElementById("global-spinner");

    if (!spinner) return;

    spinner.style.display = "flex";
  }

  function hideSpinner() {
    var spinner = document.getElementById("global-spinner");

    if (!spinner) return;

    spinner.style.display = "none";
  }

  function initSpinner() {

    /* Hide spinner once page has completely loaded */
    window.addEventListener("load", function () {
      hideSpinner();
    });

    /*
     * Show spinner when a normal form is submitted.
     *
     * Do NOT show it for the support chat form.
     * The chat uses AJAX/fetch and should remain visible.
     */
    document.addEventListener("submit", function (e) {

      var form = e.target;

      if (!form || form.tagName !== "FORM") {
        return;
      }

      /*
       * Don't trigger the global spinner for the AI/support chat.
       */
      if (
        form.id === "chat-form" ||
        form.closest("#support-chat-widget")
      ) {
        return;
      }

      showSpinner();
    });
  }


  /* =========================================================
     SUPPORT CHAT SAFETY
  ========================================================= */

  function initChatSafety() {

    /*
     * The actual chat functionality lives in base.html.
     *
     * This function only makes sure the chat does not
     * interfere with the global page behaviour.
     */

    var chatWidget =
      document.getElementById("support-chat-widget");

    if (!chatWidget) return;

    var chatWindow =
      document.getElementById("chat-window");

    var chatToggle =
      document.getElementById("chat-toggle-btn");

    if (!chatWindow || !chatToggle) return;

    /*
     * Prevent clicks inside the chat from accidentally
     * triggering page-level handlers.
     */
    chatWidget.addEventListener("click", function (e) {
      e.stopPropagation();
    });

    /*
     * Prevent Enter in chat from submitting other forms.
     */
    var chatForm =
      document.getElementById("chat-form");

    if (chatForm) {
      chatForm.addEventListener("submit", function (e) {
        e.stopPropagation();
      });
    }
  }


  /* =========================================================
     INITIALIZE
  ========================================================= */

  function ready(fn) {
    if (document.readyState !== "loading") {
      fn();
    } else {
      document.addEventListener(
        "DOMContentLoaded",
        fn
      );
    }
  }


  ready(function () {

    initTheme();

    initMobileNav();

    initHeaderScroll();

    initAccordions();

    initPasswordToggles();

    initAccountSelection();

    initReveal();

    initSpinner();

    initChatSafety();

  });

})();