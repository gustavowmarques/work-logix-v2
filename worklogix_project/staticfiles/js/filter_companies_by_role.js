document.addEventListener('DOMContentLoaded', function () {
    // ========== Existing Role-Company Filtering ==========
    const roleSelect = document.getElementById('id_role');
    const companySelect = document.getElementById('id_company');

    function filterCompanies() {
        const selectedRole = roleSelect.value;
        const options = companySelect.options;

        for (let i = 0; i < options.length; i++) {
            const option = options[i];
            const roles = option.getAttribute('data-role') || "";

            const shouldShow =
                (selectedRole === 'contractor' && roles.includes('contractor')) ||
                (selectedRole === 'property_manager' && roles.includes('pm')) ||
                (selectedRole === 'assistant' && roles.includes('pm')) || // assistants tied to PMs
                (selectedRole === 'admin' && roles.includes('pm'));       // admins assign PM-type users

            option.style.display = shouldShow || option.value === "" ? 'block' : 'none';
        }

        if (companySelect.selectedIndex > 0 && companySelect.options[companySelect.selectedIndex].style.display === 'none') {
            companySelect.selectedIndex = 0;
        }
    }

    if (roleSelect && companySelect) {
        roleSelect.addEventListener('change', filterCompanies);
        filterCompanies(); // Run on page load
    }

    // ========== New Client-Unit Dynamic Loading ==========
    const clientSelect = document.getElementById('id_client');
    const unitSelect = document.getElementById('id_unit');

    if (clientSelect && unitSelect) {
        clientSelect.addEventListener('change', function () {
            const clientId = this.value;

            fetch(`/ajax/load-units/?client_id=${clientId}`)
                .then(response => response.json())
                .then(data => {
                    // Clear previous options
                    unitSelect.innerHTML = '<option value="">---------</option>';

                    data.units.forEach(unit => {
                        const option = document.createElement('option');
                        option.value = unit.id;
                        option.textContent = unit.name;
                        unitSelect.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error fetching units:', error);
                });
        });
    }
});
