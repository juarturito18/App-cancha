document.getElementById('loginForm').addEventListener('submit', async function(event) {
  event.preventDefault();
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const responseElement = document.getElementById('response');
  responseElement.textContent = ''; // Limpiar mensajes previos
  responseElement.className = '';

  // Preparar datos en formato OAuth2 (username/password)
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  try {
    const res = await fetch('http://127.0.0.1:8000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    });

    const data = await res.json();

    if (res.ok && data.access_token) {
      responseElement.textContent = '¡Bienvenido, ' + (data.first_name || 'usuario') + '! Redirigiendo...';
      responseElement.className = 'success';
      // Guardar token y nombre en localStorage
      localStorage.setItem('accessToken', data.access_token);
      localStorage.setItem('userFirstName', data.first_name || '');
      localStorage.setItem('userEmail', email);
      // Redirigir a la página principal tras breve espera
      setTimeout(() => {
        window.location.href = 'http://127.0.0.1:8000/index/';  // Ajustar según ruta real del índice
      }, 1500);
    } else {
      responseElement.textContent = data.detail || 'Error al iniciar sesión. Verifica tus credenciales.';
      responseElement.className = 'error';
    }
  } catch (error) {
    console.error('Error en el login:', error);
    responseElement.textContent = 'Ocurrió un error en la conexión. Inténtalo de nuevo.';
    responseElement.className = 'error';
  }
});
