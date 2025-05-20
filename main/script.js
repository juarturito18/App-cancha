 // Función para cambiar el mapa (asumo que ya la tienes o la implementarás)
    function cambiarMapa(horaInicio, horaFin) {
      const iframe = document.getElementById('iframeMapa');
      // Lógica para cambiar el src del iframe, por ejemplo:
      iframe.src = `canchas-sinteticas${horaInicio}-${horaFin}PM.html`;
      console.log(`Cambiando mapa a ${horaInicio}-${horaFin} PM`);
    }

    document.addEventListener('DOMContentLoaded', () => {
        const token = localStorage.getItem('accessToken');
        const userFirstName = localStorage.getItem('userFirstName');

        const authNavLinks = document.getElementById('auth-nav-links');
        const userGreetingDiv = document.getElementById('user-greeting');
        const userNameDisplay = document.getElementById('user-name-display');
        const logoutButton = document.getElementById('logout-button');
        const goToReservaButton = document.getElementById('goToReservaButton');

        if (token && userFirstName) {
            // Usuario logueado
            authNavLinks.style.display = 'none';
            userGreetingDiv.style.display = 'block';
            userNameDisplay.textContent = userFirstName;

            logoutButton.addEventListener('click', () => {
                localStorage.removeItem('accessToken');
                localStorage.removeItem('userFirstName');
                window.location.reload(); // Recargar para reflejar el estado de logout
            });

            goToReservaButton.addEventListener('click', () => {
                // Asumiendo que la página de reserva está en /reservar/reserva.html
                // y que main.py la sirve desde el directorio "Reserva"
                window.location.href = '/reservar/reserva.html'; 
            });

        } else {
            // Usuario no logueado
            authNavLinks.style.display = 'block';
            userGreetingDiv.style.display = 'none';

            goToReservaButton.addEventListener('click', () => {
                alert('Debes iniciar sesión para poder reservar.');
                // Los enlaces de login/registro se sirven desde /auth/
                window.location.href = 'http://127.0.0.1:8000/auth/login.html'; 
            });
            // Limpiar por si acaso quedaron restos de un token inválido
            localStorage.removeItem('accessToken');
            localStorage.removeItem('userFirstName');
        }
    });

