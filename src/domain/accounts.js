/**
 * accounts.js — Account constants for the double-entry ledger.
 * All accounts used in Life Journey Phase 1.
 */

/** @enum {string} */
export const AccountId = {
  KAS_PRIBADI: 'KAS_PRIBADI',
  TABUNGAN: 'TABUNGAN',
  KEKAYAAN_BERSIH: 'KEKAYAAN_BERSIH',
  UANG_SAKU: 'UANG_SAKU',
  BONUS: 'BONUS',
  BEBAN_JAJAN: 'BEBAN_JAJAN',
  BEBAN_TRANSPORTASI: 'BEBAN_TRANSPORTASI',
  BEBAN_SEKOLAH: 'BEBAN_SEKOLAH',
  BEBAN_PERAWATAN_DIRI: 'BEBAN_PERAWATAN_DIRI',
  BEBAN_HIBURAN: 'BEBAN_HIBURAN',
  BEBAN_KOMUNIKASI: 'BEBAN_KOMUNIKASI',
  BEBAN_LAIN: 'BEBAN_LAIN',
};

/** Map categoryId → beban AccountId */
export const CATEGORY_ACCOUNT_MAP = {
  jajan: AccountId.BEBAN_JAJAN,
  transportasi: AccountId.BEBAN_TRANSPORTASI,
  sekolah: AccountId.BEBAN_SEKOLAH,
  perawatanDiri: AccountId.BEBAN_PERAWATAN_DIRI,
  hiburan: AccountId.BEBAN_HIBURAN,
  komunikasi: AccountId.BEBAN_KOMUNIKASI,
  lainLain: AccountId.BEBAN_LAIN,
};

/**
 * Account definitions.
 * type: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense'
 * normal: 'D' (debit-normal) | 'K' (kredit-normal)
 */
export const ACCOUNTS = [
  { id: AccountId.KAS_PRIBADI,         name: 'Kas Pribadi',         type: 'asset',   normal: 'D' },
  { id: AccountId.TABUNGAN,            name: 'Tabungan',            type: 'asset',   normal: 'D' },
  { id: AccountId.KEKAYAAN_BERSIH,     name: 'Kekayaan Bersih',     type: 'equity',  normal: 'K' },
  { id: AccountId.UANG_SAKU,           name: 'Uang Saku',           type: 'revenue', normal: 'K' },
  { id: AccountId.BONUS,               name: 'Bonus',               type: 'revenue', normal: 'K' },
  { id: AccountId.BEBAN_JAJAN,         name: 'Beban Jajan',         type: 'expense', normal: 'D' },
  { id: AccountId.BEBAN_TRANSPORTASI,  name: 'Beban Transportasi',  type: 'expense', normal: 'D' },
  { id: AccountId.BEBAN_SEKOLAH,       name: 'Beban Sekolah',       type: 'expense', normal: 'D' },
  { id: AccountId.BEBAN_PERAWATAN_DIRI,'name': 'Beban Perawatan Diri', type: 'expense', normal: 'D' },
  { id: AccountId.BEBAN_HIBURAN,       name: 'Beban Hiburan',       type: 'expense', normal: 'D' },
  { id: AccountId.BEBAN_KOMUNIKASI,    name: 'Beban Komunikasi',    type: 'expense', normal: 'D' },
  { id: AccountId.BEBAN_LAIN,          name: 'Beban Lain-lain',     type: 'expense', normal: 'D' },
];

export const ACCOUNT_MAP = Object.fromEntries(ACCOUNTS.map(a => [a.id, a]));
