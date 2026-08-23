/* Capitalix — illustrative loan payment calculator (vanilla JS)
   Results are estimates only; no backend involved.
   Django-ready: move to static/js/calculator.js */
(function () {
  "use strict";

  function money(value) {
    if (!isFinite(value)) return "$0";
    return value.toLocaleString("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    });
  }

  function money2(value) {
    if (!isFinite(value)) return "$0.00";
    return value.toLocaleString("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  function init() {
    var form = document.getElementById("loan-calculator");
    if (!form) return;

    var amount = document.getElementById("calc-amount");
    var rate = document.getElementById("calc-rate");
    var term = document.getElementById("calc-term");
    var amountOut = document.getElementById("calc-amount-out");
    var rateOut = document.getElementById("calc-rate-out");
    var termOut = document.getElementById("calc-term-out");
    var payment = document.getElementById("calc-payment");
    var totalInterest = document.getElementById("calc-interest");
    var totalPaid = document.getElementById("calc-total");
    var payments = document.getElementById("calc-payments");

    function compute() {
      var principal = Math.max(0, parseFloat(amount.value) || 0);
      var apr = Math.max(0, parseFloat(rate.value) || 0);
      var months = Math.max(1, parseInt(term.value, 10) || 1);
      var monthlyRate = apr / 100 / 12;

      var monthly =
        monthlyRate === 0
          ? principal / months
          : (principal * monthlyRate) / (1 - Math.pow(1 + monthlyRate, -months));

      var total = monthly * months;

      if (amountOut) amountOut.textContent = money(principal);
      if (rateOut) rateOut.textContent = apr.toFixed(2) + "%";
      if (termOut) {
        termOut.textContent =
          months % 12 === 0 ? months / 12 + " years" : months + " months";
      }
      if (payment) payment.textContent = money2(monthly);
      if (totalInterest) totalInterest.textContent = money2(Math.max(0, total - principal));
      if (totalPaid) totalPaid.textContent = money2(total);
      if (payments) payments.textContent = months + " payments";
    }

    [amount, rate, term].forEach(function (input) {
      if (!input) return;
      input.addEventListener("input", compute);
      input.addEventListener("change", compute);
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      compute();
    });

    compute();
  }

  if (document.readyState !== "loading") init();
  else document.addEventListener("DOMContentLoaded", init);
})();
