/**
 * player.js — Player controller for Life Journey.
 * WASD/arrow key movement, 4-direction animation using character spritesheet,
 * Tahap A walking bounce animation, collision, and gasoline drain.
 */

export class PlayerController {
  constructor(scene, x, y, config) {
    this.scene = scene;
    this.config = config || {};
    this.speed = 3 * (config?.tileSize || 32); // 96 px/s smooth walking

    this._store = scene.game.registry.get('store');
    const state = this._store ? this._store.getState() : null;
    const gender = state?.character?.gender || 'm';
    const playerName = state?.character?.name || 'Pemain';
    this.textureKey = gender === 'f' ? 'char_player_f_casual' : 'char_player_m_casual';

    // Shadow at feet
    this.shadow = scene.add.ellipse(x, y, 22, 10, 0x121A2E, 0.4);
    this.shadow.setOrigin(0.5, 0.5);

    // Sprite (using real spritesheet if loaded, otherwise fallback rectangle)
    if (scene.textures.exists(this.textureKey)) {
      this.sprite = scene.add.sprite(x, y, this.textureKey, 0);
      this.sprite.setOrigin(0.5, 1.0); // anchor at feet
      this.hasTexture = true;
    } else {
      this.sprite = scene.add.rectangle(x, y, 24, 48, 0x34456B);
      this.sprite.setOrigin(0.5, 1.0);
      this.hasTexture = false;
    }

    // Player indicator label above sprite (floating name tag with arrow)
    const indicatorBg = scene.add.rectangle(x, y - 60, 70, 20, 0xD9A441, 0.9);
    indicatorBg.setOrigin(0.5, 1.0);
    indicatorBg.setStrokeStyle(1, 0x121A2E, 1);

    this._indicatorBg = indicatorBg;
    this._indicatorText = scene.add.text(x, y - 61, playerName, {
      font: 'bold 10px sans-serif',
      fill: '#121A2E',
      resolution: 2,
    }).setOrigin(0.5, 1.0);

    // Small downward arrow triangle below the label
    this._indicatorArrow = scene.add.triangle(
      x, y - 42,
      -6, 0, 6, 0, 0, 7,
      0xD9A441, 0.9
    ).setOrigin(0.5, 0.5);

    // Adjust indicator width to fit player name
    indicatorBg.width = Math.max(60, this._indicatorText.width + 16);

    // Set initial depths for indicator
    indicatorBg.setDepth(5000);
    this._indicatorText.setDepth(5001);
    this._indicatorArrow.setDepth(5000);
    this._updateIndicator();

    // Input keys
    this.cursors = scene.input.keyboard.createCursorKeys();
    this.wasd = scene.input.keyboard.addKeys({
      up: Phaser.Input.Keyboard.KeyCodes.W,
      down: Phaser.Input.Keyboard.KeyCodes.S,
      left: Phaser.Input.Keyboard.KeyCodes.A,
      right: Phaser.Input.Keyboard.KeyCodes.D,
    });

    // State
    this.vx = 0;
    this.vy = 0;
    this.facing = 'down';
    this.moving = false;
    this.walkTimer = 0;
    this.isMounted = false;

    const dayDurSec = this.config.dayDurationSeconds || 12;
    this.gasolineDrainRate = (this.config.gasolineDrainPerDay || 5) / (dayDurSec * 1000);
  }

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

    if (this.vx !== 0 && this.vy !== 0) {
      const factor = 1 / Math.SQRT2;
      this.vx *= factor;
      this.vy *= factor;
    }

    this.moving = this.vx !== 0 || this.vy !== 0;
    if (!this.moving) return;

    const dt = delta / 1000;
    const nx = this.sprite.x + this.vx * dt;
    const ny = this.sprite.y + this.vy * dt;

    // Feet collision box (Rule 73 §5: 16x10 px normal, 24x12 px mounted)
    const hw = this.isMounted ? 12 : 8;
    const hh = this.isMounted ? 6 : 5;

    const canX = !this._collidesAt(nx, this.sprite.y, hw, hh, colliders);
    const canY = !this._collidesAt(this.sprite.x, ny, hw, hh, colliders);

    if (canX) {
      this.sprite.x = nx;
      this.shadow.x = nx;
    }
    if (canY) {
      this.sprite.y = ny;
      this.shadow.y = ny;
    }

    // Depth sort: lower Y = in front
    this.sprite.setDepth(this.sprite.y);
    this.shadow.setDepth(this.sprite.y - 1);
    this._updateIndicator();
  }

  _updateIndicator() {
    if (!this._indicatorBg) return;
    const sx = this.sprite.x;
    const sy = this.sprite.y;
    // Position label ~70px above feet, in world space
    const labelY = sy - 70;
    this._indicatorBg.setPosition(sx, labelY);
    this._indicatorText.setPosition(sx, labelY - 1);
    this._indicatorArrow.setPosition(sx, labelY + 8);
  }

  _collidesAt(x, y, hw, hh, colliders) {
    const left   = x - hw;
    const right  = x + hw;
    const top    = y - hh;
    const bottom = y + hh;

    if (!colliders) return false;
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
    if (Math.abs(newGas - gasoline) > 0.05) {
      this._store.setState({ gasoline: newGas });
    }
  }

  _animate(delta) {
    if (!this.hasTexture) return;

    // Set correct frame according to facing direction
    // Frame 0: down, 1: up, 2: left
    if (this.facing === 'down') {
      this.sprite.setFrame(0);
      this.sprite.setFlipX(false);
    } else if (this.facing === 'up') {
      this.sprite.setFrame(1);
      this.sprite.setFlipX(false);
    } else if (this.facing === 'left') {
      this.sprite.setFrame(2);
      this.sprite.setFlipX(false);
    } else if (this.facing === 'right') {
      this.sprite.setFrame(2);
      this.sprite.setFlipX(true); // Mirrored left
    }

    // Tahap A walk bounce: vertical oscillation when moving (~8Hz)
    if (this.moving) {
      this.walkTimer += delta * 0.018; // approx 8 Hz
      const bounceOffset = Math.abs(Math.sin(this.walkTimer)) * 3;
      this.sprite.setDisplayOrigin(0.5, 64 + bounceOffset);
    } else {
      this.walkTimer = 0;
      this.sprite.setDisplayOrigin(0.5, 64);
    }
  }

  get x() { return this.sprite.x; }
  get y() { return this.sprite.y; }
}
