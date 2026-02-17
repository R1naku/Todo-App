document.addEventListener('DOMContentLoaded', () => {
  const tg = window.Telegram.WebApp;
  tg.ready();
  const initData = tg.initData;

  const apiUrl = '';

  const navButtons = document.querySelectorAll('.nav-btn');
  const homeScreen = document.getElementById('screen-home');
  const addScreen = document.getElementById('screen-add');
  const profileScreen = document.getElementById('screen-profile');

  if (!homeScreen) {
    console.error('Home screen not found. Add <div id="screen-home" class="screen active"></div> to HTML.');
  }
  if (!addScreen) {
    console.error('Add screen not found. Add <div id="screen-add" class="screen"></div> to HTML.');
  }
  if (!profileScreen) {
    console.error('Profile screen not found. Add <div id="screen-profile" class="screen"></div> to HTML.');
  }

  navButtons[0].setAttribute('data-screen', 'home');
  navButtons[1].setAttribute('data-screen', 'add');
  navButtons[2].setAttribute('data-screen', 'profile');

  navButtons.forEach(button => {
    button.addEventListener('click', () => {
      navButtons.forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');

      const screens = [homeScreen, addScreen, profileScreen];
      screens.forEach(screen => screen && screen.classList.remove('active'));

      const screenId = button.getAttribute('data-screen');
      const targetScreen = document.getElementById(`screen-${screenId}`);
      if (targetScreen) {
        targetScreen.classList.add('active');
        if (screenId === 'home') loadHome();
        if (screenId === 'profile') loadProfile();
      }
    });
  });