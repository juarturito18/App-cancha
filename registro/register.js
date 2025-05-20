// register.js corregido
document.getElementById('registerForm').addEventListener('submit', async function(event) {
  event.preventDefault();
  const firstName = document.getElementById('first_name').value;
  const lastName = document.getElementById('last_name').value;
  const email = document.getElementById('email').value;
  const age = document.getElementById('age').value;
  const password = document.getElementById('password').value;
  const responseElement = document.getElementById('response');
  responseElement.textContent = '';
  responseElement.className = '';

  // Validaciones básicas en cliente
  if (parseInt(age) < 18) {
    responseElement.textContent = 'Debes ser mayor de 18 años para registrarte.';
    responseElement.className = 'error';
    return;
  }
  if (password.length < 8) {
    responseElement.textContent = 'La contraseña debe tener al menos 8 caracteres.';
    responseElement.className = 'error';
    return;
  }

  const formData = new FormData();
  formData.append('first_name', firstName);
  formData.append('last_name', lastName);
  formData.append('email', email);
  formData.append('age', age);
  formData.append('password', password);

  try {
    // Enviar POST al endpoint /register
    const res = await fetch('http://127.0.0.1:8000/register', {
      method: 'POST',
      body: formData
    });

    const data = await res.json();

    if (res.ok) {
      responseElement.textContent = '¡Registro exitoso, ' + data.first_name + '! Ahora puedes iniciar sesión.';
      responseElement.className = 'success';
      // Redirigir al login tras breve espera
      setTimeout(() => {
        window.location.href = 'http://127.0.0.1:8000/auth/login.html';
      }, 2000);
    } else {
      // Mostrar detalles de error devueltos por el backend
      let errorMessage = 'Error en el registro.';
      if (data && data.detail) {
        if (Array.isArray(data.detail)) {
          errorMessage = data.detail.map(err => `${err.loc.join('.')} - ${err.msg}`).join('; ');
        } else {
          errorMessage = data.detail;
        }
      }
      responseElement.textContent = errorMessage;
      responseElement.className = 'error';
    }
  } catch (error) {
    console.error('Error en el registro:', error);
    responseElement.textContent = 'Ocurrió un error en la conexión. Inténtalo de nuevo.';
    responseElement.className = 'error';
  }
});
