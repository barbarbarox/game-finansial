/**
 * ledger.js — Double-entry ledger engine for Life Journey.
 *
 * Rules:
 *  - Every entry must balance: Σ Debit == Σ Kredit
 *  - Kas Pribadi cannot go negative
 *  - Tabungan cannot go negative
 *  - All amounts are integer rupiah (no floats)
 *  - Ledger is append-only; never mutate existing entries
 */

import { AccountId, CATEGORY_ACCOUNT_MAP } from './accounts.js';

let _entryCounter = 0;

/** Create an empty ledger */
export function createLedger() {
  return { entries: [] };
}

/**
 * Validate and add an entry to the ledger.
 * @param {object} ledger
 * @param {object} entry - { id?, day, month, categoryId?, kind, description, lines }
 * @returns {{ ledger: object, error: string|null }}
 */
export function addEntry(ledger, entry) {
  // Validate lines balance
  const sumD = entry.lines
    .filter(l => l.side === 'D')
    .reduce((s, l) => s + l.amount, 0);
  const sumK = entry.lines
    .filter(l => l.side === 'K')
    .reduce((s, l) => s + l.amount, 0);

  if (sumD !== sumK) {
    return { ledger, error: `Entry tidak balance: D=${sumD} K=${sumK}` };
  }

  // Check integer
  for (const line of entry.lines) {
    if (!Number.isInteger(line.amount) || line.amount < 0) {
      return { ledger, error: `Jumlah harus bilangan bulat non-negatif: ${line.amount}` };
    }
  }

  // Build tentative new ledger to test for negative balances
  const newEntry = {
    id: entry.id ?? `E${++_entryCounter}`,
    day: entry.day,
    month: entry.month,
    minuteOfDay: entry.minuteOfDay ?? 360,
    categoryId: entry.categoryId ?? null,
    kind: entry.kind,
    description: entry.description,
    lines: entry.lines.map(l => ({ accountId: l.accountId, side: l.side, amount: l.amount })),
  };

  const tentativeLedger = { entries: [...ledger.entries, newEntry] };

  if (getBalance(tentativeLedger, AccountId.KAS_PRIBADI) < 0) {
    return { ledger, error: 'Saldo Kas Pribadi tidak boleh negatif.' };
  }
  if (getBalance(tentativeLedger, AccountId.TABUNGAN) < 0) {
    return { ledger, error: 'Saldo Tabungan tidak boleh negatif.' };
  }

  return { ledger: tentativeLedger, error: null };
}

/**
 * Calculate the balance of an account from all entries.
 * Assets/Expenses: D increases, K decreases.
 * Equity/Revenue: K increases, D decreases.
 */
export function getBalance(ledger, accountId) {
  // asset/expense accounts: D increases balance
  const isDebitNormal = [
    AccountId.KAS_PRIBADI,
    AccountId.TABUNGAN,
    AccountId.BEBAN_JAJAN,
    AccountId.BEBAN_TRANSPORTASI,
    AccountId.BEBAN_SEKOLAH,
    AccountId.BEBAN_PERAWATAN_DIRI,
    AccountId.BEBAN_HIBURAN,
    AccountId.BEBAN_KOMUNIKASI,
    AccountId.BEBAN_LAIN,
  ].includes(accountId);

  let balance = 0;
  for (const entry of ledger.entries) {
    for (const line of entry.lines) {
      if (line.accountId !== accountId) continue;
      if (isDebitNormal) {
        balance += line.side === 'D' ? line.amount : -line.amount;
      } else {
        balance += line.side === 'K' ? line.amount : -line.amount;
      }
    }
  }
  return balance;
}

/** Current cash balance */
export function getCash(ledger) {
  return getBalance(ledger, AccountId.KAS_PRIBADI);
}

/** Current savings balance */
export function getSavings(ledger) {
  return getBalance(ledger, AccountId.TABUNGAN);
}

/**
 * Total income (revenue accounts) for a month (optional).
 * @param {object} ledger
 * @param {number|null} month - if null, total all months
 */
export function getTotalIncome(ledger, month = null) {
  const revenueAccounts = [AccountId.UANG_SAKU, AccountId.BONUS];
  let total = 0;
  for (const entry of ledger.entries) {
    if (month !== null && entry.month !== month) continue;
    for (const line of entry.lines) {
      if (revenueAccounts.includes(line.accountId) && line.side === 'K') {
        total += line.amount;
      }
    }
  }
  return total;
}

/**
 * Total expenses for a month and/or category.
 * @param {object} ledger
 * @param {number|null} month
 * @param {string|null} categoryId
 */
export function getTotalExpense(ledger, month = null, categoryId = null) {
  const expenseAccounts = [
    AccountId.BEBAN_JAJAN,
    AccountId.BEBAN_TRANSPORTASI,
    AccountId.BEBAN_SEKOLAH,
    AccountId.BEBAN_PERAWATAN_DIRI,
    AccountId.BEBAN_HIBURAN,
    AccountId.BEBAN_KOMUNIKASI,
    AccountId.BEBAN_LAIN,
  ];
  let total = 0;
  for (const entry of ledger.entries) {
    if (month !== null && entry.month !== month) continue;
    if (categoryId !== null && entry.categoryId !== categoryId) continue;
    for (const line of entry.lines) {
      if (expenseAccounts.includes(line.accountId) && line.side === 'D') {
        total += line.amount;
      }
    }
  }
  return total;
}

/**
 * Net worth = Cash + Savings
 */
export function getNetWorth(ledger) {
  return getCash(ledger) + getSavings(ledger);
}

/** Create allowance entry: Rp1.000.000 uang saku per month */
export function createAllowanceEntry(day, month, minuteOfDay = 360) {
  const amount = 1000000;
  return {
    day,
    month,
    minuteOfDay,
    kind: 'allowance',
    description: 'Uang saku bulanan',
    categoryId: null,
    lines: [
      { accountId: AccountId.KAS_PRIBADI, side: 'D', amount },
      { accountId: AccountId.UANG_SAKU,   side: 'K', amount },
    ],
  };
}

/**
 * Create expense entry: pay from cash to expense account.
 * @param {number} day
 * @param {number} month
 * @param {string} categoryId
 * @param {number} amount - positive integer rupiah
 * @param {string} description
 * @param {number} [minuteOfDay=360]
 */
export function createExpenseEntry(day, month, categoryId, amount, description, minuteOfDay = 360) {
  const bebanAccount = CATEGORY_ACCOUNT_MAP[categoryId] ?? AccountId.BEBAN_LAIN;
  return {
    day,
    month,
    minuteOfDay,
    kind: 'expense',
    description,
    categoryId,
    lines: [
      { accountId: bebanAccount,          side: 'D', amount },
      { accountId: AccountId.KAS_PRIBADI, side: 'K', amount },
    ],
  };
}

/**
 * Create savings deposit entry: transfer from kas to tabungan.
 */
export function createSavingsDepositEntry(day, month, amount, minuteOfDay = 360) {
  return {
    day,
    month,
    minuteOfDay,
    kind: 'savings_deposit',
    description: 'Setor tabungan',
    categoryId: null,
    lines: [
      { accountId: AccountId.TABUNGAN,     side: 'D', amount },
      { accountId: AccountId.KAS_PRIBADI,  side: 'K', amount },
    ],
  };
}

/**
 * Create savings withdraw entry: transfer from tabungan to kas.
 */
export function createSavingsWithdrawEntry(day, month, amount, minuteOfDay = 360) {
  return {
    day,
    month,
    minuteOfDay,
    kind: 'savings_withdraw',
    description: 'Tarik tabungan',
    categoryId: null,
    lines: [
      { accountId: AccountId.KAS_PRIBADI,  side: 'D', amount },
      { accountId: AccountId.TABUNGAN,     side: 'K', amount },
    ],
  };
}

/**
 * Create income entry (bonus/windfall): credit revenue, debit kas.
 */
export function createIncomeEntry(day, month, amount, description, minuteOfDay = 360) {
  return {
    day,
    month,
    minuteOfDay,
    kind: 'income',
    description,
    categoryId: null,
    lines: [
      { accountId: AccountId.KAS_PRIBADI, side: 'D', amount },
      { accountId: AccountId.BONUS,       side: 'K', amount },
    ],
  };
}

/**
 * Run accounting invariants against the ledger.
 * @param {object} ledger
 * @returns {{ pass: boolean, failures: string[] }}
 */
export function runInvariants(ledger) {
  const failures = [];

  // Invariant 1: each entry must balance
  for (const entry of ledger.entries) {
    const sumD = entry.lines.filter(l => l.side === 'D').reduce((s, l) => s + l.amount, 0);
    const sumK = entry.lines.filter(l => l.side === 'K').reduce((s, l) => s + l.amount, 0);
    if (sumD !== sumK) {
      failures.push(`Entry ${entry.id} tidak balance: D=${sumD} K=${sumK}`);
    }
  }

  // Invariant 2: Kas tidak negatif
  if (getCash(ledger) < 0) {
    failures.push(`Kas Pribadi negatif: ${getCash(ledger)}`);
  }

  // Invariant 3: Tabungan tidak negatif
  if (getSavings(ledger) < 0) {
    failures.push(`Tabungan negatif: ${getSavings(ledger)}`);
  }

  // Invariant 4: Total Debit == Total Kredit across all entries
  let totalD = 0;
  let totalK = 0;
  for (const entry of ledger.entries) {
    for (const line of entry.lines) {
      if (line.side === 'D') totalD += line.amount;
      else totalK += line.amount;
    }
  }
  if (totalD !== totalK) {
    failures.push(`Total ledger tidak balance: D=${totalD} K=${totalK}`);
  }

  return { pass: failures.length === 0, failures };
}
