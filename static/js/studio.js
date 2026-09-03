/**
 * INTERACTIVE LIVE PHOTO FRAME VISUALIZER ENGINE
 * Real-time canvas rendering of frames, mats, photos, zoom/pan/rotation, and wall scenes.
 */

document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('frameCanvas');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');

  // Studio State
  const state = {
    image: null,
    imageSrc: '',
    imageFile: null,
    frameType: 'walnut',
    frameTitle: 'Classic Solid Walnut Wood',
    frameSize: '12x18',
    frameSizeText: '12 x 18 inches',
    matColor: 'offwhite',
    matWidthInches: 1.5,
    glassType: 'Anti-Glare Acrylic',
    wallTheme: 'living',
    
    // Zoom / Pan / Rotation
    zoom: 1.0,
    panX: 0,
    panY: 0,
    rotation: 0,
    isDragging: false,
    dragStartX: 0,
    dragStartY: 0,
    
    // Pricing table
    basePrices: {
      '6x4': 499,
      '8x10': 649,
      '12x18': 899,
      '16x24': 1299,
      '20x30': 1799,
      '24x36': 2399
    },
    frameMultipliers: {
      'walnut': 1.0,
      'black': 0.9,
      'gold': 1.35,
      'oak': 1.05,
      'white': 0.85,
      'acrylic': 1.25,
      'barnwood': 1.1,
      'canvas': 1.3
    }
  };

  // Color & texture profiles for frames
  const frameProfiles = {
    'walnut': { border: '#3e2723', bevelLight: '#5d4037', bevelDark: '#1b0000', widthRatio: 0.08 },
    'black': { border: '#171717', bevelLight: '#2e2e2e', bevelDark: '#0a0a0a', widthRatio: 0.05 },
    'gold': { border: '#d4af37', bevelLight: '#f9e076', bevelDark: '#aa820a', widthRatio: 0.09 },
    'oak': { border: '#c8a265', bevelLight: '#dfbe87', bevelDark: '#99733e', widthRatio: 0.07 },
    'white': { border: '#f8fafc', bevelLight: '#ffffff', bevelDark: '#cbd5e1', widthRatio: 0.06 },
    'acrylic': { border: 'rgba(255,255,255,0.7)', bevelLight: '#ffffff', bevelDark: 'rgba(0,0,0,0.1)', widthRatio: 0.07, isAcrylic: true },
    'barnwood': { border: '#6d655f', bevelLight: '#8d857f', bevelDark: '#443e39', widthRatio: 0.08 },
    'canvas': { border: '#1f1f1f', bevelLight: '#3a3a3a', bevelDark: '#050505', widthRatio: 0.06, isCanvas: true }
  };

  const matProfiles = {
    'none': { color: null, widthPx: 0 },
    'offwhite': { color: '#fcfbf7', bevel: '#e0ded7' },
    'cream': { color: '#f5f0e1', bevel: '#ded5bf' },
    'charcoal': { color: '#2d3748', bevel: '#1a202c' },
    'black': { color: '#1a1a1a', bevel: '#000000' }
  };

  // Dimensions aspect ratio map
  const sizeAspectRatios = {
    '6x4': 6 / 4,
    '8x10': 8 / 10,
    '12x18': 12 / 18,
    '16x24': 16 / 24,
    '20x30': 20 / 30,
    '24x36': 24 / 36
  };

  // 1. Initial Photo Load
  function loadInitialImage() {
    const defaultSample = 'https://images.unsplash.com/photo-1534447677768-be436bb09401?w=1000&auto=format&fit=crop&q=80';
    state.imageSrc = defaultSample;
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = defaultSample;
    img.onload = () => {
      state.image = img;
      render();
    };
  }

  // 2. Main Canvas Render Function
  function render() {
    const dpr = window.devicePixelRatio || 1;
    const maxCanvasWidth = 700;
    const maxCanvasHeight = 650;
    
    // Calculate aspect ratio
    const aspect = sizeAspectRatios[state.frameSize] || (12 / 18);
    let canvasW, canvasH;
    
    if (aspect >= 1) { // Landscape
      canvasW = maxCanvasWidth;
      canvasH = maxCanvasWidth / aspect;
      if (canvasH > maxCanvasHeight) {
        canvasH = maxCanvasHeight;
        canvasW = canvasH * aspect;
      }
    } else { // Portrait
      canvasH = maxCanvasHeight;
      canvasW = maxCanvasHeight * aspect;
      if (canvasW > maxCanvasWidth) {
        canvasW = maxCanvasWidth;
        canvasH = canvasW / aspect;
      }
    }

    canvas.width = canvasW * dpr;
    canvas.height = canvasH * dpr;
    canvas.style.width = `${canvasW}px`;
    canvas.style.height = `${canvasH}px`;

    ctx.save();
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, canvasW, canvasH);

    const frameConfig = frameProfiles[state.frameType] || frameProfiles['walnut'];
    const frameBorderW = Math.max(16, canvasW * frameConfig.widthRatio);
    
    // Mat width calculation
    let matBorderW = 0;
    if (state.matColor !== 'none' && state.matWidthInches > 0) {
      matBorderW = Math.max(20, (state.matWidthInches / 12) * (canvasW * 0.45));
    }

    const totalBorder = frameBorderW + matBorderW;
    const photoAreaX = totalBorder;
    const photoAreaY = totalBorder;
    const photoAreaW = canvasW - (totalBorder * 2);
    const photoAreaH = canvasH - (totalBorder * 2);

    // =============================
    // DRAW FRAME OUTER SHADOW & BASE
    // =============================
    ctx.shadowColor = 'rgba(0, 0, 0, 0.35)';
    ctx.shadowBlur = 30;
    ctx.shadowOffsetY = 15;
    ctx.fillStyle = frameConfig.border;
    ctx.fillRect(0, 0, canvasW, canvasH);
    ctx.shadowColor = 'transparent'; // Reset shadow

    // =============================
    // DRAW FRAME MOULDING & 3D BEVELS
    // =============================
    if (frameConfig.isAcrylic) {
      // Clear Acrylic glass floating look
      const acrylicGrad = ctx.createLinearGradient(0, 0, canvasW, canvasH);
      acrylicGrad.addColorStop(0, 'rgba(255,255,255,0.85)');
      acrylicGrad.addColorStop(0.5, 'rgba(240,244,248,0.7)');
      acrylicGrad.addColorStop(1, 'rgba(215,225,235,0.85)');
      ctx.fillStyle = acrylicGrad;
      ctx.fillRect(0, 0, canvasW, canvasH);

      // Chrome Corner Standoff Bolts
      const boltRadius = 8;
      const boltMargin = 16;
      const boltCoords = [
        [boltMargin, boltMargin],
        [canvasW - boltMargin, boltMargin],
        [boltMargin, canvasH - boltMargin],
        [canvasW - boltMargin, canvasH - boltMargin]
      ];
      boltCoords.forEach(([bx, by]) => {
        const boltGrad = ctx.createRadialGradient(bx-2, by-2, 1, bx, by, boltRadius);
        boltGrad.addColorStop(0, '#ffffff');
        boltGrad.addColorStop(0.6, '#cbd5e1');
        boltGrad.addColorStop(1, '#475569');
        ctx.fillStyle = boltGrad;
        ctx.beginPath();
        ctx.arc(bx, by, boltRadius, 0, Math.PI * 2);
        ctx.fill();
      });
    } else {
      // Top & Left Light Bevel
      ctx.fillStyle = frameConfig.bevelLight;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(canvasW, 0);
      ctx.lineTo(canvasW - frameBorderW, frameBorderW);
      ctx.lineTo(frameBorderW, frameBorderW);
      ctx.lineTo(frameBorderW, canvasH - frameBorderW);
      ctx.lineTo(0, canvasH);
      ctx.closePath();
      ctx.fill();

      // Bottom & Right Dark Bevel
      ctx.fillStyle = frameConfig.bevelDark;
      ctx.beginPath();
      ctx.moveTo(canvasW, 0);
      ctx.lineTo(canvasW, canvasH);
      ctx.lineTo(0, canvasH);
      ctx.lineTo(frameBorderW, canvasH - frameBorderW);
      ctx.lineTo(canvasW - frameBorderW, canvasH - frameBorderW);
      ctx.lineTo(canvasW - frameBorderW, frameBorderW);
      ctx.closePath();
      ctx.fill();

      // Gold pattern overlay if gold
      if (state.frameType === 'gold') {
        ctx.strokeStyle = 'rgba(255, 235, 150, 0.4)';
        ctx.lineWidth = 2;
        ctx.strokeRect(frameBorderW / 2, frameBorderW / 2, canvasW - frameBorderW, canvasH - frameBorderW);
      }
    }

    // =============================
    // DRAW MAT / PASSE-PARTOUT
    // =============================
    if (state.matColor !== 'none' && matBorderW > 0) {
      const matConf = matProfiles[state.matColor] || matProfiles['offwhite'];
      ctx.fillStyle = matConf.color;
      ctx.fillRect(frameBorderW, frameBorderW, canvasW - (frameBorderW * 2), canvasH - (frameBorderW * 2));

      // Inner Mat Bevel Cut Shadow
      ctx.fillStyle = matConf.bevel || '#dedede';
      ctx.fillRect(photoAreaX - 2, photoAreaY - 2, photoAreaW + 4, photoAreaH + 4);
    }

    // =============================
    // DRAW CUSTOMER PHOTO (CLIPPED)
    // =============================
    ctx.save();
    ctx.beginPath();
    ctx.rect(photoAreaX, photoAreaY, photoAreaW, photoAreaH);
    ctx.clip();

    // Photo Area Background
    ctx.fillStyle = '#111';
    ctx.fillRect(photoAreaX, photoAreaY, photoAreaW, photoAreaH);

    if (state.image) {
      ctx.save();
      const centerX = photoAreaX + (photoAreaW / 2) + state.panX;
      const centerY = photoAreaY + (photoAreaH / 2) + state.panY;
      
      ctx.translate(centerX, centerY);
      ctx.rotate((state.rotation * Math.PI) / 180);
      ctx.scale(state.zoom, state.zoom);

      // Fit or fill dimensions
      const imgW = state.image.width;
      const imgH = state.image.height;
      const scale = Math.max(photoAreaW / imgW, photoAreaH / imgH);
      const drawW = imgW * scale;
      const drawH = imgH * scale;

      ctx.drawImage(state.image, -drawW / 2, -drawH / 2, drawW, drawH);
      ctx.restore();
    }

    // Inner shadow on glass edge
    const innerShadow = ctx.createLinearGradient(photoAreaX, photoAreaY, photoAreaX, photoAreaY + 15);
    innerShadow.addColorStop(0, 'rgba(0,0,0,0.25)');
    innerShadow.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = innerShadow;
    ctx.fillRect(photoAreaX, photoAreaY, photoAreaW, 15);

    ctx.restore(); // Restore clip

    // Subtle Glass Light Reflection diagonal
    if (state.glassType !== 'Canvas Wrap') {
      ctx.save();
      ctx.beginPath();
      ctx.rect(photoAreaX, photoAreaY, photoAreaW, photoAreaH);
      ctx.clip();
      
      const glassReflect = ctx.createLinearGradient(photoAreaX, photoAreaY, photoAreaX + photoAreaW, photoAreaY + photoAreaH);
      glassReflect.addColorStop(0, 'rgba(255,255,255,0.12)');
      glassReflect.addColorStop(0.3, 'rgba(255,255,255,0.05)');
      glassReflect.addColorStop(0.35, 'rgba(255,255,255,0.18)');
      glassReflect.addColorStop(0.5, 'rgba(255,255,255,0)');
      ctx.fillStyle = glassReflect;
      ctx.fillRect(photoAreaX, photoAreaY, photoAreaW, photoAreaH);
      ctx.restore();
    }

    ctx.restore();
    updatePrice();
  }

  // 3. Price Calculation
  function updatePrice() {
    const base = state.basePrices[state.frameSize] || 799;
    const mult = state.frameMultipliers[state.frameType] || 1.0;
    const matAdd = state.matColor !== 'none' ? 100 : 0;
    const finalPrice = Math.round((base * mult) + matAdd);
    const origPrice = Math.round(finalPrice * 1.95);
    const savings = origPrice - finalPrice;

    const priceEl = document.getElementById('studioCurrentPrice');
    const origPriceEl = document.getElementById('studioOrigPrice');
    const savingsEl = document.getElementById('studioSavingsAmount');

    if (priceEl) priceEl.textContent = `₹${finalPrice.toLocaleString('en-IN')}`;
    if (origPriceEl) origPriceEl.textContent = `₹${origPrice.toLocaleString('en-IN')}`;
    if (savingsEl) savingsEl.textContent = `Save ₹${savings.toLocaleString('en-IN')} (48% OFF)`;

    state.calculatedPrice = finalPrice;
  }

  // 4. Interactive Drag & Pan Events on Canvas
  canvas.addEventListener('mousedown', (e) => {
    state.isDragging = true;
    state.dragStartX = e.clientX - state.panX;
    state.dragStartY = e.clientY - state.panY;
  });

  window.addEventListener('mousemove', (e) => {
    if (!state.isDragging) return;
    state.panX = e.clientX - state.dragStartX;
    state.panY = e.clientY - state.dragStartY;
    render();
  });

  window.addEventListener('mouseup', () => {
    state.isDragging = false;
  });

  // Touch support for mobile
  canvas.addEventListener('touchstart', (e) => {
    if (e.touches.length === 1) {
      state.isDragging = true;
      state.dragStartX = e.touches[0].clientX - state.panX;
      state.dragStartY = e.touches[0].clientY - state.panY;
    }
  });

  window.addEventListener('touchmove', (e) => {
    if (state.isDragging && e.touches.length === 1) {
      state.panX = e.touches[0].clientX - state.dragStartX;
      state.panY = e.touches[0].clientY - state.dragStartY;
      render();
    }
  });

  window.addEventListener('touchend', () => {
    state.isDragging = false;
  });

  // 5. Canvas Floating Controls (Zoom / Rotate / Reset)
  document.getElementById('btnZoomIn')?.addEventListener('click', () => {
    state.zoom = Math.min(3.0, state.zoom + 0.15);
    render();
  });

  document.getElementById('btnZoomOut')?.addEventListener('click', () => {
    state.zoom = Math.max(0.6, state.zoom - 0.15);
    render();
  });

  document.getElementById('btnRotate')?.addEventListener('click', () => {
    state.rotation = (state.rotation + 90) % 360;
    render();
  });

  document.getElementById('btnResetView')?.addEventListener('click', () => {
    state.zoom = 1.0;
    state.panX = 0;
    state.panY = 0;
    state.rotation = 0;
    render();
  });

  // 6. Photo Upload Handlers
  const photoInput = document.getElementById('studioPhotoInput');
  const uploadBox = document.getElementById('studioUploadBox');

  function handleFile(file) {
    if (!file || !file.type.startsWith('image/')) {
      alert('Please upload a valid image file (JPG, PNG, WEBP).');
      return;
    }
    state.imageFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.src = e.target.result;
      img.onload = () => {
        state.image = img;
        state.imageSrc = e.target.result;
        state.panX = 0;
        state.panY = 0;
        state.zoom = 1.0;
        
        // Update upload box preview
        const thumb = document.getElementById('uploadedThumb');
        const filename = document.getElementById('uploadedFileName');
        const previewRow = document.getElementById('uploadPreviewRow');
        if (thumb) thumb.src = e.target.result;
        if (filename) filename.textContent = `${file.name} (${Math.round(file.size / 1024)} KB)`;
        if (previewRow) previewRow.style.display = 'flex';
        
        render();
      };
    };
    reader.readAsDataURL(file);
  }

  if (photoInput) {
    photoInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        handleFile(e.target.files[0]);
      }
    });
  }

  if (uploadBox) {
    uploadBox.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadBox.classList.add('dragover');
    });
    uploadBox.addEventListener('dragleave', () => {
      uploadBox.classList.remove('dragover');
    });
    uploadBox.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadBox.classList.remove('dragover');
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFile(e.dataTransfer.files[0]);
      }
    });
  }

  // 7. Frame Style Swatches
  document.querySelectorAll('.frame-swatch-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.frame-swatch-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      state.frameType = card.dataset.frame;
      state.frameTitle = card.querySelector('.swatch-title')?.textContent || 'Custom Frame';
      render();
    });
  });

  // 8. Size Selectors
  document.querySelectorAll('.size-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.size-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      state.frameSize = pill.dataset.size;
      state.frameSizeText = pill.querySelector('.size-dim')?.textContent || '12 x 18 inches';
      render();
    });
  });

  // 9. Mat Color Swatches & Width
  document.querySelectorAll('.mat-color-dot').forEach(dot => {
    dot.addEventListener('click', () => {
      document.querySelectorAll('.mat-color-dot').forEach(d => d.classList.remove('active'));
      dot.classList.add('active');
      state.matColor = dot.dataset.mat;
      render();
    });
  });

  document.getElementById('matWidthSelect')?.addEventListener('change', (e) => {
    state.matWidthInches = parseFloat(e.target.value);
    render();
  });

  // 10. Glass Type
  document.querySelectorAll('.glass-pill-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.glass-pill-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.glassType = btn.dataset.glass;
      render();
    });
  });

  // 11. Room Wall Switcher
  document.querySelectorAll('.room-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.room-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const theme = btn.dataset.room;
      const container = document.getElementById('studioCanvasContainer');
      if (container) {
        container.className = `studio-canvas-container wall-${theme}`;
      }
    });
  });

  // 12. Submit Custom Frame (Add to Cart / Buy Now)
  async function submitCustomFrame(redirectToCheckout = false) {
    const btn = redirectToCheckout ? document.getElementById('btnStudioBuy') : document.getElementById('btnStudioCart');
    const origText = btn ? btn.innerHTML : '';
    if (btn) {
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
      btn.disabled = true;
    }

    try {
      // 1. Capture Mockup Preview Image from Canvas
      const previewDataUri = canvas.toDataURL('image/jpeg', 0.9);

      // 2. Prepare Form Data
      const formData = new FormData();
      formData.append('product_title', `${state.frameTitle} (${state.frameSizeText})`);
      formData.append('price', state.calculatedPrice);
      formData.append('frame_type', state.frameTitle);
      formData.append('frame_size', state.frameSizeText);
      formData.append('mat_color', state.matColor.toUpperCase());
      formData.append('mat_width', `${state.matWidthInches} inch`);
      formData.append('glass_type', state.glassType);
      formData.append('quantity', 1);
      formData.append('preview_mockup_base64', previewDataUri);
      
      const cropInfo = {
        zoom: state.zoom,
        panX: state.panX,
        panY: state.panY,
        rotation: state.rotation
      };
      formData.append('crop_data', JSON.stringify(cropInfo));

      if (state.imageFile) {
        // High-res user photo upload
        formData.append('photo_file', state.imageFile);
      } else {
        formData.append('high_res_image_path', state.imageSrc);
      }

      const res = await fetch('/api/cart/add', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      if (data.success) {
        // Update header badge
        const badge = document.querySelector('.fk-cart-badge');
        if (badge) badge.textContent = data.cart_count;

        if (redirectToCheckout) {
          window.location.href = '/checkout';
        } else {
          window.location.href = '/cart';
        }
      } else {
        alert(data.error || 'Failed to add frame to cart.');
      }
    } catch (err) {
      console.error(err);
      alert('Network error while saving custom frame.');
    } finally {
      if (btn) {
        btn.innerHTML = origText;
        btn.disabled = false;
      }
    }
  }

  document.getElementById('btnStudioCart')?.addEventListener('click', () => submitCustomFrame(false));
  document.getElementById('btnStudioBuy')?.addEventListener('click', () => submitCustomFrame(true));

  // Initialize
  loadInitialImage();
});
