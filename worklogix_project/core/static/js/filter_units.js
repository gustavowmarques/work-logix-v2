document.addEventListener('DOMContentLoaded', function () {
    const clientSelect = document.getElementById('id_client');
    const unitSelect = document.getElementById('id_unit');
  
    if (clientSelect && unitSelect) {
      clientSelect.addEventListener('change', function () {
        const clientId = this.value;
        if (!clientId) return;
  
        fetch(`/ajax/get-units/${clientId}/`)
          .then(response => response.json())
          .then(data => {
            unitSelect.innerHTML = '<option value="">---------</option>';
            data.units.forEach(unit => {
              const option = document.createElement('option');
              option.value = unit.id;
              option.text = unit.name;
              unitSelect.appendChild(option);
            });
          })
          .catch(error => console.error("Failed to load units:", error));
      });
    }
  });
  