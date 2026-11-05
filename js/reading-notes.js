/* Progressive enhancement: the full journal and archive also work without JS. */
(() => {
  const panel = document.querySelector('.reading-topic-panel');
  if (!panel) return;
  panel.hidden = false;
  const buttons = [...panel.querySelectorAll('button')];
  const days = [...document.querySelectorAll('.reading-day')];
  const status = document.querySelector('.reading-filter-status');
  panel.addEventListener('click', (event) => {
    const button = event.target.closest('button[data-topic]');
    if (!button) return;
    const topic = button.dataset.topic;
    let count = 0;
    buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    days.forEach(day => {
      let visible = 0;
      day.querySelectorAll('.reading-entry').forEach(entry => {
        entry.hidden = topic !== 'all' && !JSON.parse(entry.dataset.topics).includes(topic);
        if (!entry.hidden) visible++;
      });
      count += visible;
      day.hidden = visible === 0;
      const reflection = day.querySelector('.reading-reflection');
      if (reflection) reflection.hidden = topic !== 'all';
    });
    status.hidden = topic === 'all';
    status.textContent = `${count} ${count === 1 ? 'note' : 'notes'} on ${topic}`;
  });
})();
