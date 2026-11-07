/**
 * budgetPanel.js — Perencana Anggaran Bulanan
 * Menampilkan alokasi pos anggaran vs realisasi pengeluaran.
 * Anti-XSS: textContent only.
 */

import { getTotalExpense } from '../domain/ledger.js';

export function createBudgetModal(container, store, config, onClose) {
  const backdrop = document.createElement('div');
  backdrop.className = 'lj-modal-backdrop';

  const modal = document.createElement('div');
  modal.className = 'lj-panel budget-panel';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');

  const header = document.createElement('div');
  header.className = 'panel-header';
  const title = document.createElement('h2');
  title.className = 'panel-title';
  title.textContent = 'Perencana Anggaran Bulanan';
  const closeBtn = document.createElement('button');
  closeBtn.type = 'button';
  closeBtn.className = 'btn-close';
  closeBtn.textContent = '✕';
  closeBtn.addEventListener('click', () => {
    backdrop.remove();
    if (onClose) onClose();
  });
  header.appendChild(title);
  header.appendChild(closeBtn);
  modal.appendChild(header);

  const rupiah = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 });
  const state = store.getState();
  const currentBudget = state.budget || {};

  const body = document.createElement('div');
  body.className = 'budget-body';

  const table = document.createElement('table');
  table.className = 'lj-table';
  const thead = document.createElement('thead');
  const trH = document.createElement('tr');
  ['Kategori', 'Anggaran (Rp)', 'Realisasi', 'Sisa'].forEach(h => {
    const th = document.createElement('th');
    th.textContent = h;
    trH.appendChild(th);
  });
  thead.appendChild(trH);
  table.appendChild(thead);

  const tbody = document.createElement('tbody');
  const inputs = {};

  Object.entries(config.categories).forEach(([catId, catName]) => {
    const tr = document.createElement('tr');

    const tdName = document.createElement('td');
    tdName.textContent = catName;

    const tdInput = document.createElement('td');
    const inp = document.createElement('input');
    inp.type = 'number';
    inp.step = '5000';
    inp.min = '0';
    inp.value = currentBudget[catId] || 0;
    inp.className = 'input-field tabular-nums';
    inputs[catId] = inp;
    tdInput.appendChild(inp);

    const spent = getTotalExpense(state.ledger, state.clock.month, catId);
    const allocated = currentBudget[catId] || 0;
    const remaining = allocated - spent;

    const tdSpent = document.createElement('td');
    tdSpent.className = 'tabular-nums text-right';
    tdSpent.textContent = rupiah.format(spent);

    const tdRemaining = document.createElement('td');
    tdRemaining.className = `tabular-nums text-right ${remaining < 0 ? 'text-negative' : 'text-positive'}`;
    tdRemaining.textContent = rupiah.format(remaining);

    tr.appendChild(tdName);
    tr.appendChild(tdInput);
    tr.appendChild(tdSpent);
    tr.appendChild(tdRemaining);
    tbody.appendChild(tr);
  });

  table.appendChild(tbody);
  body.appendChild(table);

  // Footer Actions
  const actions = document.createElement('div');
  actions.className = 'panel-actions';

  const useSuggestionBtn = document.createElement('button');
  useSuggestionBtn.className = 'btn btn-secondary';
  useSuggestionBtn.textContent = 'Gunakan Saran Anggaran';
  useSuggestionBtn.addEventListener('click', () => {
    Object.entries(config.budgetSuggestion).forEach(([key, val]) => {
      if (inputs[key]) {
        inputs[key].value = val;
      }
    });
  });

  const saveBtn = document.createElement('button');
  saveBtn.className = 'btn btn-primary';
  saveBtn.textContent = 'Simpan Anggaran';
  saveBtn.addEventListener('click', () => {
    const newBudget = {};
    Object.entries(inputs).forEach(([key, inp]) => {
      newBudget[key] = parseInt(inp.value, 10) || 0;
    });
    store.setState({ budget: newBudget });
    backdrop.remove();
    if (onClose) onClose();
  });

  actions.appendChild(useSuggestionBtn);
  actions.appendChild(saveBtn);
  modal.appendChild(body);
  modal.appendChild(actions);
  backdrop.appendChild(modal);
  container.appendChild(backdrop);
}

