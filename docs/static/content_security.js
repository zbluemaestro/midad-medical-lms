/**
 * Midad LMS - Content Security & Anti-Piracy Engine
 * Protects medical course lectures, videos, PDFs, and assessments.
 */

(function () {
  'use strict';

  // 1. Prevent Right-Click on Protected Content
  document.addEventListener('contextmenu', function (e) {
    // Allow right click in form inputs or textareas for editing
    if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;

    // Check if target is inside a protected area (video, notes, player)
    const protectedZone = e.target.closest('.video-player, video, .lesson-content, .pdf-viewer, #player-container');
    if (protectedZone) {
      e.preventDefault();
      showSecurityNotice("Content Protected: Right-click is disabled on Midad course media.");
    }
  }, false);

  // 2. Prevent Media Dragging (Video, Audio, Images)
  document.addEventListener('dragstart', function (e) {
    if (['IMG', 'VIDEO', 'AUDIO'].includes(e.target.tagName)) {
      e.preventDefault();
    }
  }, false);

  // 3. Harden HTML5 Video Elements (Strip Download Controls)
  function secureVideoElements() {
    const videos = document.querySelectorAll('video');
    videos.forEach(function (v) {
      v.setAttribute('controlsList', 'nodownload');
      v.setAttribute('disablePictureInPicture', 'true');
      v.oncontextmenu = function () { return false; };
    });
  }

  // Observe DOM for dynamic video player mounts
  const observer = new MutationObserver(secureVideoElements);
  observer.observe(document.body, { childList: true, subtree: true });
  secureVideoElements();

  // 4. Dynamic Forensic Anti-Screen-Recording Watermark
  function initDynamicWatermark() {
    // Get student identifier from Frappe session or fallback
    let studentId = window.frappe?.session?.user_email || window.frappe?.session?.user || 'MIDAD-STUDENT-SECURED';
    if (studentId === 'Guest') return; // Don't watermark public previews

    const watermark = document.createElement('div');
    watermark.id = 'midad-security-watermark';
    watermark.style.position = 'fixed';
    watermark.style.pointerEvents = 'none';
    watermark.style.zIndex = '999999';
    watermark.style.color = 'rgba(245, 158, 11, 0.14)'; // Soft translucent gold
    watermark.style.fontSize = '14px';
    watermark.style.fontFamily = 'monospace';
    watermark.style.fontWeight = 'bold';
    watermark.style.transform = 'rotate(-25deg)';
    watermark.style.userSelect = 'none';
    watermark.innerText = studentId + ' • MIDAD SECURE STREAM • ' + new Date().toLocaleDateString();

    document.body.appendChild(watermark);

    // Random drift position every 30 seconds to bypass static watermark erasers
    function reposition() {
      const maxX = window.innerWidth - 300;
      const maxY = window.innerHeight - 100;
      watermark.style.left = Math.floor(Math.random() * Math.max(maxX, 50)) + 'px';
      watermark.style.top = Math.floor(Math.random() * Math.max(maxY, 50)) + 'px';
    }

    reposition();
    setInterval(reposition, 30000);
  }

  // 5. Lightweight Security Toast
  function showSecurityNotice(msg) {
    let notice = document.getElementById('midad-security-notice');
    if (!notice) {
      notice = document.createElement('div');
      notice.id = 'midad-security-notice';
      notice.style.position = 'fixed';
      notice.style.bottom = '24px';
      notice.style.right = '24px';
      notice.style.backgroundColor = '#0F1A36';
      notice.style.color = '#FDE68A';
      notice.style.border = '1px solid #F59E0B';
      notice.style.padding = '12px 18px';
      notice.style.borderRadius = '8px';
      notice.style.fontSize = '13px';
      notice.style.fontWeight = '600';
      notice.style.zIndex = '1000000';
      notice.style.boxShadow = '0 10px 25px rgba(0,0,0,0.6)';
      notice.style.transition = 'opacity 0.3s ease';
      document.body.appendChild(notice);
    }
    notice.innerText = msg;
    notice.style.opacity = '1';
    setTimeout(function () {
      if (notice) notice.style.opacity = '0';
    }, 2800);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDynamicWatermark);
  } else {
    initDynamicWatermark();
  }
})();
