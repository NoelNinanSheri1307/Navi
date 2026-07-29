/**
 * Navi Framework — Advanced Microscopic Traffic Simulation Engine
 * Canvas-based visualization of intersection signal phases with car deceleration,
 * smooth follower queuing models, and active countdown timers.
 */

export class TrafficSim {
    constructor(canvas, greenTimes = [30, 30, 30, 30], themeColor = "#10b981", congestionPressure = 80, avgSpeed = 2.5) {
        this.canvas = canvas;
        this.ctx = canvas.getContext("2d");
        this.greenTimes = greenTimes;
        this.themeColor = themeColor;
        this.pressure = congestionPressure;
        this.running = true;

        // Lanes aligned to drive on the right side of the road
        this.lanes = [
            { id: "North", cars: [], direction: [0, 1], spawnX: 380, spawnY: -50, stopY: 185, name: "NORTH" },
            { id: "South", cars: [], direction: [0, -1], spawnX: 420, spawnY: 550, stopY: 315, name: "SOUTH" },
            { id: "East", cars: [], direction: [1, 0], spawnX: -50, spawnY: 265, stopX: 345, name: "EAST" },
            { id: "West", cars: [], direction: [-1, 0], spawnX: 850, spawnY: 235, stopX: 455, name: "WEST" },
        ];

        this.currentLane = 0;
        this.cycleTimer = 0;
        this.maxSpeed = Math.max(1.5, Math.min(5.0, avgSpeed));
        this.carSpacing = 38; // Safe physical bounding limit

        this.metrics = {
            avgWait: 0,
            throughput: 0,
            activeCars: 0,
            queueLength: 0
        };

        // Elegant professional UI vehicle palette
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

        // 2. Dynamic Spawning Model (Proportional to congestion pressure + minimum occupancy)
        const activeCarCount = this.lanes.reduce((acc, l) => acc + l.cars.length, 0);
        const baseProb = 0.03 + (this.pressure / 1500);
        const spawnProbability = activeCarCount < 4 ? 0.3 : Math.min(0.18, baseProb);

        if (Math.random() < spawnProbability) {
            this.spawnCar(Math.floor(Math.random() * 4));
        }

        // 3. Microscopic Follower Physics updates
        this.metrics.queueLength = 0;

        this.lanes.forEach((lane, idx) => {
            const isGreen = this.currentLane === idx;
            
            for (let i = 0; i < lane.cars.length; i++) {
                const car = lane.cars[i];
                const nextCar = i > 0 ? lane.cars[i - 1] : null;
                let targetSpeed = this.maxSpeed;

                const atLight = this.isAtLight(car, lane);
                
                // Decelerate smoothly at red lights
                if (!isGreen && atLight) {
                    let distToStop = 999;
                    if (lane.id === "North") distToStop = lane.stopY - car.y;
                    else if (lane.id === "South") distToStop = car.y - lane.stopY;
                    else if (lane.id === "East") distToStop = lane.stopX - car.x;
                    else if (lane.id === "West") distToStop = car.x - lane.stopX;

                    if (distToStop > 0 && distToStop < 100) {
                        targetSpeed = this.maxSpeed * (distToStop / 100);
                        if (distToStop < 15) {
                            targetSpeed = 0;
                            this.metrics.queueLength++;
                        }
                    } else if (distToStop <= 0) {
                        targetSpeed = 0;
                    }
                }

                // Decelerate smoothly behind trailing vehicle to prevent overlaps
                if (nextCar) {
                    const dist = this.getDistance(car, nextCar);
                    const safeDistance = this.carSpacing;
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

                // Smooth acceleration adjustments
                car.speed += (targetSpeed - car.speed) * 0.12;
                if (car.speed < 0.02) car.speed = 0;
                
                // Update coordinates
                car.x += car.vx * car.speed;
                car.y += car.vy * car.speed;
            }

            // Exited vehicles filtering
            const initialCount = lane.cars.length;
            lane.cars = lane.cars.filter(car => car.x >= -120 && car.x <= 920 && car.y >= -120 && car.y <= 620);
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
            if (dist < 55) return; // Prevent spawning overlap collisions
        }

        lane.cars.push({
            x: lane.spawnX,
            y: lane.spawnY,
            vx: lane.direction[0],
            vy: lane.direction[1],
            speed: this.maxSpeed * 0.8,
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
        
        // 1. Draw Asphalt Background Layout
        this.ctx.fillStyle = "#09090b";
        this.ctx.fillRect(0, 0, 800, 500);

        // Dark grey road lanes cross section
        this.ctx.fillStyle = "#121215";
        this.ctx.fillRect(350, 0, 100, 500); // Vertical road
        this.ctx.fillRect(0, 200, 800, 100); // Horizontal road

        // Road lane center dividing lines
        this.ctx.strokeStyle = "rgba(255,255,255,0.06)";
        this.ctx.setLineDash([12, 18]);
        this.ctx.lineWidth = 1.5;
        this.ctx.beginPath();
        this.ctx.moveTo(400, 0); this.ctx.lineTo(400, 500);
        this.ctx.moveTo(0, 250); this.ctx.lineTo(800, 250);
        this.ctx.stroke();
        this.ctx.setLineDash([]);

        // Stop Bars
        this.ctx.fillStyle = "rgba(255,255,255,0.15)";
        this.ctx.fillRect(350, 182, 50, 3); // North Stop line
        this.ctx.fillRect(400, 315, 50, 3); // South Stop line
        this.ctx.fillRect(342, 250, 3, 50); // East Stop line
        this.ctx.fillRect(455, 200, 3, 50); // West Stop line

        // 2. Active Lane Guidance Arrow Animation
        this.ctx.save();
        const activeLane = this.lanes[this.currentLane];
        if (activeLane) {
            this.ctx.strokeStyle = this.themeColor;
            this.ctx.lineWidth = 2.5;
            this.ctx.shadowBlur = 8;
            this.ctx.shadowColor = this.themeColor;
            this.ctx.setLineDash([4, 6]);
            this.ctx.beginPath();
            if (activeLane.id === "North") {
                this.ctx.moveTo(380, 50); this.ctx.lineTo(380, 150);
            } else if (activeLane.id === "South") {
                this.ctx.moveTo(420, 450); this.ctx.lineTo(420, 350);
            } else if (activeLane.id === "East") {
                this.ctx.moveTo(50, 265); this.ctx.lineTo(300, 265);
            } else if (activeLane.id === "West") {
                this.ctx.moveTo(750, 235); this.ctx.lineTo(500, 235);
            }
            this.ctx.stroke();
        }
        this.ctx.restore();

        // 3. Traffic Signals with glowing visual indicators and timers
        const signals = [
            { id: 0, x: 335, y: 175, name: "NORTH" },
            { id: 1, x: 465, y: 325, name: "SOUTH" },
            { id: 2, x: 335, y: 325, name: "EAST" },
            { id: 3, x: 465, y: 175, name: "WEST" },
        ];

        signals.forEach((s, idx) => {
            const isGreen = this.currentLane === idx;
            
            // Draw Signal Body Box
            this.ctx.fillStyle = "#1e1e24";
            this.ctx.strokeStyle = "#27272a";
            this.ctx.lineWidth = 1;
            this.ctx.beginPath();
            this.ctx.roundRect(s.x - 12, s.y - 12, 24, 24, 4);
            this.ctx.fill();
            this.ctx.stroke();

            // Active Glow Light
            this.ctx.save();
            if (isGreen) {
                this.ctx.shadowBlur = 15;
                this.ctx.shadowColor = this.themeColor;
                this.ctx.fillStyle = this.themeColor;
            } else {
                this.ctx.fillStyle = "#7f1d1d"; // Dark red stop light
            }
            this.ctx.beginPath();
            this.ctx.arc(s.x, s.y, 7, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.restore();

            // Print countdown timer text next to the signal light
            if (isGreen) {
                const currentPhaseDuration = this.greenTimes[this.currentLane] || 30;
                const rem = Math.max(0, currentPhaseDuration - this.cycleTimer);
                
                this.ctx.fillStyle = "#ffffff";
                this.ctx.font = "bold 10px monospace";
                this.ctx.textAlign = "center";
                this.ctx.fillText(`${Math.ceil(rem)}s`, s.x, s.y - 18);
            }
        });

        // 4. Draw Vehicles
        this.lanes.forEach(lane => {
            lane.cars.forEach(car => {
                this.ctx.fillStyle = car.color;
                this.ctx.beginPath();
                if (this.ctx.roundRect) {
                    this.ctx.roundRect(car.x - car.width/2, car.y - car.height/2, car.width, car.height, 3.5);
                } else {
                    this.ctx.rect(car.x - car.width/2, car.y - car.height/2, car.width, car.height);
                }
                this.ctx.fill();
            });
        });
    }
}
