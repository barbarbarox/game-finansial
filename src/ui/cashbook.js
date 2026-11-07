/**
 * cashbook.js — Dashboard buku kas pribadi.
 * Menampilkan riwayat transaksi, pemasukan, pengeluaran, saldo, dan filter kategori.
 * Anti-XSS: textContent only.
 */

import { getCash, getSavings, getTotalIncome, getTotalExpense } from '../domain/ledger.js';

export function createCashbookModal(container, store, onClose) {
  const backdrop = document.createElement('div');
  backdrop.className = 'lj-modal-backdrop';

  const modal = document.createElement('div');
  modal.className = 'lj-panel cashbook-panel';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');
  modal.setAttribute('aria-label', 'Buku Kas Pribadi');

  // Header
  const header = document.createElement('div');
  header.className = 'panel-header';
  const title = document.createElement('h2');
  title.className = 'panel-title';
  title.textContent = 'Buku Kas Pribadi';
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

  // Summary Cards
  const summaryGrid = document.createElement('div');
  summaryGrid.className = 'cashbook-summary-grid';

  const state = store.getState();
  const rupiah = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 });

  const cash = getCash(state.ledger);
  const savings = getSavings(state.ledger);
  const income = getTotalIncome(state.ledger);
  const expense = getTotalExpense(state.ledger);

  const stats = [
    { label: 'Saldo Kas', value: rupiah.format(cash), color: 'text-primary' },
    { label: 'Tabungan', value: rupiah.format(savings), color: 'text-positive' },
    { label: 'Total Pemasukan', value: rupiah.format(income), color: 'text-positive' },
    { label: 'Total Pengeluaran', value: rupiah.format(expense), color: 'text-negative' }
  ];

  stats.forEach(st => {
    const card = document.createElement('div');
    card.className = 'summary-card';
    const l = document.createElement('span');
    l.className = 'card-label';
    l.textContent = st.label;
    const v = document.createElement('strong');
    v.className = `card-val ${st.color}`;
    v.textContent = st.value;
    card.appendChild(l);
    card.appendChild(v);
    summaryGrid.appendChild(card);
  });

  // Transaction Table
  const tableWrap = document.createElement('div');
  tableWrap.className = 'cashbook-table-wrap';

  const table = document.createElement('table');
  table.className = 'lj-table';

  const thead = document.createElement('thead');
  const trHead = document.createElement('tr');
  ['Waktu', 'Keterangan', 'Kategori', 'Jumlah'].forEach(h => {
    const th = document.createElement('th');
    th.textContent = h;
    trHead.appendChild(th);
  });
  thead.appendChild(trHead);
  table.appendChild(thead);

  const tbody = document.createElement('tbody');
  const entries = state.ledger?.entries || [];

  if (entries.length === 0) {
    const emptyRow = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = 4;
    td.className = 'text-center';
    td.textContent = 'Belum ada transaksi.';
    emptyRow.appendChild(td);
    tbody.appendChild(emptyRow);
  } else {
    entries.slice().reverse().forEach(entry => {
      const tr = document.createElement('tr');

      const tdTime = document.createElement('td');
      tdTime.textContent = `Bln ${entry.month} · Hari ${entry.day}`;

      const tdDesc = document.createElement('td');
      tdDesc.textContent = entry.description || '-';

      const tdCat = document.createElement('td');
      tdCat.textContent = entry.categoryId || (entry.kind === 'allowance' ? 'Uang Saku' : 'Umum');

      const tdAmount = document.createElement('td');
      tdAmount.className = 'text-right tabular-nums';
      const kasLine = entry.lines.find(l => l.accountId === 'kas_pribadi');
      if (kasLine) {
        const isDebit = kasLine.side === 'D';
        tdAmount.textContent = `${isDebit ? '+' : '-'}${rupiah.format(kasLine.amount)}`;
        tdAmount.className += isDebit ? ' text-positive' : ' text-negative';
      } else {
        tdAmount.textContent = '-';
      }

      tr.appendChild(tdTime);
      tr.appendChild(tdDesc);
      tr.appendChild(tdCat);
      tr.appendChild(tdAmount);
      tbody.appendChild(tr);
    });
  }

  table.appendChild(tbody);
  tableWrap.appendChild(table);

  modal.appendChild(header);
  modal.appendChild(summaryGrid);
  modal.appendChild(tableWrap);
  backdrop.appendChild(modal);
  container.appendChild(backdrop);
}

