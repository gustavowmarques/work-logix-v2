document.addEventListener('DOMContentLoaded', function () {
    const businessTypeSelect = document.getElementById('id_business_type');
    const preferredSelect = document.getElementById('id_preferred_contractor');
    const secondSelect = document.getElementById('id_second_contractor');
  
    function updateContractors(businessTypeId) {
      fetch(`/api/contractors/${businessTypeId}/`)
        .then(response => response.json())
        .then(data => {
          // Clear existing options
          preferredSelect.innerHTML = '<option value="">---------</option>';
          secondSelect.innerHTML = '<option value="">---------</option>';
  
          // Populate both dropdowns
          data.contractors.forEach(contractor => {
            const option1 = new Option(contractor.name, contractor.id);
            const option2 = new Option(contractor.name, contractor.id);
            preferredSelect.add(option1);
            secondSelect.add(option2);
          });
        });
    }
  
    if (businessTypeSelect) {
      businessTypeSelect.addEventListener('change', function () {
        const selectedId = this.value;
        if (selectedId) {
          updateContractors(selectedId);
        } else {
          preferredSelect.innerHTML = '<option value="">---------</option>';
          secondSelect.innerHTML = '<option value="">---------</option>';
        }
      });
    }

    document.addEventListener('DOMContentLoaded', function () {
        const clientSelect = document.getElementById('id_client');
        const unitSelect = document.getElementById('id_unit');
      
        function updateUnits(clientId) {
          fetch(`/api/units/${clientId}/`)
            .then(response => response.json())
            .then(data => {
              unitSelect.innerHTML = '<option value="">---------</option>';
              data.units.forEach(unit => {
                const option = new Option(unit.name, unit.id);
                unitSelect.add(option);
              });
            });
        }
      
        if (clientSelect) {
          clientSelect.addEventListener('change', function () {
            const clientId = this.value;
            if (clientId) {
              updateUnits(clientId);
            } else {
              unitSelect.innerHTML = '<option value="">---------</option>';
            }
          });
        }
      });
      
  });
  