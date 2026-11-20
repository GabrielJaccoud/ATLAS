import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";

export type SceneNode = {
  id: string;
  label: string;
  weight?: number;
  tone?: "gold" | "blue" | "cyan" | "amber";
};

export type SceneEdge = { source: string; target: string; weight?: number };

type Props = {
  mode?: "core" | "worlds" | "network";
  state?: string;
  nodes?: SceneNode[];
  edges?: SceneEdge[];
  className?: string;
};

const colors = {
  gold: 0xc9a96a,
  blue: 0x4da3ff,
  cyan: 0x57e6d9,
  amber: 0xe0a34a,
};

function pointOnShell(index: number, count: number, radius: number) {
  const goldenAngle = Math.PI * (3 - Math.sqrt(5));
  const y = 1 - (index / Math.max(count - 1, 1)) * 2;
  const ring = Math.sqrt(Math.max(0, 1 - y * y));
  const angle = goldenAngle * index;
  return new THREE.Vector3(Math.cos(angle) * ring * radius, y * radius, Math.sin(angle) * ring * radius);
}

export default function AtlasScene3D({
  mode = "core",
  state = "ready",
  nodes = [],
  edges = [],
  className = "",
}: Props) {
  const mountRef = useRef<HTMLDivElement>(null);
  const stateRef = useRef(state);
  const drawRef = useRef<(() => void) | null>(null);
  const [fallback, setFallback] = useState(false);
  const nodeSignature = nodes.map((node) => `${node.id}:${node.weight ?? 0}:${node.tone ?? ""}`).join("|");
  const edgeSignature = edges.map((edge) => `${edge.source}:${edge.target}:${edge.weight ?? 1}`).join("|");

  useEffect(() => {
    stateRef.current = state;
    drawRef.current?.();
  }, [state]);

  useEffect(() => {
    const host = mountRef.current;
    if (!host) return;

    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: "low-power" });
    } catch {
      setFallback(true);
      return;
    }
    setFallback(false);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 30);
    camera.position.set(0, 0, mode === "core" ? 5.0 : 5.7);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    renderer.setClearColor(0x000000, 0);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.08;
    renderer.domElement.className = "atlas-scene-canvas";
    renderer.domElement.setAttribute("aria-hidden", "true");
    host.appendChild(renderer.domElement);

    const world = new THREE.Group();
    scene.add(world);
    scene.add(new THREE.AmbientLight(0x93a9bd, 1.05));
    const keyLight = new THREE.PointLight(colors.cyan, 42, 12);
    keyLight.position.set(2.2, 1.5, 3.5);
    scene.add(keyLight);
    const rimLight = new THREE.PointLight(colors.gold, 28, 10);
    rimLight.position.set(-2.5, -1.2, -2.2);
    scene.add(rimLight);

    const nucleusMaterial = new THREE.MeshPhysicalMaterial({
      color: 0x101b26,
      metalness: 0.58,
      roughness: 0.24,
      clearcoat: 1,
      clearcoatRoughness: 0.16,
      emissive: state === "critical" ? 0x4c1716 : state === "alert" ? 0x392a15 : 0x082b40,
      emissiveIntensity: state === "critical" ? 0.55 : state === "alert" ? 0.36 : 0.48,
    });
    const nucleus = new THREE.Mesh(new THREE.SphereGeometry(mode === "core" ? 0.84 : 0.56, 56, 40), nucleusMaterial);
    world.add(nucleus);

    const innerMaterial = new THREE.MeshPhysicalMaterial({
        color: state === "critical" ? 0xb65448 : state === "alert" ? 0xb58a4c : 0x6dbfca,
        metalness: 0.56,
        roughness: 0.22,
        clearcoat: 1,
        emissive: state === "critical" ? 0x54201b : 0x16404c,
        emissiveIntensity: 0.9,
      });
    const innerCore = new THREE.Mesh(new THREE.IcosahedronGeometry(mode === "core" ? 0.39 : 0.25, 2), innerMaterial);
    world.add(innerCore);

    const latitude = new THREE.Mesh(
      new THREE.SphereGeometry(mode === "core" ? 0.92 : 0.62, 32, 20),
      new THREE.MeshBasicMaterial({ color: colors.cyan, wireframe: true, transparent: true, opacity: 0.105 }),
    );
    world.add(latitude);

    const orbitMaterials = [
      new THREE.MeshBasicMaterial({ color: colors.gold, transparent: true, opacity: 0.54 }),
      new THREE.MeshBasicMaterial({ color: colors.blue, transparent: true, opacity: 0.42 }),
      new THREE.MeshBasicMaterial({ color: colors.cyan, transparent: true, opacity: 0.28 }),
    ];
    const orbits: THREE.Mesh[] = [];
    [1.14, 1.34, 1.56].forEach((radius, index) => {
      const orbit = new THREE.Mesh(new THREE.TorusGeometry(radius, index === 0 ? 0.006 : 0.003, 8, 144), orbitMaterials[index]);
      orbit.rotation.set(index * 0.63 + 0.45, index * 0.84, index * 0.39);
      world.add(orbit);
      orbits.push(orbit);
    });

    const positionById = new Map<string, THREE.Vector3>();
    const scenePoints = mode === "core" ? [] : nodes;
    const pointRadius = mode === "network" ? 1.48 : 1.12;
    scenePoints.forEach((node, index) => {
      const position = pointOnShell(index, scenePoints.length, pointRadius);
      positionById.set(node.id, position);
      const nodeRadius = 0.026 + Math.min(Math.max(node.weight ?? 0.5, 0), 1) * 0.048;
      const color = colors[node.tone || (mode === "worlds" ? "gold" : "cyan")];
      const mesh = new THREE.Mesh(
        new THREE.SphereGeometry(nodeRadius, 16, 12),
        new THREE.MeshStandardMaterial({ color, metalness: 0.45, roughness: 0.25, emissive: color, emissiveIntensity: 0.28 }),
      );
      mesh.position.copy(position);
      world.add(mesh);
    });

    const lineMaterial = new THREE.LineBasicMaterial({ color: mode === "worlds" ? colors.gold : colors.blue, transparent: true, opacity: 0.28 });
    const linePairs = mode === "worlds"
      ? scenePoints.slice(1).map((node, index) => [scenePoints[index].id, node.id] as const)
      : edges.map((edge) => [edge.source, edge.target] as const);
    linePairs.forEach(([source, target]) => {
      const start = positionById.get(source);
      const end = positionById.get(target);
      if (!start || !end) return;
      const arcMid = start.clone().add(end).multiplyScalar(0.5).normalize().multiplyScalar(pointRadius + 0.22);
      const curve = new THREE.QuadraticBezierCurve3(start, arcMid, end);
      world.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(curve.getPoints(28)), lineMaterial));
    });

    if (mode === "core") {
      const starPositions = new Float32Array(180 * 3);
      for (let index = 0; index < 180; index += 1) {
        const point = pointOnShell(index, 180, 1.78 + (index % 7) * 0.045);
        starPositions[index * 3] = point.x;
        starPositions[index * 3 + 1] = point.y;
        starPositions[index * 3 + 2] = point.z;
      }
      const starGeometry = new THREE.BufferGeometry();
      starGeometry.setAttribute("position", new THREE.BufferAttribute(starPositions, 3));
      world.add(new THREE.Points(starGeometry, new THREE.PointsMaterial({ color: colors.cyan, size: 0.012, transparent: true, opacity: 0.52, sizeAttenuation: true })));
    }

    let appliedState = stateRef.current;
    const renderFrame = () => {
      const nextState = stateRef.current;
      if (nextState !== appliedState) {
        const critical = nextState === "critical";
        const alert = nextState === "alert";
        nucleusMaterial.emissive.setHex(critical ? 0x4c1716 : alert ? 0x392a15 : 0x082b40);
        nucleusMaterial.emissiveIntensity = critical ? 0.55 : alert ? 0.36 : 0.48;
        innerMaterial.color.setHex(critical ? 0xb65448 : alert ? 0xb58a4c : 0x6dbfca);
        innerMaterial.emissive.setHex(critical ? 0x54201b : 0x16404c);
        appliedState = nextState;
      }
      renderer.render(scene, camera);
    };
    drawRef.current = renderFrame;
    const resize = () => {
      const width = Math.max(1, host.clientWidth);
      const height = Math.max(1, host.clientHeight);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height, false);
      renderFrame();
    };
    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(host);
    resize();

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let targetX = 0;
    let targetY = 0;
    const pointerMove = (event: PointerEvent) => {
      const rect = host.getBoundingClientRect();
      targetY = ((event.clientX - rect.left) / rect.width - 0.5) * 0.34;
      targetX = ((event.clientY - rect.top) / rect.height - 0.5) * 0.24;
    };
    const pointerLeave = () => { targetX = 0; targetY = 0; };
    host.addEventListener("pointermove", pointerMove);
    host.addEventListener("pointerleave", pointerLeave);

    const animate = (time: number) => {
      if (document.hidden || !host.isConnected) return;
      const seconds = time * 0.001;
      world.rotation.x += (targetX - world.rotation.x) * 0.025;
      world.rotation.y += (targetY + Math.sin(seconds * 0.16) * 0.07 - world.rotation.y) * 0.025;
      innerCore.rotation.x = seconds * 0.11;
      innerCore.rotation.y = seconds * 0.17;
      latitude.rotation.y = -seconds * 0.035;
      orbits.forEach((orbit, index) => { orbit.rotation.z += (index % 2 ? -1 : 1) * 0.0008; });
      renderFrame();
    };
    if (!reducedMotion) renderer.setAnimationLoop(animate);
    else renderFrame();

    const visibility = () => {
      if (reducedMotion) return;
      renderer.setAnimationLoop(document.hidden ? null : animate);
    };
    document.addEventListener("visibilitychange", visibility);

    return () => {
      document.removeEventListener("visibilitychange", visibility);
      host.removeEventListener("pointermove", pointerMove);
      host.removeEventListener("pointerleave", pointerLeave);
      resizeObserver.disconnect();
      if (drawRef.current === renderFrame) drawRef.current = null;
      renderer.setAnimationLoop(null);
      const geometries = new Set<THREE.BufferGeometry>();
      const materials = new Set<THREE.Material>();
      scene.traverse((object) => {
        const mesh = object as THREE.Mesh;
        if (mesh.geometry) geometries.add(mesh.geometry);
        const material = mesh.material;
        if (Array.isArray(material)) material.forEach((item) => materials.add(item));
        else if (material) materials.add(material);
      });
      geometries.forEach((geometry) => geometry.dispose());
      materials.forEach((material) => material.dispose());
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, [mode, nodeSignature, edgeSignature]);

  return (
    <div className={`atlas-scene-3d ${className} ${fallback ? "fallback" : ""}`} data-state={state} aria-hidden="true">
      <div className="atlas-scene-glow" />
      <div className="atlas-scene-fallback" />
      <div className="atlas-scene-mount" ref={mountRef} />
    </div>
  );
}
