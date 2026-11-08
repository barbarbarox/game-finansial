/**
 * navigationGrid.js — A* Pathfinding and Navigation Grid for Life Journey (Gate H5).
 * Features:
 * - Sub-tile resolution (16px cells for smooth movement)
 * - Inflated obstacle bounds preventing player clipping
 * - Corner-cutting prevention on diagonal moves
 * - Path smoothing (line-of-sight raycasting / string pulling)
 * - Auto-interact candidate proximity detection
 */

export class NavigationGrid {
  /**
   * @param {number} mapWidthPx - map width in pixels
   * @param {number} mapHeightPx - map height in pixels
   * @param {Array<{x: number, y: number, w: number, h: number}>} colliders
   * @param {number} [cellSize=16]
   */
  constructor(mapWidthPx, mapHeightPx, colliders = [], cellSize = 16) {
    this.cellSize = cellSize;
    this.cols = Math.ceil(mapWidthPx / cellSize);
    this.rows = Math.ceil(mapHeightPx / cellSize);
    this.mapWidthPx = mapWidthPx;
    this.mapHeightPx = mapHeightPx;
    this.colliders = colliders;

    // Grid: true = blocked, false = walkable
    this.grid = new Uint8Array(this.cols * this.rows);
    this._buildGrid(colliders);
  }

  _buildGrid(colliders) {
    // Player feet collision half-dimensions: hw = 8, hh = 5
    // Inflate obstacles slightly so center of player never clips
    const inflateX = 8;
    const inflateY = 6;

    for (const c of colliders) {
      const minX = Math.max(0, c.x - inflateX);
      const minY = Math.max(0, c.y - inflateY);
      const maxX = Math.min(this.mapWidthPx, c.x + c.w + inflateX);
      const maxY = Math.min(this.mapHeightPx, c.y + c.h + inflateY);

      const colStart = Math.floor(minX / this.cellSize);
      const colEnd = Math.min(this.cols - 1, Math.floor(maxX / this.cellSize));
      const rowStart = Math.floor(minY / this.cellSize);
      const rowEnd = Math.min(this.rows - 1, Math.floor(maxY / this.cellSize));

      for (let r = rowStart; r <= rowEnd; r++) {
        for (let cIdx = colStart; cIdx <= colEnd; cIdx++) {
          this.grid[r * this.cols + cIdx] = 1;
        }
      }
    }
  }

  isWalkable(col, row) {
    if (col < 0 || col >= this.cols || row < 0 || row >= this.rows) return false;
    return this.grid[row * this.cols + col] === 0;
  }

  worldToGrid(x, y) {
    return {
      col: Math.max(0, Math.min(this.cols - 1, Math.floor(x / this.cellSize))),
      row: Math.max(0, Math.min(this.rows - 1, Math.floor(y / this.cellSize)))
    };
  }

  gridToWorld(col, row) {
    return {
      x: col * this.cellSize + this.cellSize / 2,
      y: row * this.cellSize + this.cellSize / 2
    };
  }

  /**
   * Find path from (startX, startY) to (targetX, targetY).
   * @param {number} startX
   * @param {number} startY
   * @param {number} targetX
   * @param {number} targetY
   * @returns {Array<{x: number, y: number}>}
   */
  findPath(startX, startY, targetX, targetY) {
    const start = this.worldToGrid(startX, startY);
    let target = this.worldToGrid(targetX, targetY);

    if (start.col === target.col && start.row === target.row) {
      return [{ x: targetX, y: targetY }];
    }

    // If destination cell is blocked (e.g. user clicked directly on bed, NPC, or counter),
    // find nearest walkable neighbor cell to target
    if (!this.isWalkable(target.col, target.row)) {
      const nearest = this._findNearestWalkable(target.col, target.row, start.col, start.row);
      if (!nearest) return [];
      target = nearest;
    }

    const openSet = [];
    const closedSet = new Uint8Array(this.cols * this.rows);
    const gScore = new Float32Array(this.cols * this.rows).fill(Infinity);
    const cameFrom = new Int32Array(this.cols * this.rows).fill(-1);

    const startIndex = start.row * this.cols + start.col;
    const targetIndex = target.row * this.cols + target.col;

    gScore[startIndex] = 0;
    const hStart = this._heuristic(start.col, start.row, target.col, target.row);
    openSet.push({ index: startIndex, col: start.col, row: start.row, f: hStart });

    // 8 directions: [dx, dy, cost]
    const neighbors = [
      [ 1,  0, 1.0],
      [-1,  0, 1.0],
      [ 0,  1, 1.0],
      [ 0, -1, 1.0],
      [ 1,  1, 1.414],
      [-1,  1, 1.414],
      [ 1, -1, 1.414],
      [-1, -1, 1.414]
    ];

    let found = false;

    while (openSet.length > 0) {
      // Find lowest f-score in open set
      let lowestIdx = 0;
      for (let i = 1; i < openSet.length; i++) {
        if (openSet[i].f < openSet[lowestIdx].f) {
          lowestIdx = i;
        }
      }

      const current = openSet.splice(lowestIdx, 1)[0];
      const curIdx = current.index;

      if (curIdx === targetIndex) {
        found = true;
        break;
      }

      closedSet[curIdx] = 1;

      for (const [dx, dy, cost] of neighbors) {
        const ncol = current.col + dx;
        const nrow = current.row + dy;
        const nIdx = nrow * this.cols + ncol;

        if (!this.isWalkable(ncol, nrow)) continue;
        if (closedSet[nIdx]) continue;

        // Corner-cutting prevention: diagonal moves cannot cut across blocked orthogonal tiles
        if (dx !== 0 && dy !== 0) {
          if (!this.isWalkable(current.col + dx, current.row) || !this.isWalkable(current.col, current.row + dy)) {
            continue;
          }
        }

        const tentativeG = gScore[curIdx] + cost;
        if (tentativeG < gScore[nIdx]) {
          cameFrom[nIdx] = curIdx;
          gScore[nIdx] = tentativeG;
          const h = this._heuristic(ncol, nrow, target.col, target.row);
          const f = tentativeG + h;

          const existing = openSet.find(o => o.index === nIdx);
          if (existing) {
            existing.f = f;
          } else {
            openSet.push({ index: nIdx, col: ncol, row: nrow, f });
          }
        }
      }
    }

    if (!found) return [];

    // Reconstruct raw path
    const rawPath = [];
    let curr = targetIndex;
    while (curr !== -1) {
      const c = curr % this.cols;
      const r = Math.floor(curr / this.cols);
      rawPath.push(this.gridToWorld(c, r));
      curr = cameFrom[curr];
    }
    rawPath.reverse();

    // Replace first node with exact start and last node with exact target if walkable
    if (rawPath.length > 0) {
      rawPath[0] = { x: startX, y: startY };
      rawPath[rawPath.length - 1] = { x: targetX, y: targetY };
    }

    // Path smoothing
    return this._smoothPath(rawPath);
  }

  _heuristic(c1, r1, c2, r2) {
    // Octile distance
    const dx = Math.abs(c1 - c2);
    const dy = Math.abs(r1 - r2);
    return Math.max(dx, dy) + 0.414 * Math.min(dx, dy);
  }

  _findNearestWalkable(col, row, preferCol, preferRow) {
    for (let radius = 1; radius <= 6; radius++) {
      const candidates = [];
      for (let r = row - radius; r <= row + radius; r++) {
        for (let c = col - radius; c <= col + radius; c++) {
          if (Math.abs(r - row) === radius || Math.abs(c - col) === radius) {
            if (this.isWalkable(c, r)) {
              const dStart = Math.hypot(c - preferCol, r - preferRow);
              candidates.push({ col: c, row: r, d: dStart });
            }
          }
        }
      }
      if (candidates.length > 0) {
        candidates.sort((a, b) => a.d - b.d);
        return { col: candidates[0].col, row: candidates[0].row };
      }
    }
    return null;
  }

  /**
   * Raycast line of sight between two world points.
   * Checks if box along line segment intersects any collider.
   */
  hasLineOfSight(p1, p2) {
    const dist = Math.hypot(p2.x - p1.x, p2.y - p1.y);
    const steps = Math.ceil(dist / (this.cellSize / 2));
    if (steps <= 1) return true;

    for (let i = 1; i < steps; i++) {
      const t = i / steps;
      const x = p1.x + (p2.x - p1.x) * t;
      const y = p1.y + (p2.y - p1.y) * t;
      const g = this.worldToGrid(x, y);
      if (!this.isWalkable(g.col, g.row)) {
        return false;
      }
    }
    return true;
  }

  /**
   * String-pulling path smoothing.
   */
  _smoothPath(path) {
    if (path.length <= 2) return path;

    const smoothed = [path[0]];
    let currentIdx = 0;

    while (currentIdx < path.length - 1) {
      let furthest = currentIdx + 1;
      for (let next = path.length - 1; next > currentIdx + 1; next--) {
        if (this.hasLineOfSight(path[currentIdx], path[next])) {
          furthest = next;
          break;
        }
      }
      smoothed.push(path[furthest]);
      currentIdx = furthest;
    }

    return smoothed;
  }
}

