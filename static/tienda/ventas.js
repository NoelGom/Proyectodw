(function () {
  function fmt(num) {
    var n = parseFloat(num || 0);
    return "Q " + n.toFixed(2);
  }

  function updateRow(row) {
    var select = row.querySelector('select');
    var litros = parseFloat(row.querySelector('input[name$="litros"]').value || 0);
    var precioInput = row.querySelector('input[name$="precio_unitario"]');

    if (select && select.value) {
      var pid = parseInt(select.value, 10);
      var precios = window.PRODUCT_PRICES || {};
      var precio = parseFloat(precios[pid] || 0);
      if (!precioInput.value || parseFloat(precioInput.value) === 0) {
        precioInput.value = precio.toFixed(2);
      }
    }
  }

  function updateTotal() {
    var total = 0;
    document.querySelectorAll('.detalle-row').forEach(function (row) {
      var litros = parseFloat(row.querySelector('input[name$="litros"]').value || 0);
      var precio = parseFloat(row.querySelector('input[name$="precio_unitario"]').value || 0);
      total += litros * precio;
    });
    var t = document.getElementById('total');
    if (t) t.textContent = fmt(total);
  }

  function hook(row) {
    var select = row.querySelector('select');
    var litrosInput = row.querySelector('input[name$="litros"]');
    var precioInput = row.querySelector('input[name$="precio_unitario"]');

    [select, litrosInput, precioInput].forEach(function (el) {
      if (!el) return;
      el.addEventListener('change', function () {
        if (el === select) updateRow(row);
        updateTotal();
      });
      el.addEventListener('input', updateTotal);
    });

    updateRow(row);
    updateTotal();
  }

  document.querySelectorAll('.detalle-row').forEach(hook);
})();
