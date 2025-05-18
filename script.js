function cambiarMapa(numeroMapa) {
  const iframe = document.getElementById('iframeMapa');
  iframe.src = `Canchas sinteticas${numeroMapa}.html`;
}

