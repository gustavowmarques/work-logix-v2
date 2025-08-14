document.addEventListener('DOMContentLoaded', function () {
    const contractorCheckbox = document.getElementById('id_is_contractor');
    const businessTypeField = document.querySelector('.field-business_type');
    const businessTypeInput = document.getElementById('id_business_type');
  
    function toggleBusinessTypeField() {
      if (contractorCheckbox.checked) {
        businessTypeField.style.display = 'block';
      } else {
        businessTypeField.style.display = 'none';
        businessTypeInput.value = '';
      }
    }
  
    if (contractorCheckbox && businessTypeField) {
      toggleBusinessTypeField();
      contractorCheckbox.addEventListener('change', toggleBusinessTypeField);
    }
  });
  