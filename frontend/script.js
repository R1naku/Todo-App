document.addEventListener('DOMContentLoaded', () => {
  const navButtons = document.querySelectorAll('.nav-btn');
  const screens = document.querySelectorAll('.screen');

  navButtons.forEach(button => {
    button.addEventListener('click', () => {
      // Убираем active со всех кнопок
      navButtons.forEach(btn => btn.classList.remove('active'));
      // Добавляем active на кликнутую
      button.classList.add('active');

      // Убираем active со всех экранов
      screens.forEach(screen => screen.classList.remove('active'));

      // Показываем нужный экран
      const screenId = button.getAttribute('data-screen');
      const targetScreen = document.getElementById(`screen-${screenId}`);
      if (targetScreen) {
        targetScreen.classList.add('active');
      }
    });
  });
});