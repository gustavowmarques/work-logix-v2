document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const selectAllCheckbox = document.getElementById('selectAll');
    const tableRows = document.querySelectorAll('tbody tr');
  
    searchInput.addEventListener('input', function () {
      const searchTerm = this.value.toLowerCase();
  
      tableRows.forEach(row => {
        const rowText = row.textContent.toLowerCase();
        const visible = rowText.includes(searchTerm);
        row.style.display = visible ? '' : 'none';
      });
    });
  
    selectAllCheckbox.addEventListener('change', function () {
      const checked = this.checked;
  
      tableRows.forEach(row => {
        // Always toggle DELETE even if hidden — Django needs it
        const deleteCheckbox = row.querySelector('input[type="checkbox"][name$="DELETE"]');
        if (deleteCheckbox) {
          deleteCheckbox.checked = checked;
        }
      });
    });
  });
  