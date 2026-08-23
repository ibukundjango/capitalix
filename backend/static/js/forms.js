/* Capitalix — lightweight client-side form validation (vanilla JS)
   NOTE: This is presentation-layer validation only. No data is submitted or
   stored anywhere. Every form below is ready to be wired to Django views:
   add {% csrf_token %}, an action="{% url '...' %}" and server-side validation.
   Django-ready: move to static/js/forms.js */
(function () {
  "use strict";

  var EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  function fieldError(input) {
    var id = input.getAttribute("aria-describedby");
    return id ? document.getElementById(id) : null;
  }

  function setError(input, message) {
    var slot = fieldError(input);
    if (message) {
      input.setAttribute("aria-invalid", "true");
      if (slot) slot.textContent = message;
    } else {
      input.removeAttribute("aria-invalid");
      if (slot) slot.textContent = "";
    }
  }

  function validateField(input) {
    var value = (input.value || "").trim();
    var label = input.getAttribute("data-label") || "This field";

    if (input.hasAttribute("required") && !value) {
      setError(input, label + " is required.");
      return false;
    }
    if (value && input.type === "email" && !EMAIL.test(value)) {
      setError(input, "Enter a valid email address.");
      return false;
    }
    if (value && input.type === "tel" && value.replace(/[^0-9]/g, "").length < 7) {
      setError(input, "Enter a valid phone number.");
      return false;
    }
    if (input.type === "password" && value && value.length < 8) {
      setError(input, "Use at least 8 characters.");
      return false;
    }
    setError(input, "");
    return true;
  }

  function initForm(form) {
    var fields = form.querySelectorAll("input, select, textarea");

    fields.forEach(function (input) {
      if (input.type === "hidden" || input.type === "submit") return;
      input.addEventListener("blur", function () { validateField(input); });
      input.addEventListener("input", function () {
        if (input.getAttribute("aria-invalid") === "true") validateField(input);
      });
    });

    form.addEventListener("submit", function (e) {
      var ok = true;
      var firstBad = null;

      fields.forEach(function (input) {
        if (input.type === "hidden" || input.type === "submit") return;
        if (!validateField(input)) {
          ok = false;
          if (!firstBad) firstBad = input;
        }
      });

      // No backend is connected yet — always prevent a real submission.
      e.preventDefault();

      var status = form.querySelector("[data-form-status]");
      if (!ok) {
        if (firstBad) firstBad.focus();
        if (status) {
          status.textContent =
            "Please review the highlighted fields before continuing.";
        }
        return;
      }
      if (status) {
        status.textContent =
          form.getAttribute("data-success-message") ||
          "Form validated. This interface is ready to be connected to the Capitalix backend — no information was submitted or stored.";
      }
    });
  }

  function init() {
    document.querySelectorAll("[data-validate]").forEach(initForm);
  }

  if (document.readyState !== "loading") init();
  else document.addEventListener("DOMContentLoaded", init);
})();
