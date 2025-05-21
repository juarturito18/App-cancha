document.addEventListener("DOMContentLoaded", async () => {
    const email = localStorage.getItem("userEmail"); // Asegúrate de guardar esto al iniciar sesión

    if (!email) {
        alert("No estás logueado");
        window.location.href = "http://127.0.0.1:8000/auth/login.html";
        return;
    }

    const contenedor = document.getElementById("contenedor-reservas");

    const response = await fetch(`http://127.0.0.1:8000/reservas/por_email?email=${email}`);
    const misReservas = await response.json();

    if (misReservas.length === 0) {
        contenedor.innerHTML = "<p>No tienes reservas.</p>";
        return;
    }

    misReservas.forEach(reserva => {
        const div = document.createElement("div");
        div.classList.add("reserva");

        div.innerHTML = `
            <p><strong>Cancha:</strong> ${reserva.cancha}</p>
            <p><strong>Fecha:</strong> ${reserva.fecha}</p>
            <p><strong>Hora:</strong> ${reserva.hora}</p>
            <button>Cancelar</button>
        `;

        const btn = div.querySelector("button");
        btn.addEventListener("click", () => cancelarReserva(reserva));

        contenedor.appendChild(div);
    });
});

async function cancelarReserva(reserva) {
    const confirmacion = confirm("¿Estás seguro de que deseas cancelar esta reserva?");
    if (!confirmacion) return;

    const response = await fetch("http://127.0.0.1:8000/reservas/eliminar", {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(reserva)
    });

    if (response.ok) {
        alert("Reserva cancelada");
        await actualizarCSV(reserva);
        location.reload();
    } else {
        const error = await response.json();
        alert("Error al cancelar: " + error.detail);
    }
}

async function actualizarCSV(reserva) {
    await fetch("http://127.0.0.1:8000/cancelar_csv", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(reserva)
    });
}

