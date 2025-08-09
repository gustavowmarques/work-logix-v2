// /core/static/js/toggle_password_visibility.js
document.addEventListener('click', function (e) {
  const btn = e.target.closest('.toggle-pw');
  if (!btn) return;

  const targetId = btn.getAttribute('data-target');
  const input = document.getElementById(targetId);
  if (!input) return;

  // Toggle input type
  const toText = input.type === 'password';
  input.type = toText ? 'text' : 'password';

  // Toggle pressed state and icon
  btn.setAttribute('aria-pressed', String(toText));
  const icon = btn.querySelector('i');
  if (icon) {
    icon.classList.toggle('fa-eye', !toText);
    icon.classList.toggle('fa-eye-slash', toText);
  }
});

// Optional: still support a global checkbox if you keep it in the template
document.addEventListener('change', function (e) {
  if (e.target && e.target.id === 'showPasswordToggle') {
    const show = e.target.checked;
    document.querySelectorAll('input[type="password"], input[type="text"]').forEach(inp => {
      if (inp.id === 'id_password1' || inp.id === 'id_password2') {
        inp.type = show ? 'text' : 'password';
      }
    });
  }
});
