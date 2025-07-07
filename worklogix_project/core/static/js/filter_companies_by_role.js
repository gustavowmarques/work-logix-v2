document.addEventListener('DOMContentLoaded', function () {
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
                (selectedRole === 'assistant' && roles.includes('pm')) ||  // assistants tied to PMs
                (selectedRole === 'admin' && roles.includes('pm'));       // admins assign PM-type users

            option.style.display = shouldShow || option.value === "" ? 'block' : 'none';
        }

        // Reset selection if currently selected company is hidden
        if (companySelect.selectedIndex > 0 && companySelect.options[companySelect.selectedIndex].style.display === 'none') {
            companySelect.selectedIndex = 0;
        }
    }

    if (roleSelect && companySelect) {
        roleSelect.addEventListener('change', filterCompanies);
        filterCompanies(); // Run on page load
    }
});
