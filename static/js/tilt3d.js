/**
 * 3D INTERACTIVE TILT & DYNAMIC LIGHTING ENGINE (60 FPS)
 * Adds realistic 3D perspective depth, rotational tilt, and moving specular glare to frames and cards.
 */

document.addEventListener('DOMContentLoaded', () => {
  
  // 1. Apply 3D Tilt to Product Cards and Floating Mockups
  const tiltElements = document.querySelectorAll('.fk-product-card, .fk-hero-frame-mock, .adm-stat-card, .order-item-row');

  tiltElements.forEach(card => {
    // Inject 3D Glare Overlay
    if (!card.querySelector('.tilt-3d-glare')) {
      const glare = document.createElement('div');
      glare.className = 'tilt-3d-glare';
      card.style.position = 'relative';
      card.style.transformStyle = 'preserve-3d';
      card.appendChild(glare);
    }

    let isHovered = false;
    let reqId = null;
    let mouseX = 0, mouseY = 0;
    let cardRect = null;

    card.addEventListener('mouseenter', (e) => {
      isHovered = true;
      cardRect = card.getBoundingClientRect();
      card.style.transition = 'transform 0.1s ease-out, box-shadow 0.2s ease-out';
    });

    card.addEventListener('mousemove', (e) => {
      if (!isHovered || !cardRect) return;
      mouseX = e.clientX - cardRect.left;
      mouseY = e.clientY - cardRect.top;

      if (!reqId) {
        reqId = requestAnimationFrame(() => {
          const w = cardRect.width;
          const h = cardRect.height;
          const xPct = (mouseX / w) - 0.5;
          const yPct = (mouseY / h) - 0.5;

          const rotX = -(yPct * 18).toFixed(2);
          const rotY = (xPct * 18).toFixed(2);

          card.style.transform = `perspective(1000px) rotateX(${rotX}deg) rotateY(${rotY}deg) scale3d(1.03, 1.03, 1.03) translateZ(10px)`;
          card.style.boxShadow = `${-xPct * 20}px ${-yPct * 20 + 15}px 30px rgba(0,0,0,0.25)`;

          // Glare light reflection calculation
          const glare = card.querySelector('.tilt-3d-glare');
          if (glare) {
            glare.style.opacity = '1';
            glare.style.background = `radial-gradient(circle at ${(mouseX/w)*100}% ${(mouseY/h)*100}%, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0) 70%)`;
          }

          reqId = null;
        });
      }
    });

    card.addEventListener('mouseleave', () => {
      isHovered = false;
      card.style.transition = 'transform 0.5s ease-out, box-shadow 0.5s ease-out';
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1) translateZ(0px)';
      card.style.boxShadow = '';
      
      const glare = card.querySelector('.tilt-3d-glare');
      if (glare) {
        glare.style.opacity = '0';
      }
    });
  });

  // 2. Interactive 3D Wall Perspective on Studio Canvas
  const studioContainer = document.getElementById('studioCanvasContainer');
  const frameCanvas = document.getElementById('frameCanvas');

  if (studioContainer && frameCanvas) {
    let containerRect = null;
    let studioReqId = null;

    studioContainer.addEventListener('mouseenter', () => {
      containerRect = studioContainer.getBoundingClientRect();
      frameCanvas.style.transition = 'transform 0.1s ease-out, box-shadow 0.2s ease-out';
    });

    studioContainer.addEventListener('mousemove', (e) => {
      if (!containerRect) return;
      const x = e.clientX - containerRect.left;
      const y = e.clientY - containerRect.top;

      if (!studioReqId) {
        studioReqId = requestAnimationFrame(() => {
          const w = containerRect.width;
          const h = containerRect.height;
          const xPct = (x / w) - 0.5;
          const yPct = (y / h) - 0.5;

          const tiltX = -(yPct * 16).toFixed(2);
          const tiltY = (xPct * 20).toFixed(2);

          frameCanvas.style.transform = `perspective(1200px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) translateZ(25px)`;
          frameCanvas.style.boxShadow = `${-xPct * 40}px ${-yPct * 40 + 30}px 60px rgba(0, 0, 0, 0.5)`;

          studioReqId = null;
        });
      }
    });

    studioContainer.addEventListener('mouseleave', () => {
      frameCanvas.style.transition = 'transform 0.6s cubic-bezier(0.25, 1, 0.5, 1), box-shadow 0.6s ease';
      frameCanvas.style.transform = 'perspective(1200px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
      frameCanvas.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.45)';
    });
  }

});
