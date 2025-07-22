document.addEventListener('DOMContentLoaded', function () {
    const eircodeInputs = document.querySelectorAll('.eircode-input');
  
    eircodeInputs.forEach((input, index) => {
      input.addEventListener('change', async function () {
        const eircode = input.value;
  
        if (eircode.length >= 5) {
          // Example fetch — replace URL with your lookup endpoint
          const response = await fetch(`/api/eircode-lookup/?eircode=${eircode}`);
          if (response.ok) {
            const data = await response.json();
            document.querySelector(`[name="form-${index}-street"]`).value = data.street;
            document.querySelector(`[name="form-${index}-city"]`).value = data.city;
            document.querySelector(`[name="form-${index}-county"]`).value = data.county;
          }
        }
      });
    });
  });
  