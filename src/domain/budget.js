/**
 * budget.js — Budget planner for Life Journey.
 * Handles per-category budget allocation vs. actual spending.
 */

import { getTotalExpense } from './ledger.js';

/**
 * Create an empty budget.
 * @returns {object}
 */
export function createBudget() {
  return { items: {} };
}

/**
 * Set a budget item for a category.
 * @param {object} budget
 * @param {string} categoryId
 * @param {number} amount - positive integer rupiah
 * @returns {object} new budget
 */
export function setBudgetItem(budget, categoryId, amount) {
  if (!Number.isInteger(amount) || amount < 0) {
    throw new Error(`Jumlah anggaran tidak valid: ${amount}`);
  }
  return {
    items: {
      ...budget.items,
      [categoryId]: amount,
    },
  };
}

/**
 * Compare budget vs actual spending.
 * @param {object} budget
 * @param {object} ledger
 * @param {number} month
 * @returns {object[]} array of { categoryId, budgeted, actual, diff, overBudget }
 */
export function getBudgetVsActual(budget, ledger, month) {
  const allCategories = new Set([
    ...Object.keys(budget.items),
    'jajan', 'transportasi', 'sekolah', 'perawatanDiri', 'hiburan', 'komunikasi', 'lainLain',
  ]);

  return Array.from(allCategories).map(categoryId => {
    const budgeted = budget.items[categoryId] ?? 0;
    const actual = getTotalExpense(ledger, month, categoryId);
    const diff = budgeted - actual;
    return {
      categoryId,
      budgeted,
      actual,
      diff,
      overBudget: diff < 0,
    };
  });
}

/**
 * Load suggested budget from config.
 * @param {object} config - phase1.config.json
 * @returns {object} budget
 */
export function useSuggestion(config) {
  let budget = createBudget();
  const suggestion = config.budgetSuggestion ?? {};
  for (const [categoryId, amount] of Object.entries(suggestion)) {
    budget = setBudgetItem(budget, categoryId, amount);
  }
  return budget;
}
