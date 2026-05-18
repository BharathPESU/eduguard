import { useEffect, useRef } from 'react'
import * as THREE from 'three'

const canUseWebGL = () => {
  const canvas = document.createElement('canvas')
  return Boolean(
    window.WebGLRenderingContext &&
    (canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
  )
}

const NeuralCanvas = () => {
  const mountRef = useRef(null)

  useEffect(() => {
    const mount = mountRef.current
    if (!mount) return
    if (!canUseWebGL()) return

    const width = mount.clientWidth
    const height = mount.clientHeight

    // Scene
    const scene = new THREE.Scene()

    // Camera
    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000)
    camera.position.z = 80

    // Renderer
    let renderer
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    } catch {
      return
    }

    renderer.setSize(width, height)
    renderer.setPixelRatio(window.devicePixelRatio)
    renderer.setClearColor(0x000000, 0)
    mount.appendChild(renderer.domElement)

    // Particles (nodes)
    const nodeCount = 120
    const positions = []
    const nodes = []

    for (let i = 0; i < nodeCount; i++) {
      const x = (Math.random() - 0.5) * 160
      const y = (Math.random() - 0.5) * 100
      const z = (Math.random() - 0.5) * 60
      positions.push(new THREE.Vector3(x, y, z))
    }

    // Node geometry
    const nodeGeometry = new THREE.SphereGeometry(0.4, 8, 8)

    positions.forEach((pos) => {
      const hue = 0.55 + Math.random() * 0.15 // blue to cyan range
      const color = new THREE.Color().setHSL(hue, 1, 0.6)
      const mat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.8 })
      const mesh = new THREE.Mesh(nodeGeometry, mat)
      mesh.position.copy(pos)
      scene.add(mesh)
      nodes.push({
        mesh,
        velocity: new THREE.Vector3(
          (Math.random() - 0.5) * 0.04,
          (Math.random() - 0.5) * 0.04,
          (Math.random() - 0.5) * 0.02
        ),
        originalY: pos.y
      })
    })

    // Lines (connections)
    const linesGroup = new THREE.Group()
    scene.add(linesGroup)

    const updateLines = () => {
      linesGroup.clear()
      const threshold = 28

      for (let i = 0; i < positions.length; i++) {
        for (let j = i + 1; j < positions.length; j++) {
          const dist = positions[i].distanceTo(positions[j])
          if (dist < threshold) {
            const opacity = (1 - dist / threshold) * 0.3
            const mat = new THREE.LineBasicMaterial({
              color: 0x00D4FF,
              transparent: true,
              opacity,
            })
            const geo = new THREE.BufferGeometry().setFromPoints([
              positions[i].clone(),
              positions[j].clone(),
            ])
            linesGroup.add(new THREE.Line(geo, mat))
          }
        }
      }
    }

    updateLines()

    // Mouse parallax
    let mouseX = 0
    let mouseY = 0
    const handleMouseMove = (e) => {
      mouseX = (e.clientX / window.innerWidth - 0.5) * 2
      mouseY = (e.clientY / window.innerHeight - 0.5) * 2
    }
    window.addEventListener('mousemove', handleMouseMove)

    // Resize
    const handleResize = () => {
      const w = mount.clientWidth
      const h = mount.clientHeight
      renderer.setSize(w, h)
      camera.aspect = w / h
      camera.updateProjectionMatrix()
    }
    window.addEventListener('resize', handleResize)

    // Animation loop
    let frameCount = 0
    let animationId
    const animate = () => {
      animationId = requestAnimationFrame(animate)
      frameCount++

      nodes.forEach((node, i) => {
        node.mesh.position.add(node.velocity)
        positions[i].copy(node.mesh.position)

        // Boundary bounce
        if (Math.abs(node.mesh.position.x) > 80) node.velocity.x *= -1
        if (Math.abs(node.mesh.position.y) > 50) node.velocity.y *= -1
        if (Math.abs(node.mesh.position.z) > 30) node.velocity.z *= -1

        // Pulse opacity
        node.mesh.material.opacity = 0.5 + Math.sin(frameCount * 0.02 + i) * 0.3
      })

      // Update lines every 3 frames for performance
      if (frameCount % 3 === 0) updateLines()

      // Camera parallax on mouse
      camera.position.x += (mouseX * 8 - camera.position.x) * 0.03
      camera.position.y += (-mouseY * 5 - camera.position.y) * 0.03
      camera.lookAt(scene.position)

      renderer.render(scene, camera)
    }

    animate()

    return () => {
      cancelAnimationFrame(animationId)
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('resize', handleResize)
      if (mount.contains(renderer.domElement)) {
        mount.removeChild(renderer.domElement)
      }
      renderer.dispose()
    }
  }, [])

  return (
    <div
      ref={mountRef}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 0,
        background: [
          'radial-gradient(circle at 20% 30%, rgba(0,212,255,0.18), transparent 28%)',
          'radial-gradient(circle at 80% 40%, rgba(0,255,136,0.12), transparent 26%)',
          'linear-gradient(135deg, rgba(21,72,183,0.14), rgba(10,15,30,0.4))',
        ].join(', '),
      }}
    />
  )
}

export default NeuralCanvas
