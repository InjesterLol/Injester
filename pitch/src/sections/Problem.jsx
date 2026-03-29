import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import './Problem.css'

const RAW_HTML_LINES = [
  '<!DOCTYPE html>',
  '<html lang="en" dir="ltr" class="js-focus-visible" data-js-focus-visible>',
  '<head>',
  '  <meta charset="utf-8">',
  '  <script src="/analytics/gtm.js?id=GTM-XXXX"></script>',
  '  <script src="/vendor/tracking-pixel.min.js"></script>',
  '  <link rel="stylesheet" href="/css/bundle.7f3a2b.css">',
  '  <link rel="stylesheet" href="/css/vendor.d91c4e.css">',
  '  <link rel="stylesheet" href="/css/marketing.2b8f91.css">',
  '  <style>/* 2,847 lines of inline CSS */</style>',
  '</head>',
  '<body class="page-booking responsive-grid theme-travel">',
  '  <div id="app-shell" data-reactroot>',
  '    <nav class="global-header" role="navigation">',
  '      <div class="header-inner">',
  '        <div class="logo-wrapper">...</div>',
  '        <ul class="nav-links" aria-label="Main">',
  '          <li><a href="/deals">Deals</a></li>',
  '          <li><a href="/destinations">Destinations</a></li>',
  '          <li><a href="/loyalty">MileagePlus</a></li>',
  '          <!-- 14 more nav items -->',
  '        </ul>',
  '        <div class="user-menu">...</div>',
  '      </div>',
  '    </nav>',
  '    <div class="hero-banner" style="background-image:url(hero.webp)">',
  '      <div class="promo-overlay">',
  '        <h2>Spring Sale: Save up to 20%</h2>',
  '        <p>Book by March 31...</p>',
  '      </div>',
  '    </div>',
  '    <main id="booking-widget" class="search-form-container">',
  '      <form action="/api/search" method="POST">',
  '        <div class="form-group trip-type">',
  '          <label>Round trip</label>',
  '          <label>One-way</label>',
  '          <label>Multi-city</label>',
  '        </div>',
  '        <div class="form-group origin">',
  '          <input placeholder="From" autocomplete="off"/>',
  '        </div>',
  '        <div class="form-group destination">',
  '          <input placeholder="To" autocomplete="off"/>',
  '        </div>',
  '        <!-- ...200 more lines of form HTML... -->',
  '      </form>',
  '    </main>',
  '    <section class="upsell-carousel">',
  '      <!-- 34 promotional cards -->',
  '    </section>',
  '    <section class="partner-offers">',
  '      <!-- hotel, car rental, insurance cross-sell -->',
  '    </section>',
  '    <footer class="global-footer">',
  '      <!-- 89 links, legal text, cookie consent -->',
  '    </footer>',
  '  </div>',
  '  <script src="/js/vendor.bundle.3fa82b.js"></script>',
  '  <script src="/js/app.bundle.91d2ef.js"></script>',
  '  <script src="/js/tracking.bundle.a7c1d3.js"></script>',
  '  <script>/* 340 lines of inline analytics */</script>',
  '  <div id="modal-root"></div>',
  '  <div id="tooltip-root"></div>',
  '  <div id="cookie-consent" class="gdpr-banner">...</div>',
  '</body>',
  '</html>',
]

export default function Problem() {
  const sectionRef = useRef(null)
  const counterRef = useRef(null)
  const codeRef = useRef(null)
  const noiseRefs = useRef([])

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Fade in section
      gsap.fromTo(
        '.problem-label',
        { opacity: 0, x: -20 },
        {
          opacity: 1,
          x: 0,
          duration: 0.6,
          scrollTrigger: {
            trigger: sectionRef.current,
            start: 'top 80%',
          },
        }
      )

      gsap.fromTo(
        '.problem-title',
        { opacity: 0, y: 20 },
        {
          opacity: 1,
          y: 0,
          duration: 0.6,
          scrollTrigger: {
            trigger: sectionRef.current,
            start: 'top 75%',
          },
        }
      )

      gsap.fromTo(
        '.problem-desc',
        { opacity: 0, y: 15 },
        {
          opacity: 1,
          y: 0,
          duration: 0.5,
          scrollTrigger: {
            trigger: sectionRef.current,
            start: 'top 70%',
          },
        }
      )

      // Animate token counter
      const counter = { val: 0 }
      gsap.to(counter, {
        val: 45280,
        duration: 2,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: '.html-viewer',
          start: 'top 70%',
        },
        onUpdate: () => {
          if (counterRef.current) {
            counterRef.current.textContent = Math.floor(counter.val).toLocaleString()
          }
        },
      })

      // Code lines reveal
      gsap.fromTo(
        '.code-line',
        { opacity: 0, x: -10 },
        {
          opacity: 1,
          x: 0,
          duration: 0.3,
          stagger: 0.03,
          scrollTrigger: {
            trigger: '.html-viewer',
            start: 'top 75%',
          },
        }
      )

      // Highlight noise elements
      ScrollTrigger.create({
        trigger: '.noise-callouts',
        start: 'top 60%',
        onEnter: () => {
          gsap.to('.noise-tag', {
            opacity: 1,
            scale: 1,
            duration: 0.4,
            stagger: 0.15,
          })
        },
      })
    }, sectionRef)

    return () => ctx.revert()
  }, [])

  return (
    <section ref={sectionRef} className="problem-section">
      <div className="problem-inner">
        <div className="problem-text">
          <span className="problem-label label label-orange">THE PROBLEM</span>
          <h2 className="problem-title">
            An AI agent sees <em>everything</em>
          </h2>
          <p className="problem-desc">
            When an agent visits a booking site, it doesn't see a clean search form.
            It sees 45,000 tokens of navigation bars, tracking scripts, promotional
            carousels, cookie banners, and inline CSS. The actual content — the part
            that matters — is buried in noise.
          </p>

          <div className="noise-callouts">
            <div className="noise-item">
              <span className="noise-tag" style={{ opacity: 0, transform: 'scale(0.8)' }}>
                <span className="noise-pct">38%</span>
                <span className="noise-what">scripts &amp; tracking</span>
              </span>
            </div>
            <div className="noise-item">
              <span className="noise-tag" style={{ opacity: 0, transform: 'scale(0.8)' }}>
                <span className="noise-pct">24%</span>
                <span className="noise-what">navigation &amp; chrome</span>
              </span>
            </div>
            <div className="noise-item">
              <span className="noise-tag" style={{ opacity: 0, transform: 'scale(0.8)' }}>
                <span className="noise-pct">19%</span>
                <span className="noise-what">CSS &amp; styling</span>
              </span>
            </div>
            <div className="noise-item">
              <span className="noise-tag" style={{ opacity: 0, transform: 'scale(0.8)' }}>
                <span className="noise-pct">12%</span>
                <span className="noise-what">promotions &amp; ads</span>
              </span>
            </div>
            <div className="noise-item">
              <span className="noise-tag highlight" style={{ opacity: 0, transform: 'scale(0.8)' }}>
                <span className="noise-pct">7%</span>
                <span className="noise-what">actual content</span>
              </span>
            </div>
          </div>
        </div>

        <div className="problem-viz">
          <div className="html-viewer">
            <div className="viewer-header">
              <span className="viewer-title mono">RAW HTML</span>
              <div className="token-badge">
                <span className="token-icon">&#9679;</span>
                <span ref={counterRef} className="token-count mono">0</span>
                <span className="token-label mono">tokens</span>
              </div>
            </div>
            <div ref={codeRef} className="viewer-code">
              {RAW_HTML_LINES.map((line, i) => (
                <div key={i} className="code-line" style={{ opacity: 0 }}>
                  <span className="line-num">{i + 1}</span>
                  <span className={`line-content ${getLineClass(line)}`}>
                    {line}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function getLineClass(line) {
  if (line.includes('script') || line.includes('analytics') || line.includes('tracking'))
    return 'line-noise'
  if (line.includes('style') || line.includes('css') || line.includes('CSS'))
    return 'line-noise'
  if (line.includes('nav') || line.includes('footer') || line.includes('cookie') || line.includes('modal'))
    return 'line-noise'
  if (line.includes('promo') || line.includes('upsell') || line.includes('partner') || line.includes('banner'))
    return 'line-noise'
  if (line.includes('form') || line.includes('input') || line.includes('booking') || line.includes('search'))
    return 'line-content-highlight'
  if (line.includes('<!--'))
    return 'line-comment'
  return ''
}
