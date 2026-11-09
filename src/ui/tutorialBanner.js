/**
 * tutorialBanner.js — Objective Banner & HUD Highlight Controller (Rule 82 §4.1, §4.4).
 * Mounts a responsive guided objective card at the top center of the game screen.
 */

import { DOMAIN_EVENTS, subscribe } from '../domain/events.js';

export class TutorialBanner {
  /**
   * @param {object} store
   * @param {object} tutorialManager
   */
  constructor(store, tutorialManager) {
    this.store = store;
    this.tutorialManager = tutorialManager;
    this.el = null;
    this.collapsed = false;
    this.unsubscribers = [];
    this._interval = null;

    this._mount();
  }

  destroy() {
    for (const unsub of this.unsubscribers) {
      if (typeof unsub === 'function') unsub();
    }
    this.unsubscribers = [];
    if (this._interval) clearInterval(this._interval);
    if (this.el && this.el.parentNode) {
      this.el.parentNode.removeChild(this.el);
    }
    this._clearHighlights();
  }

  _mount() {
    const uiContainer = document.getElementById('ui-container') || document.body;

    this.el = document.createElement('div');
    this.el.className = 'tutorial-objective-card';
    this.el.setAttribute('role', 'region');
    this.el.setAttribute('aria-label', 'Panduan Misi Tutorial');

    this.el.innerHTML = `
      <div class="tutorial-card-header">
        <span class="tutorial-step-badge" id="tut-badge">LANGKAH 1/20</span>
        <span class="tutorial-title" id="tut-title">Bangun dan bergerak</span>
        <button type="button" class="tutorial-btn-toggle" id="tut-toggle" title="Ciutkan/Perluas">▲</button>
      </div>
      <div class="tutorial-card-body" id="tut-body">
        <p class="tutorial-instruction" id="tut-instruction">...</p>
        <div class="tutorial-dots" id="tut-dots"></div>
        <div class="tutorial-card-footer">
          <span class="tutorial-hint" id="tut-hint"></span>
          <button type="button" class="tutorial-skip-btn hidden" id="tut-skip">Lewati Langkah (Anti-Macet)</button>
        </div>
      </div>
    `;

    uiContainer.appendChild(this.el);

    // Toggle collapse
    const toggleBtn = this.el.querySelector('#tut-toggle');
    const bodyEl = this.el.querySelector('#tut-body');
    toggleBtn.addEventListener('click', () => {
      this.collapsed = !this.collapsed;
      bodyEl.classList.toggle('hidden', this.collapsed);
      toggleBtn.textContent = this.collapsed ? '▼' : '▲';
    });

    // Skip button
    const skipBtn = this.el.querySelector('#tut-skip');
    skipBtn.addEventListener('click', () => {
      this.tutorialManager.skipCurrentStep();
    });

    // Listen to store & tutorial events
    this.unsubscribers.push(
      subscribe(DOMAIN_EVENTS.TUTORIAL_STEP_CHANGED, () => this.render()),
      subscribe(DOMAIN_EVENTS.TUTORIAL_COMPLETED, () => this.destroy())
    );

    // Check 180s timer for skip button
    this._interval = setInterval(() => this._checkSkipButton(), 5000);

    this.render();
  }

  render() {
    if (!this.el) return;

    const tut = this.store.getState()?.tutorial;
    if (!tut || !tut.active || tut.completed) {
      this.el.classList.add('hidden');
      this._clearHighlights();
      return;
    }

    this.el.classList.remove('hidden');

    const step = this.tutorialManager.getCurrentStep();
    if (!step) return;

    const stepIndex = tut.stepIndex;
    const totalSteps = this.tutorialManager.steps.length;

    // Header
    const badge = this.el.querySelector('#tut-badge');
    if (badge) badge.textContent = `LANGKAH ${stepIndex + 1}/${totalSteps}`;

    const title = this.el.querySelector('#tut-title');
    if (title) title.textContent = step.title;

    // Instruction & Hint
    const instr = this.el.querySelector('#tut-instruction');
    if (instr) instr.textContent = step.instruction;

    const hint = this.el.querySelector('#tut-hint');
    if (hint) hint.textContent = step.hint ? `💡 ${step.hint}` : '';

    // Render 20 progress dots
    const dotsContainer = this.el.querySelector('#tut-dots');
    if (dotsContainer) {
      dotsContainer.innerHTML = '';
      for (let i = 0; i < totalSteps; i++) {
        const dot = document.createElement('span');
        dot.className = 'tut-dot';
        if (i < stepIndex) dot.classList.add('completed');
        else if (i === stepIndex) dot.classList.add('active');
        dotsContainer.appendChild(dot);
      }
    }

    this._checkSkipButton();
    this._applyHighlights(step.highlights || []);
  }

  _checkSkipButton() {
    if (!this.el) return;
    const skipBtn = this.el.querySelector('#tut-skip');
    if (!skipBtn) return;

    const tut = this.store.getState()?.tutorial;
    if (!tut || !tut.stepStartTime) {
      skipBtn.classList.add('hidden');
      return;
    }

    const elapsedSec = (Date.now() - tut.stepStartTime) / 1000;
    // Show skip button only after 180 seconds (Rule 82 §4.6)
    if (elapsedSec >= 180) {
      skipBtn.classList.remove('hidden');
    } else {
      skipBtn.classList.add('hidden');
    }
  }

  _clearHighlights() {
    const pulsed = document.querySelectorAll('.hud-tutorial-pulse');
    pulsed.forEach(el => el.classList.remove('hud-tutorial-pulse'));
  }

  _applyHighlights(highlights) {
    this._clearHighlights();
    for (const h of highlights) {
      let targetSelector = null;
      if (h === 'hud.anggaran') targetSelector = '.hud-nav button:nth-child(3)';
      else if (h === 'hud.hotbar') targetSelector = '#hud-hotbar';
      else if (h === 'hud.motor') targetSelector = '.hud-btn-vehicle';
      else if (h === 'hud.ransel') targetSelector = '#hud-backpack-btn';
      else if (h === 'hud.energi') targetSelector = '.hm-energy-track';

      if (targetSelector) {
        const targetEl = document.querySelector(targetSelector);
        if (targetEl) targetEl.classList.add('hud-tutorial-pulse');
      }
    }
  }
}
