/* ============================================
   FRESH HENS - Landing Page JavaScript
   Premium Interactions & Animations
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
  // ---- Preloader ----
  initPreloader();

  // ---- Navigation ----
  initNavbar();

  // ---- Scroll Animations ----
  initScrollAnimations();

  // ---- Counter Animation ----
  initCounters();

  // ---- Scroll To Top ----
  initScrollTop();

  // ---- Smooth Scroll ----
  initSmoothScroll();

  // ---- Active Nav Link ----
  initActiveNavTracking();

  // ---- Parallax Effects ----
  initParallaxEffects();
});

/* ============================================
   PRELOADER
   ============================================ */
function initPreloader() {
  const preloader = document.getElementById('preloader');
  if (!preloader) return;

  window.addEventListener('load', () => {
    setTimeout(() => {
      preloader.classList.add('hidden');
      // Trigger hero animations
      document.querySelectorAll('.hero__content, .hero__visual').forEach(el => {
        el.style.opacity = '1';
      });
    }, 800);
  });

  // Fallback: hide preloader after 3 seconds anyway
  setTimeout(() => {
    preloader.classList.add('hidden');
  }, 3000);
}

/* ============================================
   NAVBAR
   ============================================ */
function initNavbar() {
  const navbar = document.getElementById('navbar');
  const hamburger = document.getElementById('hamburger');
  const navbarNav = document.getElementById('navbar-nav');

  if (!navbar) return;

  // Scroll behavior
  let lastScroll = 0;
  window.addEventListener('scroll', () => {
    const currentScroll = window.scrollY;

    if (currentScroll > 80) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }

    lastScroll = currentScroll;
  });

  // Mobile menu toggle
  if (hamburger && navbarNav) {
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('active');
      navbarNav.classList.toggle('open');
      document.body.style.overflow = navbarNav.classList.contains('open') ? 'hidden' : '';
    });

    // Close menu when clicking a link
    navbarNav.querySelectorAll('.navbar__link').forEach(link => {
      link.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navbarNav.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  }
}

/* ============================================
   SCROLL ANIMATIONS (Intersection Observer)
   ============================================ */
function initScrollAnimations() {
  const elements = document.querySelectorAll('.animate-on-scroll');
  if (!elements.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animated');
        // Optionally stop observing after animation
        // observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -60px 0px'
  });

  elements.forEach(el => observer.observe(el));
}

/* ============================================
   COUNTER ANIMATION
   ============================================ */
function initCounters() {
  const counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(counter => observer.observe(counter));
}

function animateCounter(element) {
  const target = parseInt(element.getAttribute('data-count'));
  const duration = 2000;
  const step = target / (duration / 16);
  let current = 0;

  const timer = setInterval(() => {
    current += step;
    if (current >= target) {
      current = target;
      clearInterval(timer);
    }

    // Format number
    if (target >= 1000) {
      element.textContent = Math.floor(current).toLocaleString() + '+';
    } else if (target === 100) {
      element.textContent = Math.floor(current) + '%';
    } else {
      element.textContent = Math.floor(current) + '+';
    }
  }, 16);
}

/* ============================================
   SCROLL TO TOP
   ============================================ */
function initScrollTop() {
  const scrollTopBtn = document.getElementById('scroll-top');
  if (!scrollTopBtn) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 600) {
      scrollTopBtn.classList.add('visible');
    } else {
      scrollTopBtn.classList.remove('visible');
    }
  });

  scrollTopBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

/* ============================================
   SMOOTH SCROLL
   ============================================ */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href === '#') return;

      e.preventDefault();
      const target = document.querySelector(href);
      if (target) {
        const navHeight = document.getElementById('navbar')?.offsetHeight || 0;
        const targetPosition = target.getBoundingClientRect().top + window.scrollY - navHeight;

        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
      }
    });
  });
}

/* ============================================
   ACTIVE NAV LINK TRACKING
   ============================================ */
function initActiveNavTracking() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.navbar__link');

  if (!sections.length || !navLinks.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        navLinks.forEach(link => {
          link.classList.remove('active');
          if (link.getAttribute('href') === `#${id}`) {
            link.classList.add('active');
          }
        });
      }
    });
  }, {
    threshold: 0.3,
    rootMargin: '-100px 0px -50% 0px'
  });

  sections.forEach(section => observer.observe(section));
}

/* ============================================
   PARALLAX EFFECTS
   ============================================ */
function initParallaxEffects() {
  const floatingCards = document.querySelectorAll('.hero__floating-card');

  if (floatingCards.length && window.innerWidth > 768) {
    window.addEventListener('mousemove', (e) => {
      const mouseX = e.clientX / window.innerWidth - 0.5;
      const mouseY = e.clientY / window.innerHeight - 0.5;

      floatingCards.forEach((card, index) => {
        const speed = (index + 1) * 15;
        const x = mouseX * speed;
        const y = mouseY * speed;
        card.style.transform = `translate(${x}px, ${y}px)`;
      });
    });
  }
}

/* ============================================
   FORM HANDLERS
   ============================================ */
function handleContact(e) {
  e.preventDefault();

  const form = e.target;
  const name = form.querySelector('#contact-name')?.value || '';
  const phone = form.querySelector('#contact-phone-input')?.value || '';
  const email = form.querySelector('#contact-email-input')?.value || '';
  const subject = form.querySelector('#contact-subject')?.value || '';
  const message = form.querySelector('#contact-message')?.value || '';

  // Build WhatsApp message
  const whatsappMsg = encodeURIComponent(
    `Hi Anbu! I'm ${name}.\n\n` +
    `📱 Phone: ${phone}\n` +
    `📧 Email: ${email}\n` +
    `📋 Interest: ${subject}\n\n` +
    `💬 Message: ${message}`
  );

  // Open WhatsApp with the message
  window.open(`https://wa.me/917406174324?text=${whatsappMsg}`, '_blank');

  // Show success feedback
  showToast('Message sent! We\'ll get back to you soon. 🐔');

  // Reset form
  form.reset();
}

function handleNewsletter(e) {
  e.preventDefault();

  const form = e.target;
  const emailInput = form.querySelector('input[type="email"]');
  if (!emailInput || !emailInput.value) return;

  showToast('Thanks for subscribing! 🎉 Check your email for weekly offers.');
  emailInput.value = '';
}

/* ============================================
   TOAST NOTIFICATION
   ============================================ */
function showToast(message) {
  // Remove any existing toast
  const existingToast = document.querySelector('.toast');
  if (existingToast) existingToast.remove();

  // Create toast
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;

  // Style inline to keep it self-contained
  Object.assign(toast.style, {
    position: 'fixed',
    bottom: '100px',
    left: '50%',
    transform: 'translateX(-50%) translateY(20px)',
    background: '#1A1A2E',
    color: 'white',
    padding: '16px 32px',
    borderRadius: '12px',
    fontSize: '0.95rem',
    fontFamily: "'Inter', sans-serif",
    fontWeight: '500',
    boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
    zIndex: '10000',
    opacity: '0',
    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
    maxWidth: '90%',
    textAlign: 'center'
  });

  document.body.appendChild(toast);

  // Animate in
  requestAnimationFrame(() => {
    toast.style.opacity = '1';
    toast.style.transform = 'translateX(-50%) translateY(0)';
  });

  // Auto remove after 4s
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(-50%) translateY(20px)';
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

/* ============================================
   PRODUCT CARD HOVER EFFECTS (Enhanced)
   ============================================ */
document.querySelectorAll('.product-card').forEach(card => {
  card.addEventListener('mouseenter', function () {
    this.style.borderImage = 'linear-gradient(135deg, rgba(200, 68, 46, 0.3), rgba(212, 160, 23, 0.3)) 1';
  });

  card.addEventListener('mouseleave', function () {
    this.style.borderImage = 'none';
  });
});

/* ============================================
   TYPING EFFECT FOR HERO (Subtle)
   ============================================ */
(function addCursorBlink() {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes blink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0; }
    }
  `;
  document.head.appendChild(style);
})();
