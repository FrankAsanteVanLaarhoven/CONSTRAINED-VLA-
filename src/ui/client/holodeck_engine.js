import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export class HolodeckEngine {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, this.container.clientWidth / this.container.clientHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        
        this.init();
    }

    init() {
        // Setup Renderer
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.container.appendChild(this.renderer.domElement);

        // Lighting (Cyberpunk Style)
        const ambientLight = new THREE.AmbientLight(0x404040, 2); // Soft white light
        this.scene.add(ambientLight);

        const pointLight = new THREE.PointLight(0x00f2ff, 1, 100);
        pointLight.position.set(10, 10, 10);
        this.scene.add(pointLight);
        
        const gridHelper = new THREE.GridHelper(50, 50, 0x00f2ff, 0x222222);
        this.scene.add(gridHelper);

        // Voxel World (Minecraft Style Floor)
        const geometry = new THREE.BoxGeometry(1, 1, 1);
        const material = new THREE.MeshLambertMaterial({ color: 0x222222 });
        
        for (let x = -5; x < 5; x++) {
            for (let z = -5; z < 5; z++) {
                if (Math.random() > 0.8) { // Random "Obstacles"
                    const voxel = new THREE.Mesh(geometry, new THREE.MeshLambertMaterial({ color: 0xff2a6d }));
                    voxel.position.set(x * 1, 0.5, z * 1);
                    this.scene.add(voxel);
                }
            }
        }

        // Robot Avatar (Simple Blocky Twin)
        this.robot = new THREE.Group();
        
        // Base
        const baseGeo = new THREE.BoxGeometry(0.8, 0.2, 0.8);
        const baseMat = new THREE.MeshStandardMaterial({ color: 0xaaaaaa });
        const base = new THREE.Mesh(baseGeo, baseMat);
        this.robot.add(base);
        
        // Torso
        const torsoGeo = new THREE.BoxGeometry(0.4, 0.8, 0.2);
        const torso = new THREE.Mesh(torsoGeo, new THREE.MeshStandardMaterial({ color: 0x00f2ff, emissive: 0x001133 }));
        torso.position.y = 0.5;
        this.robot.add(torso);
        
        // Head
        const headGeo = new THREE.BoxGeometry(0.3, 0.3, 0.3);
        const head = new THREE.Mesh(headGeo, new THREE.MeshStandardMaterial({ color: 0xffffff }));
        head.position.y = 1.1;
        this.robot.add(head);

        // Arms (Pivot points for IK)
        this.leftArm = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.6, 0.1), new THREE.MeshStandardMaterial({ color: 0x888888 }));
        this.leftArm.position.set(-0.3, 0.8, 0);
        this.robot.add(this.leftArm);
        
        this.rightArm = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.6, 0.1), new THREE.MeshStandardMaterial({ color: 0x888888 }));
        this.rightArm.position.set(0.3, 0.8, 0);
        this.robot.add(this.rightArm);

        this.scene.add(this.robot);

        // Camera
        this.camera.position.set(0, 5, 5);
        this.camera.lookAt(0, 0, 0);

        // Controls
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;

        // Render Loop
        this.animate();
        
        // Resize Listener
        window.addEventListener('resize', () => this.onWindowResize(), false);
    }
    
    updateRobotPose(handData) {
        // "Virtual Kinetics": Map MediaPipe hand Y to Robot Arm Rotation
        if (handData && handData.y) {
            // Simple mapping: Hand up (0.0) -> Arm up (-Math.PI/2)
            // MediaPipe Y is 0 (top) to 1 (bottom)
            const angle = (1 - handData.y) * Math.PI - (Math.PI / 2); // Map 0..1 to -90..+90 deg approx
            this.rightArm.rotation.x = -angle; // Rotate arm x-axis
        }
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Idle Animation
        this.robot.position.y = Math.sin(Date.now() * 0.002) * 0.05 + 0.1;

        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    onWindowResize() {
        this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    }
}
