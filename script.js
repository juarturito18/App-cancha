function cambiarMapa(num1, num2) {
  const iframe = document.getElementById('iframeMapa');
  const newSrc = `canchas-sinteticas${num1}-${num2}PM.html`;
  console.log('Attempting to load:', newSrc); // Check browser console
  iframe.src = newSrc;
}

