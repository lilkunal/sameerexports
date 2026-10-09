// Procedural brass door knocker with a keyframed strike loop (pattern of three.js webgl_animation_keyframes).
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const canvas = document.getElementById('knock');
const wrap = canvas.parentElement;
const still = matchMedia('(prefers-reduced-motion: reduce)').matches;

let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
} catch (e) {
  wrap.classList.add('no3d');
  throw e;
}
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;

const scene = new THREE.Scene();
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 50);
camera.position.set(2.2, 0.6, 6.4);

const brass = new THREE.MeshStandardMaterial({ color: 0xd4a640, metalness: 1, roughness: 0.22 });
const dark = new THREE.MeshStandardMaterial({ color: 0x9a7424, metalness: 1, roughness: 0.38 });
const knocker = new THREE.Group();
scene.add(knocker);

// back plate: a rounded shield, extruded with a bevel
const s = new THREE.Shape();
s.moveTo(0, 1.55);
s.bezierCurveTo(0.75, 1.55, 0.95, 0.9, 0.9, 0.2);
s.bezierCurveTo(0.85, -0.7, 0.45, -1.35, 0, -1.55);
s.bezierCurveTo(-0.45, -1.35, -0.85, -0.7, -0.9, 0.2);
s.bezierCurveTo(-0.95, 0.9, -0.75, 1.55, 0, 1.55);
const plate = new THREE.Mesh(new THREE.ExtrudeGeometry(s, { depth: 0.08, bevelEnabled: true, bevelThickness: 0.06, bevelSize: 0.06, bevelSegments: 6, curveSegments: 48 }), dark);
plate.position.z = -0.14;
knocker.add(plate);
const rim = new THREE.Mesh(new THREE.TorusGeometry(0.42, 0.05, 20, 64), brass);
rim.position.set(0, 0.95, 0.02);
knocker.add(rim);
const boss = new THREE.Mesh(new THREE.SphereGeometry(0.2, 32, 24), brass);
boss.position.set(0, 0.95, 0.02);
boss.scale.z = 0.6;
knocker.add(boss);
const striker = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.2, 0.16, 40), brass);
striker.rotation.x = Math.PI / 2;
striker.position.set(0, -1.12, 0.04);
knocker.add(striker);

// hinge pivot + swinging ring (the animated part)
const hinge = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.62, 32), brass);
hinge.rotation.z = Math.PI / 2;
hinge.position.set(0, 0.48, 0.16);
knocker.add(hinge);
const pivot = new THREE.Group();
pivot.name = 'pivot';
pivot.position.set(0, 0.48, 0.16);
knocker.add(pivot);
const ring = new THREE.Mesh(new THREE.TorusGeometry(0.72, 0.1, 32, 96), brass);
ring.position.y = -0.74;
pivot.add(ring);
const drop = new THREE.Mesh(new THREE.SphereGeometry(0.14, 32, 24), brass);
drop.position.y = -1.48;
pivot.add(drop);

// keyframes: lift the ring, strike the plate, small bounce, rest
const q = (x) => new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), x).toArray();
const times = [0, 0.9, 1.25, 1.42, 1.6, 1.78, 3.6];
const angles = [0, 0.75, -0.04, 0.16, 0, 0.04, 0];
const swing = new THREE.QuaternionKeyframeTrack('pivot.quaternion', times, angles.flatMap(q));
const clip = new THREE.AnimationClip('knock', 3.6, [swing]);
const mixer = new THREE.AnimationMixer(knocker);
mixer.clipAction(clip).play();

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.enableZoom = false;
controls.enablePan = false;
controls.autoRotate = !still;
controls.autoRotateSpeed = 0.9;
controls.minPolarAngle = Math.PI * 0.3;
controls.maxPolarAngle = Math.PI * 0.62;
controls.target.set(0, 0, 0);

function size() {
  const w = wrap.clientWidth, h = wrap.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
new ResizeObserver(size).observe(wrap);
size();

const clock = new THREE.Clock();
let visible = true;
new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(canvas);
renderer.setAnimationLoop(() => {
  const dt = clock.getDelta();
  if (!visible) return;
  if (!still) mixer.update(dt);
  controls.update();
  renderer.render(scene, camera);
});
wrap.classList.add('ready');
