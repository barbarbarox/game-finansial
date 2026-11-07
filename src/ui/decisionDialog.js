/**
 * decisionDialog.js — Dialog interaktif kejadian & pilihan keputusan.
 * Anti-XSS: textContent only.
 */

export function createDecisionModal(container, eventData, onSelectChoice) {
  const backdrop = document.createElement('div');
  backdrop.className = 'lj-modal-backdrop';

  const modal = document.createElement('div');
  modal.className = 'lj-panel decision-panel';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');

  const header = document.createElement('div');
  header.className = 'panel-header';
  const title = document.createElement('h2');
  title.className = 'panel-title';
  title.textContent = 'Kejadian Menarik';
  header.appendChild(title);

  const body = document.createElement('div');
  body.className = 'decision-body';

  const desc = document.createElement('p');
  desc.className = 'decision-text';
  desc.textContent = eventData.text;
  body.appendChild(desc);

  if (eventData.learningTag) {
    const tag = document.createElement('span');
    tag.className = 'learning-tag';
    tag.textContent = `Pelajaran: ${eventData.learningTag}`;
    body.appendChild(tag);
  }

  const choicesContainer = document.createElement('div');
  choicesContainer.className = 'decision-choices';

  eventData.choices.forEach((choice, idx) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn btn-secondary choice-btn';
    btn.textContent = choice.text;
    btn.addEventListener('click', () => {
      backdrop.remove();
      onSelectChoice(choice, idx);
    });
    choicesContainer.appendChild(btn);
  });

  body.appendChild(choicesContainer);
  modal.appendChild(header);
  modal.appendChild(body);
  backdrop.appendChild(modal);
  container.appendChild(backdrop);
}
