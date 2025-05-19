async function generarPDF() {
  const nombre = document.getElementById("nombre").value.trim();
  const email = document.getElementById("email").value.trim();
  const cancha = document.getElementById("cancha").value;
  const fecha = document.getElementById("fecha").value;
  const hora = document.getElementById("hora").value;

  if (!nombre || !email || !cancha || !fecha || !hora) {
    alert("Por favor, complete todos los campos.");
    return;
  }

  // Validar disponibilidad en el servidor antes de reservar
  const reservaExitosa = await guardarReservaServidor(cancha, hora);
  if (!reservaExitosa) return;

  // Generar PDF
  const firmaBase64 = await cargarFirma("Juan_Sabino_cocosign.png");
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();
  const fechaHora = new Date().toLocaleString();

  // Encabezado
  doc.setFontSize(18);
  doc.setFont("Arial", "bolditalic");
  doc.text(`Confirmación de Reserva – ${cancha}`, 30, 30);

  doc.setFontSize(14);
  doc.setFont("Arial", "normal");
  doc.text(`Barranquilla, Atlántico, Colombia`, 10, 50);
  doc.text(`Fecha de emisión: ${fechaHora}`, 10, 60);

  const cuerpo = [
    `A quien corresponda,`,
    ``,
    `Por medio de la presente, dejamos constancia de que el señor(a) "${nombre}",`,
    `identificado con el correo electrónico "${email}", ha realizado una`,
    `reserva formal de la instalación deportiva conocida como "${cancha}".`,
    ``,
    `Dicha reserva otorga el derecho de uso exclusivo de la cancha por un período`,
    `de una hora, comenzando puntualmente a las "${hora}" horas del día "${fecha}".`,
    `Durante este tiempo, la cancha permanecerá cerrada al público general y se`,
    `considerará como un espacio de uso privado del solicitante.`,
    ``,
    `Esta autorización se emite bajo la normativa de reservas de la institución, y`,
    `deberá ser presentada en caso de requerirse validación por parte del personal encargado.`,
    ``,
    `Agradecemos al usuario por utilizar nuestros servicios y recordamos que es`,
    `responsabilidad del mismo hacer uso adecuado de las instalaciones, mantener`,
    `la limpieza del espacio y respetar el horario asignado.`,
    ``,
  ];

  let y = 70;
  cuerpo.forEach(linea => {
    doc.text(linea, 10, y);
    y += 10;
  });

  doc.text("Atentamente,", 10, y + 10);
  doc.text("Administración de Reservas", 10, y + 20);
  doc.text("Centro Deportivo la pateada", 10, y + 30);

  // Insertar firma
  doc.addImage(firmaBase64, "PNG", 130, y + 5, 60, 30);
  doc.save("reserva_con_firma.pdf");
}

async function cargarFirma(path) {
  const response = await fetch(path);
  const blob = await response.blob();
  return await convertirImagenABase64(blob);
}

function convertirImagenABase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// Cargar canchas disponibles desde el backend según hora seleccionada
async function actualizarCanchasDisponibles() {
  const hora = document.getElementById("hora").value;
  const selectCancha = document.getElementById("cancha");

  if (!hora) return;

  try {
    const response = await fetch(`http://localhost:8000/disponibles?hora=${hora}`);
    const canchas = await response.json();

    // Limpiar el select
    selectCancha.innerHTML = '<option value="" disabled selected>Seleccione la cancha</option>';

    if (canchas.length === 0) {
      const option = document.createElement("option");
      option.value = "";
      option.disabled = true;
      option.textContent = "No hay canchas disponibles";
      selectCancha.appendChild(option);
    } else {
      canchas.forEach(cancha => {
        const option = document.createElement("option");
        option.value = cancha;
        option.textContent = cancha;
        selectCancha.appendChild(option);
      });
    }
  } catch (error) {
    console.error("Error al obtener canchas disponibles:", error);
    alert("No se pudieron cargar las canchas disponibles.");
  }
}

// Enviar reserva al backend y actualizar CSV
async function guardarReservaServidor(cancha, hora) {
  try {
    const response = await fetch("http://localhost:8000/reservar", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ cancha, hora })
    });

    const data = await response.json();

    if (!response.ok) {
      alert(data.detail || "No se pudo realizar la reserva.");
      return false;
    }

    return true;
  } catch (error) {
    console.error("Error al enviar la reserva:", error);
    alert("No se pudo conectar con el servidor.");
    return false;
  }
}

