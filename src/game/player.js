/**
 * player.js — Player controller for Life Journey.
 * WASD/arrow key movement, 4-direction animation, collision, gasoline drain.
 */

export class PlayerController {
  /**
   * @param {Phaser.Scene} scene
   * @param {number} x
   * @param {number} y
   * @param {object} config
   */
  constructor(scene, x, y, config) {
    this.scene = scene;
    this.config = config ?? {};
    this.speed = 2 * (config?.tileSize ?? 32); // 64 px/s

    // Sprite (placeholder rectangle if no texture)
    this.sprite = scene.add.rectangle(x, y, 20, 32, 0x34456B);
    this.sprite.setDepth(500);

    // Shadow
    this.shadow = scene.add.ellipse(x, y + 14, 18, 8, 0x000000, 0.3);
    this.shadow.setDepth(499);

    // Direction indicator
    this.dirIndicator = scene.add.triangle(x, y - 20, 0, 10, 10, -10, -10, -10, 0xD9A441);
    this.dirIndicator.setDepth(501);

    // Input
    this.cursors = scene.input.keyboard.createCursorKeys();
    this.wasd = scene.input.keyboard.addKeys({
      up:    Phaser.Input.Keyboard.KeyCodes.W,
      down:  Phaser.Input.Keyboard.KeyCodes.S,
      left:  Phaser.Input.Keyboard.KeyCodes.A,
      right: Phaser.Input.Keyboard.KeyCodes.D,
    });

    // State
    this.vx = 0;
    this.vy = 0;
    this.facing = 'down';
    this.moving = false;
    this.bounceTimer = 0;

    // Gasoline drain (per real second, converted from per game-day)
    // dayDurationSeconds * gasolineDrainPerDay gives % per real second
    this.gasolineDrainRate = 0; // set by store subscription
    this._store = scene.game.registry.get('store');
    if (this._store) {
      const cfg = this.config;
      const dayDurSec = cfg.dayDurationSeconds ?? 12;
      this.gasolineDrainRate = (cfg.gasolineDrainPerDay ?? 5) / (dayDurSec * 1000); // %/ms
    }
  }

  /** @param {number} delta - ms since last frame */
  update(delta, colliders) {
    this._handleInput(delta, colliders);
    this._drainGasoline(delta);
    this._animate(delta);
  }

  _handleInput(delta, colliders) {
    const up    = this.cursors.up.isDown    || this.wasd.up.isDown;
    const down  = this.cursors.down.isDown  || this.wasd.down.isDown;
    const left  = this.cursors.left.isDown  || this.wasd.left.isDown;
    const right = this.cursors.right.isDown || this.wasd.right.isDown;

    this.vx = 0;
    this.vy = 0;

    if (left)  { this.vx = -this.speed; this.facing = 'left'; }
    if (right) { this.vx =  this.speed; this.facing = 'right'; }
    if (up)    { this.vy = -this.speed; this.facing = 'up'; }
    if (down)  { this.vy =  this.speed; this.facing = 'down'; }

    // Normalize diagonal
    if (this.vx !== 0 && this.vy !== 0) {
      const factor = 1 / Math.SQRT2;
      this.vx *= factor;
      this.vy *= factor;
    }

    this.moving = this.vx !== 0 || this.vy !== 0;

    if (!this.moving) return;

    const dt = delta / 1000; // seconds
    const nx = this.sprite.x + this.vx * dt;
    const ny = this.sprite.y + this.vy * dt;

    // Collision check
    const halfW = 10;
    const halfH = 12;

    const canX = !this._collidesAt(nx, this.sprite.y, halfW, halfH, colliders);
    const canY = !this._collidesAt(this.sprite.x, ny, halfW, halfH, colliders);

    if (canX) {
      this.sprite.x = nx;
      this.shadow.x = nx;
      this.dirIndicator.x = nx;
    }
    if (canY) {
      this.sprite.y = ny;
      this.shadow.y = ny + 14;
      this.dirIndicator.y = ny - 20;
    }

    // Depth sort by Y
    this.sprite.setDepth(500 + this.sprite.y / 1000);
  }

  _collidesAt(x, y, hw, hh, colliders) {
    const left   = x - hw;
    const right  = x + hw;
    const top    = y - hh;
    const bottom = y + hh;

    for (const c of colliders) {
      if (right > c.x && left < c.x + c.w &&
          bottom > c.y && top < c.y + c.h) {
        return true;
      }
    }
    return false;
  }

  _drainGasoline(delta) {
    if (!this._store || !this.moving) return;
    const state = this._store.getState();
    const gasoline = state.gasoline ?? 100;
    const newGas = Math.max(0, gasoline - this.gasolineDrainRate * delta);
    if (Math.abs(newGas - gasoline) > 0.01) {
      this._store.setState({ gasoline: newGas });
    }
  }

  _animate(delta) {
    if (!this.moving) return;

    // Bounce animation: vertical sine wave
    this.bounceTimer = (this.bounceTimer + delta * 0.01) % (Math.PI * 2);
    const bounceY = Math.sin(this.bounceTimer * 4) * 2;
    this.sprite.y += bounceY / 20; // subtle

    // Rotate direction indicator
    const angles = { down: 90, up: -90, left: 180, right: 0 };
    this.dirIndicator.setAngle(angles[this.facing] ?? 90);
  }

  get x() { return this.sprite.x; }
  get y() { return this.sprite.y; }
}
