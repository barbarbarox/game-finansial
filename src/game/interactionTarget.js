/**
 * interactionTarget.js — Deterministic Interaction Targeting System (Rule 84).
 * Determines the best interactable candidate based on distance, facing direction,
 * and priority weights (NPC bonus +20px, Tutorial objective bonus +40px).
 */

export const DEFAULT_INTERACTION_CONFIG = {
  interactRangePx: 44,
  npcBonusPx: 20,
  objectiveBonusPx: 40,
  facingPenaltyMaxPx: 12,
  cycleKey: 'Tab',
  npcClearanceTiles: 1.5,
  npcSelectedMinRatio: 0.9
};

/**
 * Calculates dot product or angle penalty based on player facing direction.
 * @param {string} facing - 'up' | 'down' | 'left' | 'right'
 * @param {number} dx - targetX - playerX
 * @param {number} dy - targetY - playerY
 * @param {number} maxPenalty
 * @returns {number} penalty in pixels [0..maxPenalty]
 */
function calculateFacingPenalty(facing, dx, dy, maxPenalty = 12) {
  const dist = Math.hypot(dx, dy);
  if (dist === 0) return 0;

  const nx = dx / dist;
  const ny = dy / dist;

  let fx = 0, fy = 0;
  if (facing === 'up') fy = -1;
  else if (facing === 'down') fy = 1;
  else if (facing === 'left') fx = -1;
  else if (facing === 'right') fx = 1;

  // Dot product in [-1..1]
  const dot = fx * nx + fy * ny;

  // If in the forward hemisphere (dot >= 0), penalty ranges from 0 (straight ahead) to maxPenalty/2
  // If behind (dot < 0), penalty ranges from maxPenalty/2 to maxPenalty
  if (dot >= 0) {
    return (1 - dot) * (maxPenalty * 0.5);
  } else {
    return (maxPenalty * 0.5) + (-dot) * (maxPenalty * 0.5);
  }
}

/**
 * Select the single best interaction target from available entities.
 * @param {object} player - { x, y, facing } in world pixels
 * @param {Array} interactables - list of world interactable definitions
 * @param {Array} [npcs] - list of world NPC definitions
 * @param {string|null} [objectiveTargetId] - ID of active tutorial / mission objective
 * @param {object} [config]
 * @returns {object|null} { target, entityType, score, prompt, candidates }
 */
export function findBestInteractionTarget(player, interactables = [], npcs = [], objectiveTargetId = null, config = DEFAULT_INTERACTION_CONFIG) {
  if (!player) return null;

  const px = player.x;
  const py = player.y;
  const facing = player.facing || 'down';
  const range = config.interactRangePx ?? 44;
  const maxPenalty = config.facingPenaltyMaxPx ?? 12;

  const candidates = [];

  // 1. Evaluate NPCs
  for (const npc of npcs) {
    const nx = (npc.x !== undefined ? npc.x * 32 + 16 : npc.pixelX ?? 0);
    const ny = (npc.y !== undefined ? npc.y * 32 + 24 : npc.pixelY ?? 0);
    const dist = Math.hypot(nx - px, ny - py);

    if (dist <= range + 10) {
      const penalty = calculateFacingPenalty(facing, nx - px, ny - py, maxPenalty);
      const isObjective = objectiveTargetId && (npc.id === objectiveTargetId || npc.dialogId === objectiveTargetId);
      const bonus = (config.npcBonusPx ?? 20) + (isObjective ? (config.objectiveBonusPx ?? 40) : 0);
      const score = dist - bonus + penalty;

      const name = npc.name || 'NPC';
      candidates.push({
        target: npc,
        entityType: 'npc',
        id: npc.id,
        score,
        dist,
        prompt: `E · Bicara dengan ${name}`,
        x: nx,
        y: ny
      });
    }
  }

  // 2. Evaluate Map Interactables
  for (const int of interactables) {
    const rx0 = (int.x || 0) * 32;
    const ry0 = (int.y || 0) * 32;
    const rw = (int.w || 1) * 32;
    const rh = (int.h || 1) * 32;

    const closestX = Math.max(rx0, Math.min(px, rx0 + rw));
    const closestY = Math.max(ry0, Math.min(py, ry0 + rh));
    const dist = Math.hypot(closestX - px, closestY - py);

    if (dist <= range) {
      const penalty = calculateFacingPenalty(facing, closestX - px, closestY - py, maxPenalty);
      const isObjective = objectiveTargetId && int.id === objectiveTargetId;
      const bonus = isObjective ? (config.objectiveBonusPx ?? 40) : 0;
      const score = dist - bonus + penalty;

      let prompt = int.prompt || 'Tekan [E]';
      // Format prompt into clean verb format: E · Action
      if (prompt.includes('[E]')) {
        prompt = prompt.replace('Tekan [E]', 'E ·').trim();
      }

      candidates.push({
        target: int,
        entityType: int.type || 'interactable',
        id: int.id,
        score,
        dist,
        prompt,
        x: closestX,
        y: closestY
      });
    }
  }

  if (candidates.length === 0) return null;

  // Sort by score ascending (lowest score wins), then by ID for deterministic tie-break
  candidates.sort((a, b) => {
    if (Math.abs(a.score - b.score) > 0.001) {
      return a.score - b.score;
    }
    return String(a.id).localeCompare(String(b.id));
  });

  const best = candidates[0];
  best.candidates = candidates;
  return best;
}

/**
 * Validates interaction overlap for an NPC across radial sample points (Rule 84 §3).
 * Samples standing points around the NPC within 32-40px;
 * Returns the percentage of positions where the NPC is chosen as best target.
 * @param {object} npc - { id, x, y, name } in tile coordinates
 * @param {Array} interactables
 * @param {Array} otherNpcs
 * @param {object} [config]
 * @returns {{ npcId: string, pass: boolean, ratio: number, totalSamples: number, wonSamples: number }}
 */
export function checkNpcInteractionOverlap(npc, interactables = [], otherNpcs = [], config = DEFAULT_INTERACTION_CONFIG) {
  const npcPx = (npc.x * 32) + 16;
  const npcPy = (npc.y * 32) + 24;

  const angles = [0, 45, 90, 135, 180, 225, 270, 315];
  const radii = [28, 36, 42];
  let won = 0;
  let total = 0;

  const allNpcs = [npc, ...otherNpcs.filter(n => n.id !== npc.id)];

  for (const r of radii) {
    for (const deg of angles) {
      const rad = (deg * Math.PI) / 180;
      const px = npcPx + Math.cos(rad) * r;
      const py = npcPy + Math.sin(rad) * r;

      // Determine facing towards NPC
      const dx = npcPx - px;
      const dy = npcPy - py;
      let facing = 'down';
      if (Math.abs(dx) > Math.abs(dy)) {
        facing = dx > 0 ? 'right' : 'left';
      } else {
        facing = dy > 0 ? 'down' : 'up';
      }

      total++;
      const best = findBestInteractionTarget({ x: px, y: py, facing }, interactables, allNpcs, null, config);
      if (best && best.id === npc.id) {
        won++;
      }
    }
  }

  const ratio = total > 0 ? won / total : 0;
  const minRatio = config.npcSelectedMinRatio ?? 0.9;
  return {
    npcId: npc.id,
    pass: ratio >= minRatio,
    ratio: Math.round(ratio * 100) / 100,
    totalSamples: total,
    wonSamples: won
  };
}
