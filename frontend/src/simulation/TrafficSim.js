/**
 * Navi Framework — High-Fidelity Microscopic Traffic Simulation Engine
 * Canvas-based visualization of intersection signal phases with physical queuing models,
 * yellow light deceleration transitions, lane trackers, and headlights/taillights drawings.
 */

export class TrafficSim {
    constructor(canvas, greenTimes = [30, 30, 30, 30], themeColor = "#10b981", congestionPressure = 80, avgSpeed = 2.5) {
        this.canvas = canvas;
        this.ctx = canvas.getContext("2d");
        this.greenTimes = greenTimes;
        this.themeColor = themeColor;
        this.pressure = congestionPressure;
        this.running = true;

        // Coordinates aligned to drive on the right side of the road
        this.lanes = [
            { id: "North", cars: [], direction: [0, 1], spawnX: 380, spawnY: -50, stopY: 185, name: "NORTH" },
            { id: "South", cars: [], direction: [0, -1], spawnX: 420, spawnY: 550, stopY: 315, name: "SOUTH" },
            { id: "East", cars: [], direction: [1, 0], spawnX: -50, spawnY: 265, stopX: 345, name: "EAST" },
            { id: "West", cars: [], direction: [-1, 0], spawnX: 850, spawnY: 235, stopX: 455, name: "WEST" },
        ];

        this.currentLane = 0;
        this.cycleTimer = 0;
        this.maxSpeed = Math.max(1.5, Math.min(5.0, avgSpeed));
        
        // Dynamic Spacing Constants
        this.movingSpacing = 42;  // Safe spacing when driving
        this.stoppedSpacing = 28; // Compact spacing when queued

        this.metrics = {
            avgWait: 0,
            throughput: 0,
            activeCars: 0,
            queueLength: 0
        };

        this.carColors = ["#10b981", "#3b82f6", "#f59e0b", "#f43f5e", "#8b5cf6", "#22d3ee", "#e2e8f0"];
    }

    update(dt) {
        if (!this.running) return;

        // 1. Advance Active Phase Timer
        this.cycleTimer += dt / 1000;
        const currentPhaseDuration = this.greenTimes[this.currentLane] || 30;
        
        if (this.cycleTimer >= currentPhaseDuration) {
            this.cycleTimer = 0;
            this.currentLane = (this.currentLane + 1) % 4;
        }

        // 2. Proportional Spawning: Spawns cars stochastically based on queue indices
        const activeCarCount = this.lanes.reduce((acc, l) => acc + l.cars.length, 0);
        
        // Spawn probability linked directly to pressure
        const spawnProbability = activeCarCount < 4 ? 0.35 : Math.min(0.20, 0.04 + (this.pressure / 1200));

        if (Math.random() < spawnProbability) {
            this.spawnCar(Math.floor(Math.random() * 4));
        }

        // 3. Follower Physics with Compression Queues and Yellow Light warnings
        this.metrics.queueLength = 0;
        const yellowTimeLimit = 3.0; // Show yellow for the final 3 seconds
        const currentPhaseRemaining = currentPhaseDuration - this.cycleTimer;
        const isYellowPhase = currentPhaseRemaining <= yellowTimeLimit;

        this.lanes.forEach((lane, idx) => {
            const isGreen = this.currentLane === idx && !isYellowPhase;
            const isYellow = this.currentLane === idx && isYellowPhase;
            
            for (let i = 0; i < lane.cars.length; i++) {
                const car = lane.cars[i];
                const nextCar = i > 0 ? lane.cars[i - 1] : null;
                let targetSpeed = this.maxSpeed;

                const atLight = this.isAtLight(car, lane);
                
                // Decelerate for Red/Yellow lights
                if ((!isGreen && atLight) || (isYellow && atLight)) {
                    let distToStop = 999;
                    if (lane.id === "North") distToStop = lane.stopY - car.y;
                    else if (lane.id === "South") distToStop = car.y - lane.stopY;
                    else if (lane.id === "East") distToStop = lane.stopX - car.x;
                    else if (lane.id === "West") distToStop = car.x - lane.stopX;

                    if (distToStop > 0 && distToStop < 120) {
                        // Harder stop if Red, gentler if Yellow warning
                        const stopFactor = isYellow ? 0.5 : 1.0;
                        targetSpeed = this.maxSpeed * (distToStop / 120) * stopFactor;
                        if (distToStop < 18) {
                            targetSpeed = 0;
                            this.metrics.queueLength++;
                        }
                    } else if (distToStop <= 0) {
                        targetSpeed = 0;
                    }
                }

                // Smooth queue spacing follower model
                if (nextCar) {
                    const dist = this.getDistance(car, nextCar);
                    
                    // Compact spacing when leader is stopped, wider when driving
                    const safeDistance = nextCar.speed < 0.1 ? this.stoppedSpacing : this.movingSpacing;
                    const warningDistance = safeDistance * 2.2;

                    if (dist < safeDistance) {
                        targetSpeed = 0;
                        if (nextCar.speed === 0) {
                            this.metrics.queueLength++;
                        }
                    } else if (dist < warningDistance) {
                        const ratio = (dist - safeDistance) / (warningDistance - safeDistance);
                        targetSpeed = Math.min(nextCar.speed, targetSpeed) * ratio;
                    }
                }

                // Acceleration transitions
                car.speed += (targetSpeed - car.speed) * 0.14;
                if (car.speed < 0.02) car.speed = 0;
                
                car.x += car.vx * car.speed;
                car.y += car.vy * car.speed;
            }

            // Despawn out-of-bounds vehicles
            const initialCount = lane.cars.length;
            lane.cars = lane.cars.filter(car => car.x >= -100 && car.x <= 900 && car.y >= -100 && car.y <= 600);
            const exited = initialCount - lane.cars.length;
            this.metrics.throughput += exited;
        });

        this.metrics.activeCars = this.lanes.reduce((acc, l) => acc + l.cars.length, 0);
    }

    spawnCar(laneIdx) {
        const lane = this.lanes[laneIdx];
        if (lane.cars.length > 0) {
            const last = lane.cars[lane.cars.length - 1];
            const dist = Math.sqrt((last.x - lane.spawnX)**2 + (last.y - lane.spawnY)**2);
            if (dist < 55) return;
        }

        lane.cars.push({
            x: lane.spawnX,
            y: lane.spawnY,
            vx: lane.direction[0],
            vy: lane.direction[1],
            speed: this.maxSpeed * 0.75,
            color: this.carColors[Math.floor(Math.random() * this.carColors.length)],
            width: lane.direction[0] === 0 ? 14 : 22,
            height: lane.direction[0] === 0 ? 22 : 14,
        });
    }

    isAtLight(car, lane) {
        if (lane.id === "North") return car.y < lane.stopY;
        if (lane.id === "South") return car.y > lane.stopY;
        if (lane.id === "East") return car.x < lane.stopX;
        if (lane.id === "West") return car.x > lane.stopX;
        return false;
    }

    getDistance(c1, c2) {
        return Math.sqrt((c1.x - c2.x)**2 + (c1.y - c2.y)**2);
    }

    draw() {
        if (!this.ctx || !this.canvas) return;
        
        // 1. Road Layout
        this.ctx.fillStyle = "#09090b";
        this.ctx.fillRect(0, 0, 800, 500);

        this.ctx.fillStyle = "#111113";
        this.ctx.fillRect(350, 0, 100, 500); // Vertical road
        this.ctx.fillRect(0, 200, 800, 100); // Horizontal road

        this.ctx.strokeStyle = "rgba(255,255,255,0.05)";
        this.ctx.setLineDash([12, 18]);
        this.ctx.lineWidth = 1.5;
        this.ctx.beginPath();
        this.ctx.moveTo(400, 0); this.ctx.lineTo(400, 500);
        this.ctx.moveTo(0, 250); this.ctx.lineTo(800, 250);
        this.ctx.stroke();
        this.ctx.setLineDash([]);

        // White Stop Bars
        this.ctx.fillStyle = "rgba(255,255,255,0.18)";
        this.ctx.fillRect(350, 182, 50, 3);
        this.ctx.fillRect(400, 315, 50, 3);
        this.ctx.fillRect(342, 250, 3, 50);
        this.ctx.fillRect(455, 200, 3, 50);

        // 2. Active Phase Guides
        this.ctx.save();
        const activeLane = this.lanes[this.currentLane];
        const yellowTimeLimit = 3.0;
        const currentPhaseDuration = this.greenTimes[this.currentLane] || 30;
        const currentPhaseRemaining = currentPhaseDuration - this.cycleTimer;
        const isYellowPhase = currentPhaseRemaining <= yellowTimeLimit;
        const activeColor = isYellowPhase ? "#eab308" : this.themeColor;

        if (activeLane) {
            this.ctx.strokeStyle = activeColor;
            this.ctx.lineWidth = 2;
            this.ctx.shadowBlur = 10;
            this.ctx.shadowColor = activeColor;
            this.ctx.setLineDash([6, 8]);
            this.ctx.beginPath();
            if (activeLane.id === "North") {
                this.ctx.moveTo(380, 40); this.ctx.lineTo(380, 150);
            } else if (activeLane.id === "South") {
                this.ctx.moveTo(420, 460); this.ctx.lineTo(420, 350);
            } else if (activeLane.id === "East") {
                this.ctx.moveTo(40, 265); this.ctx.lineTo(310, 265);
            } else if (activeLane.id === "West") {
                this.ctx.moveTo(760, 235); this.ctx.lineTo(490, 235);
            }
            this.ctx.stroke();
        }
        this.ctx.restore();

        // 3. Signals with yellow transitions and timers
        const signals = [
            { id: 0, x: 335, y: 175 },
            { id: 1, x: 465, y: 325 },
            { id: 2, x: 335, y: 325 },
            { id: 3, x: 465, y: 175 },
        ];

        signals.forEach((s, idx) => {
            const isActive = this.currentLane === idx;
            const lightColor = isActive ? (isYellowPhase ? "#eab308" : this.themeColor) : "#7f1d1d";
            
            // Signal Box
            this.ctx.fillStyle = "#1e1e24";
            this.ctx.strokeStyle = "#27272a";
            this.ctx.lineWidth = 1;
            this.ctx.beginPath();
            this.ctx.roundRect(s.x - 12, s.y - 12, 24, 24, 4);
            this.ctx.fill();
            this.ctx.stroke();

            // Bulb Glow
            this.ctx.save();
            if (isActive) {
                this.ctx.shadowBlur = 15;
                this.ctx.shadowColor = lightColor;
            }
            this.ctx.fillStyle = lightColor;
            this.ctx.beginPath();
            this.ctx.arc(s.x, s.y, 7, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.restore();

            // Floating countdown text
            if (isActive) {
                const rem = Math.max(0, currentPhaseDuration - this.cycleTimer);
                this.ctx.fillStyle = "#ffffff";
                this.ctx.font = "bold 10px monospace";
                this.ctx.textAlign = "center";
                this.ctx.fillText(`${Math.ceil(rem)}s`, s.x, s.y - 18);
            }
        });

        // 4. Vehicles with Headlights/Taillights
        this.lanes.forEach(lane => {
            lane.cars.forEach(car => {
                this.ctx.fillStyle = car.color;
                this.ctx.beginPath();
                if (this.ctx.roundRect) {
                    this.ctx.roundRect(car.x - car.width/2, car.y - car.height/2, car.width, car.height, 4);
                } else {
                    this.ctx.rect(car.x - car.width/2, car.y - car.height/2, car.width, car.height);
                }
                this.ctx.fill();

                // Draw Headlights & Taillights for realism
                this.ctx.fillStyle = "#fef08a"; // Yellow headlights
                if (lane.direction[0] === 0) { // Vertical moving
                    const yOffset = lane.direction[1] * (car.height / 2);
                    this.ctx.fillRect(car.x - car.width/2 + 2, car.y + yOffset - 1, 2, 2);
                    this.ctx.fillRect(car.x + car.width/2 - 4, car.y + yOffset - 1, 2, 2);
                    
                    this.ctx.fillStyle = "#ef4444"; // Red brake lights
                    const tailOffset = -lane.direction[1] * (car.height / 2);
                    this.ctx.fillRect(car.x - car.width/2 + 2, car.y + tailOffset - 1, 2, 2);
                    this.ctx.fillRect(car.x + car.width/2 - 4, car.y + tailOffset - 1, 2, 2);
                } else { // Horizontal moving
                    const xOffset = lane.direction[0] * (car.width / 2);
                    this.ctx.fillRect(car.x + xOffset - 1, car.y - car.height/2 + 2, 2, 2);
                    this.ctx.fillRect(car.x + xOffset - 1, car.y + car.height/2 - 4, 2, 2);

                    this.ctx.fillStyle = "#ef4444"; // Red brake lights
                    const tailOffset = -lane.direction[0] * (car.width / 2);
                    this.ctx.fillRect(car.x + tailOffset - 1, car.y - car.height/2 + 2, 2, 2);
                    this.ctx.fillRect(car.x + tailOffset - 1, car.y + car.height/2 - 4, 2, 2);
                }
            });
        });
    }
}
