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
    this.isMounting = false;
    this._motorFuelAccumulatorMs = 0;
    this._bikeUnderlay = null;

    // Click-to-Move Pathfinding state (Gate H5)
    this._path = [];
    this._targetInteractable = null;
    this._isClickMoving = false;
    this._markerGfx = null;
    this._markerTimer = null;

    window.addEventListener('keydown', (e) => {
      const k = e.key?.toLowerCase();
      if (['w', 'a', 's', 'd', 'arrowup', 'arrowdown', 'arrowleft', 'arrowright', 'escape'].includes(k)) {
        if (this._isClickMoving) {
          this.clearPath();
        }
      }
    });

    const dayDurSec = this.config.dayDurationSeconds || 12;
    this.gasolineDrainRate = (this.config.gasolineDrainPerDay || 5) / (dayDurSec * 1000);
  }

  setPath(path, targetInteractable = null) {
    if (!path || path.length === 0) return;
    this._path = [...path];
    this._targetInteractable = targetInteractable;
    this._isClickMoving = true;

    // Show visual pulsating marker at final destination point
    const dest = path[path.length - 1];
    this._createDestinationMarker(dest.x, dest.y);
  }

  clearPath() {
    this._path = [];
    this._targetInteractable = null;
    this._isClickMoving = false;
    this.vx = 0;
    this.vy = 0;
    this.moving = false;
    this._removeDestinationMarker();
  }

  _createDestinationMarker(x, y) {
    this._removeDestinationMarker();
    if (!this.scene || !this.scene.add) return;

    const gfx = this.scene.add.graphics();
    gfx.setDepth(100);
    this._markerGfx = gfx;

    let radius = 6;
    let alpha = 0.9;
    let growing = true;

    this._markerTimer = this.scene.time.addEvent({
      delay: 50,
      loop: true,
      callback: () => {
        if (!this._markerGfx) return;
        this._markerGfx.clear();

        // Inner glowing dot
        this._markerGfx.fillStyle(0xD9A441, alpha);
        this._markerGfx.fillCircle(x, y, 3);

        // Outer expanding ring
        this._markerGfx.lineStyle(2, 0xD9A441, alpha * 0.8);
        this._markerGfx.strokeCircle(x, y, radius);

        if (growing) {
          radius += 0.8;
          alpha -= 0.05;
          if (radius >= 14) growing = false;
        } else {
          radius -= 0.8;
          alpha += 0.05;
          if (radius <= 6) growing = true;
        }
      }
    });
  }

  _removeDestinationMarker() {
    if (this._markerTimer) {
      this._markerTimer.remove();
      this._markerTimer = null;
    }
    if (this._markerGfx) {
      this._markerGfx.destroy();
      this._markerGfx = null;
    }
  }

  mount(callback) {
    if (this.isMounting || this.isMounted) return;
    this.isMounting = true;
    this.vx = 0;
    this.vy = 0;
    this.moving = false;

    const reducedMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches;
    const duration = this.config.vehicle?.mountAnimationMs || 350;

    if (reducedMotion) {
      this.isMounted = true;
      this.isMounting = false;
      this._updateVehicleAppearance(true);
      if (this._store) {
        this._store.setState({ vehicle: { mounted: true } });
      }
      if (callback) callback();
      return;
    }

    const startY = this.sprite.y;
    this.scene.tweens.add({
      targets: this.sprite,
      y: startY - 6,
      duration: duration / 2,
      ease: 'Cubic.easeOut',
      yoyo: true,
      onYoyo: () => {
        this.isMounted = true;
        this._updateVehicleAppearance(true);
      },
      onComplete: () => {
        this.sprite.y = startY;
        this.isMounting = false;
        this._spawnDustParticles(this.sprite.x, this.sprite.y);
        if (this._store) {
          this._store.setState({ vehicle: { mounted: true } });
        }
        if (callback) callback();
      }
    });
  }

  dismount(reason = null, callback) {
    if (!this.isMounted && !this.isMounting) return;
    this.isMounted = false;
    this.isMounting = false;
    this._updateVehicleAppearance(false);

    if (this._store) {
      this._store.setState({ vehicle: { mounted: false } });
    }

    if (reason && this.scene?.showPromptFeedback) {
      this.scene.showPromptFeedback(reason, 3000);
    }
    if (callback) callback();
  }

  _updateVehicleAppearance(mounted) {
    const gender = this._store?.getState()?.character?.gender || 'm';
    const riderKey = gender === 'f' ? 'char_rider_f' : 'char_rider_m';

    if (mounted) {
      if (this.scene.textures.exists(riderKey)) {
        this.sprite.setTexture(riderKey);
        if (this._bikeUnderlay) this._bikeUnderlay.setVisible(false);
      } else {
        if (!this._bikeUnderlay && this.scene.textures.exists('prop_motor_parkir')) {
          this._bikeUnderlay = this.scene.add.sprite(this.sprite.x, this.sprite.y + 2, 'prop_motor_parkir');
          this._bikeUnderlay.setOrigin(0.5, 1.0);
          this._bikeUnderlay.setScale(0.85);
        }
        if (this._bikeUnderlay) {
          this._bikeUnderlay.setVisible(true);
          this._bikeUnderlay.setDepth(this.sprite.depth - 1);
        }
      }
    } else {
      if (this.scene.textures.exists(this.textureKey)) {
        this.sprite.setTexture(this.textureKey);
      }
      if (this._bikeUnderlay) {
        this._bikeUnderlay.setVisible(false);
      }
    }
  }

  _spawnDustParticles(x, y) {
    const colors = [0xF7EEDA, 0xB8A88A, 0x8A715D];
    for (let i = 0; i < 5; i++) {
      const col = colors[i % colors.length];
      const p = this.scene.add.rectangle(x + (Math.random() - 0.5) * 16, y - 2 + (Math.random() - 0.5) * 4, 3, 3, col);
      p.setDepth(this.sprite.depth - 2);
      this.scene.tweens.add({
        targets: p,
        y: p.y - (4 + Math.random() * 6),
        alpha: 0,
        duration: 300 + Math.random() * 200,
        ease: 'Linear',
        onComplete: () => p.destroy()
      });
    }
  }

  measureSpeed() {
    let effSpeed = this.speed;
    const st = this._store ? this._store.getState() : null;
    if (st?.energy && st.energy.current === 0) {
      effSpeed *= (this.config.energy?.exhaustedSpeedMultiplier ?? 0.7);
    }
    if (this.isMounted) {
      effSpeed *= (this.config.vehicle?.speedMultiplier ?? 1.8);
    }
    return effSpeed;
  }

  update(delta, colliders) {
    this._handleInput(delta, colliders);
    this._drainGasoline(delta);
    this._animate(delta);
  }

  _handleInput(delta, colliders) {
    if (this.isMounting) {
      this.vx = 0;
      this.vy = 0;
      this.moving = false;
      return;
    }

    const up    = this.cursors.up.isDown    || this.wasd.up.isDown;
    const down  = this.cursors.down.isDown  || this.wasd.down.isDown;
    const left  = this.cursors.left.isDown  || this.wasd.left.isDown;
    const right = this.cursors.right.isDown || this.wasd.right.isDown;
    const hasManual = up || down || left || right;

    let effSpeed = this.speed;
    const st = this._store ? this._store.getState() : null;
    if (st?.energy && st.energy.current === 0) {
      effSpeed *= (this.config.energy?.exhaustedSpeedMultiplier ?? 0.7);
    }
    if (this.isMounted) {
      effSpeed *= (this.config.vehicle?.speedMultiplier ?? 1.8);
    }

    const dt = delta / 1000;

    // 1. Manual keyboard input cancels click-to-move immediately
    if (hasManual) {
      if (this._isClickMoving) {
        this.clearPath();
      }

      this.vx = 0;
      this.vy = 0;
      if (left)  { this.vx = -effSpeed; this.facing = 'left'; }
      if (right) { this.vx =  effSpeed; this.facing = 'right'; }
      if (up)    { this.vy = -effSpeed; this.facing = 'up'; }
      if (down)  { this.vy =  effSpeed; this.facing = 'down'; }

      if (this.vx !== 0 && this.vy !== 0) {
        const factor = 1 / Math.SQRT2;
        this.vx *= factor;
        this.vy *= factor;
      }

      this.moving = this.vx !== 0 || this.vy !== 0;
      if (!this.moving) return;

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
      return;
    }

    // 2. Click-to-Move Path Following (Gate H5)
    if (this._isClickMoving && this._path.length > 0) {
      const wp = this._path[0];
      const dx = wp.x - this.sprite.x;
      const dy = wp.y - this.sprite.y;
      const dist = Math.hypot(dx, dy);

      if (dist <= Math.max(4, effSpeed * dt * 1.1)) {
        this.sprite.x = wp.x;
        this.sprite.y = wp.y;
        this.shadow.x = wp.x;
        this.shadow.y = wp.y;
        this._path.shift();

        if (this._path.length === 0) {
          const target = this._targetInteractable;
          this.clearPath();
          if (target && this.scene && this.scene._onArrivalAtTarget) {
            this.scene._onArrivalAtTarget(target);
          }
          return;
        }
      } else {
        this.vx = (dx / dist) * effSpeed;
        this.vy = (dy / dist) * effSpeed;
        this.moving = true;

        if (Math.abs(dx) > Math.abs(dy)) {
          this.facing = dx > 0 ? 'right' : 'left';
        } else {
          this.facing = dy > 0 ? 'down' : 'up';
        }

        const nx = this.sprite.x + this.vx * dt;
        const ny = this.sprite.y + this.vy * dt;

        this.sprite.x = nx;
        this.sprite.y = ny;
        this.shadow.x = nx;
        this.shadow.y = ny;

        this.sprite.setDepth(this.sprite.y);
        this.shadow.setDepth(this.sprite.y - 1);
        this._updateIndicator();
        return;
      }
    }

    this.vx = 0;
    this.vy = 0;
    this.moving = false;
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
    if (!this._store) return;
    // Only motor riding drains gasoline (Rule 75 §1: 2% per 5s of moving)
    if (!this.isMounted || !this.moving) return;

    this._motorFuelAccumulatorMs += delta;
    if (this._motorFuelAccumulatorMs >= 5000) {
      const ticks = Math.floor(this._motorFuelAccumulatorMs / 5000);
      this._motorFuelAccumulatorMs %= 5000;
      const state = this._store.getState();
      const gasoline = state.gasoline ?? 100;
      const newGas = Math.max(0, gasoline - (ticks * 2));
      this._store.setState({ gasoline: newGas });
      if (newGas <= 0) {
        this.dismount('Bensin habis! Dorong atau isi bensin di SPBU.');
      }
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

    if (this.isMounted) {
      this.walkTimer = 0;
      this.sprite.setDisplayOrigin(0.5, 64);
      if (this._bikeUnderlay) {
        this._bikeUnderlay.setPosition(this.sprite.x, this.sprite.y + 2);
        this._bikeUnderlay.setDepth(this.sprite.depth - 1);
        this._bikeUnderlay.setFlipX(this.facing === 'right');
      }
      // Subtle 1px engine vibration when moving
      if (this.moving) {
        this.sprite.y += (Math.random() > 0.5 ? 0.5 : -0.5);
      }
    } else {
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
  }

  get x() { return this.sprite.x; }
  get y() { return this.sprite.y; }
}
