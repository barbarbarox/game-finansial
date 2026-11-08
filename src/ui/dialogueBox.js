/**
 * dialogueBox.js — Dialogue System with Character Portraits.
 * Complies with Rule 71 (Dialogue System with Portraits) and Rule 50 (Security).
 */

import { getCash, addEntry, createExpenseEntry, createAllowanceEntry } from '../domain/ledger.js';
import { showTimeSkip } from './timeSkip.js';

let dialogueContainer = null;
let currentDialogue = null;
let currentNode = null;
let activeSpeaker = 'npc';
let isTyping = false;
let typeInterval = null;
let currentChoices = [];
let selectedChoiceIndex = 0;
let onDialogueClose = null;

/**
 * Ensure dialogue DOM elements are created and mounted.
 */
function ensureDialogueDOM() {
  if (dialogueContainer) return dialogueContainer;

  dialogueContainer = document.createElement('div');
  dialogueContainer.id = 'dialogue-overlay';
  dialogueContainer.className = 'dialogue-overlay hidden';
  dialogueContainer.setAttribute('role', 'dialog');
  dialogueContainer.setAttribute('aria-modal', 'true');

  dialogueContainer.innerHTML = `
    <div class="dialogue-backdrop"></div>
    <div class="dialogue-stage">
      <div class="dialogue-portrait-wrap portrait-left" id="dlg-player-portrait">
        <div class="portrait-box">
          <div class="portrait-img-placeholder">PEMAIN</div>
          <img class="portrait-img hidden" src="" alt="Player Portrait" />
        </div>
      </div>
      <div class="dialogue-portrait-wrap portrait-right" id="dlg-npc-portrait">
        <div class="portrait-box">
          <div class="portrait-img-placeholder" id="dlg-npc-placeholder">NPC</div>
          <img class="portrait-img hidden" src="" alt="NPC Portrait" />
        </div>
      </div>
    </div>
    <div class="dialogue-box-container">
      <div class="dialogue-choices-menu hidden" id="dlg-choices-menu"></div>
      <div class="dialogue-box" id="dlg-box">
        <div class="dialogue-nameplate" id="dlg-nameplate">NPC</div>
        <div class="dialogue-content">
          <p class="dialogue-text" id="dlg-text"></p>
          <span class="dialogue-prompt-hint" id="dlg-prompt-hint">▼ [Spasi / Enter]</span>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(dialogueContainer);

  // Setup click & keyboard navigation
  window.addEventListener('keydown', handleDialogueKeydown);
  const dlgBox = document.getElementById('dlg-box');
  dlgBox.addEventListener('click', handleDialogueAdvance);

  return dialogueContainer;
}

function handleDialogueKeydown(e) {
  if (!currentDialogue || dialogueContainer.classList.contains('hidden')) return;

  if (currentChoices.length > 0) {
    if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') {
      e.preventDefault();
      changeChoiceSelection(-1);
    } else if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') {
      e.preventDefault();
      changeChoiceSelection(1);
    } else if (e.key === 'Enter' || e.key === ' ' || e.key === 'e' || e.key === 'E') {
      e.preventDefault();
      confirmSelectedChoice();
    } else if (['1', '2', '3', '4'].includes(e.key)) {
      const idx = parseInt(e.key, 10) - 1;
      if (idx < currentChoices.length) {
        selectedChoiceIndex = idx;
        updateChoiceHighlight();
        confirmSelectedChoice();
      }
    }
  } else {
    if (e.key === 'Enter' || e.key === ' ' || e.key === 'e' || e.key === 'E') {
      e.preventDefault();
      handleDialogueAdvance();
    }
  }
}

function handleDialogueAdvance() {
  if (isTyping) {
    // Fast-skip typewriter
    clearInterval(typeInterval);
    isTyping = false;
    const textEl = document.getElementById('dlg-text');
    textEl.textContent = currentNode._fullText || '';
    onTypingFinished();
    return;
  }

  // If node has choices, wait for choice selection
  if (currentChoices.length > 0) return;

  // Next node or close
  if (currentNode && currentNode.next && currentDialogue.nodes[currentNode.next]) {
    displayNode(currentNode.next);
  } else {
    closeDialogue();
  }
}

/**
 * Replace tokens in text ({player}, {ibu}, {ayah})
 */
function substituteTokens(text) {
  const store = window.__LJ__?.getStore?.();
  const state = store?.getState?.() || {};
  const char = state.character || {};
  return text
    .replace(/{player}/g, char.name || state.playerName || 'Pemain')
    .replace(/{ibu}/g, char.motherName || state.motherName || 'Ibu')
    .replace(/{ayah}/g, char.fatherName || state.fatherName || 'Ayah');
}

/**
 * Display a dialogue node by id.
 */
function displayNode(nodeId) {
  const node = currentDialogue.nodes[nodeId];
  if (!node) {
    closeDialogue();
    return;
  }

  currentNode = node;
  activeSpeaker = node.speaker || 'npc';

  const textEl = document.getElementById('dlg-text');
  const nameplate = document.getElementById('dlg-nameplate');
  const choicesMenu = document.getElementById('dlg-choices-menu');
  const promptHint = document.getElementById('dlg-prompt-hint');

  choicesMenu.classList.add('hidden');
  choicesMenu.innerHTML = '';
  currentChoices = [];

  // Execute node effects if any
  if (node.effects) {
    executeEffects(node.effects);
  }

  const store = window.__LJ__?.getStore?.();
  const state = store?.getState?.() || {};
  const playerName = state.character?.name || state.playerName || 'Pemain';
  const npcName = currentDialogue.npcName || 'NPC';

  // Update Speaker Highlighting
  const playerWrap = document.getElementById('dlg-player-portrait');
  const npcWrap = document.getElementById('dlg-npc-portrait');

  if (activeSpeaker === 'player') {
    nameplate.textContent = playerName;
    nameplate.className = 'dialogue-nameplate side-player';
    playerWrap.classList.add('speaker-active');
    playerWrap.classList.remove('speaker-inactive');
    npcWrap.classList.add('speaker-inactive');
    npcWrap.classList.remove('speaker-active');
  } else {
    nameplate.textContent = npcName;
    nameplate.className = 'dialogue-nameplate side-npc';
    npcWrap.classList.add('speaker-active');
    npcWrap.classList.remove('speaker-inactive');
    playerWrap.classList.add('speaker-inactive');
    playerWrap.classList.remove('speaker-active');
  }

  // Typewriter effect
  const fullText = substituteTokens(node.text || '');
  currentNode._fullText = fullText;
  textEl.textContent = '';
  promptHint.classList.add('hidden');
  isTyping = true;

  let charIndex = 0;
  clearInterval(typeInterval);
  typeInterval = setInterval(() => {
    if (charIndex < fullText.length) {
      textEl.textContent += fullText[charIndex];
      charIndex++;
    } else {
      clearInterval(typeInterval);
      isTyping = false;
      onTypingFinished();
    }
  }, 22);
}

function onTypingFinished() {
  const promptHint = document.getElementById('dlg-prompt-hint');

  // If node has choices, render them
  if (currentNode.choices && currentNode.choices.length > 0) {
    renderChoices(currentNode.choices);
    promptHint.classList.add('hidden');

    // While choices are shown, highlight player (Rule 71 §2)
    const playerWrap = document.getElementById('dlg-player-portrait');
    const npcWrap = document.getElementById('dlg-npc-portrait');
    playerWrap.classList.add('speaker-active');
    playerWrap.classList.remove('speaker-inactive');
    npcWrap.classList.add('speaker-inactive');
    npcWrap.classList.remove('speaker-active');
  } else {
    promptHint.classList.remove('hidden');
  }
}

/**
 * Render choices menu (2–4 options).
 */
function renderChoices(choices) {
  const choicesMenu = document.getElementById('dlg-choices-menu');
  choicesMenu.innerHTML = '';
  currentChoices = [];
  selectedChoiceIndex = 0;

  const store = window.__LJ__?.getStore?.();
  const state = store?.getState?.() || {};
  const cash = state.ledger ? getCash(state.ledger) : 0;

  choices.forEach((choice, idx) => {
    let disabled = false;
    let reason = '';

    if (choice.requires?.minCash && cash < choice.requires.minCash) {
      disabled = true;
      reason = choice.disabledReason || `(Kurang Rp${(choice.requires.minCash - cash).toLocaleString('id-ID')})`;
    } else if (choice.requires?.flagNot && state.flags?.[choice.requires.flagNot]) {
      disabled = true;
      reason = choice.disabledReason || '(Sudah dilakukan)';
    } else if (choice.requires?.flag && !state.flags?.[choice.requires.flag]) {
      disabled = true;
      reason = choice.disabledReason || '(Belum tersedia)';
    }

    const btn = document.createElement('button');
    btn.className = `dialogue-choice-btn ${disabled ? 'disabled' : ''}`;
    btn.setAttribute('type', 'button');
    btn.setAttribute('tabindex', disabled ? '-1' : '0');

    const numBadge = document.createElement('span');
    numBadge.className = 'choice-number';
    numBadge.textContent = `${idx + 1}.`;

    const labelSpan = document.createElement('span');
    labelSpan.className = 'choice-label';
    labelSpan.textContent = substituteTokens(choice.text);

    btn.appendChild(numBadge);
    btn.appendChild(labelSpan);

    if (disabled && reason) {
      const reasonSpan = document.createElement('span');
      reasonSpan.className = 'choice-disabled-reason';
      reasonSpan.textContent = reason;
      btn.appendChild(reasonSpan);
    }

    if (!disabled) {
      btn.addEventListener('click', () => {
        selectedChoiceIndex = idx;
        confirmSelectedChoice();
      });
      btn.addEventListener('mouseenter', () => {
        selectedChoiceIndex = idx;
        updateChoiceHighlight();
      });
    }

    choicesMenu.appendChild(btn);
    currentChoices.push({ choice, element: btn, disabled });
  });

  // Find first non-disabled choice to highlight
  const firstEnabled = currentChoices.findIndex(c => !c.disabled);
  selectedChoiceIndex = firstEnabled >= 0 ? firstEnabled : 0;
  updateChoiceHighlight();

  choicesMenu.classList.remove('hidden');
}

function updateChoiceHighlight() {
  currentChoices.forEach((c, idx) => {
    if (idx === selectedChoiceIndex && !c.disabled) {
      c.element.classList.add('selected');
    } else {
      c.element.classList.remove('selected');
    }
  });
}

function changeChoiceSelection(dir) {
  if (currentChoices.length === 0) return;
  let next = selectedChoiceIndex + dir;
  if (next < 0) next = currentChoices.length - 1;
  if (next >= currentChoices.length) next = 0;

  // Skip disabled if possible
  if (currentChoices[next].disabled) {
    next = (next + dir + currentChoices.length) % currentChoices.length;
  }

  selectedChoiceIndex = next;
  updateChoiceHighlight();
}

/**
 * Execute whitelisted effects safely.
 */
function executeEffects(effects = []) {
  if (!Array.isArray(effects)) return;

  const store = window.__LJ__?.getStore?.();
  if (!store) return;
  let state = store.getState();

  for (const eff of effects) {
    if (!eff || typeof eff !== 'object') continue;

    switch (eff.type) {
      case 'ledger_expense': {
        if (state.ledger) {
          const clock = state.clock || {};
          const entry = createExpenseEntry(
            clock.day || 1,
            clock.month || 1,
            eff.categoryId || 'BEBAN_LAIN',
            eff.amount || 0,
            eff.description || 'Pengeluaran',
            clock.timeOfDay || 360
          );
          const res = addEntry(state.ledger, entry);
          if (!res.error) {
            state = { ...state, ledger: res.ledger };
            store.setState({ ledger: res.ledger });
          }
        }
        break;
      }

      case 'grant_allowance': {
        if (state.ledger) {
          const clock = state.clock || {};
          const currentMonth = clock.month || 1;
          const alreadyGranted = state.ledger.entries?.some(e => (e.kind === 'allowance' || e.type === 'allowance') && e.month === currentMonth);
          if (!alreadyGranted) {
            const entry = createAllowanceEntry(clock.day || 1, currentMonth, clock.timeOfDay || 360);
            const res = addEntry(state.ledger, entry);
            if (!res.error) {
              const updatedMissions = (state.missions || []).map(m =>
                m.id === 'M1' ? { ...m, completed: true } : m
              );
              state = { ...state, ledger: res.ledger, missions: updatedMissions };
              store.setState({ ledger: res.ledger, missions: updatedMissions });
            }
          }
        }
        break;
      }

      case 'start_activity': {
        const actId = eff.activityId;
        const minutes = actId === 'pelajaran_sekolah' ? 120 : (actId === 'main_game' ? 60 : 30);
        showTimeSkip({
          title: `Aktivitas: ${actId}`,
          minutes: minutes,
          onComplete: () => {
            if (window.__LJ__) window.__LJ__.advanceTime(minutes, actId);
          }
        });
        break;
      }

      case 'map_transition': {
        const mapMgr = window.__LJ__?.getMapManager?.();
        if (mapMgr && eff.targetMap) {
          mapMgr.transitionTo(eff.targetMap, eff.targetSpawn || 'default');
        }
        break;
      }

      case 'set_flag': {
        if (eff.flagKey) {
          const flags = { ...(state.flags || {}), [eff.flagKey]: eff.value ?? true };
          store.setState({ flags });
        }
        break;
      }

      case 'open_budget': {
        document.dispatchEvent(new CustomEvent('lj:openPanel', { detail: { panel: 'budget' } }));
        break;
      }

      default:
        console.warn(`[Dialogue] Effect tipe tidak dikenal / tidak di-whitelist: ${eff.type}`);
    }
  }
}

function confirmSelectedChoice() {
  const chosen = currentChoices[selectedChoiceIndex];
  if (!chosen || chosen.disabled) return;

  const choice = chosen.choice;

  // Execute choice effects
  if (choice.effects) {
    executeEffects(choice.effects);
  }

  // Go to next node or close
  if (choice.next && currentDialogue.nodes[choice.next]) {
    displayNode(choice.next);
  } else {
    closeDialogue();
  }
}

/**
 * Start a dialogue by id or dialogue object.
 * @param {string|object} dialogueOrId
 * @param {string} [npcId]
 * @param {function} [onClose]
 */
export async function startDialogue(dialogueOrId, npcId = null, onClose = null) {
  ensureDialogueDOM();

  let dialogue = dialogueOrId;
  if (typeof dialogueOrId === 'string') {
    try {
      const res = await fetch(`data/dialogues/${dialogueOrId}.json`);
      dialogue = await res.json();
    } catch (err) {
      console.error(`[Dialogue] Gagal memuat dialog: ${dialogueOrId}`, err);
      return false;
    }
  }

  if (!dialogue || !dialogue.nodes || !dialogue.nodes.start) {
    console.error('[Dialogue] Format data dialog tidak valid (harus punya nodes.start)');
    return false;
  }

  currentDialogue = dialogue;
  onDialogueClose = onClose;

  // Set NPC placeholder label
  const npcPlaceholder = document.getElementById('dlg-npc-placeholder');
  if (npcPlaceholder) {
    npcPlaceholder.textContent = (dialogue.npcName || npcId || 'NPC').toUpperCase();
  }

  // Set Player portrait
  const playerImg = document.querySelector('#dlg-player-portrait .portrait-img');
  const playerPlaceholder = document.querySelector('#dlg-player-portrait .portrait-img-placeholder');
  const store = window.__LJ__?.getStore?.();
  const state = store?.getState?.() || {};
  const isFemale = state.character?.gender === 'female';
  const playerPortraitSrc = isFemale ? 'assets/portraits/portrait_player_f.png' : 'assets/portraits/portrait_player_m.png';
  if (playerImg) {
    playerImg.src = playerPortraitSrc;
    playerImg.classList.remove('hidden');
    if (playerPlaceholder) playerPlaceholder.classList.add('hidden');
  }

  // Set NPC portrait if available
  const npcImg = document.querySelector('#dlg-npc-portrait .portrait-img');
  let portraitSrc = dialogue.portrait;
  if (!portraitSrc) {
    const portraitMap = {
      'npc_ibu': 'assets/portraits/portrait_ibu.png',
      'npc_ayah': 'assets/portraits/portrait_ayah.png',
      'npc_budi': 'assets/portraits/portrait_teman_l.png',
      'npc_teman': 'assets/portraits/portrait_teman_l.png',
      'npc_siti': 'assets/portraits/portrait_teman_p.png',
      'npc_kantin': 'assets/portraits/portrait_penjual_kantin.png',
      'npc_penjual': 'assets/portraits/portrait_penjual_kantin.png',
      'npc_kasir_minimarket': 'assets/portraits/portrait_kasir_minimarket.png',
      'npc_kasir': 'assets/portraits/portrait_kasir_minimarket.png',
      'npc_cindy': 'assets/portraits/portrait_penjaga_kosmetik.png',
      'npc_penjaga_kosmetik': 'assets/portraits/portrait_penjaga_kosmetik.png',
      'npc_doni': 'assets/portraits/portrait_petugas_spbu.png',
      'npc_petugas_spbu': 'assets/portraits/portrait_petugas_spbu.png',
      'npc_pak_anto': 'assets/portraits/portrait_petugas_spbu.png',
      'npc_riko': 'assets/portraits/portrait_penjaga_game.png',
      'npc_penjaga_game': 'assets/portraits/portrait_penjaga_game.png'
    };
    portraitSrc = portraitMap[npcId] || portraitMap[dialogue.npcId];
  }

  if (portraitSrc) {
    if (npcImg) {
      npcImg.src = portraitSrc;
      npcImg.classList.remove('hidden');
      if (npcPlaceholder) npcPlaceholder.classList.add('hidden');
    }
  } else {
    if (npcImg) npcImg.classList.add('hidden');
    if (npcPlaceholder) npcPlaceholder.classList.remove('hidden');
  }

  // Show dialogue overlay
  dialogueContainer.classList.remove('hidden');
  dialogueContainer.classList.add('visible');

  displayNode('start');
  return true;
}

/**
 * Close dialogue overlay.
 */
export function closeDialogue() {
  clearInterval(typeInterval);
  isTyping = false;
  currentDialogue = null;
  currentNode = null;
  currentChoices = [];

  if (dialogueContainer) {
    dialogueContainer.classList.remove('visible');
    dialogueContainer.classList.add('hidden');
  }

  if (onDialogueClose) {
    const cb = onDialogueClose;
    onDialogueClose = null;
    cb();
  }
}

/**
 * Return current dialogue inspection state for tests & debug.
 */
export function getDialogueState() {
  if (isTyping) {
    clearInterval(typeInterval);
    isTyping = false;
    const textEl = document.getElementById('dlg-text');
    if (textEl) textEl.textContent = currentNode?._fullText || '';
    onTypingFinished();
  }
  return {
    active: Boolean(currentDialogue),
    currentNodeId: currentNode?.id || null,
    speaker: activeSpeaker,
    currentText: currentNode?._fullText || '',
    choices: currentChoices.map(c => ({
      text: c.choice.text,
      disabled: c.disabled,
      selected: c.element.classList.contains('selected')
    }))
  };
}

export function chooseOption(index) {
  if (isTyping) {
    clearInterval(typeInterval);
    isTyping = false;
    const textEl = document.getElementById('dlg-text');
    if (textEl) textEl.textContent = currentNode?._fullText || '';
    onTypingFinished();
  }
  if (index >= 0 && index < currentChoices.length) {
    selectedChoiceIndex = index;
    confirmSelectedChoice();
    return true;
  }
  return false;
}

