/**
 * missions.js — Mission tracker for Life Journey Phase 1.
 * Missions M1–M7 track player behaviour and progress.
 */

/** Mission definitions */
export const MISSION_DEFS = [
  {
    id: 'M1',
    title: 'Buku Kas Pertama',
    description: 'Lakukan 5 transaksi pertamamu.',
    type: 'transaction_count',
    target: 5,
  },
  {
    id: 'M2',
    title: 'Penabung Pemula',
    description: 'Tabung uang untuk pertama kali.',
    type: 'savings_ever',
    target: 1,
  },
  {
    id: 'M3',
    title: 'Pembuat Anggaran',
    description: 'Isi rencana anggaran bulan pertama.',
    type: 'budget_set',
    target: 1,
  },
  {
    id: 'M4',
    title: 'Hidup Hemat',
    description: 'Selesaikan bulan pertama tanpa kehabisan kas.',
    type: 'month1_no_broke',
    target: 1,
  },
  {
    id: 'M5',
    title: 'Pengambil Keputusan',
    description: 'Hadapi 3 kejadian dan buat pilihan.',
    type: 'events_resolved',
    target: 3,
  },
  {
    id: 'M6',
    title: 'Target Tabungan',
    description: 'Capai tabungan Rp100.000.',
    type: 'savings_reach',
    target: 100000,
  },
  {
    id: 'M7',
    title: 'Manajer Keuangan',
    description: 'Selesaikan kedua bulan dengan tabungan positif.',
    type: 'phase_complete_savings',
    target: 1,
  },
];

/**
 * Create initial missions state.
 * @returns {object[]}
 */
export function createMissions() {
  return MISSION_DEFS.map(def => ({
    ...def,
    progress: 0,
    completed: false,
    completedDay: null,
    completedMonth: null,
  }));
}

/**
 * Update missions based on current game state.
 * @param {object[]} missions
 * @param {object} state - { ledger, budget, clock, eventsResolved, savingsEver, budgetSet, month1NoBroke, phaseComplete }
 * @returns {object[]} updated missions
 */
export function checkMissions(missions, state) {
  const { ledger, clock } = state;

  return missions.map(m => {
    if (m.completed) return m;

    let newProgress = m.progress;

    switch (m.type) {
      case 'transaction_count':
        newProgress = ledger.entries.length;
        break;

      case 'savings_ever':
        newProgress = state.savingsEver ? 1 : 0;
        break;

      case 'budget_set':
        newProgress = state.budgetSet ? 1 : 0;
        break;

      case 'month1_no_broke':
        newProgress = state.month1NoBroke ? 1 : 0;
        break;

      case 'events_resolved':
        newProgress = state.eventsResolved ?? 0;
        break;

      case 'savings_reach': {
        const savings = ledger ? (ledger.entries.reduce((acc, entry) => {
          for (const line of entry.lines) {
            if (line.accountId === 'TABUNGAN') {
              acc += line.side === 'D' ? line.amount : -line.amount;
            }
          }
          return acc;
        }, 0)) : 0;
        newProgress = savings;
        break;
      }

      case 'phase_complete_savings':
        newProgress = state.phaseComplete ? 1 : 0;
        break;
    }

    const completed = newProgress >= m.target;
    return {
      ...m,
      progress: newProgress,
      completed,
      completedDay: completed && !m.completed ? (clock?.day ?? null) : m.completedDay,
      completedMonth: completed && !m.completed ? (clock?.month ?? null) : m.completedMonth,
    };
  });
}

/**
 * Get the current active (incomplete) mission.
 * @param {object[]} missions
 * @returns {object|null}
 */
export function getActiveMission(missions) {
  return missions.find(m => !m.completed) ?? null;
}

/**
 * Check if all missions are complete.
 * @param {object[]} missions
 * @returns {boolean}
 */
export function isAllComplete(missions) {
  return missions.every(m => m.completed);
}
