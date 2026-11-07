/**
 * evaluation.js — End-of-phase evaluation for Life Journey.
 */

import { getTotalIncome, getTotalExpense, getCash, getSavings } from './ledger.js';

/**
 * Evaluate a single month.
 * @param {object} ledger
 * @param {number} month
 * @param {object} config
 * @returns {object} month summary
 */
export function evaluateMonth(ledger, month, config) {
  const income = getTotalIncome(ledger, month);
  const expense = getTotalExpense(ledger, month);
  const categories = config.categories ?? {};

  const categoryBreakdown = Object.keys(categories).map(catId => ({
    categoryId: catId,
    name: categories[catId],
    amount: getTotalExpense(ledger, month, catId),
  }));

  const netSaved = income - expense;

  return {
    month,
    income,
    expense,
    netSaved,
    categoryBreakdown,
  };
}

/**
 * Evaluate full Phase 1 (all months).
 * @param {object} ledger
 * @param {object} config
 * @returns {object} phase1Result
 */
export function evaluatePhase1(ledger, config) {
  const months = config.months ?? 2;
  const monthResults = [];

  for (let m = 1; m <= months; m++) {
    monthResults.push(evaluateMonth(ledger, m, config));
  }

  const totalIncome = getTotalIncome(ledger);
  const totalExpense = getTotalExpense(ledger);
  const finalCash = getCash(ledger);
  const finalSavings = getSavings(ledger);

  // Savings rate = savings deposited / total income
  const savingsRate = totalIncome > 0 ? finalSavings / totalIncome : 0;

  // Wants ratio = discretionary spending / total expense
  const wantsCategories = ['jajan', 'hiburan', 'perawatanDiri'];
  const wantsSpend = wantsCategories.reduce(
    (sum, cat) => sum + getTotalExpense(ledger, null, cat),
    0
  );
  const wantsRatio = totalExpense > 0 ? wantsSpend / totalExpense : 0;

  // Budget adherence (placeholder metric: percentage of months without overspend)
  const budgetAdherence = 1.0; // Will be computed when budget is passed in

  // Rating
  let rating;
  const thresholds = config.savingsRateThresholds ?? { great: 0.15, good: 0.08 };
  const labels = config.savingsRateLabels ?? { great: 'Sangat Baik', good: 'Cukup Baik', poor: 'Perlu Berlatih' };

  if (savingsRate >= thresholds.great) {
    rating = labels.great;
  } else if (savingsRate >= thresholds.good) {
    rating = labels.good;
  } else {
    rating = labels.poor;
  }

  // Key decisions summary (from ledger entry descriptions)
  const keyDecisions = ledger.entries
    .filter(e => e.kind === 'expense' && e.description)
    .slice(-10)
    .map(e => ({ description: e.description, amount: e.lines.find(l => l.side === 'K')?.amount ?? 0, categoryId: e.categoryId }));

  return {
    totalIncome,
    totalExpense,
    finalCash,
    finalSavings,
    savingsRate,
    wantsRatio,
    budgetAdherence,
    rating,
    monthResults,
    keyDecisions,
  };
}
