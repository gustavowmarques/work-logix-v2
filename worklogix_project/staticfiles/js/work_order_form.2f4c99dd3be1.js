document.addEventListener('DOMContentLoaded', function () {
  const chk = document.getElementById('id_is_common_area');
  const unitGroup = document.getElementById('unit-field-group');
  const unitSelect = document.getElementById('id_unit');

  function sync() {
    if (!unitGroup || !unitSelect || !chk) return;
    const common = chk.checked;
    unitGroup.style.display = common ? 'none' : '';
    if (common) {
      unitSelect.removeAttribute('required');
    } else {
      unitSelect.setAttribute('required', 'required');
    }
  }

  if (chk) {
    chk.addEventListener('change', sync);
    sync(); // initialize on load
  }
});
