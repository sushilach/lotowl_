// Minimal map script: start app toggling and call leaflet.
function startApp() {
  const landing = document.getElementById('landing');
  const mainScreen = document.getElementById('main-screen');
  if (landing) landing.classList.add('hidden');
  if (mainScreen) mainScreen.classList.remove('hidden');
  setTimeout(function () {
    if (typeof initLeafletMap === 'function') initLeafletMap();
  }, 50);
}

window.addEventListener('DOMContentLoaded', function () {
  document.getElementById('advance-btn')?.addEventListener('click', startApp);
});
