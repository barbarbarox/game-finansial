/**
 * itemsCatalog.js — Catalog of food & drink items for Life Journey (Rule 74 §4).
 * Pure domain module with zero DOM / Phaser dependencies.
 */

export const ITEMS_LIST = [
  {
    id: "air_mineral",
    label: "Air mineral",
    price: 3000,
    energy: 5,
    consumeMinutes: 2,
    stackMax: 5,
    sellAt: ["minimarket", "rumah"],
    category: "kebutuhan",
    categoryId: "jajan",
    iconAsset: "item_air_mineral"
  },
  {
    id: "isotonik",
    label: "Minuman isotonik",
    price: 8000,
    energy: 15,
    consumeMinutes: 2,
    stackMax: 5,
    sellAt: ["minimarket"],
    category: "keinginan",
    categoryId: "jajan",
    iconAsset: "item_isotonik"
  },
  {
    id: "nasi_goreng",
    label: "Nasi goreng",
    price: 15000,
    energy: 40,
    consumeMinutes: 10,
    stackMax: 5,
    sellAt: ["minimarket"],
    category: "kebutuhan",
    categoryId: "jajan",
    iconAsset: "item_nasi_goreng"
  },
  {
    id: "mie_goreng",
    label: "Mie goreng",
    price: 12000,
    energy: 35,
    consumeMinutes: 10,
    stackMax: 5,
    sellAt: ["minimarket"],
    category: "kebutuhan",
    categoryId: "jajan",
    iconAsset: "item_mie_goreng"
  },
  {
    id: "nasi_kuning",
    label: "Nasi kuning",
    price: 10000,
    energy: 30,
    consumeMinutes: 15,
    stackMax: 5,
    sellAt: ["kantin"],
    category: "kebutuhan",
    categoryId: "jajan",
    iconAsset: "item_nasi_kuning"
  },
  {
    id: "bakso",
    label: "Bakso",
    price: 12000,
    energy: 30,
    consumeMinutes: 15,
    stackMax: 5,
    sellAt: ["kantin"],
    category: "kebutuhan",
    categoryId: "jajan",
    iconAsset: "item_bakso"
  },
  {
    id: "roti_isi",
    label: "Roti isi",
    price: 7000,
    energy: 20,
    consumeMinutes: 5,
    stackMax: 5,
    sellAt: ["minimarket"],
    category: "kebutuhan",
    categoryId: "jajan",
    iconAsset: "item_roti_isi"
  },
  {
    id: "pisang",
    label: "Pisang",
    price: 5000,
    energy: 12,
    consumeMinutes: 3,
    stackMax: 5,
    sellAt: ["minimarket"],
    category: "kebutuhan",
    categoryId: "jajan",
    iconAsset: "item_pisang"
  },
  {
    id: "keripik",
    label: "Keripik",
    price: 8000,
    energy: 10,
    consumeMinutes: 3,
    stackMax: 5,
    sellAt: ["minimarket"],
    category: "keinginan",
    categoryId: "jajan",
    iconAsset: "item_keripik"
  },
  {
    id: "gorengan",
    label: "Gorengan",
    price: 5000,
    energy: 10,
    consumeMinutes: 3,
    stackMax: 5,
    sellAt: ["kantin"],
    category: "keinginan",
    categoryId: "jajan",
    iconAsset: "item_gorengan"
  },
  {
    id: "mie_cup",
    label: "Mie cup",
    price: 6000,
    energy: 15,
    consumeMinutes: 5,
    stackMax: 5,
    sellAt: ["minimarket"],
    category: "keinginan",
    categoryId: "jajan",
    iconAsset: "item_mie_cup"
  },
  {
    id: "susu_kotak",
    label: "Susu kotak",
    price: 6000,
    energy: 12,
    consumeMinutes: 2,
    stackMax: 5,
    sellAt: ["minimarket"],
    category: "kebutuhan",
    categoryId: "jajan",
    iconAsset: "item_susu_kotak"
  },
  {
    id: "teh_kemasan",
    label: "Teh kemasan",
    price: 5000,
    energy: 8,
    consumeMinutes: 2,
    stackMax: 5,
    sellAt: ["minimarket"],
    category: "keinginan",
    categoryId: "jajan",
    iconAsset: "item_teh_kemasan"
  },
  {
    id: "jus_kotak",
    label: "Jus kotak",
    price: 7000,
    energy: 12,
    consumeMinutes: 2,
    stackMax: 5,
    sellAt: ["minimarket"],
    category: "keinginan",
    categoryId: "jajan",
    iconAsset: "item_jus_kotak"
  },
  {
    id: "es_teh",
    label: "Es teh",
    price: 3000,
    energy: 5,
    consumeMinutes: 2,
    stackMax: 5,
    sellAt: ["kantin"],
    category: "keinginan",
    categoryId: "jajan",
    iconAsset: "item_es_teh"
  },
  {
    id: "coklat_batang",
    label: "Coklat batang",
    price: 10000,
    energy: 8,
    consumeMinutes: 2,
    stackMax: 5,
    sellAt: ["minimarket"],
    category: "keinginan",
    categoryId: "jajan",
    iconAsset: "item_coklat_batang"
  }
];

export const ITEMS_MAP = Object.fromEntries(
  ITEMS_LIST.map(item => [item.id, item])
);

export function getItemsForLocation(locationId) {
  return ITEMS_LIST.filter(item => Array.isArray(item.sellAt) && item.sellAt.includes(locationId));
}

