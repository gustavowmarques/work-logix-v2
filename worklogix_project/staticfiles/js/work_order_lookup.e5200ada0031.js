document.addEventListener('DOMContentLoaded', function () {
    const clientSelect = document.querySelector('#id_client');
    const unitSelect = document.querySelector('#id_unit');

    if (clientSelect) {
      clientSelect.addEventListener('change', async function () {
        const clientId = this.value;

        // Clear existing options
        unitSelect.innerHTML = '<option value="">---------</option>';

        if (clientId) {
          try {
            const response = await fetch(`/dashboard/work-orders/load-units/?client_id=${clientId}`);
            if (!response.ok) throw new Error("Failed to fetch units.");

            const data = await response.json();

            data.units.forEach(unit => {
              const option = document.createElement('option');
              option.value = unit.id;
              option.textContent = unit.name;
              unitSelect.appendChild(option);
            });

          } catch (error) {
            console.error("Error fetching units:", error);
          }
        }
      });
    }
  });