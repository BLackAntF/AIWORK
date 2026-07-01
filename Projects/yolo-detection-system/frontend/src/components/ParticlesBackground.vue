<template>
  <canvas ref="canvasRef" class="particles-canvas"></canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useThemeStore } from '@/store/modules/theme'

const canvasRef = ref(null)
const themeStore = useThemeStore()

let ctx = null
let animationId = null
let particles = []
let mouse = { x: null, y: null, radius: 80 }

const particleCount = 80
const lineDistance = 150

function initParticles() {
  const canvas = canvasRef.value
  if (!canvas) return

  particles = []
  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      radius: Math.random() * 2 + 1,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5
    })
  }
}

function resizeCanvas() {
  const canvas = canvasRef.value
  if (!canvas) return

  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  initParticles()
}

function getColors() {
  const isDark = themeStore.isDark
  return {
    particleColor: isDark ? 'rgba(212, 175, 55, 0.5)' : 'rgba(224, 122, 95, 0.5)',
    lineColorBase: isDark ? 'rgba(212, 175, 55,' : 'rgba(224, 122, 95,',
    mouseGlowColor: isDark ? 'rgba(212, 175, 55, 0.2)' : 'rgba(224, 122, 95, 0.2)'
  }
}

function animate() {
  const canvas = canvasRef.value
  if (!canvas || !ctx) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  const colors = getColors()

  particles.forEach((p, i) => {
    p.x += p.vx
    p.y += p.vy

    if (p.x < 0 || p.x > canvas.width) p.vx *= -1
    if (p.y < 0 || p.y > canvas.height) p.vy *= -1

    if (mouse.x !== null && mouse.y !== null) {
      const dx = p.x - mouse.x
      const dy = p.y - mouse.y
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < mouse.radius) {
        const force = (mouse.radius - dist) / mouse.radius
        p.x += dx * force * 0.02
        p.y += dy * force * 0.02
      }
    }

    ctx.beginPath()
    ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
    ctx.fillStyle = colors.particleColor
    ctx.fill()

    particles.slice(i + 1).forEach(p2 => {
      const dx = p.x - p2.x
      const dy = p.y - p2.y
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < lineDistance) {
        ctx.beginPath()
        ctx.moveTo(p.x, p.y)
        ctx.lineTo(p2.x, p2.y)
        const opacity = 0.15 * (1 - dist / lineDistance)
        ctx.strokeStyle = colors.lineColorBase + opacity + ')'
        ctx.stroke()
      }
    })

    if (mouse.x !== null && mouse.y !== null) {
      const dx = p.x - mouse.x
      const dy = p.y - mouse.y
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < mouse.radius) {
        ctx.beginPath()
        ctx.moveTo(p.x, p.y)
        ctx.lineTo(mouse.x, mouse.y)
        const opacity = 0.3 * (1 - dist / mouse.radius)
        ctx.strokeStyle = colors.lineColorBase + opacity + ')'
        ctx.stroke()
      }
    }
  })

  if (mouse.x !== null && mouse.y !== null) {
    const gradient = ctx.createRadialGradient(
      mouse.x, mouse.y, 0,
      mouse.x, mouse.y, mouse.radius
    )
    gradient.addColorStop(0, colors.mouseGlowColor)
    gradient.addColorStop(1, 'transparent')
    ctx.beginPath()
    ctx.arc(mouse.x, mouse.y, mouse.radius, 0, Math.PI * 2)
    ctx.fillStyle = gradient
    ctx.fill()
  }

  animationId = requestAnimationFrame(animate)
}

function handleMouseMove(e) {
  mouse.x = e.clientX
  mouse.y = e.clientY
}

function handleMouseLeave() {
  mouse.x = null
  mouse.y = null
}

onMounted(() => {
  const canvas = canvasRef.value
  if (!canvas) return

  ctx = canvas.getContext('2d')
  resizeCanvas()
  animate()

  window.addEventListener('resize', resizeCanvas)
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mouseleave', handleMouseLeave)
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  window.removeEventListener('resize', resizeCanvas)
  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('mouseleave', handleMouseLeave)
})

watch(() => themeStore.isDark, () => {})
</script>

<style scoped>
.particles-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}
</style>
